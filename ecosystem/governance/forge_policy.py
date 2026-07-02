#!/usr/bin/env python3
"""Forge branch policy as code: check/apply GitHub rulesets from a versioned policy.

Governance flow (ADR 0031): agents propose policy changes via pull request;
a human merges; CI applies. Branch protection is never edited by hand or from
an interactive agent session.

Commands:
    check [--repo OWNER/NAME]   compare live state to the policy; exit 2 on drift
    apply [--repo OWNER/NAME]   converge live state to the policy, then re-check
    dump --repo OWNER/NAME      print live state (onboarding aid for new repos)

Auth: uses the `gh` CLI. In CI, set GH_TOKEN to a fine-grained PAT with
"Administration: read and write" on the target repositories.
"""

from __future__ import annotations

import argparse
import dataclasses
import json
import subprocess
import sys
from pathlib import Path

GITHUB_ACTIONS_APP_ID = 15368
DEFAULT_POLICY_PATH = Path(__file__).parent / "branch-policy.json"

# --------------------------------------------------------------------------
# Pure core (unit-tested, no IO)
# --------------------------------------------------------------------------


@dataclasses.dataclass
class RepoState:
    """Live state of one repository, as fetched from the GitHub API."""

    ruleset: dict | None
    settings: dict
    classic_protection_present: bool


def desired_ruleset(policy: dict, repo: str) -> dict:
    """Build the ruleset payload the policy mandates for `repo`.

    Raises KeyError for repos not listed in the policy: applying policy to an
    unlisted repo must be an explicit decision, never a fallback.
    """
    repo_entry = policy["repos"][repo]
    defaults = policy["defaults"]

    rules: list[dict] = []
    if defaults.get("block_deletions", True):
        rules.append({"type": "deletion"})
    if defaults.get("block_force_pushes", True):
        rules.append({"type": "non_fast_forward"})
    rules.append(
        {
            "type": "pull_request",
            "parameters": {
                "required_approving_review_count": defaults[
                    "required_approving_review_count"
                ],
                "dismiss_stale_reviews_on_push": defaults[
                    "dismiss_stale_reviews_on_push"
                ],
                "require_code_owner_review": defaults["require_code_owner_review"],
                "require_last_push_approval": defaults["require_last_push_approval"],
                "required_review_thread_resolution": defaults[
                    "required_review_thread_resolution"
                ],
            },
        }
    )
    checks = repo_entry.get("required_checks", [])
    if checks:
        rules.append(
            {
                "type": "required_status_checks",
                "parameters": {
                    "strict_required_status_checks_policy": repo_entry.get(
                        "strict_up_to_date", True
                    ),
                    "required_status_checks": [
                        {
                            "context": context,
                            "integration_id": GITHUB_ACTIONS_APP_ID,
                        }
                        for context in checks
                    ],
                },
            }
        )

    return {
        "name": policy["ruleset_name"],
        "target": "branch",
        "enforcement": "active",
        "bypass_actors": [],
        "conditions": {"ref_name": {"include": ["~DEFAULT_BRANCH"], "exclude": []}},
        "rules": rules,
    }


def desired_repo_settings(policy: dict) -> dict:
    return dict(policy["defaults"]["repo_settings"])


def _rules_by_type(ruleset: dict) -> dict[str, dict]:
    return {rule["type"]: rule.get("parameters", {}) for rule in ruleset["rules"]}


def _check_contexts(parameters: dict) -> list[str]:
    return sorted(
        check["context"] for check in parameters.get("required_status_checks", [])
    )


def diff_ruleset(desired: dict, actual: dict | None) -> list[str]:
    """Compare the desired ruleset to the live one. Server-side extra fields
    are ignored: only the keys the policy mandates are compared."""
    if actual is None:
        return [f"ruleset '{desired['name']}' missing"]

    drift: list[str] = []
    if actual.get("enforcement") != desired["enforcement"]:
        drift.append(
            "enforcement is "
            f"'{actual.get('enforcement')}' (want '{desired['enforcement']}')"
        )
    if actual.get("bypass_actors"):
        drift.append(
            f"bypass_actors is {actual['bypass_actors']} (want none: nobody "
            "bypasses the policy, the policy itself changes via PR)"
        )
    desired_include = desired["conditions"]["ref_name"]["include"]
    actual_include = (
        actual.get("conditions", {}).get("ref_name", {}).get("include", [])
    )
    if actual_include != desired_include:
        drift.append(
            f"target refs are {actual_include} (want {desired_include})"
        )

    desired_rules = _rules_by_type(desired)
    actual_rules = _rules_by_type(actual)
    for rule_type, desired_params in desired_rules.items():
        if rule_type not in actual_rules:
            drift.append(f"rule '{rule_type}' missing")
            continue
        actual_params = actual_rules[rule_type]
        if rule_type == "required_status_checks":
            desired_contexts = _check_contexts(desired_params)
            actual_contexts = _check_contexts(actual_params)
            for context in desired_contexts:
                if context not in actual_contexts:
                    drift.append(f"required check '{context}' missing")
            for context in actual_contexts:
                if context not in desired_contexts:
                    drift.append(f"required check '{context}' not in policy")
            key = "strict_required_status_checks_policy"
            if actual_params.get(key) != desired_params[key]:
                drift.append(
                    f"{key} is {actual_params.get(key)} (want {desired_params[key]})"
                )
            continue
        for key, desired_value in desired_params.items():
            if actual_params.get(key) != desired_value:
                drift.append(
                    f"rule '{rule_type}' parameter {key} is "
                    f"{actual_params.get(key)!r} (want {desired_value!r})"
                )
    for rule_type in actual_rules:
        if rule_type not in desired_rules:
            drift.append(f"rule '{rule_type}' present but not in policy")
    return drift


def diff_classic_protection(defaults: dict, protection_present: bool) -> list[str]:
    if protection_present and defaults.get("remove_classic_protection", False):
        return [
            "legacy branch protection still present (superseded by the "
            "ruleset; remove it so there is a single source of policy)"
        ]
    return []


def diff_repo_settings(desired: dict, actual: dict) -> list[str]:
    drift = []
    for key, desired_value in desired.items():
        if actual.get(key) != desired_value:
            drift.append(
                f"repo setting {key} is {actual.get(key)!r} (want {desired_value!r})"
            )
    return drift


def warnings_for(policy: dict, repo: str) -> list[str]:
    if not policy["repos"][repo].get("required_checks"):
        return [
            f"{repo}: no required checks declared - merges gate on nothing "
            "but the pull-request rule; declare its CI contexts in the policy"
        ]
    return []


def repo_drift(policy: dict, repo: str, state: RepoState) -> list[str]:
    desired = desired_ruleset(policy, repo)
    drift = diff_ruleset(desired, state.ruleset)
    drift += diff_classic_protection(
        policy["defaults"], state.classic_protection_present
    )
    drift += diff_repo_settings(desired_repo_settings(policy), state.settings)
    return drift


# --------------------------------------------------------------------------
# gh-backed IO (exercised by the governance workflow's post-apply re-check)
# --------------------------------------------------------------------------


def gh_api(path: str, method: str = "GET", payload: dict | None = None) -> dict | list:
    command = ["gh", "api", "-X", method, path]
    stdin = None
    if payload is not None:
        command += ["--input", "-"]
        stdin = json.dumps(payload)
    result = subprocess.run(
        command, input=stdin, capture_output=True, text=True, check=True
    )
    return json.loads(result.stdout) if result.stdout.strip() else {}


def _gh_api_or_none(path: str) -> dict | list | None:
    """GET that treats 404 as None (absence), any other failure as an error."""
    try:
        return gh_api(path)
    except subprocess.CalledProcessError as error:
        if "HTTP 404" in (error.stderr or ""):
            return None
        raise


def fetch_state(policy: dict, repo: str) -> RepoState:
    branch = policy["defaults"]["target_branch"]
    ruleset = None
    listed = gh_api(f"repos/{repo}/rulesets")
    for candidate in listed:
        if candidate["name"] == policy["ruleset_name"]:
            ruleset = gh_api(f"repos/{repo}/rulesets/{candidate['id']}")
            break
    repo_info = gh_api(f"repos/{repo}")
    settings = {
        key: repo_info.get(key)
        for key in desired_repo_settings(policy)
    }
    protection = _gh_api_or_none(f"repos/{repo}/branches/{branch}/protection")
    return RepoState(
        ruleset=ruleset,
        settings=settings,
        classic_protection_present=protection is not None,
    )


def apply_repo(policy: dict, repo: str) -> None:
    branch = policy["defaults"]["target_branch"]
    desired = desired_ruleset(policy, repo)

    existing_id = None
    for candidate in gh_api(f"repos/{repo}/rulesets"):
        if candidate["name"] == policy["ruleset_name"]:
            existing_id = candidate["id"]
            break
    if existing_id is None:
        gh_api(f"repos/{repo}/rulesets", method="POST", payload=desired)
        print(f"{repo}: ruleset '{desired['name']}' created")
    else:
        gh_api(f"repos/{repo}/rulesets/{existing_id}", method="PUT", payload=desired)
        print(f"{repo}: ruleset '{desired['name']}' updated")

    gh_api(f"repos/{repo}", method="PATCH", payload=desired_repo_settings(policy))
    print(f"{repo}: repo settings converged")

    if policy["defaults"].get("remove_classic_protection", False):
        protection_path = f"repos/{repo}/branches/{branch}/protection"
        if _gh_api_or_none(protection_path) is not None:
            gh_api(protection_path, method="DELETE")
            print(f"{repo}: legacy branch protection removed")


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------


def load_policy(path: Path) -> dict:
    with path.open() as handle:
        return json.load(handle)


def _selected_repos(policy: dict, repo: str | None) -> list[str]:
    if repo is None:
        return sorted(policy["repos"])
    if repo not in policy["repos"]:
        sys.exit(f"error: {repo} is not listed in the policy (explicit-list only)")
    return [repo]


def command_check(policy: dict, repo: str | None) -> int:
    exit_code = 0
    for target in _selected_repos(policy, repo):
        state = fetch_state(policy, target)
        drift = repo_drift(policy, target, state)
        for warning in warnings_for(policy, target):
            print(f"warning: {warning}")
        if drift:
            exit_code = 2
            print(f"DRIFT {target}:")
            for line in drift:
                print(f"  - {line}")
        else:
            print(f"OK {target}")
    return exit_code


def command_apply(policy: dict, repo: str | None) -> int:
    for target in _selected_repos(policy, repo):
        apply_repo(policy, target)
    print("post-apply verification:")
    return command_check(policy, repo)


def command_dump(policy: dict, repo: str) -> int:
    branch = policy["defaults"]["target_branch"]
    print(json.dumps(
        {
            "rulesets": gh_api(f"repos/{repo}/rulesets"),
            "classic_protection": _gh_api_or_none(
                f"repos/{repo}/branches/{branch}/protection"
            ),
            "settings": {
                key: gh_api(f"repos/{repo}").get(key)
                for key in desired_repo_settings(policy)
            },
        },
        indent=2,
    ))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "command", choices=["check", "apply", "dump"], help="operation to run"
    )
    parser.add_argument("--repo", help="restrict to one OWNER/NAME from the policy")
    parser.add_argument(
        "--policy",
        type=Path,
        default=DEFAULT_POLICY_PATH,
        help="path to branch-policy.json",
    )
    arguments = parser.parse_args()
    policy = load_policy(arguments.policy)

    if arguments.command == "check":
        return command_check(policy, arguments.repo)
    if arguments.command == "apply":
        return command_apply(policy, arguments.repo)
    if arguments.repo is None:
        sys.exit("error: dump requires --repo")
    return command_dump(policy, arguments.repo)


if __name__ == "__main__":
    sys.exit(main())
