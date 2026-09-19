"""Enforce this project's declared artifact budgets on active changes."""
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]


class OpenSpecScopeTests(unittest.TestCase):
    def test_active_changes_respect_configured_limits(self):
        config = (ROOT / "openspec/config.yaml").read_text(encoding="utf-8")
        policy = config.split("team_harness:\n", 1)[1]

        def limit(key):
            match = re.search(rf"(?m)^  {key}: (\d+)\s*$", policy)
            self.assertIsNotNone(match, f"Missing configured limit: {key}")
            return int(match.group(1))

        proposal_limit = limit("proposal_max_words")
        task_limit = limit("tasks_max_items")
        requirement_limit = limit("max_requirements_per_change")
        section_match = re.search(r"(?m)^  proposal_required_sections:\n((?:    - .+\n?)+)", policy)
        self.assertIsNotNone(section_match, "Missing required section configuration")
        sections = [line.strip()[2:] for line in section_match.group(1).splitlines()]
        changes = ROOT / "openspec/changes"
        for change in sorted(changes.iterdir()):
            if not change.is_dir() or change.name == "archive":
                continue
            with self.subTest(change=change.name):
                proposal = (change / "proposal.md").read_text(encoding="utf-8")
                tasks = (change / "tasks.md").read_text(encoding="utf-8")
                specs = list((change / "specs").rglob("spec.md"))
                self.assertTrue(specs, "A product change must declare a capability delta")
                self.assertLess(len(proposal.split()), proposal_limit)
                self.assertLessEqual(len(re.findall(r"(?m)^- \[[ xX]\]", tasks)), task_limit)
                for section in sections:
                    self.assertRegex(proposal, rf"(?m)^## {re.escape(section)}\s*$")
                requirements = sum(
                    len(re.findall(r"(?m)^### Requirement:", spec.read_text(encoding="utf-8")))
                    for spec in specs
                )
                self.assertGreater(requirements, 0)
                self.assertLessEqual(requirements, requirement_limit)


if __name__ == "__main__":
    unittest.main()
