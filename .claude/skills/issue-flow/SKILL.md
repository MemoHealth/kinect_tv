---
name: issue-flow
description: Implement a single Magic Rain roadmap issue with WDD-first design, tests, one review, and an honest hardware gate.
---

# Single-issue implementation skill

1. Read `AGENTS.md`, `WDD/README.md`, roadmap issue and dependent specifications. Check main/master and conflicting branches/PRs when repository is connected.
2. State a **4–8 sentence plan**: task ID, interfaces, requirement IDs, tests, files, exclusions. Do not widen scope into the next roadmap issue.
3. Update the applicable canonical WDD file first **only when actual design changes**. Implement minimal vertical slice, keep hardware imports behind `sensors/`, add synthetic fixtures/tests.
4. Run `ruff check .`, `pytest -q`, and relevant manual `--demo` verification as available; report NOT RUN instead of claiming a nonexistent execution.
5. Delegate/perform one independent, focused review: no HUD, no required gestures, no runtime network, no camera recordings, true sensor-vs-demo distinction, performance regression, tests.
6. Fix defects, rerun verification, then summarize with `DONE`, `PARTIAL` or `BLOCKED`. If a physical Kinect requirement is untested, explicitly mark it **pending** and stop short of a live-device completion claim.
7. One issue per PR; before PR refresh latest main, check conflicts; do not merge without approval. Short handoff, no transcript bloat.

If an operator asks for multiple independent issues, tackle one at a time unless concurrent independent work and branch ownership are explicit. If driver changes need admin, stop and provide a reviewed command plan.
