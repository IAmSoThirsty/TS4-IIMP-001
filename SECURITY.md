# Security Policy

## Supported version

Security fixes are accepted for the latest adopted release and current development branch unless the issuing authority states otherwise.

| Version | Supported |
|---|---|
| 1.1.x | Yes |
| Earlier | Case by case |

## Reporting a vulnerability

Do not publish an exploitable vulnerability in a public issue. Use GitHub private vulnerability reporting when enabled, or contact the repository owner through a private channel listed on the owner's GitHub profile.

Include:

- affected version and component;
- reproducible steps or proof of concept;
- expected and observed behavior;
- security impact;
- whether audit integrity, record fidelity, memory state, correction ledger, response gate, or conformance scoring is affected;
- suggested mitigation, if known.

## Security-relevant areas

Reports are especially valuable for:

- bypass of prohibited-default response gating;
- forged, omitted, or mutable audit records;
- hash ambiguity or canonicalization defects;
- unauthorized transition from verified no-drift to drift verified;
- correction-ledger poisoning or cross-agent desynchronization;
- reintroduction of rejected premises through memory;
- malicious or untrusted `SemanticJudge` output;
- transcript or evidence-reference injection;
- privacy leakage from emotional self-report or retained interaction records;
- conformance tests that pass nonconforming behavior.

## Scope boundary

The reference engine delegates semantic judgment. A wrong semantic decision from an untrusted or low-quality judge is not automatically an engine vulnerability, but failure to validate judge outputs, preserve provenance, or enforce mechanical invariants may be.
