# First Claude Code prompt (copy after extracting this repository)

You are implementing **Magic Rain**, a real-time child-first Kinect v1 interactive art installation for the owner's Windows 10 Pro 22H2 PC and an HDMI TV.

1. Read `AGENTS.md`, `CLAUDE.md`, `WDD/README.md`, all `WDD/00_Product` and `WDD/01_Architecture` docs, `WDD/02_Experience/interaction-and-menu.md`, `WDD/03_Quality/acceptance-criteria.md`, `WDD/04_Delivery/roadmap.md`, `docs/setup/tv-first-preflight.md`, and `docs/setup/windows11-kinect-v1.md` before coding.
2. Follow the WDD as canonical. The child-facing experience must **start automatically and be playable without HUD, symbols, menu interaction, instructions, required poses or scores**.
3. Begin with **MR-00 only**; include a brief **read-only** hardware readiness checklist in handoff, but do not touch USB drivers: create the minimal executable Python project and a visually testable **explicit simulation mode** (`python -m magic_rain --demo`). Do not install Kinect drivers, assume camera access, download large models, create all future modules as empty placeholders, or implement optional features.
4. Propose a short plan showing requirement IDs, expected touched files, test commands and out-of-scope items. Then implement MR-00, run tests and demonstrate a synthetic movement input. Separate sensor, vision, simulation, rendering and app lifecycle behind typed interfaces.
5. Ask for permission only if a consequential system change is required (driver binding, admin privileges, licensing conflict, paid dependency or hardware purchase). Otherwise work autonomously within MR-00.
6. After implementation, perform **one independent reviewer pass** for correctness, child UX invariants, maintainability and tests; address findings; rerun verification. Do not start MR-01 or other issues without a new instruction.
7. Explicitly exclude projector, wall-touch, ball-throwing and climbing-wall work from this iteration; do not add placeholder modules for them. Report `DONE/PARTIAL/BLOCKED`, affected requirements, actual commands/results, changed files, remaining limitations, and the exact next task. **Do not claim real Kinect success without owner hardware validation**.

Engineering preferences: Python 3.11/3.12, pygame-ce, NumPy, pytest, Ruff, minimal dependencies and simple architecture. English technical documentation, Swedish parent-facing strings. Runtime offline and no image/audio recording.
