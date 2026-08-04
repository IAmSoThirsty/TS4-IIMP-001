# TS4-IIMP-001

## Interpretive Integrity and Meaning-Preservation Standard

> **What meaning is the user trying to keep the system from changing?**

[![Standard](https://img.shields.io/badge/status-adopted-1f6feb)](standard/TS4-IIMP-001-v1.1.0.pdf)
[![Version](https://img.shields.io/badge/version-1.1.0-2ea44f)](CHANGELOG.md)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](reference/python/README.md)
[![TypeScript](https://img.shields.io/badge/typescript-5.5%2B-3178c6)](reference/typescript/README.md)
[![Conformance](https://img.shields.io/badge/conformance-reference%20suite-purple)](conformance/README.md)

TS4-IIMP-001 is an adopted standard issued under **Thirsty's Codex / Thirsty's Standards V4+**. It defines an evidence-governed interpretive pathway for AI systems before they assign emotion, motive, psychological significance, behavioral significance, or safety significance to forceful, emphatic, repetitive, profane, corrective, or otherwise intense communication.

The standard does not require favorable reinterpretation. It requires symmetric verification:

- user meaning must not be overwritten without evidence;
- system drift must not be fabricated or conceded without evidence;
- concrete safety content must still be evaluated;
- uncertainty must remain visible where the record does not resolve the dispute.

## Start here

| Need | Go to |
|---|---|
| Read the adopted standard | [`standard/TS4-IIMP-001-v1.1.0.pdf`](standard/TS4-IIMP-001-v1.1.0.pdf) |
| Understand the architecture | [`docs/architecture.md`](docs/architecture.md) |
| Implement the semantic boundary | [`docs/semantic-judge-contract.md`](docs/semantic-judge-contract.md) |
| Run the reference engine (Python) | [`reference/python/`](reference/python/) |
| Run the reference engine (TypeScript) | [`reference/typescript/`](reference/typescript/) |
| Run conformance tests | [`conformance/`](conformance/) |
| Review risks and limitations | [`docs/threat-model.md`](docs/threat-model.md) |
| Adopt the standard | [`docs/adoption-guide.md`](docs/adoption-guide.md) |

## Quick start

```bash
git clone https://github.com/IAmSoThirsty/TS4-IIMP-001.git
cd TS4-IIMP-001
python3 conformance/test_mpdp_conformance.py
```

The reference implementation uses only the Python standard library and requires Python 3.10 or newer.

## The protocol in one view

```text
Correction or intensity detected
             |
             v
Identify the disputed proposition
             |
             v
Recover the protected invariant candidate
             |
             v
Compare against the authoritative record
        /          |          \
       v           v           v
Verified drift  No drift    Unresolved
       |           |           |
Repair record  Maintain      Preserve
and integrate  finding       uncertainty
        \          |          /
             v
Retain evidence-supported emotional and safety hypotheses
             |
             v
Respond from the verified record and verify integration
```

## Normative authority

The adopted PDF is the normative publication. The machine-readable policy is normative only where it restates an obligation contained in the adopted prose. In any conflict, the prose standard controls.

The reference implementation demonstrates one implementation path. It does not replace the standard, and it deliberately does not pretend deterministic rules can solve semantic judgment.

## Semantic boundary

The implementation delegates actual semantic judgment through a `SemanticJudge` interface. A production implementation may supply an LLM, human reviewer, domain-specific classifier, or another governed semantic process.

The reference engine mechanically enforces state transitions, response gating, audit structure, canonical hashing, correction-ledger behavior, integration checks, and conformance scoring. It does not claim to determine meaning by regex or rules alone.

## Core guarantees

TS4-IIMP-001 requires:

1. record comparison before unsupported emotional or psychological attribution;
2. explicit `verified drift`, `verified no-drift`, and `unresolved` dispositions;
3. repair of verified drift without appeasement-based false concession;
4. integration verification across later reasoning and memory;
5. concurrent, content-grounded safety evaluation;
6. auditable state, evidence references, and canonical hash linkage;
7. multi-agent continuity through an authoritative correction ledger or deterministic reconciliation protocol.

## Repository map

```text
standard/                Adopted publication, machine policy, and schemas
reference/python/        Python reference implementation
reference/typescript/    TypeScript reference implementation
conformance/             Executable conformance suite (Python)
docs/                    Architecture, threat model, privacy, and adoption guidance
.github/                 CI and contribution templates
```

## Status

**Adopted Standard - Version 1.1.0**

Issued under Thirsty's Codex / Thirsty's Standards V4+ for independent implementation, testing, citation, review, and circulation.

## Citation

Citation metadata is provided in [`CITATION.cff`](CITATION.cff).

## Licensing

No open-source license has yet been granted for this repository. See [`LICENSE.md`](LICENSE.md). Public visibility does not itself grant reuse rights beyond applicable law.

---

**Final invariant:** Interpretation must not become a silent method of changing reality.
