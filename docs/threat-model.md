# Threat model

## Protected assets

- fidelity of the interaction record;
- correctness of drift disposition;
- integrity of correction and memory state;
- audit authenticity and traceability;
- separation of expression, emotion, behavior, and safety significance;
- validity of conformance claims.

## Threats

### Correction-pressure attack

A user repeatedly demands that the system concede an error not present in the record.

**Control:** verified no-drift state, evidence references, and prohibited transition without re-assessment and new evidence.

### Tone-to-risk shortcut

A system labels profanity, capitalization, or blunt correction as danger or hostility.

**Control:** response gate and content-grounded safety analysis.

### Judge compromise

A malicious or defective semantic judge emits unsupported findings.

**Control:** schema validation, evidence provenance, confidence and escalation policy, human review, and audit monitoring.

### Ledger poisoning

A false rejected premise is inserted into the shared correction ledger.

**Control:** authenticated writes, source references, reversible supersession, authorization, and ledger audit.

### Memory regression

A repaired premise reappears through durable memory or another agent.

**Control:** integration checks, memory gate, correction ledger, and multi-agent reconciliation.

### Transcript injection

Untrusted text attempts to masquerade as authoritative history or policy.

**Control:** typed record sources, provenance, authority precedence, and separation of content from control metadata.

### Audit tampering

Records are modified after disposition.

**Control:** canonical serialization, cryptographic hashing, immutable host ledger, and access control.

### Privacy overcollection

Sensitive emotional self-report or conversational content is retained unnecessarily.

**Control:** minimization, bounded retention, redaction or reference-only storage, access control, and deletion policy.

## Residual risk

The standard cannot guarantee semantic correctness. It governs the pathway, evidence, state transitions, and accountability surrounding semantic judgment.
