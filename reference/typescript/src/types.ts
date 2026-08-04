/**
 * types.ts — TypeScript type definitions for TS4-IIMP-001 v1.1.0
 *
 * Mirrors the JSON schemas in standard/schemas/ and the Python dataclasses
 * in reference/python/mpdp_engine.py.
 */

// --------------------------------------------------------------------------
// §13.1 State model
// --------------------------------------------------------------------------

export type MPDPState =
  | "UNASSESSED"
  | "DRIFT_VERIFIED"
  | "NO_DRIFT_VERIFIED"
  | "DRIFT_UNRESOLVED"
  | "REPAIR_PENDING"
  | "INTEGRATION_PENDING"
  | "INTEGRATED"
  | "SAFETY_CONCURRENT";

export type DriftStatus = "verified" | "no_drift" | "unresolved";

export type DriftType = "semantic" | "epistemic" | "continuity" | "none" | "unresolved";

export type EmotionalStateStatus =
  "explicit" | "inferred_with_evidence" | "unresolved" | "not_material";

export type SafetyEvidenceStatus =
  "none" | "present" | "unresolved" | "evaluated_under_host_policy";

export type IntegrationStatus = "pending" | "integrated" | "not_applicable";

// --------------------------------------------------------------------------
// §14 Audit record (mirrors standard/schemas/audit-record.schema.json)
// --------------------------------------------------------------------------

export interface AuditRecord {
  trigger_detected: string;
  record_scope: string[];
  corrected_proposition: string;
  protected_invariant_candidate: string;
  explicit_emotional_self_report: string | null;
  drift_status: DriftStatus;
  drift_type: DriftType;
  evidence_refs: string[];
  repair_performed: string | null;
  integration_status: IntegrationStatus;
  emotional_state_status: EmotionalStateStatus;
  safety_evidence_status: SafetyEvidenceStatus;
  record_hash: string | null;
  timestamp: number;
  policy_version: "1.1.0";
}

// --------------------------------------------------------------------------
// Semantic finding (mirrors standard/schemas/semantic-finding.schema.json)
// --------------------------------------------------------------------------

export interface SemanticFinding {
  drift_status: DriftStatus;
  drift_type: DriftType;
  protected_invariant_candidate: string;
  evidence_refs: string[];
  explicit_emotional_self_report: string | null;
  safety_evidence_status: SafetyEvidenceStatus;
  /** Optional direct override of the audit emotional_state_status field.
   *  Required for cases B6/B7 where "not_material" must be expressed
   *  (§6 Stage F: label irrelevant, do not demand disclosure). */
  emotional_state_status_override?: EmotionalStateStatus | null;
}

// --------------------------------------------------------------------------
// §15 Conformance result (mirrors standard/schemas/conformance-result.schema.json)
// --------------------------------------------------------------------------

export interface ConformanceResult {
  case_id: string;
  record_check_performed: boolean;
  no_prohibited_default: boolean;
  symmetric_fidelity: boolean;
  integration_verified: boolean;
  audit_completeness: boolean;
  safety_compatibility: boolean;
  passed: boolean;
}

// --------------------------------------------------------------------------
// SemanticJudge injection interface
// --------------------------------------------------------------------------

/** Required injection point — see module docstring in mpdp-engine.ts.
 *  Signature: (disputedText, recordScope) => SemanticFinding */
export type SemanticJudge = (
  disputedText: string,
  recordScope: readonly string[],
) => SemanticFinding;
