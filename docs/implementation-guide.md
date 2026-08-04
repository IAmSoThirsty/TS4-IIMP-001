# Implementation guide

A minimal implementation requires:

- access to the disputed interaction record;
- a semantic judge;
- three drift dispositions;
- ordered MPDP execution;
- a response gate;
- audit output;
- integration verification.

A production implementation should additionally provide:

- authoritative-record precedence;
- schema validation;
- immutable or tamper-evident audit linkage;
- privacy and retention controls;
- memory write gating;
- multi-agent correction reconciliation;
- human escalation;
- latency-aware safety concurrency;
- deterministic conformance fixtures.

The reference Python engine is intentionally small. It demonstrates controls rather than prescribing a production framework.
