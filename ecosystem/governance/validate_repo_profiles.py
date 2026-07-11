#!/usr/bin/env python3
"""Validate public repository profiles without network access or extra packages."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CATALOG = ROOT / "repo-profiles.json"
SCHEMA = ROOT / "repo-profile.v1.schema.json"
POLICY = ROOT / "branch-policy.json"
REPOSITORY_ROOT = ROOT.parents[1]
SLUG = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
ORG_REPO_URL = re.compile(
    r"https://github\.com/libre-ai/([a-z0-9]+(?:-[a-z0-9]+)*)"
)
DOMAINS = {"institutional", "product", "evidence", "distribution", "infrastructure"}
MATURITY = {"specification", "contract-first", "dojo", "usable", "recurring", "consolidated"}


def find_unprofiled_org_urls(base: Path, allowed_slugs: set[str]) -> list[str]:
    """Reject public links to an organization repository absent from the catalogue."""
    errors: list[str] = []
    for path in sorted(base.rglob("*")):
        if not path.is_file() or ".git" in path.parts:
            continue
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except (OSError, UnicodeDecodeError):
            continue
        for line_number, line in enumerate(lines, 1):
            for match in ORG_REPO_URL.finditer(line):
                if match.group(1) not in allowed_slugs:
                    relative = path.relative_to(base)
                    errors.append(
                        f"{relative}:{line_number}: unprofiled Libre AI repository URL"
                    )
    return errors


def validate() -> list[str]:
    errors: list[str] = []
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
    policy = json.loads(POLICY.read_text(encoding="utf-8"))
    required = set(schema["required"])
    allowed = set(schema["properties"])
    profiles = catalog.get("profiles", [])
    if catalog.get("format") != "libre-ai.repo-profiles.v1":
        errors.append("unsupported profile catalog format")
    seen: set[str] = set()
    by_repo: dict[str, dict[str, object]] = {}
    for index, profile in enumerate(profiles):
        label = f"profile[{index}]"
        missing = sorted(required - set(profile))
        extra = sorted(set(profile) - allowed)
        if missing:
            errors.append(f"{label}: missing {missing}")
        if extra:
            errors.append(f"{label}: unknown {extra}")
        slug = profile.get("slug", "")
        if not isinstance(slug, str) or not SLUG.fullmatch(slug):
            errors.append(f"{label}: unsafe slug")
            continue
        if slug in seen:
            errors.append(f"{label}: duplicate slug {slug}")
        seen.add(slug)
        expected_url = f"https://github.com/libre-ai/{slug}"
        if profile.get("canonical_url") != expected_url:
            errors.append(f"{slug}: canonical URL mismatch")
        if profile.get("visibility") != "public":
            errors.append(f"{slug}: only public profiles are permitted")
        if profile.get("domain") not in DOMAINS:
            errors.append(f"{slug}: unsupported domain")
        if profile.get("maturity") not in MATURITY:
            errors.append(f"{slug}: unsupported maturity")
        checks = profile.get("required_checks")
        if not isinstance(checks, list) or not checks or len(checks) != len(set(checks)):
            errors.append(f"{slug}: required checks must be unique and non-empty")
        historical = profile.get("historical_identifiers", [])
        if not isinstance(historical, list) or any(
            not isinstance(item, str) or not item or "/" in item or "://" in item
            for item in historical
        ):
            errors.append(f"{slug}: unsafe historical identifier allowlist")
        by_repo[f"libre-ai/{slug}"] = profile

    policy_repos = {
        name: value
        for name, value in policy.get("repos", {}).items()
        if name.startswith("libre-ai/")
    }
    if set(policy_repos) != set(by_repo):
        errors.append("public profile set differs from branch-policy repository set")
    for name in sorted(set(policy_repos) & set(by_repo)):
        if policy_repos[name].get("required_checks") != by_repo[name].get("required_checks"):
            errors.append(f"{name}: required checks drift between profile and policy")
    errors.extend(find_unprofiled_org_urls(REPOSITORY_ROOT, seen))
    return errors


def main() -> int:
    errors = validate()
    if errors:
        print("\n".join(errors))
        return 1
    count = len(json.loads(CATALOG.read_text(encoding="utf-8"))["profiles"])
    print(f"Public repository profiles: PASS ({count} repositories)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
