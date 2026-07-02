"""Unit tests for the pure policy-diff core of forge_policy.py.

Run: python3 -m unittest discover ecosystem/governance
No network, no gh: only the pure functions are tested here. The gh-backed
IO is exercised by the governance workflow's post-apply re-check.
"""

from __future__ import annotations

import copy
import unittest

import forge_policy as fp


def sample_policy() -> dict:
    return {
        "version": 1,
        "ruleset_name": "forge-standard",
        "defaults": {
            "target_branch": "main",
            "required_approving_review_count": 0,
            "dismiss_stale_reviews_on_push": True,
            "require_code_owner_review": False,
            "require_last_push_approval": False,
            "required_review_thread_resolution": True,
            "block_force_pushes": True,
            "block_deletions": True,
            "remove_classic_protection": True,
            "repo_settings": {
                "allow_auto_merge": True,
                "delete_branch_on_merge": True,
            },
        },
        "repos": {
            "constantin-jais/constantin-jais": {
                "required_checks": [
                    "Stack workflow conventions",
                    "json-schema-fixtures",
                ],
                "strict_up_to_date": True,
            },
            "constantin-jais/no-checks-yet": {},
        },
    }


def actual_matching_desired(desired: dict) -> dict:
    """Simulate the API response for a ruleset that matches `desired`:
    same content plus server-side noise (ids, timestamps, extra params)."""
    actual = copy.deepcopy(desired)
    actual["id"] = 4242
    actual["created_at"] = "2026-07-02T12:00:00Z"
    actual["updated_at"] = "2026-07-02T12:00:00Z"
    for rule in actual["rules"]:
        if rule["type"] == "pull_request":
            rule["parameters"]["extra_server_side_field"] = "noise"
    return actual


class DesiredRulesetTests(unittest.TestCase):
    def test_shape_for_repo_with_checks(self) -> None:
        desired = fp.desired_ruleset(
            sample_policy(), "constantin-jais/constantin-jais"
        )
        self.assertEqual(desired["name"], "forge-standard")
        self.assertEqual(desired["target"], "branch")
        self.assertEqual(desired["enforcement"], "active")
        self.assertEqual(desired["bypass_actors"], [])
        self.assertEqual(
            desired["conditions"]["ref_name"]["include"], ["~DEFAULT_BRANCH"]
        )
        rules = {rule["type"]: rule for rule in desired["rules"]}
        self.assertIn("deletion", rules)
        self.assertIn("non_fast_forward", rules)
        pr_params = rules["pull_request"]["parameters"]
        self.assertEqual(pr_params["required_approving_review_count"], 0)
        self.assertFalse(pr_params["require_code_owner_review"])
        self.assertTrue(pr_params["required_review_thread_resolution"])
        checks_params = rules["required_status_checks"]["parameters"]
        self.assertTrue(checks_params["strict_required_status_checks_policy"])
        self.assertEqual(
            [c["context"] for c in checks_params["required_status_checks"]],
            ["Stack workflow conventions", "json-schema-fixtures"],
        )
        for check in checks_params["required_status_checks"]:
            self.assertEqual(check["integration_id"], fp.GITHUB_ACTIONS_APP_ID)

    def test_no_status_checks_rule_when_repo_declares_none(self) -> None:
        desired = fp.desired_ruleset(
            sample_policy(), "constantin-jais/no-checks-yet"
        )
        rule_types = [rule["type"] for rule in desired["rules"]]
        self.assertNotIn("required_status_checks", rule_types)

    def test_unknown_repo_is_an_error(self) -> None:
        with self.assertRaises(KeyError):
            fp.desired_ruleset(sample_policy(), "constantin-jais/unlisted")


class DiffRulesetTests(unittest.TestCase):
    def setUp(self) -> None:
        self.policy = sample_policy()
        self.repo = "constantin-jais/constantin-jais"
        self.desired = fp.desired_ruleset(self.policy, self.repo)

    def test_missing_ruleset(self) -> None:
        drift = fp.diff_ruleset(self.desired, None)
        self.assertEqual(len(drift), 1)
        self.assertIn("missing", drift[0])

    def test_clean_when_actual_matches_with_server_noise(self) -> None:
        actual = actual_matching_desired(self.desired)
        self.assertEqual(fp.diff_ruleset(self.desired, actual), [])

    def test_enforcement_drift(self) -> None:
        actual = actual_matching_desired(self.desired)
        actual["enforcement"] = "disabled"
        drift = fp.diff_ruleset(self.desired, actual)
        self.assertTrue(any("enforcement" in line for line in drift))

    def test_approval_count_drift(self) -> None:
        actual = actual_matching_desired(self.desired)
        for rule in actual["rules"]:
            if rule["type"] == "pull_request":
                rule["parameters"]["required_approving_review_count"] = 1
        drift = fp.diff_ruleset(self.desired, actual)
        self.assertTrue(
            any("required_approving_review_count" in line for line in drift)
        )

    def test_missing_required_check_context(self) -> None:
        actual = actual_matching_desired(self.desired)
        for rule in actual["rules"]:
            if rule["type"] == "required_status_checks":
                rule["parameters"]["required_status_checks"] = [
                    {
                        "context": "Stack workflow conventions",
                        "integration_id": fp.GITHUB_ACTIONS_APP_ID,
                    }
                ]
        drift = fp.diff_ruleset(self.desired, actual)
        self.assertTrue(any("json-schema-fixtures" in line for line in drift))

    def test_missing_rule_type(self) -> None:
        actual = actual_matching_desired(self.desired)
        actual["rules"] = [
            rule for rule in actual["rules"] if rule["type"] != "non_fast_forward"
        ]
        drift = fp.diff_ruleset(self.desired, actual)
        self.assertTrue(any("non_fast_forward" in line for line in drift))

    def test_unexpected_bypass_actor(self) -> None:
        actual = actual_matching_desired(self.desired)
        actual["bypass_actors"] = [
            {"actor_id": 5, "actor_type": "RepositoryRole", "bypass_mode": "always"}
        ]
        drift = fp.diff_ruleset(self.desired, actual)
        self.assertTrue(any("bypass_actors" in line for line in drift))


class DiffClassicProtectionTests(unittest.TestCase):
    def test_present_when_removal_required(self) -> None:
        drift = fp.diff_classic_protection(
            sample_policy()["defaults"], protection_present=True
        )
        self.assertEqual(len(drift), 1)
        self.assertIn("legacy branch protection", drift[0])

    def test_absent_is_clean(self) -> None:
        drift = fp.diff_classic_protection(
            sample_policy()["defaults"], protection_present=False
        )
        self.assertEqual(drift, [])


class DiffRepoSettingsTests(unittest.TestCase):
    def test_settings_drift(self) -> None:
        desired = fp.desired_repo_settings(sample_policy())
        actual = {"allow_auto_merge": False, "delete_branch_on_merge": True}
        drift = fp.diff_repo_settings(desired, actual)
        self.assertEqual(len(drift), 1)
        self.assertIn("allow_auto_merge", drift[0])

    def test_settings_clean(self) -> None:
        desired = fp.desired_repo_settings(sample_policy())
        actual = {"allow_auto_merge": True, "delete_branch_on_merge": True}
        self.assertEqual(fp.diff_repo_settings(desired, actual), [])


class WarningsTests(unittest.TestCase):
    def test_repo_without_declared_checks_warns(self) -> None:
        warnings = fp.warnings_for(
            sample_policy(), "constantin-jais/no-checks-yet"
        )
        self.assertTrue(any("required checks" in w for w in warnings))

    def test_repo_with_checks_has_no_warning(self) -> None:
        warnings = fp.warnings_for(
            sample_policy(), "constantin-jais/constantin-jais"
        )
        self.assertEqual(warnings, [])


class RepoDriftTests(unittest.TestCase):
    def test_aggregates_all_sources(self) -> None:
        policy = sample_policy()
        repo = "constantin-jais/constantin-jais"
        desired = fp.desired_ruleset(policy, repo)
        state = fp.RepoState(
            ruleset=None,
            settings={"allow_auto_merge": False, "delete_branch_on_merge": False},
            classic_protection_present=True,
        )
        drift = fp.repo_drift(policy, repo, state)
        self.assertGreaterEqual(len(drift), 4)
        joined = "\n".join(drift)
        self.assertIn("missing", joined)
        self.assertIn("legacy branch protection", joined)
        self.assertIn("allow_auto_merge", joined)
        self.assertIn("delete_branch_on_merge", joined)
        self.assertIsNotNone(desired)


if __name__ == "__main__":
    unittest.main()
