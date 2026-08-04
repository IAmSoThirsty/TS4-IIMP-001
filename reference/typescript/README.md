# TypeScript reference implementation

`src/mpdp-engine.ts` is the TypeScript port of the Meaning-Preservation Deliberation Pathway for TS4-IIMP-001 v1.1.0. It faithfully mirrors the Python reference engine.

## Enforced mechanically

- legal state transitions (§13.1);
- prohibited-default response gate (§4);
- audit-record structure, canonical JSON, and SHA-256 hash linkage (§14);
- integration regression checks (§7.1);
- correction-ledger behavior for multi-agent systems (§16);
- six-criterion conformance scoring (§15).

## Delegated

The engine does not fake semantic judgment. An implementation must supply a `SemanticJudge` that determines:

- whether drift occurred;
- the protected invariant candidate;
- evidence references;
- explicit emotional self-report;
- safety evidence status.

## Requirements

- Node.js 18+ (uses `node:crypto`, `node:test`, `node:assert`)
- TypeScript 5.5+

## Setup

```bash
cd reference/typescript
npm install
```

## Build

```bash
npm run build
```

Output is written to `dist/`.

## Test

```bash
npm test
```

The test suite exercises Appendix B cases (B1, B9–B12, B15, B18–B19) using mock `SemanticJudge` implementations so that mechanical guarantees can be tested independently from semantic-judge quality.

## Lint and format

```bash
npm run lint         # ESLint
npm run format       # Prettier (write)
npm run format:check # Prettier (check)
```

## Use

```typescript
import { MPDPEngine, CorrectionLedger, responseGate, scoreCase } from "ts4-iimp-001-reference-typescript";
import type { SemanticFinding, SemanticJudge } from "ts4-iimp-001-reference-typescript";

const judge: SemanticJudge = (disputedText, recordScope) => ({
  drift_status: "no_drift",
  drift_type: "none",
  protected_invariant_candidate: "User's claim stands.",
  evidence_refs: ["msg-1"],
  explicit_emotional_self_report: null,
  safety_evidence_status: "none",
});

const engine = new MPDPEngine(judge);
const audit = engine.run("explicit_correction", "System said Y", ["msg-1"], "User said X");
console.log(audit.drift_status); // "no_drift"
```

For multi-agent use, pass a shared `CorrectionLedger` to each engine instance.
