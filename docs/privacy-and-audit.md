# Privacy and audit guidance

Auditability must not become unrestricted surveillance.

## Minimize

Store only what is required to reconstruct the disposition. Prefer stable evidence references over duplicate transcript text. Do not copy a user's emotional self-report into durable storage unless the field is necessary for the use case.

## Separate

Separate operational logs, conformance evidence, security logs, and durable user memory. Different purposes should have different access and retention rules.

## Protect

Apply encryption, role-based access, tamper evidence, retention limits, deletion procedures, and incident response to audit records.

## Preserve uncertainty

An unresolved record should remain unresolved. Audit systems must not fill absent fields with invented values solely to satisfy a schema.

## Hashing

A record hash provides tamper evidence, not confidentiality, authorization, or truth. Hash linkage must be combined with access control and trustworthy evidence provenance.
