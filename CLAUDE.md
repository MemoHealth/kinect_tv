# Claude Code instructions

This repository is **Magic Rain**, a children's full-screen Kinect v1 interactive art installation. This file is an entry point; read and follow [`AGENTS.md`](AGENTS.md) first. Use [`WDD/README.md`](WDD/README.md) to find canonical requirements. Do not reinterpret child UX requirements as a standard game interface.

## Workflow

Read relevant WDD + issue; propose a short plan with requirement IDs, tests and exclusions; implement one bounded vertical slice; add tests; perform one review; verify; write a concise result with any hardware gates still outstanding. Follow [`.claude/skills/issue-flow/SKILL.md`](.claude/skills/issue-flow/SKILL.md) when executing a task.

First task: follow [`docs/claude/FIRST_PROMPT.md`](docs/claude/FIRST_PROMPT.md). Read [`docs/setup/tv-first-preflight.md`](docs/setup/tv-first-preflight.md) for non-invasive hardware readiness checks; implementation remains **MR-00 only** until separately authorized. No request to build all phases at once. Do not silently install drivers, run third-party admin scripts, or download models without clear operator authorization.
