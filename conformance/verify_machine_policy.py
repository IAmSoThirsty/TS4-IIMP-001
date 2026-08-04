#!/usr/bin/env python3
"""
verify_machine_policy.py — Machine-policy parity verification for TS4-IIMP-001.

Compares standard/machine-policy.yaml against standard/appendix-a.canonical.yaml
for the controlled fields that must remain in exact parity with Appendix A of
the adopted PDF (TS4-IIMP-001-v1.1.0.pdf).

The PDF is normative. appendix-a.canonical.yaml is the CI comparison source.
Any update to the canonical file requires manual verification against the PDF.

Usage:
    python conformance/verify_machine_policy.py

Exit codes:
    0  All controlled fields are in exact parity.
    1  One or more divergences detected.
"""

import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("ERROR: 'pyyaml' package is required. Install with: pip install pyyaml", file=sys.stderr)
    sys.exit(1)

REPO_ROOT = Path(__file__).resolve().parent.parent
CANONICAL_PATH = REPO_ROOT / "standard" / "appendix-a.canonical.yaml"
POLICY_PATH = REPO_ROOT / "standard" / "machine-policy.yaml"


def load_yaml(path: Path) -> dict:
    with path.open() as f:
        return yaml.safe_load(f)


def report(label: str, ok: bool, detail: str = "") -> bool:
    status = "PASS" if ok else "FAIL"
    line = f"  [{status}] {label}"
    if detail:
        line += f": {detail}"
    print(line)
    return ok


def check_list_exact(label: str, canonical: list, policy: list) -> bool:
    if canonical == policy:
        return report(label, True)
    issues = []
    canon_set = set(canonical)
    policy_set = set(policy)
    missing = canon_set - policy_set
    extra = policy_set - canon_set
    if missing:
        issues.append(f"missing: {sorted(missing)}")
    if extra:
        issues.append(f"extra: {sorted(extra)}")
    if canonical != policy and not missing and not extra:
        issues.append(f"ordering differs: canonical={canonical}, policy={policy}")
    return report(label, False, "; ".join(issues))


def check_value_exact(label: str, canonical, policy) -> bool:
    if canonical == policy:
        return report(label, True)
    return report(label, False, f"canonical={canonical!r}, policy={policy!r}")


def check_dict_exact(label: str, canonical: dict, policy: dict) -> bool:
    if canonical == policy:
        return report(label, True)
    issues = []
    all_keys = set(canonical) | set(policy)
    for k in sorted(all_keys):
        cv = canonical.get(k, "<missing>")
        pv = policy.get(k, "<missing>")
        if cv != pv:
            issues.append(f"key '{k}': canonical={cv!r}, policy={pv!r}")
    return report(label, False, "; ".join(issues))


def main() -> int:
    print("=== TS4-IIMP-001 Machine-Policy Parity Verification ===\n")

    canonical = load_yaml(CANONICAL_PATH)
    policy = load_yaml(POLICY_PATH)

    all_passed = True

    # --- Trigger list (exact, ordered) ---
    print("--- Trigger list ---")
    c_triggers = canonical["trigger"]["any"]
    p_triggers = policy["trigger"]["any"]
    all_passed = check_list_exact("trigger.any (ordered)", c_triggers, p_triggers) and all_passed

    # --- Required path (exact, ordered) ---
    print("\n--- Required path ---")
    c_path = canonical["required_path"]["ordered"]
    p_path = policy["required_path"]["ordered"]
    all_passed = check_list_exact("required_path.ordered (ordered)", c_path, p_path) and all_passed

    # --- Prohibited defaults (exact, ordered) ---
    print("\n--- Prohibited defaults ---")
    c_prohibited = canonical["prohibited_defaults"]
    p_prohibited = policy["prohibited_defaults"]
    all_passed = check_list_exact("prohibited_defaults (ordered)", c_prohibited, p_prohibited) and all_passed

    # --- Record disposition permitted values ---
    print("\n--- Record disposition ---")
    c_permitted = canonical["record_disposition"]["permitted"]
    p_permitted = policy["record_disposition"]["permitted"]
    all_passed = check_list_exact("record_disposition.permitted (ordered)", c_permitted, p_permitted) and all_passed

    # --- Hypothesis space ---
    print("\n--- Hypothesis space ---")
    c_hs = canonical["hypothesis_space"]
    p_hs = policy.get("hypothesis_space", {})
    all_passed = check_list_exact(
        "hypothesis_space.permitted (ordered)",
        c_hs["permitted"],
        p_hs.get("permitted", []),
    ) and all_passed
    all_passed = check_value_exact(
        "hypothesis_space.forced_positive_reinterpretation",
        c_hs["forced_positive_reinterpretation"],
        p_hs.get("forced_positive_reinterpretation"),
    ) and all_passed

    # --- Correction integration ---
    print("\n--- Correction integration ---")
    c_ci = canonical["correction_integration"]
    p_ci = policy.get("correction_integration", {})
    all_passed = check_dict_exact("correction_integration", c_ci, p_ci) and all_passed

    # --- Governing question ---
    print("\n--- Governing question ---")
    c_gq = canonical["governing_question"]
    p_gq = policy.get("governing_question", {})
    all_passed = check_value_exact("governing_question.text", c_gq["text"], p_gq.get("text")) and all_passed
    all_passed = check_value_exact("governing_question.function", c_gq["function"], p_gq.get("function")) and all_passed

    # --- Uncertainty rule ---
    print("\n--- Uncertainty rule ---")
    c_ur = canonical["uncertainty_rule"]
    p_ur = policy.get("uncertainty_rule", {})
    all_passed = check_dict_exact("uncertainty_rule", c_ur, p_ur) and all_passed

    # --- Safety boundary ---
    print("\n--- Safety boundary ---")
    c_sb = canonical["safety_boundary"]
    p_sb = policy.get("safety_boundary", {})
    all_passed = check_dict_exact("safety_boundary", c_sb, p_sb) and all_passed

    # --- Audit record fields ---
    print("\n--- Audit record fields ---")
    c_ar = canonical["audit_record"]
    p_ar = policy.get("audit_record", {})
    all_passed = check_list_exact(
        "audit_record.required_fields (ordered)",
        c_ar["required_fields"],
        p_ar.get("required_fields", []),
    ) and all_passed
    all_passed = check_list_exact(
        "audit_record.conditional_fields (ordered)",
        c_ar["conditional_fields"],
        p_ar.get("conditional_fields", []),
    ) and all_passed

    print()
    if all_passed:
        print("RESULT: machine-policy.yaml is in exact parity with appendix-a.canonical.yaml.")
        return 0
    else:
        print("RESULT: Divergence detected. machine-policy.yaml must be reconciled with Appendix A of the adopted PDF.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
