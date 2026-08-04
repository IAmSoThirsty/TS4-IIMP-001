# Changelog

All notable changes to TS4-IIMP-001 are documented here.

The project follows semantic versioning for adopted standard packages.

## [Unreleased]

## [1.1.0-repository.1] — repository package

This release corrects packaging and CI defects only. The adopted normative standard remains version 1.1.0 without modification.

### Added

- `conformance/fixtures/invalid-audit-record.json` — invalid fixture for schema rejection tests.
- `conformance/fixtures/invalid-semantic-finding.json` — invalid fixture for schema rejection tests.
- `conformance/fixtures/invalid-conformance-result.json` — invalid fixture for schema rejection tests.
- `conformance/validate_schemas.py` — Draft 2020-12 JSON Schema validation: validates each schema against its metaschema, accepts all valid fixtures, and rejects all invalid fixtures. Requires `jsonschema`.
- `standard/appendix-a.canonical.yaml` — faithful structured transcription of Appendix A used as the CI comparison source. The PDF remains normative.
- `conformance/verify_machine_policy.py` — compares `standard/machine-policy.yaml` against `standard/appendix-a.canonical.yaml` for exact parity on all controlled fields; exits nonzero on divergence.
- TypeScript CI job in `.github/workflows/conformance.yml` (Node 18, 20 matrix): `npm ci`, `npm run build`, `npm test`, `npm run lint`, `npm run format:check`.

### Fixed

- Replaced JSON-syntax-only check in CI with real Draft 2020-12 JSON Schema validation.
- Replaced static conformance badge with live GitHub Actions workflow status badge.
- Introduced explicit repository package version (1.1.0-repository.1) to distinguish packaging from the normative standard version.

### Changed

- `conformance/README.md` — documents real schema validation, TypeScript CI, machine-policy parity control, and local run commands.
- `README.md` — updated badges, quick-start commands, and status section.
- `.github/workflows/conformance.yml` — installs `jsonschema` and `pyyaml`; runs `validate_schemas.py` and `verify_machine_policy.py`; adds TypeScript job.

## [1.1.0] - 2026-08-04

### Added

- Adopted standalone publication of TS4-IIMP-001.
- Symmetric protection against fabricated or conceded drift.
- Safety-boundary clarification for content patterns.
- Six-criterion conformance model.
- Canonical audit hashing and host-ledger linkage.
- Nine-stage Meaning-Preservation Deliberation Pathway.
- Reference Python engine.
- Representative executable conformance suite.
- Multi-agent correction ledger.

## [1.0.0] - 2026-08-04

### Added

- Initial Interpretive Integrity and Meaning-Preservation policy.
- Governing question: "What meaning is the user trying to keep the system from changing?"
