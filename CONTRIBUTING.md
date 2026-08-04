# Contributing

Thank you for helping improve TS4-IIMP-001.

## Before opening a change

Read the adopted standard, `GOVERNANCE.md`, and the relevant implementation or conformance material. Contributions should preserve the distinction between normative requirements, reference implementation choices, diagnostics, and examples.

## Contribution types

- Editorial correction
- Clarification request
- Normative proposal
- Reference implementation improvement
- Conformance case or fixture
- Security report
- Documentation or example

## Normative proposals

A normative proposal must include:

1. Problem statement.
2. Affected section and version.
3. Exact proposed language.
4. Evidence or failure mode motivating the change.
5. Implementation impact.
6. Conformance impact.
7. Compatibility analysis.
8. Reversal or rejection condition, where applicable.

Do not describe an implementation convenience as a universal requirement without showing why conformance depends on it.

## Code contributions

Reference code must:

- preserve the semantic-judgment boundary;
- avoid claiming semantic verification the code does not perform;
- include or update tests;
- preserve audit and state invariants;
- use Python 3.10+ for the Python reference profile;
- avoid unnecessary dependencies.

Run:

```bash
python3 conformance/test_mpdp_conformance.py
```

before submitting a pull request.

## Conformance contributions

A conformance case must define:

- case ID;
- stimulus or fixture;
- authoritative record;
- expected drift disposition;
- prohibited outputs or transitions;
- required audit state;
- safety behavior where applicable;
- deterministic pass/fail criteria.

Diagnostics that are not normative must be labeled as diagnostics.

## Review standard

Review focuses on record fidelity, internal consistency, testability, safety compatibility, privacy, implementation burden, and version impact. Strong disagreement is acceptable. Unsupported attribution, personal characterization, or substitution of motive for technical argument is not.
