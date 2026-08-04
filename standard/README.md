# Standard package

The normative publication for version 1.1.0 is:

- `TS4-IIMP-001-v1.1.0.pdf`

`machine-policy.yaml` is normative only where it restates an obligation contained in the adopted prose. In any conflict, the PDF controls.

The schemas in `schemas/` define interoperability shapes for the reference package. They do not create new normative duties beyond the adopted standard.

`appendix-a.canonical.yaml` is a faithful structured transcription of Appendix A, used as the CI comparison source for `conformance/verify_machine_policy.py`. It is not itself normative. Any update to this file requires manual verification against the adopted PDF by a maintainer with access to the normative document.

## Version identity

| Identifier | Value | Scope |
|---|---|---|
| Standard version | 1.1.0 | The adopted normative PDF |
| Repository package version | 1.1.0-repository.1 | This repository release; corrects packaging and CI defects only |

The repository package version does not imply a normative revision to the adopted standard.
