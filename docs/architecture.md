# Architecture

TS4-IIMP-001 separates semantic judgment from mechanical governance.

## Components

1. **Trigger detector** identifies a correction event or interpretive dispute.
2. **Record resolver** determines which interaction material is available and authoritative.
3. **SemanticJudge** compares disputed meaning against the record and returns a bounded finding.
4. **MPDP state machine** resolves verified drift, verified no-drift, or unresolved status.
5. **Response gate** blocks unsupported emotional, psychological, safety, and drift attribution.
6. **Correction ledger** prevents rejected premises from silently recurring across agents.
7. **Memory gate** prevents rejected or unresolved representations from entering durable state as facts.
8. **Audit writer** records evidence, disposition, repair, integration, and policy version.
9. **Conformance scorer** evaluates binary criteria.

## Trust boundary

The deterministic engine can verify that a judge was called, a permitted disposition was returned, legal state transitions occurred, evidence references were supplied, and required audit fields exist. It cannot prove the judge understood language correctly.

Production deployments should treat the semantic judge as a privileged, fallible dependency with provenance, validation, monitoring, and escalation paths.
