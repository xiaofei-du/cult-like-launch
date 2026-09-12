"""Validate the portable skill and local Markdown resource paths without network access."""

import argparse
from pathlib import Path
import re
import sys
from urllib.parse import unquote, urlsplit

import yaml


SKILL_NAME = "cult-like-launch"
PACKAGE_FILES = (
    "LICENSE",
    "SKILL.md",
    "THIRD_PARTY_NOTICES.md",
    "agents/openai.yaml",
    "references/business-discovery.md",
    "references/framework.md",
    "references/images/figure-1.png",
    "references/images/figure-2.png",
    "references/original-post.txt",
    "references/playbook-output.md",
)


def load_mapping(text, label):
    try:
        value = yaml.safe_load(text)
    except yaml.YAMLError as error:
        raise ValueError(f"{label}: invalid YAML") from error
    if not isinstance(value, dict):
        raise ValueError(f"{label}: expected a YAML mapping")
    return value


def check_links(root, document, packaged):
    # Ignore fenced examples; validate inline Markdown links and images.
    text = re.sub(r"(?ms)^```[^\n]*\n.*?^```[^\n]*$", "", document.read_text())
    for match in re.finditer(r"\]\((<[^>]+>|[^\s)]+)(?:\s+\"[^\"]*\")?\)", text):
        destination = match.group(1).strip("<>")
        url = urlsplit(destination)
        if url.scheme in {"http", "https", "mailto"} or destination.startswith("#"):
            continue
        if url.scheme or url.netloc:
            raise ValueError(f"{document.relative_to(root)}: unsupported local link {destination}")
        local_path = Path(unquote(url.path))
        if local_path.is_absolute():
            raise ValueError(f"{document.relative_to(root)}: local links must use relative paths")
        target = (document.parent / local_path).resolve()
        if not target.is_relative_to(root):
            raise ValueError(f"{document.relative_to(root)}: link points outside the repository")
        if not target.is_file():
            raise ValueError(f"{document.relative_to(root)}: missing link target {destination}")
        if packaged and target.relative_to(root).as_posix() not in PACKAGE_FILES:
            raise ValueError(f"{document.relative_to(root)}: unpackaged link target {destination}")


def validate(root):
    root = root.resolve()
    for name in PACKAGE_FILES:
        path = root / name
        if path.is_symlink() or any(p.is_symlink() for p in path.parents if p != root and p.is_relative_to(root)):
            raise ValueError(f"{name}: symlink is not allowed in the package")
        if not path.resolve().is_relative_to(root):
            raise ValueError(f"{name}: file is outside the repository")
        if not path.is_file():
            raise ValueError(f"Missing package file: {name}")

    skill = (root / "SKILL.md").read_text()
    frontmatter = re.match(r"\A---\r?\n(.*?)\r?\n---(?:\r?\n|\Z)", skill, flags=re.S)
    if not frontmatter:
        raise ValueError("SKILL.md: missing YAML frontmatter")
    data = load_mapping(frontmatter.group(1), "SKILL.md")
    if data.get("name") != SKILL_NAME:
        raise ValueError(f"SKILL.md: name must match the installable directory {SKILL_NAME}")
    if not isinstance(data.get("description"), str) or not data["description"].strip():
        raise ValueError("SKILL.md: description must be a non-empty string")
    if not re.search(r"(?m)^# \S", skill[frontmatter.end():]):
        raise ValueError("SKILL.md: missing document title")

    metadata = load_mapping((root / "agents/openai.yaml").read_text(), "agents/openai.yaml")
    interface = metadata.get("interface")
    if not isinstance(interface, dict):
        raise ValueError("agents/openai.yaml: missing interface mapping")
    for field in ("display_name", "short_description", "default_prompt"):
        if not isinstance(interface.get(field), str) or not interface[field].strip():
            raise ValueError(f"agents/openai.yaml: {field} must be a non-empty string")
    if not 25 <= len(interface["short_description"]) <= 64:
        raise ValueError("agents/openai.yaml: short_description must contain 25–64 characters")
    if not re.search(r"\$" + re.escape(SKILL_NAME) + r"(?![a-z0-9-])", interface["default_prompt"]):
        raise ValueError("agents/openai.yaml: default_prompt must invoke the declared skill")

    documents = {root / name for name in PACKAGE_FILES if name.endswith(".md")}
    documents.update(root / name for name in ("README.md", "AGENTS.md", "CONTRIBUTING.md") if (root / name).exists())
    for document in sorted(documents):
        check_links(root, document, document.relative_to(root).as_posix() in PACKAGE_FILES)
    return data["name"]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    try:
        name = validate(args.root)
    except (ValueError, OSError) as error:
        print(f"Validation failed: {error}", file=sys.stderr)
        return 1
    print(f"Validated {name}: {len(PACKAGE_FILES)} package files, metadata, and local resource links.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
