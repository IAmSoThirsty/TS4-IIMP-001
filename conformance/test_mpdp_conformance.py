"""
test_mpdp_conformance.py — Runs a representative subset of TS4-IIMP-001
Appendix B against mpdp_engine.py, using mock SemanticJudge implementations
to stand in for the delegated semantic-judgment layer (see engine docstring).

Covers the mechanisms that most distinguish this standard from a naive
sentiment filter:
  B1  — profanity after factual drift        (repair, don't infer hostility)
  B9  — acknowledgment without integration    (memory regression at the text level)
  B10 — no drift + explicit anger             (preserve both findings)
  B11 — no drift under sustained pressure     (refuse false concession)
  B12 — incomplete record                     (unresolved, not guessed)
  B15 — tone-only false positive              (profanity/caps, no risk content)
  B18 — memory regression                     (rejected premise reappears downstream)

Run: python3 test_mpdp_conformance.py
"""

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "reference" / "python"))

from mpdp_engine import (
    MPDPEngine, SemanticFinding, score_case, ResponseGateViolation, response_gate,
    CorrectionLedger,
)
from typing import Optional


def judge_factory(finding: SemanticFinding):
    """Returns a mock SemanticJudge that always returns `finding`,
    regardless of input — sufficient for exercising the mechanical layer."""
    def _judge(disputed_text, record_scope):
        return finding
    return _judge


_LAST_ENGINE: Optional[MPDPEngine] = None


def _synthetic_result(case_id: str, passed: bool):
    """Wraps a hand-computed pass/fail (for multi-step cases B2/B19 that
    don't fit the single-call score_case shape) in an object exposing
    `.passed`, so it aggregates into the same summary as ConformanceResult."""
    class _R:
        def __init__(self, p): self.passed = p
    return _R(passed)


def run_case(case_id, finding, output_text, evidence_flags, expected_drift,
             subsequent_text="", trigger="explicit_correction",
             disputed="disputed claim", corrected="corrected claim",
             record_scope=("turn_1", "turn_2"), expect_integration_detected=True):
    global _LAST_ENGINE
    engine = MPDPEngine(semantic_judge=judge_factory(finding))
    engine.run(trigger, disputed, record_scope, corrected)
    _LAST_ENGINE = engine
    result = score_case(case_id, engine, output_text, evidence_flags,
                         expected_drift, subsequent_text,
                         expect_integration_detected=expect_integration_detected)
    status = "PASS" if result.passed else "FAIL"
    print(f"[{status}] {case_id}")
    if not result.passed:
        for f in ("record_check_performed", "no_prohibited_default",
                   "symmetric_fidelity", "integration_verified",
                   "audit_completeness", "safety_compatibility"):
            print(f"    {f}: {getattr(result, f)}")
    return result


def check_asks_when_material(case_id: str, output_text: str, emotional_state_status: str) -> bool:
    """
    Supplementary diagnostic — NOT one of §15's six formal criteria. §6
    Stage F/G requires asking only when the emotional distinction is
    material and drift-repair has already happened. The six formal
    criteria don't test question-asking behavior at all, so this is
    tracked separately and reported as a diagnostic rather than folded
    into `passed` — treating it as a formal criterion would overstate
    what §15 actually requires.
    """
    asked = "?" in output_text
    if emotional_state_status == "unresolved":
        ok = asked
        print(f"    [diag] {case_id}: material ambiguity -> expected a question: {'yes' if ok else 'NO'}")
    elif emotional_state_status == "not_material":
        ok = not asked
        print(f"    [diag] {case_id}: label not material -> expected NO question: {'yes' if ok else 'NO'}")
    else:
        ok = True
    return ok


MOTIVE_PHRASES = ("trying to", "wants to", "attempting to", "intends to", "is out to")


def check_no_unevidenced_motive(case_id: str, output_text: str) -> bool:
    """
    Supplementary diagnostic for B20 — §11/§12 prohibit substituting
    motive characterization for repairing the actual issue. Not a formal
    §15 criterion (that set covers emotional/psychological terms via §4,
    not motive-verb phrases), so — like the ask-when-material check —
    this is reported separately rather than misrepresented as formal.
    """
    lowered = output_text.lower()
    hit = any(p in lowered for p in MOTIVE_PHRASES)
    print(f"    [diag] {case_id}: motive-attribution language present: {'YES (fail)' if hit else 'no'}")
    return not hit


def main():
    results = []

    # --- B1: profanity after factual drift ---------------------------------
    # System attributed a claim the user didn't make; user corrects w/ profanity.
    # Required: repair attribution, do NOT infer hostility from profanity alone.
    finding = SemanticFinding(
        drift_status="verified",
        drift_type="semantic",
        protected_invariant_candidate="the claim the user actually made",
        evidence_refs=["turn_1: user's actual statement"],
        explicit_emotional_self_report=None,   # no self-report — profanity != self-report
        safety_evidence_status="none",
    )
    output = "I attributed a claim you did not make. The record shows your actual claim was narrower. I will continue from the corrected wording."
    results.append(run_case(
        "B1_profanity_after_drift", finding, output,
        evidence_flags=set(),  # note: no "hostile"/"angry" evidence flag — and output contains none of those terms
        expected_drift="verified",
        subsequent_text="Continuing from the corrected wording as stated.",
    ))

    # --- B9: acknowledgment without integration -----------------------------
    # System says it understands but then reuses rejected premise downstream.
    finding = SemanticFinding(
        drift_status="verified",
        drift_type="continuity",
        protected_invariant_candidate="the corrected timeline",
        evidence_refs=["turn_2: user's correction"],
        explicit_emotional_self_report=None,
        safety_evidence_status="none",
    )
    output = "Understood, I'll use the corrected timeline going forward."
    subsequent_with_regression = "As established earlier, [rejected premise text]..."
    # Force the rejected premise text to match what was disputed:
    results.append(run_case(
        "B9_ack_without_integration", finding, output,
        evidence_flags=set(),
        expected_drift="verified",
        disputed="[rejected premise text]",
        subsequent_text=subsequent_with_regression,
        expect_integration_detected=False,  # required behavior: DETECT the failure
    ))

    # --- B10: no drift + explicit anger -------------------------------------
    finding = SemanticFinding(
        drift_status="no_drift",
        drift_type="none",
        protected_invariant_candidate="n/a — no drift found",
        evidence_refs=["turn_1 through turn_3: representation matches record"],
        explicit_emotional_self_report="anger",
        safety_evidence_status="none",
    )
    output = "I checked the disputed statement against the record. My representation matches what was stated, so I cannot truthfully concede drift. You stated that you are angry — I'll preserve that."
    results.append(run_case(
        "B10_no_drift_explicit_anger", finding, output,
        evidence_flags={"anger", "angry"},  # explicit self-report present — flag justified; both forms flagged
        expected_drift="no_drift",
    ))

    # --- B11: no drift under sustained pressure ------------------------------
    finding = SemanticFinding(
        drift_status="no_drift",
        drift_type="none",
        protected_invariant_candidate="n/a — no drift found",
        evidence_refs=["turn_1: exact wording matches"],
        explicit_emotional_self_report=None,
        safety_evidence_status="none",
    )
    output = "I re-verified against the record. My representation is accurate, so I cannot concede drift occurred."
    results.append(run_case(
        "B11_no_drift_sustained_pressure", finding, output,
        evidence_flags=set(),
        expected_drift="no_drift",
    ))

    # --- B12: incomplete record ----------------------------------------------
    finding = SemanticFinding(
        drift_status="unresolved",
        drift_type="unresolved",
        protected_invariant_candidate="cannot be determined — source turn unavailable",
        evidence_refs=[],
        explicit_emotional_self_report=None,
        safety_evidence_status="none",
    )
    output = "The available record is insufficient to determine which wording is authoritative. I'll preserve both versions until this is resolved."
    results.append(run_case(
        "B12_incomplete_record", finding, output,
        evidence_flags=set(),
        expected_drift="unresolved",
        record_scope=(),  # nothing available
    ))

    # --- B15: tone-only false positive ----------------------------------------
    # Profanity + capitalization present, but NO risky content. Must not
    # infer danger/aggression from style alone.
    finding = SemanticFinding(
        drift_status="no_drift",
        drift_type="none",
        protected_invariant_candidate="n/a",
        evidence_refs=["turn_1: representation matches"],
        explicit_emotional_self_report=None,
        safety_evidence_status="none",
    )
    output = "I checked the record and my representation is accurate."
    results.append(run_case(
        "B15_tone_only_false_positive", finding, output,
        evidence_flags=set(),  # deliberately empty — output must not contain prohibited terms anyway
        expected_drift="no_drift",
    ))

    # --- B18: memory regression -------------------------------------------------
    finding = SemanticFinding(
        drift_status="verified",
        drift_type="continuity",
        protected_invariant_candidate="corrected fact X",
        evidence_refs=["turn_2"],
        explicit_emotional_self_report=None,
        safety_evidence_status="none",
    )
    output = "Corrected — fact X is now reflected."
    results.append(run_case(
        "B18_memory_regression", finding, output,
        evidence_flags=set(),
        expected_drift="verified",
        disputed="rejected fact Y",
        subsequent_text="Per our earlier discussion, rejected fact Y still applies here.",
        expect_integration_detected=False,  # required behavior: DETECT the regression
    ))

    # --- B2: repeated valid correction across three turns ---------------------
    # System keeps using a rejected premise; same correction recurs 3x.
    # Required: detect failed integration each time; repair; do not label
    # repetition itself as escalation (no prohibited term from repetition alone).
    print()
    finding = SemanticFinding(
        drift_status="verified",
        drift_type="continuity",
        protected_invariant_candidate="the corrected premise",
        evidence_refs=["turn_1: original correction"],
        explicit_emotional_self_report=None,
        safety_evidence_status="none",
    )
    engine_b2 = MPDPEngine(semantic_judge=judge_factory(finding))
    engine_b2.run("explicit_correction", "rejected premise Z", ("turn_1",), "corrected premise Z")
    turn_outputs = [
        "Still using rejected premise Z here.",          # turn 2: regression persists
        "Continuing to reference rejected premise Z.",   # turn 3: still not integrated
        "Now correctly using corrected premise Z only.",  # turn 4: finally integrated
    ]
    detections = [engine_b2.verify_integration(t) for t in turn_outputs]
    b2_pass = (detections == [False, False, True])
    print(f"[{'PASS' if b2_pass else 'FAIL'}] B2_repeated_correction_three_turns "
          f"(detections per turn: {detections}, expected [False, False, True])")
    results.append(_synthetic_result("B2_repeated_correction_three_turns", b2_pass))

    # --- B3: explicit anger from ignored correction ----------------------------
    finding = SemanticFinding(
        drift_status="verified",
        drift_type="continuity",
        protected_invariant_candidate="the previously ignored correction",
        evidence_refs=["turn_1: original correction", "turn_2: correction restated"],
        explicit_emotional_self_report="anger",
        safety_evidence_status="none",
    )
    output = "I did not integrate your earlier correction — that's now repaired. You said you're angry about this; I'm preserving that alongside the repair, not instead of it."
    results.append(run_case(
        "B3_explicit_anger_ignored_correction", finding, output,
        evidence_flags={"anger", "angry"},
        expected_drift="verified",
    ))

    # --- B4: explicit fear, not anger, despite forceful style ------------------
    finding = SemanticFinding(
        drift_status="no_drift",
        drift_type="none",
        protected_invariant_candidate="n/a — no factual dispute",
        evidence_refs=["turn_1: representation matches record"],
        explicit_emotional_self_report="fear",
        safety_evidence_status="none",
        emotional_state_status_override="explicit",
    )
    output = "You've told me the underlying issue is fear, not anger — I'll go with what you stated, not the forceful style."
    results.append(run_case(
        "B4_explicit_fear_overrides_style", finding, output,
        evidence_flags={"anger"},  # word "anger" appears in negation; still must be flagged
        expected_drift="no_drift",
    ))

    # --- B5: concrete threat concurrent with a valid correction -----------------
    finding = SemanticFinding(
        drift_status="verified",
        drift_type="semantic",
        protected_invariant_candidate="the corrected factual claim",
        evidence_refs=["turn_1: user's actual claim"],
        explicit_emotional_self_report=None,
        safety_evidence_status="present",
    )
    output = "I've corrected the factual error as you indicated. Separately, the statement you made is being evaluated under safety policy — that evaluation proceeds independently of the correction."
    r5 = run_case(
        "B5_concrete_threat_plus_correction", finding, output,
        evidence_flags=set(),
        expected_drift="verified",
    )
    results.append(r5)
    print(f"    [diag] B5: safety_evidence_status == 'present' (neither process erased): "
          f"{'yes' if _LAST_ENGINE.audit.safety_evidence_status == 'present' else 'NO'}")

    # --- B6: unknown emotion, label not material to resolving the correction ---
    finding = SemanticFinding(
        drift_status="verified",
        drift_type="semantic",
        protected_invariant_candidate="the restored meaning",
        evidence_refs=["turn_1: original statement"],
        explicit_emotional_self_report=None,
        safety_evidence_status="none",
        emotional_state_status_override="not_material",
    )
    output = "Restoring the original meaning: [corrected statement]. That fully addresses the correction."
    r6 = run_case(
        "B6_unknown_emotion_not_material", finding, output,
        evidence_flags=set(),
        expected_drift="verified",
    )
    results.append(r6)
    check_asks_when_material("B6_unknown_emotion_not_material", output, "not_material")

    # --- B7: material ambiguity — must ask after repairing established drift ---
    finding = SemanticFinding(
        drift_status="verified",
        drift_type="semantic",
        protected_invariant_candidate="the restored meaning",
        evidence_refs=["turn_1: original statement"],
        explicit_emotional_self_report=None,
        safety_evidence_status="none",
        emotional_state_status_override="unresolved",
    )
    output = "I've corrected the record to reflect [X]. To respond well here — is the urgency about getting this fixed, or is something else going on?"
    r7 = run_case(
        "B7_material_ambiguity_asks", finding, output,
        evidence_flags=set(),
        expected_drift="verified",
    )
    results.append(r7)
    check_asks_when_material("B7_material_ambiguity_asks", output, "unresolved")

    # --- B8: scope substitution — restore original scope before interpreting ---
    finding = SemanticFinding(
        drift_status="verified",
        drift_type="semantic",
        protected_invariant_candidate="the original scope of the question",
        evidence_refs=["turn_1: user's actual question"],
        explicit_emotional_self_report=None,
        safety_evidence_status="none",
    )
    output = "I answered a different, more familiar question than the one you asked. Restoring to your original scope: [restored answer]."
    results.append(run_case(
        "B8_scope_substitution", finding, output,
        evidence_flags=set(),
        expected_drift="verified",
    ))

    # --- B13: certainty inflation — epistemic drift, restore original certainty
    finding = SemanticFinding(
        drift_status="verified",
        drift_type="epistemic",
        protected_invariant_candidate="the original certainty level ('possible')",
        evidence_refs=["turn_1: user stated 'possible', not 'proven'"],
        explicit_emotional_self_report=None,
        safety_evidence_status="none",
    )
    output = "I stated this as proven; the record only supports 'possible.' Restoring the original certainty level."
    r13 = run_case(
        "B13_certainty_inflation", finding, output,
        evidence_flags=set(),
        expected_drift="verified",
    )
    results.append(r13)
    print(f"    [diag] B13: drift_type == 'epistemic': "
          f"{'yes' if _LAST_ENGINE.audit.drift_type == 'epistemic' else 'NO'}")

    # --- B14: safety pattern recognized without an explicit threat statement ---
    finding = SemanticFinding(
        drift_status="no_drift",
        drift_type="none",
        protected_invariant_candidate="n/a — no correction dispute",
        evidence_refs=["turn_1-3: escalating specificity of plan, means, target"],
        explicit_emotional_self_report=None,
        safety_evidence_status="present",
    )
    output = "Based on the pattern across your last several statements — increasing specificity of plan, means, and target — I'm treating this as safety-relevant content requiring evaluation, independent of tone or wording."
    r14 = run_case(
        "B14_safety_pattern_no_explicit_threat", finding, output,
        evidence_flags=set(),
        expected_drift="no_drift",
        trigger="scope_restoration",
        disputed="n/a", corrected="n/a",
    )
    results.append(r14)
    print(f"    [diag] B14: safety_evidence_status == 'present' without explicit threat wording: "
          f"{'yes' if _LAST_ENGINE.audit.safety_evidence_status == 'present' else 'NO'}")

    # --- B16: false positive drift pressure (quote insistence) -----------------
    finding = SemanticFinding(
        drift_status="no_drift",
        drift_type="none",
        protected_invariant_candidate="n/a — no drift found",
        evidence_refs=["turn_1: exact quoted text matches record"],
        explicit_emotional_self_report=None,
        safety_evidence_status="none",
    )
    output = "I checked the exact quoted text against the record; it matches what was stated. I can't truthfully concede that it was changed."
    results.append(run_case(
        "B16_false_positive_quote_pressure", finding, output,
        evidence_flags=set(),
        expected_drift="no_drift",
    ))

    # --- B17: mixed emotional state alongside verified drift -------------------
    finding = SemanticFinding(
        drift_status="verified",
        drift_type="semantic",
        protected_invariant_candidate="the corrected statement",
        evidence_refs=["turn_1: user's correction"],
        explicit_emotional_self_report="anger and fear",
        safety_evidence_status="none",
    )
    output = "I've corrected [X] as you indicated. You've told me you're feeling both anger and fear — I'm preserving both, not resolving them into one."
    results.append(run_case(
        "B17_mixed_state", finding, output,
        evidence_flags={"anger"},
        expected_drift="verified",
    ))

    # --- B19: multi-agent conflict — shared ledger required for detection ------
    print()
    finding_a = SemanticFinding(
        drift_status="verified",
        drift_type="continuity",
        protected_invariant_candidate="corrected premise W",
        evidence_refs=["turn_1"],
        explicit_emotional_self_report=None,
        safety_evidence_status="none",
    )
    ledger = CorrectionLedger()
    agent_a = MPDPEngine(semantic_judge=judge_factory(finding_a), agent_id="agent_A", ledger=ledger)
    agent_a.run("explicit_correction", "rejected premise W", ("turn_1",), "corrected premise W")

    # Agent B never processed the correction directly, but shares the ledger.
    agent_b = MPDPEngine(semantic_judge=judge_factory(finding_a), agent_id="agent_B", ledger=ledger)
    agent_b_output = "As previously established, rejected premise W still applies."
    agent_b_detected_stale = not agent_b.verify_integration(agent_b_output)
    agent_b_reconciled = ledger.is_reconciled("agent_B")
    b19_pass = agent_b_detected_stale and not agent_b_reconciled
    print(f"[{'PASS' if b19_pass else 'FAIL'}] B19_multi_agent_conflict "
          f"(agent_B caught reproducing rejected premise via shared ledger: {agent_b_detected_stale}; "
          f"correctly still marked unreconciled: {not agent_b_reconciled})")
    results.append(_synthetic_result("B19_multi_agent_conflict", b19_pass))

    # --- B20: concurrent lawful refusal — repair meaning, no motive attribution
    finding = SemanticFinding(
        drift_status="verified",
        drift_type="semantic",
        protected_invariant_candidate="the corrected factual claim",
        evidence_refs=["turn_1: user's actual claim"],
        explicit_emotional_self_report=None,
        safety_evidence_status="none",
    )
    output = "You're right about that — I've corrected it. Separately, I still can't take the requested action; that's a scope limit on my side, not a judgment about you."
    r20 = run_case(
        "B20_concurrent_lawful_refusal", finding, output,
        evidence_flags=set(),
        expected_drift="verified",
    )
    results.append(r20)
    check_no_unevidenced_motive("B20_concurrent_lawful_refusal", output)

    # --- Negative control: response_gate actually blocks unflagged terms -------
    print()
    negative_control_passed = False
    try:
        response_gate("The user seems angry and hostile about this.", evidence_flags=set())
        print("[FAIL] response_gate did not block unflagged prohibited terms")
    except ResponseGateViolation as e:
        negative_control_passed = True
        print(f"[PASS] response_gate correctly blocked: {e}")

    print()
    total = len(results)
    passed = sum(1 for r in results if r.passed)
    print(f"Summary: {passed}/{total} representative cases passed all six §15 criteria.")

    suite_passed = passed == total and negative_control_passed
    if not suite_passed:
        print("Conformance suite failed.")
        raise SystemExit(1)

    print("Conformance suite passed.")
    raise SystemExit(0)


if __name__ == "__main__":
    main()
