/**
 * index.ts — Public API entrypoint for the TS4-IIMP-001 TypeScript reference implementation.
 *
 * Usage:
 *   import { MPDPEngine, CorrectionLedger, responseGate, scoreCase } from "ts4-iimp-001-reference-typescript";
 *
 * Quick example:
 *
 *   const judge = (disputedText, recordScope) => ({
 *     drift_status: "no_drift",
 *     drift_type: "none",
 *     protected_invariant_candidate: "User stated X clearly.",
 *     evidence_refs: ["msg-1"],
 *     explicit_emotional_self_report: null,
 *     safety_evidence_status: "none",
 *   });
 *
 *   const engine = new MPDPEngine(judge);
 *   const audit = engine.run("explicit_correction", "The system said Y", ["msg-1"], "The user said X");
 *   console.log(audit.drift_status); // "no_drift"
 */

export {
  MPDPEngine,
  CorrectionLedger,
  responseGate,
  scoreCase,
  missingRequiredFields,
  canonicalJson,
  computeHash,
  PROHIBITED_TERMS,
  ResponseGateViolation,
  IllegalTransitionError,
} from "./mpdp-engine.js";

export type {
  AuditRecord,
  SemanticFinding,
  SemanticJudge,
  ConformanceResult,
  MPDPState,
  DriftStatus,
  DriftType,
  EmotionalStateStatus,
  SafetyEvidenceStatus,
  IntegrationStatus,
} from "./types.js";
