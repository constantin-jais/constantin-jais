import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).parent
SPEC = importlib.util.spec_from_file_location(
    "validate_repo_profiles", HERE / "validate_repo_profiles.py"
)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class RepositoryProfileTests(unittest.TestCase):
    def test_current_profiles_pass(self):
        self.assertEqual([], MODULE.validate())

    def test_non_public_profile_is_rejected(self):
        catalog = json.loads((HERE / "repo-profiles.json").read_text())
        catalog["profiles"][0]["visibility"] = "private"
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "profiles.json"
            path.write_text(json.dumps(catalog))
            previous = MODULE.CATALOG
            MODULE.CATALOG = path
            try:
                self.assertTrue(
                    any("only public profiles" in error for error in MODULE.validate())
                )
            finally:
                MODULE.CATALOG = previous

    def test_policy_check_drift_is_rejected(self):
        policy = json.loads((HERE / "branch-policy.json").read_text())
        policy["repos"]["libre-ai/website"]["required_checks"] = ["invented"]
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "policy.json"
            path.write_text(json.dumps(policy))
            previous = MODULE.POLICY
            MODULE.POLICY = path
            try:
                self.assertTrue(
                    any("required checks drift" in error for error in MODULE.validate())
                )
            finally:
                MODULE.POLICY = previous


if __name__ == "__main__":
    unittest.main()
