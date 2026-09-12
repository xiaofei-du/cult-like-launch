import os
from pathlib import Path
import subprocess
import tempfile
import unittest

import yaml


class PullRequestFormatTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        workflow = Path(__file__).resolve().parents[1] / ".github/workflows/pr-template.yml"
        cls.command = yaml.safe_load(workflow.read_text())["jobs"]["validate"]["steps"][0]["run"]

    def check(self, title, body, cwd=None):
        return subprocess.run(
            ["bash", "-e", "-c", self.command], text=True, capture_output=True, cwd=cwd,
            env={**os.environ, "PR_TITLE": title, "PR_BODY": body},
        )

    def test_semantic_titles_and_filled_sections_are_accepted(self):
        for title in ["ci: validate skill packages", "fix(links): resolve relative resources", "feat(skill)!: rename an input"]:
            with self.subTest(title=title):
                result = self.check(title, "**Because**\n\n- Explain the problem.\n\n**This commit**\n\n- Fix it and report verification.\n")
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_nonsemantic_titles_are_rejected(self):
        for title in ["Update the skill", "FIX: resolve links", "docs: Explain installation", "feat(Upper): add examples"]:
            with self.subTest(title=title):
                result = self.check(title, "**Because**\n- Reason.\n**This commit**\n- Result.\n")
                self.assertNotEqual(result.returncode, 0)

    def test_comments_and_empty_bullets_do_not_fill_the_template(self):
        for body in [
            "**Because**\n- <!-- reason -->\n**This commit**\n- <!-- change -->\n",
            "**Because**\n- \n**This commit**\n- Verified result.\n",
            "## Summary\n- Reason.\n## Tests\n- Tests passed.\n",
            "**This commit**\n- Result.\n**Because**\n- Reason.\n",
        ]:
            with self.subTest(body=body):
                self.assertNotEqual(self.check("docs: clarify installation", body).returncode, 0)

    def test_title_and_body_are_data_not_shell_commands(self):
        with tempfile.TemporaryDirectory() as directory:
            result = self.check(
                "docs: explain $(touch title-marker)",
                "**Because**\n- `touch body-marker`\n**This commit**\n- Explain shell examples.\n",
                cwd=directory,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertFalse((Path(directory) / "title-marker").exists())
            self.assertFalse((Path(directory) / "body-marker").exists())


if __name__ == "__main__":
    unittest.main()
