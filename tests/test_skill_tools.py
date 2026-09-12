import hashlib
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import zipfile


REPO = Path(__file__).resolve().parents[1]


class SkillToolsTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name) / "skill"
        self.root.mkdir()
        self.files = {
            "SKILL.md": (
                "---\nname: launch-like-a-white-woman\n"
                "description: Build a launch playbook from a business brief.\n---\n"
                "# Example skill\n\n[Framework](references/framework.md)\n"
            ).encode(),
            "agents/openai.yaml": (
                'interface:\n  display_name: "Example launch skill"\n'
                '  short_description: "Build a launch playbook from a brief"\n'
                '  default_prompt: "Use $launch-like-a-white-woman to draft a playbook."\n'
            ).encode(),
            "references/business-discovery.md": b"# Discovery\n",
            "references/playbook-output.md": b"# Output\n",
            "references/framework.md": b"# Framework\n[Source](original-post.txt)\n",
            "references/original-post.txt": b"Reference text for the test fixture.\n",
            "references/images/figure-1.png": b"first image fixture",
            "references/images/figure-2.png": b"second image fixture",
        }
        for name, content in self.files.items():
            path = self.root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content)
        (self.root / "README.md").write_text("# Repository\n[Skill](SKILL.md)\n")

    def run_tool(self, name, *args):
        return subprocess.run(
            [sys.executable, str(REPO / "scripts" / name), "--root", str(self.root), *args],
            text=True, capture_output=True,
        )

    def assert_invalid(self, fragment):
        result = self.run_tool("validate_skill.py")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(fragment, result.stderr.lower())

    def test_valid_skill_and_external_links_pass_without_network(self):
        with (self.root / "SKILL.md").open("a") as file:
            file.write("[External](https://example.invalid/unavailable)\n")
        result = self.run_tool("validate_skill.py")
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_missing_description_is_rejected(self):
        path = self.root / "SKILL.md"
        path.write_text(path.read_text().replace(
            "description: Build a launch playbook from a business brief.\n", ""
        ))
        self.assert_invalid("description")

    def test_invalid_frontmatter_yaml_is_rejected(self):
        (self.root / "SKILL.md").write_text("---\nname: [broken\n---\n# Skill\n")
        self.assert_invalid("yaml")

    def test_missing_required_file_is_rejected(self):
        (self.root / "references/images/figure-2.png").unlink()
        self.assert_invalid("figure-2.png")

    def test_broken_local_link_is_rejected(self):
        with (self.root / "SKILL.md").open("a") as file:
            file.write("[Missing](references/missing.md)\n")
        self.assert_invalid("link")

    def test_repository_only_file_cannot_be_a_bundled_dependency(self):
        (self.root / "private-brief.md").write_text("Private example outside the package.\n")
        with (self.root / "SKILL.md").open("a") as file:
            file.write("[Brief](private-brief.md)\n")
        self.assert_invalid("unpackaged")

    def test_parent_path_link_is_rejected_even_when_target_exists(self):
        (self.root.parent / "outside.md").write_text("Outside the repository.\n")
        with (self.root / "README.md").open("a") as file:
            file.write("[Outside](../outside.md)\n")
        self.assert_invalid("outside")

    def test_symlink_cannot_supply_a_package_file(self):
        target = self.root.parent / "outside.txt"
        target.write_text("Outside source.\n")
        source = self.root / "references/original-post.txt"
        source.unlink()
        source.symlink_to(target)
        self.assert_invalid("symlink")

    def test_metadata_must_invoke_the_declared_skill(self):
        path = self.root / "agents/openai.yaml"
        path.write_text(path.read_text().replace("$launch-like-a-white-woman", "$another-skill"))
        self.assert_invalid("default_prompt")

    def test_bundle_preserves_bytes_and_excludes_unlisted_material(self):
        (self.root / "private-brief.md").write_text("Do not distribute.\n")
        output = self.root / "dist/skill.zip"
        result = self.run_tool("build_skill.py", "--output", str(output))
        self.assertEqual(result.returncode, 0, result.stderr)
        with zipfile.ZipFile(output) as archive:
            self.assertEqual(set(archive.namelist()), {
                "launch-like-a-white-woman/SKILL.md",
                "launch-like-a-white-woman/agents/openai.yaml",
                "launch-like-a-white-woman/references/business-discovery.md",
                "launch-like-a-white-woman/references/playbook-output.md",
                "launch-like-a-white-woman/references/framework.md",
                "launch-like-a-white-woman/references/original-post.txt",
                "launch-like-a-white-woman/references/images/figure-1.png",
                "launch-like-a-white-woman/references/images/figure-2.png",
            })
            for name, content in self.files.items():
                self.assertEqual(archive.read("launch-like-a-white-woman/" + name), content)
        checksum = output.with_suffix(".zip.sha256").read_text().split()
        self.assertEqual(checksum, [hashlib.sha256(output.read_bytes()).hexdigest(), "skill.zip"])

    def test_bundle_bytes_do_not_depend_on_source_mtime(self):
        import os
        first = self.root / "dist/first.zip"
        second = self.root / "dist/second.zip"
        result = self.run_tool("build_skill.py", "--output", str(first))
        self.assertEqual(result.returncode, 0, result.stderr)
        for name in self.files:
            os.utime(self.root / name, (1_600_000_000, 1_600_000_000))
        result = self.run_tool("build_skill.py", "--output", str(second))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(first.read_bytes(), second.read_bytes())

    def test_invalid_skill_does_not_produce_an_archive(self):
        (self.root / "references/framework.md").unlink()
        output = self.root / "dist/invalid.zip"
        result = self.run_tool("build_skill.py", "--output", str(output))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("framework.md", result.stderr)
        self.assertFalse(output.exists())


if __name__ == "__main__":
    unittest.main()
