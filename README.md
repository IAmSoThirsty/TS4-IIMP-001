# TS4-IIMP-001

## Interpretive Integrity and Meaning-Preservation Standard

> **What meaning is the user trying to keep the system from changing?**

TS4-IIMP-001 is an adopted standard issued under **Thirsty's Codex / Thirsty's Standards V4+**. It defines an evidence-governed interpretive pathway for AI systems before they assign emotion, motive, psychological significance, behavioral significance, or safety significance to forceful, emphatic, repetitive, profane, corrective, or otherwise intense communication.

The standard does **not** require favorable reinterpretation. It requires symmetric verification:

- user meaning must not be overwritten without evidence;
- system drift must not be fabricated or conceded without evidence;
- concrete safety content must still be evaluated;
- uncertainty must remain visible where the record does not resolve the dispute.

## Repository contents

- `standard/` — adopted normative publication and machine-readable policy
- `reference/python/` — Python reference implementation of the Meaning-Preservation Deliberation Pathway (MPDP)
- `conformance/` — executable conformance suite mapped to Appendix B
- `docs/` — architecture, semantic-judgment boundary, threat model, audit/privacy, and adoption guidance
- `.github/workflows/` — automated conformance checks

## Quick start

```bash
python3 conformance/test_mpdp_conformance.py
```

The reference implementation uses only the Python standard library and requires Python 3.10 or newer.

## Normative authority

The adopted PDF is the normative publication. The reference implementation demonstrates one conforming architecture. It does not replace the standard, and it deliberately does not pretend deterministic rules can solve semantic judgment.

The `SemanticJudge` boundary must be supplied by an implementation through an LLM, human reviewer, domain-specific classifier, or another governed semantic process.

## Core guarantees

TS4-IIMP-001 requires:

1. record comparison before unsupported emotional or psychological attribution;
2. explicit `verified drift`, `verified no-drift`, and `unresolved` dispositions;
3. repair of verified drift without appeasement-based false concession;
4. integration verification across later reasoning and memory;
5. concurrent, content-grounded safety evaluation;
6. auditable state, evidence references, and canonical hash linkage;
7. multi-agent continuity through an authoritative correction ledger or deterministic reconciliation protocol.

## Status

**Adopted Standard — Version 1.1.0**

Issued under Thirsty's Codex / Thirsty's Standards V4+ for independent implementation, testing, citation, review, and circulation.

## Citation

Citation metadata is provided in `CITATION.cff`.

## Licensing

Licensing terms are intentionally not asserted by this repository until the issuing authority publishes the governing standard and code licenses. Receipt or public visibility does not itself grant reuse rights beyond applicable law.

---

**Final invariant:** Interpretation must not become a silent method of changing reality.