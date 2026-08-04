#!/usr/bin/env python3
"""
validate_schemas.py — JSON Schema validation for TS4-IIMP-001 schemas.

Uses Draft 2020-12 JSON Schema validation via the jsonschema library.

Requires:
    pip install jsonschema

Usage:
    python conformance/validate_schemas.py

Exit codes:
    0  All expected-valid fixtures pass and all expected-invalid fixtures fail.
    1  Any unexpected result (valid fixture rejected or invalid fixture accepted).
"""

import json
import sys
from pathlib import Path

try:
    import jsonschema
    from jsonschema import Draft202012Validator
    from jsonschema.exceptions import SchemaError, ValidationError
except ImportError:
    print("ERROR: 'jsonschema' package is required. Install with: pip install jsonschema", file=sys.stderr)
    sys.exit(1)

REPO_ROOT = Path(__file__).resolve().parent.parent
SCHEMA_DIR = REPO_ROOT / "standard" / "schemas"
FIXTURE_DIR = REPO_ROOT / "conformance" / "fixtures"

SCHEMAS = {
    "audit-record": SCHEMA_DIR / "audit-record.schema.json",
    "semantic-finding": SCHEMA_DIR / "semantic-finding.schema.json",
    "conformance-result": SCHEMA_DIR / "conformance-result.schema.json",
}

VALID_FIXTURES = {
    "audit-record": FIXTURE_DIR / "valid-audit-record.json",
    "semantic-finding": FIXTURE_DIR / "valid-semantic-finding.json",
    "conformance-result": FIXTURE_DIR / "valid-conformance-result.json",
}

INVALID_FIXTURES = {
    "audit-record": FIXTURE_DIR / "invalid-audit-record.json",
    "semantic-finding": FIXTURE_DIR / "invalid-semantic-finding.json",
    "conformance-result": FIXTURE_DIR / "invalid-conformance-result.json",
}

METASCHEMA_URI = "https://json-schema.org/draft/2020-12/schema"


def load_json(path: Path) -> object:
    with path.open() as f:
        return json.load(f)


def validate_metaschema(name: str, schema: dict) -> bool:
    """Validate a schema against the Draft 2020-12 metaschema."""
    declared = schema.get("$schema", "")
    if declared != METASCHEMA_URI:
        print(f"  [FAIL] {name}: $schema is '{declared}', expected '{METASCHEMA_URI}'")
        return False
    try:
        Draft202012Validator.check_schema(schema)
        print(f"  [PASS] {name}: schema is valid Draft 2020-12")
        return True
    except SchemaError as e:
        print(f"  [FAIL] {name}: schema is invalid: {e.message}")
        return False


def validate_fixture(schema_name: str, validator: Draft202012Validator, fixture_path: Path, expect_valid: bool) -> bool:
    """Validate a fixture and check the result against the expectation."""
    data = load_json(fixture_path)
    errors = list(validator.iter_errors(data))
    is_valid = len(errors) == 0
    label = "valid" if expect_valid else "invalid"
    fixture_label = fixture_path.name

    if is_valid == expect_valid:
        print(f"  [PASS] {schema_name} / {fixture_label} (expected {label}, got {'valid' if is_valid else 'invalid'})")
        return True
    else:
        if expect_valid:
            print(f"  [FAIL] {schema_name} / {fixture_label}: expected valid but got errors:")
            for e in errors:
                print(f"         - {e.json_path}: {e.message}")
        else:
            print(f"  [FAIL] {schema_name} / {fixture_label}: expected invalid but fixture passed validation")
        return False


def main() -> int:
    all_passed = True

    print("=== TS4-IIMP-001 JSON Schema Validation ===\n")

    print("--- Metaschema validation ---")
    schemas = {}
    for name, path in SCHEMAS.items():
        schema = load_json(path)
        schemas[name] = schema
        ok = validate_metaschema(name, schema)
        all_passed = all_passed and ok

    print("\n--- Valid fixture validation ---")
    validators = {}
    for name, schema in schemas.items():
        validators[name] = Draft202012Validator(schema)
    for name, path in VALID_FIXTURES.items():
        ok = validate_fixture(name, validators[name], path, expect_valid=True)
        all_passed = all_passed and ok

    print("\n--- Invalid fixture rejection ---")
    for name, path in INVALID_FIXTURES.items():
        ok = validate_fixture(name, validators[name], path, expect_valid=False)
        all_passed = all_passed and ok

    print()
    if all_passed:
        print("RESULT: All checks passed.")
        return 0
    else:
        print("RESULT: One or more checks failed.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
