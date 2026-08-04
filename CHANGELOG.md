# Changelog

All notable changes to TS4-IIMP-001 are documented here.

The project follows semantic versioning for adopted standard packages.

## [Unreleased]

### Fixed

- Restored `standard/machine-policy.yaml` to exact Appendix A parity with the adopted v1.1.0 PDF, including the normative trigger list, `hypothesis_space`, `correction_integration`, and `audit_record` blocks.
- Removed the unauthorized strong/weak trigger split from the machine-readable policy.
- Made the conformance runner return a non-zero process exit status when any formal case or the response-gate negative control fails, so GitHub Actions cannot report success on a failing suite.

### Planned

- Formal repository publication package.
- Normative JSON schemas and test fixtures.
- Expanded canonical conformance vectors.
- Privacy and retention profile.
- Authoritative-record precedence profile.

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
