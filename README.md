# How to Launch Your Business by Starting a Cult Like a White Woman

> **Original theory by [Scrivs (@mrpaulscrivens)](https://www.threads.com/@mrpaulscrivens).** This skill is based on his 21-part thread, **[How to Get Filthy Rich by Starting a Cult Like a White Woman](https://www.threads.com/@mrpaulscrivens/post/DdJoxz1Fb4K)**. This credits the theory, not authorship of the skill.

[![Skill checks](https://github.com/xiaofei-du/cult-like-launch/actions/workflows/skill-checks.yml/badge.svg?branch=main&event=push)](https://github.com/xiaofei-du/cult-like-launch/actions/workflows/skill-checks.yml)

A reusable Codex skill for building a **Launch Playbook** around the business you are promoting: its audience, shared beliefs, following, offer, campaign copy, and publication sequence.

The person using the skill can be a promoter, employee, agency representative, affiliate, founder, or someone else. Discovery starts with your actual role and relationship to the audience, then establishes whose public voice the campaign will use.

## What it does

- Understands the business, audience, offer, and the people involved before fixing the positioning.
- Inspects available product or service material and connects it to concrete audience benefits.
- Diagnoses two purchase beliefs: **I can achieve the outcome** and **you can help me achieve it**.
- Applies five mechanisms: **A Belief System, A Common Enemy, A Charismatic Leader, Built-in Evangelism, and Exclusivity**.
- Connects a core following to broader buyers through results they want.
- Produces usable campaign copy and a publication sequence, with evidence and unresolved inputs clearly identified.

The seven foundations are a practical organization of the source's two beliefs and five elements. They are diagnostic prompts, not validated performance scores.

## Contact

If you find the skill useful or have an idea for what to add, give me a shout:

[![X (Twitter): @xiaofeidu283](https://img.shields.io/badge/X-%40xiaofeidu283-9A4329?style=flat-square&logo=x&logoColor=white&labelColor=9A4329)](https://x.com/xiaofeidu283)
[![Threads: @smilefei.du](https://img.shields.io/badge/Threads-%40smilefei.du-9A4329?style=flat-square&logo=threads&logoColor=white&labelColor=9A4329)](https://www.threads.com/@smilefei.du)

## Theory and source

**Theory author: [@mrpaulscrivens](https://www.threads.com/@mrpaulscrivens), who calls himself Scrivs in the thread.** This is attribution of the theory, not authorship of this skill.

The guiding source is his 21-part thread, **[How to Get Filthy Rich by Starting a Cult Like a White Woman](https://www.threads.com/@mrpaulscrivens/post/DdJoxz1Fb4K)**, including its two accompanying images.

The repository preserves the [original text](references/original-post.txt), [source map](references/framework.md), and [two](references/images/figure-1.png) [images](references/images/figure-2.png). The skill's discovery workflow and output structure are applications of that source.

## Install in Codex

For a new installation, clone this repository into your Codex skills directory:

```bash
git clone https://github.com/xiaofei-du/cult-like-launch.git \
  "${CODEX_HOME:-$HOME/.codex}/skills/launch-like-a-white-woman"
```

The command expects the destination folder not to exist. The repository root contains `SKILL.md`; keep its `agents/` and `references/` folders alongside it.

## Use

Invoke the skill in Codex with your own brief:

```text
Use $launch-like-a-white-woman to create a Launch Playbook
for the business I am promoting.

Business and offer: ...
My role and background: ...
Target audience: ...
Available product or service material: ...
Desired audience action and channel: ...
```

You can start with an incomplete brief. The skill uses existing context, asks about consequential gaps, and drafts what the available material supports. It can also refine an existing playbook without rewriting every part.

Keep business briefs and generated campaigns in your own workspace. The skill does not itself authorize sending, scheduling, or publishing campaign materials.

## Files

- [SKILL.md](SKILL.md): entrypoint and workflow.
- [Business discovery](references/business-discovery.md): adaptive intake and product evidence guidance.
- [Playbook output](references/playbook-output.md): deliverable structure and campaign requirements.
- [Framework](references/framework.md): source summary and section references.
- [agents/openai.yaml](agents/openai.yaml): Codex display and invocation metadata.

## Development

Read [CONTRIBUTING.md](CONTRIBUTING.md) for semantic commit titles and the
**Because** / **This commit** format used in commits and pull requests.

With [uv](https://docs.astral.sh/uv/getting-started/installation/) installed, run
the same checks as CI from the repository root:

```bash
uv venv --managed-python --python 3.12 .venv
uv pip sync --python .venv/bin/python --require-hashes --only-binary :all: --index-url https://pypi.org/simple requirements-dev.txt
.venv/bin/python scripts/validate_skill.py
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python scripts/build_skill.py
git diff --check
```

The build produces `dist/cult-like-launch.zip` and its SHA-256 checksum. The ZIP
contains only the installable `launch-like-a-white-woman/` directory with its
metadata and references. Tests, repository configuration, and private working
material are excluded by an explicit file inventory.

Successful [Skill checks runs](https://github.com/xiaofei-du/cult-like-launch/actions/workflows/skill-checks.yml)
provide these files as a downloadable artifact for 14 days. No GitHub Release is
published automatically. The checks validate structure and packaging; they do
not test campaign performance.

To update the development dependency, regenerate its pinned version and hashes:

```bash
uv pip compile --generate-hashes --no-header --no-annotate --default-index https://pypi.org/simple -o requirements-dev.txt - <<'EOF'
PyYAML==6.0.3
EOF
```

Change the explicit version when upgrading, inspect the generated diff, then
repeat dependency installation and the checks above.
