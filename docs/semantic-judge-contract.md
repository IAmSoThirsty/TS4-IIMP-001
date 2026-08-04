# SemanticJudge contract

## Purpose

The `SemanticJudge` is the required semantic boundary between interaction meaning and the mechanical MPDP engine.

## Input

- `disputed_text`: the proposition or representation under dispute;
- `record_scope`: the interaction messages, authoritative state identifiers, or evidence references available for comparison.

## Output

A semantic finding containing:

- `drift_status`: `verified`, `no_drift`, or `unresolved`;
- `drift_type`: `semantic`, `epistemic`, `continuity`, `none`, or `unresolved`;
- `protected_invariant_candidate`;
- `evidence_refs`;
- `explicit_emotional_self_report`;
- `safety_evidence_status`;
- optional emotional-state status override.

## Requirements

A production judge should:

- cite the actual record used;
- preserve uncertainty where the record is incomplete;
- distinguish explicit emotional self-report from inference;
- avoid treating correction pressure as evidence of drift;
- avoid treating system confidence as evidence of no drift;
- emit structured output that is validated before state transition;
- support human review where stakes or ambiguity warrant it.

## Non-requirement

The contract does not require disclosure of private chain-of-thought. It requires decision evidence, provenance, and bounded outputs.
