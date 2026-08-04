# Conformance suite

The executable suite exercises the mechanical behavior of the Python reference implementation against representative Appendix B cases.

Run from the repository root:

```bash
python3 conformance/test_mpdp_conformance.py
```

The suite uses mock `SemanticJudge` implementations so that mechanical guarantees can be tested independently from semantic-judge quality.

Passing this reference suite demonstrates that the supplied engine behaves as expected for the included cases. It does not certify an external implementation, semantic judge, model, organization, or deployment.
