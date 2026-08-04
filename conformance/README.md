# Conformance suite

The executable suite exercises the mechanical behavior of the Python reference implementation against representative Appendix B cases, validates JSON schemas against the Draft 2020-12 metaschema and test fixtures, and verifies exact parity between `standard/machine-policy.yaml` and the canonical Appendix A transcription.

## Local commands

Run all checks from the repository root:

```bash
pip install jsonschema pyyaml

# Python conformance suite (Appendix B cases)
python3 conformance/test_mpdp_conformance.py

# JSON Schema validation (Draft 2020-12 — validates schemas, accepts valid fixtures, rejects invalid fixtures)
python3 conformance/validate_schemas.py

# Machine-policy parity check (compares machine-policy.yaml against appendix-a.canonical.yaml)
python3 conformance/verify_machine_policy.py

# TypeScript reference (requires Node 18+)
cd reference/typescript && npm ci && npm run build && npm test && npm run lint && npm run format:check
```

Every command exits nonzero on failure and will fail CI.

## CI coverage

GitHub Actions (`.github/workflows/conformance.yml`) runs on every push and pull request:

- **Python job** (matrix: 3.10, 3.11, 3.12, 3.13):
  - compile Python sources (`python -m compileall`);
  - run `test_mpdp_conformance.py`;
  - run `validate_schemas.py` (real Draft 2020-12 schema validation);
  - run `verify_machine_policy.py`.

- **TypeScript job** (matrix: Node 18, 20):
  - `npm ci`, `npm run build`, `npm test`, `npm run lint`, `npm run format:check`.

## Schema validation

`validate_schemas.py` uses the `jsonschema` library to:

1. validate each schema in `standard/schemas/` against the Draft 2020-12 metaschema;
2. validate each `valid-*.json` fixture in `conformance/fixtures/` — all must pass;
3. validate each `invalid-*.json` fixture — all must be rejected.

This is real JSON Schema validation, not JSON syntax parsing.

## Machine-policy parity

`verify_machine_policy.py` compares `standard/machine-policy.yaml` against `standard/appendix-a.canonical.yaml` for exact parity on all controlled fields:

- trigger list (exact, ordered);
- required path (exact, ordered);
- prohibited defaults (exact, ordered);
- permitted record dispositions;
- hypothesis space (permitted list and `forced_positive_reinterpretation`);
- correction integration block;
- governing question text and function;
- uncertainty rule;
- safety boundary values;
- required and conditional audit record fields.

`standard/appendix-a.canonical.yaml` is a faithful structured transcription of Appendix A from the adopted PDF. The PDF remains normative. Any update to the canonical file requires manual verification against the adopted PDF.

## Scope

Passing this reference suite demonstrates that the supplied engine behaves as expected for the included cases. It does not certify an external implementation, semantic judge, model, organization, or deployment.

