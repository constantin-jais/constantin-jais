import importlib.util
import sys
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).with_name("readme_guardrail.py")
SPEC = importlib.util.spec_from_file_location("readme_guardrail", MODULE_PATH)
assert SPEC is not None
readme_guardrail = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = readme_guardrail
assert SPEC.loader is not None
SPEC.loader.exec_module(readme_guardrail)


VALID_README = """# sample-repo

**Couche** : Gear
**Rôle** : contrat de test pour le validateur README
**deployment_class** : product-linkable
**Maturité** : dojo — preuves locales présentes, intégration produit encore volontairement bornée
**Place dans la chaîne DoD** : expose une brique de preuve lisible par les produits et par les agents.
**Doctrine** : contrat explicite, pas de promesse runtime sans test.
**Souveraineté** : licences MIT/Apache/MPL compatibles ; pas d’AGPL/SSPL dans la chaîne versionnée.

## Ce que ça fait

Décrit le rôle réel du dépôt, son état courant, et les limites qui restent visibles pour les mainteneurs.

## Où ça se branche

- Amont : ADRs et contrats partagés.
- Aval : produits Rumble et gates Wrench/Bolt.
"""


def codes(markdown: str) -> set[str]:
    return {finding.code for finding in readme_guardrail.validate_text(markdown, "fixture.md")}


class ReadmeGuardrailTest(unittest.TestCase):
    def test_valid_readme_passes(self) -> None:
        self.assertEqual(readme_guardrail.validate_text(VALID_README, "fixture.md"), [])

    def test_missing_canonical_field_fails(self) -> None:
        markdown = VALID_README.replace("**Doctrine** : contrat explicite, pas de promesse runtime sans test.\n", "")
        self.assertIn("missing-field", codes(markdown))

    def test_invalid_deployment_class_fails(self) -> None:
        markdown = VALID_README.replace("product-linkable", "cloud-only")
        self.assertIn("invalid-deployment-class", codes(markdown))

    def test_maturity_requires_honest_qualifier(self) -> None:
        markdown = VALID_README.replace(
            "**Maturité** : dojo — preuves locales présentes, intégration produit encore volontairement bornée",
            "**Maturité** : dojo",
        )
        self.assertIn("maturity-needs-qualifier", codes(markdown))

    def test_maturity_must_start_with_known_level(self) -> None:
        markdown = VALID_README.replace(
            "**Maturité** : dojo — preuves locales présentes, intégration produit encore volontairement bornée",
            "**Maturité** : pas done — formulation ambiguë qui contient un mot connu mais ne commence pas par le niveau",
        )
        self.assertIn("unknown-maturity-level", codes(markdown))

    def test_machine_local_paths_fail(self) -> None:
        markdown = VALID_README + "\nDebug transcript: /home/alice/project/target/log.txt\n"
        self.assertIn("machine-local-path", codes(markdown))

    def test_required_sections_fail_when_absent(self) -> None:
        markdown = VALID_README.replace("## Où ça se branche", "## Branchements")
        self.assertIn("missing-section", codes(markdown))


if __name__ == "__main__":
    unittest.main()
