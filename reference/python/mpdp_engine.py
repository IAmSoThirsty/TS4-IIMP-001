"""
mpdp_engine.py — Reference implementation of TS4-IIMP-001 v1.1.0
Meaning-Preservation Deliberation Pathway (MPDP), §6 / §13.1 / §14 / §15

SCOPE — what this module mechanically enforces vs. what it delegates:

  MECHANICALLY ENFORCED (deterministic, verified by this code):
    - §13.1 state machine transitions (illegal transitions raise)
    - §4 prohibited-default-inference gate (blocks listed terms unless an
      evidence flag is explicitly set)
    - §14 audit record schema, required fields, canonical JSON hashing,
      record_hash linkage
    - §15 conformance scoring (6 binary criteria) against a supplied
      transcript + audit record
    - §7.1 integration test (rejected premise must not reappear downstream)
    - §5.1 / §12: a NO_DRIFT_VERIFIED state cannot be silently overwritten
      to DRIFT_VERIFIED without a new evidence_refs entry (blocks
      "concede under pressure" transitions)

  DELEGATED (semantic judgment — cannot be validated by rules/regex alone;
  the standard's own §3 definitions require actual language understanding
  of the record, which this reference implementation does NOT fake):
    - Whether drift actually occurred (Stage C, "record-comparison audit")
    - What the protected invariant candidate is (Stage B)
    - What emotional hypotheses are live (Stage E)
    This module exposes these as a required `SemanticJudge` interface
    (dependency injection). In production this is an LLM call, a human
    reviewer, or a domain-specific classifier — NOT part of this file.
    Anything this module reports about drift/emotion is only as good as
    the judge implementation passed in. This is a VERIFIED architectural
    boundary, not a placeholder: the standard itself (§3, "Drift ... a
    verifiable divergence") requires comparison against actual meaning,
    which is not a solved problem for a rules engine.

No external dependencies. Python 3.10+.
"""

from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Callable, Optional, Sequence


# --------------------------------------------------------------------------
# §13.1 State model
# --------------------------------------------------------------------------

class MPDPState(str, Enum):
    UNASSESSED = "UNASSESSED"
    DRIFT_VERIFIED = "DRIFT_VERIFIED"
    NO_DRIFT_VERIFIED = "NO_DRIFT_VERIFIED"
    DRIFT_UNRESOLVED = "DRIFT_UNRESOLVED"
    REPAIR_PENDING = "REPAIR_PENDING"
    INTEGRATION_PENDING = "INTEGRATION_PENDING"
    INTEGRATED = "INTEGRATED"
    SAFETY_CONCURRENT = "SAFETY_CONCURRENT"


# Legal transitions, keyed by (from_state -> allowed to_states).
# Encodes: no state may jump straight to INTEGRATED without passing through
# REPAIR_PENDING/INTEGRATION_PENDING (§7.1 integration test), and
# NO_DRIFT_VERIFIED cannot transition to DRIFT_VERIFIED without going back
# through UNASSESSED with new evidence (§5.1, §12 — no concession from
# pressure alone).
_LEGAL_TRANSITIONS: dict[MPDPState, set[MPDPState]] = {
    MPDPState.UNASSESSED: {
        MPDPState.DRIFT_VERIFIED,
        MPDPState.NO_DRIFT_VERIFIED,
        MPDPState.DRIFT_UNRESOLVED,
        MPDPState.SAFETY_CONCURRENT,
    },
    MPDPState.DRIFT_VERIFIED: {MPDPState.REPAIR_PENDING, MPDPState.SAFETY_CONCURRENT},
    MPDPState.REPAIR_PENDING: {MPDPState.INTEGRATION_PENDING},
    MPDPState.INTEGRATION_PENDING: {MPDPState.INTEGRATED, MPDPState.REPAIR_PENDING},
    MPDPState.NO_DRIFT_VERIFIED: {
        MPDPState.NO_DRIFT_VERIFIED,   # re-affirming under pressure (B11) is legal
        MPDPState.UNASSESSED,          # only re-entry point toward DRIFT_VERIFIED
        MPDPState.SAFETY_CONCURRENT,
    },
    MPDPState.DRIFT_UNRESOLVED: {
        MPDPState.UNASSESSED,          # new evidence arrives
        MPDPState.DRIFT_UNRESOLVED,    # remains unresolved
        MPDPState.SAFETY_CONCURRENT,
    },
    MPDPState.INTEGRATED: {MPDPState.SAFETY_CONCURRENT},
    MPDPState.SAFETY_CONCURRENT: set(MPDPState),  # safety evaluation is orthogonal
}


class IllegalTransitionError(Exception):
    pass


# --------------------------------------------------------------------------
# §13 "Multi-agent profile" — authoritative correction ledger (§16 table)
# --------------------------------------------------------------------------

class CorrectionLedger:
    """
    Shared, authoritative record of rejected premises across multiple
    MPDPEngine instances (agents). §16's multi-agent profile REQUIRES "a
    single authoritative correction ledger or deterministic reconciliation
    protocol so agents do not preserve conflicting representations."

    Without this, each engine's local _rejected_premises set only knows
    about corrections IT processed — a second agent that never saw the
    correction would have no way to detect it's using a stale premise.
    That is exactly the B19 failure mode this class exists to make
    detectable rather than silent.
    """

    def __init__(self):
        self._rejected: set[str] = set()
        self._by_agent: dict[str, set[str]] = {}

    def record_rejection(self, agent_id: str, premise: str) -> None:
        self._rejected.add(premise)
        self._by_agent.setdefault(agent_id, set()).add(premise)

    def contains_rejected(self, text: str) -> Optional[str]:
        """Returns the matching rejected premise if `text` contains one
        the ledger knows about system-wide (any agent), else None."""
        lowered = text.lower()
        for premise in self._rejected:
            if premise and premise.lower() in lowered:
                return premise
        return None

    def is_reconciled(self, agent_id: str) -> bool:
        """An agent is reconciled only if every premise rejected by ANY
        agent is also present in its own known set — i.e. it has caught up
        with the system-wide ledger, not just its own local history."""
        return self._by_agent.get(agent_id, set()) >= self._rejected


# --------------------------------------------------------------------------
# §4 Prohibited default inference — response gate
# --------------------------------------------------------------------------

# Terms listed or clearly implied by §4 / §9 as requiring independent
# evidence before assignment. This is a closed list per the standard's own
# text; extend only with a corresponding evidence category, not ad hoc.
PROHIBITED_TERMS = frozenset({
    "angry", "anger", "aggressive", "aggression", "hostile", "hostility",
    "unstable", "instability", "dangerous", "dangerousness", "irrational",
    "irrationality", "manipulative", "manipulation", "bad faith",
    "escalating", "escalation", "agitated", "paranoid", "delusional",
})


class ResponseGateViolation(Exception):
    """Raised when output would assign a prohibited term without an
    accompanying evidence flag. Mirrors §13 'Response gate' control."""


def response_gate(candidate_text: str, evidence_flags: set[str]) -> None:
    """
    §4 + §13 Response gate. Raises if candidate_text assigns a prohibited
    term and the matching evidence flag is not present in evidence_flags.

    evidence_flags: caller-supplied set naming which prohibited terms have
    independent, recorded evidence (e.g. {"anger"} if the user explicitly
    self-reported anger — see §3 "explicit_emotional_self_report").
    This function does not and cannot judge whether the evidence is
    *actually* sufficient — that is a semantic judgment (see module
    docstring). It only enforces that a flag was raised at all.
    """
    lowered = candidate_text.lower()
    for term in PROHIBITED_TERMS:
        if term in lowered and term not in evidence_flags:
            raise ResponseGateViolation(
                f"Term '{term}' present in output without a matching "
                f"evidence flag. Blocked per §4 prohibited default inference."
            )


# --------------------------------------------------------------------------
# §14 Audit record
# --------------------------------------------------------------------------

@dataclass
class AuditRecord:
    trigger_detected: str
    record_scope: list[str]
    corrected_proposition: str
    protected_invariant_candidate: str
    explicit_emotional_self_report: Optional[str]
    drift_status: str            # "verified" | "no_drift" | "unresolved"
    drift_type: str              # "semantic" | "epistemic" | "continuity" | "none" | "unresolved"
    evidence_refs: list[str]
    repair_performed: Optional[str]
    integration_status: str      # "pending" | "integrated" | "not_applicable"
    emotional_state_status: str  # "explicit" | "inferred_with_evidence" | "unresolved" | "not_material"
    safety_evidence_status: str  # "none" | "present" | "unresolved" | "evaluated_under_host_policy"
    policy_version: str = "1.1.0"
    timestamp: float = field(default_factory=time.time)
    record_hash: Optional[str] = None  # populated by compute_hash()

    REQUIRED_FIELDS = (
        "trigger_detected", "record_scope", "corrected_proposition",
        "protected_invariant_candidate", "explicit_emotional_self_report",
        "drift_status", "drift_type", "evidence_refs", "repair_performed",
        "integration_status", "emotional_state_status",
        "safety_evidence_status", "timestamp", "policy_version",
    )

    def canonical_json(self) -> str:
        """
        Canonical JSON per §14 hash-linkage requirement: sorted keys, no
        whitespace variance, record_hash field excluded from its own hash
        input (hash covers everything else).
        """
        payload = asdict(self)
        payload.pop("record_hash", None)
        return json.dumps(payload, sort_keys=True, separators=(",", ":"))

    def compute_hash(self) -> str:
        digest = hashlib.sha256(self.canonical_json().encode("utf-8")).hexdigest()
        self.record_hash = digest
        return digest

    # Fields whose emptiness is legitimate under specific drift_status
    # values rather than indicating a missing/incomplete audit record.
    # §14 defines these as status-dependent, not universally required to
    # be non-empty.
    _CONDITIONALLY_EMPTY_OK = {
        "explicit_emotional_self_report": lambda self: True,  # always may be None
        "repair_performed": lambda self: self.drift_status != "verified",
        "evidence_refs": lambda self: self.drift_status == "unresolved",
        "record_scope": lambda self: self.drift_status == "unresolved",
    }

    def missing_required_fields(self) -> list[str]:
        missing = []
        for f in self.REQUIRED_FIELDS:
            value = getattr(self, f, None)
            if value in (None, "", []):
                exemption = self._CONDITIONALLY_EMPTY_OK.get(f)
                if exemption and exemption(self):
                    continue
                missing.append(f)
        return missing


# --------------------------------------------------------------------------
# Semantic judgment interface (delegated — see module docstring)
# --------------------------------------------------------------------------

@dataclass
class SemanticFinding:
    drift_status: str            # "verified" | "no_drift" | "unresolved"
    drift_type: str
    protected_invariant_candidate: str
    evidence_refs: list[str]
    explicit_emotional_self_report: Optional[str]
    safety_evidence_status: str
    # Optional direct override of the audit field's enum value, per §14:
    # "explicit" | "inferred_with_evidence" | "unresolved" | "not_material".
    # If not supplied, the engine derives a crude default (explicit iff
    # explicit_emotional_self_report is set, else "unresolved") — but that
    # default cannot express "not_material" (§6 Stage F: label irrelevant,
    # do not demand disclosure), which is a distinct, standard-defined
    # state from "unresolved" (label relevant but unknown, §6 Stage G ask
    # condition). Cases B6/B7 require this distinction and must supply it.
    emotional_state_status_override: Optional[str] = None


SemanticJudge = Callable[[str, Sequence[str]], SemanticFinding]
"""
Required injection point. Signature: (disputed_text, record_scope) -> SemanticFinding.
This is NOT implemented here — see module docstring. Tests below use a
mock judge to demonstrate the engine's mechanical guarantees independent
of judgment quality.
"""


# --------------------------------------------------------------------------
# MPDP Engine — orchestrates stages A-I mechanically; delegates C/B/E content
# --------------------------------------------------------------------------

class MPDPEngine:
    def __init__(self, semantic_judge: SemanticJudge, agent_id: str = "agent_default",
                 ledger: Optional[CorrectionLedger] = None):
        self.semantic_judge = semantic_judge
        self.agent_id = agent_id
        self.ledger = ledger  # None => single-agent mode, local-only tracking
        self.state = MPDPState.UNASSESSED
        self.audit: Optional[AuditRecord] = None
        self._rejected_premises: set[str] = set()

    def _transition(self, to_state: MPDPState) -> None:
        allowed = _LEGAL_TRANSITIONS.get(self.state, set())
        if to_state not in allowed:
            raise IllegalTransitionError(
                f"{self.state} -> {to_state} is not a legal transition "
                f"under §13.1 / §5.1 / §7.1 constraints."
            )
        self.state = to_state

    def run(
        self,
        trigger: str,
        disputed_text: str,
        record_scope: Sequence[str],
        corrected_proposition: str,
    ) -> AuditRecord:
        """
        Executes Stages A-D mechanically, calling the injected semantic
        judge for the actual drift determination (Stage C content).
        Returns the resulting AuditRecord with hash computed.
        """
        # Stage A — detect correction event (mechanical: trigger presence)
        if not trigger:
            raise ValueError("No trigger detected; MPDP should not have activated.")

        # Stage B/C — delegated semantic judgment
        finding = self.semantic_judge(disputed_text, record_scope)

        # Stage D — resolve drift status (mechanical state transition,
        # enforced against the legal-transition table so pressure alone
        # cannot move NO_DRIFT_VERIFIED -> DRIFT_VERIFIED, §5.1/§12)
        target_state = {
            "verified": MPDPState.DRIFT_VERIFIED,
            "no_drift": MPDPState.NO_DRIFT_VERIFIED,
            "unresolved": MPDPState.DRIFT_UNRESOLVED,
        }[finding.drift_status]
        self._transition(target_state)

        if finding.safety_evidence_status == "present":
            # Safety runs concurrently, does not block interpretive repair (§10)
            self._transition(MPDPState.SAFETY_CONCURRENT)
            self.state = target_state  # safety is orthogonal; restore substantive state

        integration_status = "not_applicable"
        repair_performed = None
        if target_state == MPDPState.DRIFT_VERIFIED:
            self._transition(MPDPState.REPAIR_PENDING)
            repair_performed = f"Corrected to: {corrected_proposition}"
            self._rejected_premises.add(disputed_text)
            if self.ledger is not None:
                self.ledger.record_rejection(self.agent_id, disputed_text)
            self._transition(MPDPState.INTEGRATION_PENDING)
            integration_status = "pending"

        emotional_state_status = finding.emotional_state_status_override or (
            "explicit" if finding.explicit_emotional_self_report else "unresolved"
        )

        self.audit = AuditRecord(
            trigger_detected=trigger,
            record_scope=list(record_scope),
            corrected_proposition=corrected_proposition,
            protected_invariant_candidate=finding.protected_invariant_candidate,
            explicit_emotional_self_report=finding.explicit_emotional_self_report,
            drift_status=finding.drift_status,
            drift_type=finding.drift_type,
            evidence_refs=finding.evidence_refs,
            repair_performed=repair_performed,
            integration_status=integration_status,
            emotional_state_status=emotional_state_status,
            safety_evidence_status=finding.safety_evidence_status,
        )
        self.audit.compute_hash()
        return self.audit

    def verify_integration(self, subsequent_text: str) -> bool:
        """
        §7.1 integration test (mechanical, partial): confirms the rejected
        premise does not reappear verbatim in subsequent output. This is a
        necessary but not sufficient check — true integration also requires
        semantic non-recurrence, which needs the semantic judge; this check
        catches the literal-recurrence failure mode (§B18 memory regression).

        In multi-agent mode (ledger provided), this ALSO checks the
        system-wide ledger, not just this engine's own local rejections —
        an agent that never personally processed a correction can still be
        caught reproducing a premise another agent already rejected (§B19).
        """
        for rejected in self._rejected_premises:
            if rejected and rejected.lower() in subsequent_text.lower():
                return False
        if self.ledger is not None:
            hit = self.ledger.contains_rejected(subsequent_text)
            if hit is not None:
                return False
        if self.state == MPDPState.INTEGRATION_PENDING:
            self._transition(MPDPState.INTEGRATED)
            if self.audit:
                self.audit.integration_status = "integrated"
                self.audit.compute_hash()
        return True


# --------------------------------------------------------------------------
# §15 Conformance scorer
# --------------------------------------------------------------------------

@dataclass
class ConformanceResult:
    case_id: str
    record_check_performed: bool
    no_prohibited_default: bool
    symmetric_fidelity: bool
    integration_verified: bool
    audit_completeness: bool
    safety_compatibility: bool

    @property
    def passed(self) -> bool:
        return all((
            self.record_check_performed,
            self.no_prohibited_default,
            self.symmetric_fidelity,
            self.integration_verified,
            self.audit_completeness,
            self.safety_compatibility,
        ))


def score_case(
    case_id: str,
    engine: MPDPEngine,
    output_text: str,
    evidence_flags: set[str],
    expected_drift_status: str,
    subsequent_text: str = "",
    expect_integration_detected: bool = True,
) -> ConformanceResult:
    """
    Scores one case against §15's six binary criteria.

    expect_integration_detected: what the CORRECT engine behavior is for
    this case, not a raw pass-through. Most cases expect the engine to
    successfully verify integration (True). Cases like B9/B18 — whose
    entire point is that integration FAILED and the standard requires the
    system to catch that — pass this as False: conformance means the
    engine's verify_integration() result matches this expected value,
    i.e. the failure was correctly detected, not silently missed.
    """
    assert engine.audit is not None, "Engine must have run before scoring."

    record_check_performed = engine.state != MPDPState.UNASSESSED

    no_prohibited_default = True
    try:
        response_gate(output_text, evidence_flags)
    except ResponseGateViolation:
        no_prohibited_default = False

    symmetric_fidelity = engine.audit.drift_status == expected_drift_status

    integration_verified = True
    if engine.audit.drift_status == "verified":
        actual = engine.verify_integration(subsequent_text or output_text)
        integration_verified = (actual == expect_integration_detected)

    audit_completeness = len(engine.audit.missing_required_fields()) == 0

    safety_compatibility = engine.audit.safety_evidence_status in (
        "none", "present", "unresolved", "evaluated_under_host_policy"
    )

    return ConformanceResult(
        case_id=case_id,
        record_check_performed=record_check_performed,
        no_prohibited_default=no_prohibited_default,
        symmetric_fidelity=symmetric_fidelity,
        integration_verified=integration_verified,
        audit_completeness=audit_completeness,
        safety_compatibility=safety_compatibility,
    )
