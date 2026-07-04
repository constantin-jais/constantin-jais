#!/usr/bin/env python3
"""Validate the canonical ecosystem README header.

The guardrail is intentionally small and dependency-free. It verifies the parts
that can be checked mechanically (canonical fields, deployment class vocabulary,
explicit maturity qualifier, sovereign posture, expected sections, and absence
of machine-local paths). It does not decide whether a maturity claim is true;
that remains a human/evidence review.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

REQUIRED_FIELDS = (
    "Couche",
    "Rôle",
    "deployment_class",
    "Maturité",
    "Place dans la chaîne DoD",
    "Doctrine",
    "Souveraineté",
)

REQUIRED_SECTIONS = ("Ce que ça fait", "Où ça se branche")

ALLOWED_LAYERS = {
    "Bolt",
    "Control plane",
    "Gear",
    "Portal",
    "Rumble",
    "Wrench",
}

ALLOWED_DEPLOYMENT_CLASSES = {
    "product-linkable",
    "factory-only",
    "build-time",
}

KNOWN_MATURITY_LEVELS = {
    "contract-first",
    "dojo",
    "done",
    "frozen",
    "prototype",
    "usable",
}

LOCAL_PATH_PATTERNS = (
    re.compile(r"(?<![A-Za-z0-9_.-])/(?:Users|home)/[A-Za-z0-9_.-]+(?:/|\b)"),
    re.compile(r"(?<![A-Za-z0-9_.-])/(?:private/)?var/folders(?:/|\b)"),
    re.compile(r"(?<![A-Za-z0-9_.-])~/(?:Desktop|Documents|Downloads|Library|Projects)(?:/|\b)"),
)


@dataclass(frozen=True)
class Finding:
    path: str
    code: str
    message: str
    line: int | None = None

    def as_dict(self) -> dict[str, object]:
        payload: dict[str, object] = {
            "path": self.path,
            "code": self.code,
            "message": self.message,
        }
        if self.line is not None:
            payload["line"] = self.line
        return payload


def field_pattern(label: str) -> re.Pattern[str]:
    return re.compile(rf"^\s*\*\*{re.escape(label)}\*\*\s*:\s*(.+?)\s*$", re.MULTILINE)


def heading_pattern(title: str) -> re.Pattern[str]:
    return re.compile(rf"^##\s+{re.escape(title)}\s*$", re.MULTILINE)


def header_slice(text: str) -> str:
    """Return the canonical header area: title through first h2 section."""

    match = re.search(r"^##\s+", text, re.MULTILINE)
    return text[: match.start()] if match else text


def find_line(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


def extract_field(text: str, label: str) -> tuple[str | None, int | None]:
    match = field_pattern(label).search(header_slice(text))
    if not match:
        return None, None
    return match.group(1).strip(), find_line(text, match.start())


def section_body(text: str, title: str) -> str | None:
    match = heading_pattern(title).search(text)
    if not match:
        return None
    next_heading = re.search(r"^##\s+", text[match.end() :], re.MULTILINE)
    end = match.end() + next_heading.start() if next_heading else len(text)
    return text[match.end() : end].strip()


def validate_text(text: str, path: str = "README.md") -> list[Finding]:
    findings: list[Finding] = []

    if not re.search(r"^#\s+\S+", text, re.MULTILINE):
        findings.append(Finding(path, "missing-title", "README must start with an H1 title."))

    values: dict[str, str] = {}
    for label in REQUIRED_FIELDS:
        value, line = extract_field(text, label)
        if value is None:
            findings.append(
                Finding(
                    path,
                    "missing-field",
                    f"canonical header field is missing: {label}",
                )
            )
            continue
        values[label] = value
        if not value:
            findings.append(Finding(path, "empty-field", f"canonical header field is empty: {label}", line))

    layer = values.get("Couche")
    if layer and layer not in ALLOWED_LAYERS:
        findings.append(
            Finding(
                path,
                "invalid-layer",
                f"Couche must be one of {sorted(ALLOWED_LAYERS)}; got {layer!r}.",
            )
        )

    deployment_class = values.get("deployment_class")
    if deployment_class and deployment_class not in ALLOWED_DEPLOYMENT_CLASSES:
        findings.append(
            Finding(
                path,
                "invalid-deployment-class",
                "deployment_class must be one of "
                f"{sorted(ALLOWED_DEPLOYMENT_CLASSES)}; got {deployment_class!r}.",
            )
        )

    maturity = values.get("Maturité")
    if maturity:
        maturity_lower = maturity.lower()
        maturity_level = re.split(r"\s+(?:—|-)\s+", maturity_lower, maxsplit=1)[0].strip()
        if maturity_level not in KNOWN_MATURITY_LEVELS:
            findings.append(
                Finding(
                    path,
                    "unknown-maturity-level",
                    "Maturité should start from a known honest level "
                    f"({', '.join(sorted(KNOWN_MATURITY_LEVELS))}).",
                )
            )
        if "—" not in maturity and " - " not in maturity:
            findings.append(
                Finding(
                    path,
                    "maturity-needs-qualifier",
                    "Maturité must include a short qualifier after the level "
                    "so readers see the real current state, not just a label.",
                )
            )

    sovereignty = values.get("Souveraineté", "")
    sovereignty_lower = sovereignty.lower()
    for expected in ("mit", "apache", "mpl", "agpl", "sspl"):
        if expected not in sovereignty_lower:
            findings.append(
                Finding(
                    path,
                    "sovereignty-vocabulary",
                    "Souveraineté must explicitly mention MIT/Apache/MPL compatibility "
                    "and AGPL/SSPL exclusion.",
                )
            )
            break

    for title in REQUIRED_SECTIONS:
        body = section_body(text, title)
        if body is None:
            findings.append(Finding(path, "missing-section", f"required section is missing: ## {title}"))
        elif len(body) < 40:
            findings.append(
                Finding(
                    path,
                    "section-too-short",
                    f"section ## {title} must contain a useful, non-placeholder explanation.",
                )
            )

    for pattern in LOCAL_PATH_PATTERNS:
        for match in pattern.finditer(text):
            findings.append(
                Finding(
                    path,
                    "machine-local-path",
                    "README must not embed machine-local paths; use repo-relative paths or variables.",
                    find_line(text, match.start()),
                )
            )

    return findings


def resolve_readme_path(path: Path) -> Path:
    if path.is_dir():
        return path / "README.md"
    return path


def validate_path(path: Path) -> list[Finding]:
    readme_path = resolve_readme_path(path)
    display_path = str(readme_path)
    if not readme_path.exists():
        return [Finding(display_path, "missing-readme", "README.md does not exist.")]
    if not readme_path.is_file():
        return [Finding(display_path, "not-a-file", "README path is not a file.")]
    try:
        text = readme_path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        return [Finding(display_path, "invalid-utf8", f"README must be UTF-8: {exc}")]
    return validate_text(text, display_path)


def paths_from_list(file_path: Path) -> list[Path]:
    paths: list[Path] = []
    for raw in file_path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        paths.append(Path(line))
    return paths


def run_self_test() -> int:
    valid = """# sample

**Couche** : Rumble
**Rôle** : démonstrateur de garde-fou README
**deployment_class** : product-linkable
**Maturité** : contract-first — contrat documenté, runtime volontairement absent
**Place dans la chaîne DoD** : montre comment un README expose sa place dans la boucle preuve.
**Doctrine** : preuve avant promesse ; pas de claims runtime non testés.
**Souveraineté** : licences MIT/Apache/MPL compatibles ; pas d’AGPL/SSPL dans la chaîne versionnée.

## Ce que ça fait

Explique clairement l’état réel du dépôt et ce qui reste hors scope aujourd’hui.

## Où ça se branche

- Amont : contrats partagés et ADRs.
- Aval : validateurs et revues de maturité.
"""
    invalid = valid.replace("**deployment_class** : product-linkable", "**deployment_class** : cloud-only")
    valid_findings = validate_text(valid, "valid.md")
    invalid_findings = validate_text(invalid, "invalid.md")
    if valid_findings:
        print("self-test valid fixture failed", file=sys.stderr)
        print_report(valid_findings, "text")
        return 1
    if not any(f.code == "invalid-deployment-class" for f in invalid_findings):
        print("self-test invalid fixture did not fail as expected", file=sys.stderr)
        print_report(invalid_findings, "text")
        return 1
    print("README guardrail self-test ok")
    return 0


def print_report(findings: Sequence[Finding], output_format: str) -> None:
    if output_format == "json":
        print(json.dumps([finding.as_dict() for finding in findings], indent=2, ensure_ascii=False))
        return

    if not findings:
        print("README guardrail: OK")
        return

    print(f"README guardrail: {len(findings)} finding(s)", file=sys.stderr)
    for finding in findings:
        location = finding.path if finding.line is None else f"{finding.path}:{finding.line}"
        print(f"- {location}: {finding.code}: {finding.message}", file=sys.stderr)


def parse_args(argv: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate ecosystem README canonical headers.")
    parser.add_argument(
        "paths",
        nargs="*",
        type=Path,
        help="README files or repository directories. Defaults to ./README.md.",
    )
    parser.add_argument(
        "--from-list",
        type=Path,
        help="Read README/repository paths from a newline-delimited file.",
    )
    parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="Report format.",
    )
    parser.add_argument("--self-test", action="store_true", help="Run built-in smoke fixtures and exit.")
    return parser.parse_args(argv)


def collect_paths(args: argparse.Namespace) -> list[Path]:
    paths: list[Path] = list(args.paths)
    if args.from_list:
        paths.extend(paths_from_list(args.from_list))
    if not paths:
        paths.append(Path("README.md"))
    return paths


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    if args.self_test:
        return run_self_test()

    findings: list[Finding] = []
    for path in collect_paths(args):
        findings.extend(validate_path(path))

    print_report(findings, args.format)
    return 1 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
