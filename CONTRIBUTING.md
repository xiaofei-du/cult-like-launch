# Contributing to Cult-like Launch

## Commit messages and PR titles

Use semantic commits (Conventional Commits):

```text
type(scope): short description
```

The scope is optional. Use a lowercase type, a short lowercase scope such as
`skill`, `sources`, `package`, or `docs`, and start the English description in
lowercase. Describe the concrete change rather than saying "update" or
"improvements".

Supported types: `feat`, `fix`, `docs`, `refactor`, `perf`, `test`, `build`, `ci`,
`chore`, `style`, and `revert`. Use `!` before the colon for a breaking change and
explain its impact and migration in the body.

Examples:

```text
fix(package): reject missing reference files
feat(skill): distinguish the promoter from the public speaker
docs: explain installation and invocation
ci: validate pull request descriptions
```

Apply this format to new commits, PR titles, and squash-merge titles. Keep each
commit focused on one logical change. Do not rewrite published history solely to
change its formatting.

## Commit bodies and pull requests

Use the same two sections for the commit body and PR description:

```markdown
**Because**

- Explain the user-visible problem, requirement, or reason for the change.

**This commit**

- Describe the resulting behavior and the relevant changes.
- State what you verified, including results and any remaining limitations.
```

Start directly with `**Because**`. Both headings are bold text, and each section
needs at least one concrete bullet. Replace the template comments with your own
content. Keep small changes brief; include a before/after example when useful.

The **Validate PR title and body** check runs when a pull request is created or
edited and when its commits change. It checks the PR title and description.
Individual commit formatting remains a contributor convention; the workflow
does not inspect each Git commit. Required merge checks are a separate repository
setting.

## Scope and attribution

Keep the original theory credit to **@mrpaulscrivens (Scrivs)** prominent at the
beginning of the README. Distinguish his source claims from the skill's practical
workflow and new creative applications. The original thread and images retain
their source attribution.

Do not commit private business material or real customer campaigns as examples.
Use synthetic fixtures for automated checks. Keep the installable skill's name,
metadata, resource links, and package inventory consistent.

## Verification and distribution

Follow the [development instructions](README.md#development). The **Skill checks**
workflow runs on pull requests, pushes to `main`, and manual dispatch. It uses
Python 3.12, hash-verified dependencies, and commit-pinned GitHub Actions to:

- Validate the skill's frontmatter, invocation metadata, required files, and local
  Markdown resource paths, including whether bundled links survive installation.
- Exercise accepted and rejected validator and PR-format inputs, plus archive
  contents, checksums, and repeatable builds under the same toolchain.
- Build an explicit allowlist of skill files into a ZIP and compare its bytes
  with the source files before uploading the ZIP and SHA-256 checksum as a
  GitHub Actions artifact, retained for 14 days.

The artifact is a downloadable build, not a published GitHub Release. This
workflow does not publish campaigns or run live business experiments. Structural
validation does not prove campaign effectiveness. External website availability
and full Markdown rendering are outside the local link check.

For documentation-only changes, run the validator and `git diff --check`.
For scripts or workflow changes, also run the tests and package build. Report
the results you actually obtained. When changing dependencies, regenerate the
hash-pinned requirements as described in the development instructions.

These contribution conventions and the PR template check follow
[Attention's contributing guide](https://github.com/xiaofei-du/attention/blob/f8711397c227c683418f342bdffb29c2f0d60959/CONTRIBUTING.md),
with validation and packaging adapted to a reusable skill.
