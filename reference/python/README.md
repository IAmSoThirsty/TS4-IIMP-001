# Python reference implementation

`mpdp_engine.py` is the reference implementation of the Meaning-Preservation Deliberation Pathway for TS4-IIMP-001 v1.1.0.

## Enforced mechanically

- legal state transitions;
- prohibited-default response gate;
- audit-record structure;
- canonical JSON and SHA-256 record hashing;
- integration regression checks;
- correction-ledger behavior for multi-agent systems;
- six-criterion conformance scoring.

## Delegated

The engine does not fake semantic judgment. An implementation must supply a `SemanticJudge` that determines:

- whether drift occurred;
- the protected invariant candidate;
- evidence references;
- explicit emotional self-report;
- safety evidence status.

## Use

From the repository root:

```bash
python3 conformance/test_mpdp_conformance.py
```

For import into another program:

```python
from reference.python.mpdp_engine import MPDPEngine, SemanticFinding
```

The current test file adds `reference/python` to its import path automatically.
