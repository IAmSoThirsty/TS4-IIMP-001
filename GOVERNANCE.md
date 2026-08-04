# Governance

## Authority

TS4-IIMP-001 is governed under Thirsty's Codex / Thirsty's Standards V4+.

The repository owner is the issuing authority and final maintainer of adopted releases. Public participation is welcome, but no contribution becomes normative merely by being proposed, discussed, merged, or implemented.

## Normative hierarchy

Where artifacts conflict, authority is resolved in this order:

1. Adopted standard publication for the applicable version.
2. Normative machine-readable policy where it restates the adopted prose.
3. Published conformance requirements for that version.
4. Reference implementation.
5. Examples, guides, diagrams, and commentary.

The reference implementation demonstrates one implementation path. It does not override the standard.

## Change classes

- **Editorial** - wording, formatting, references, or examples that do not alter requirements.
- **Clarifying** - removes ambiguity without changing an existing obligation.
- **Additive** - introduces a new requirement, interface, profile, test, or artifact.
- **Breaking** - weakens, removes, reverses, or incompatibly changes an existing requirement or machine contract.

## Versioning

The project uses semantic versioning for published standards packages:

- PATCH: editorial corrections only.
- MINOR: clarifying or additive changes that preserve existing conformance claims.
- MAJOR: breaking changes or incompatible conformance changes.

A release must identify the exact standard, policy, implementation, and conformance-suite versions it contains.

## Proposal process

Substantive changes should be proposed through a GitHub issue or pull request containing:

- the problem being addressed;
- the affected section or control;
- the proposed normative text;
- implementation consequences;
- conformance consequences;
- backward-compatibility analysis;
- known risks or unresolved questions.

## Adoption states

Artifacts may be labeled:

- Working Draft
- Public Review Draft
- Candidate Standard
- Adopted Standard
- Reference Implementation
- Conformance Suite
- Certified Implementation

Only an artifact explicitly marked **Adopted Standard** is normative.

## Conformance claims

A system may claim conformance only when it passes every mandatory case and criterion for the claimed version. Partial results may be reported diagnostically but must not be represented as conformance.

## Maintainer responsibility

Maintainers must preserve evidence, uncertainty, version traceability, and the distinction between normative requirements and implementation choices. No maintainer may silently convert an implementation convenience into a standard requirement.
