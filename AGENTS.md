# Agent operating contract (canonical)

Applies to Claude Code, Codex and other coding agents. `CLAUDE.md` is a brief Claude-specific entry point; **this document is authoritative for agent behavior**. The WDD is authoritative for what to build.

## Non-negotiable product invariants

1. A child starts playing by **entering the camera field**, not by navigating a UI.
2. During normal play: **zero instructional text, zero visible HUD, zero score, zero icons, zero buttons**. The scene itself gives feedback.
3. Rain responds to the body's silhouette even if pose estimation fails. Advanced pose gestures must never block baseline play.
4. Runtime is offline, locally processed, with no image/audio/video recording or transmission by default.
5. Keyboard-only parent controls, not child-facing controls. Calm visuals, no flashes/strobes or jump scares.
6. The app must also work in an **explicit simulated sensor mode** so developers and CI can test without hardware; simulation must not masquerade as a connected Kinect.
7. Sensor code and rendering code are isolated behind typed contracts; never let USB/driver calls leak into art/physics modules.
8. **TV-first scope:** no projector mapping, touch wall, climbing-wall, ball detection or console controls in v1. Keep existing coordinate interfaces reusable; do not build speculative hardware plugins or projection-calibration layers.

## Read in order before coding

`README.md` -> `WDD/README.md` -> relevant WDD section -> `WDD/04_Delivery/roadmap.md` -> `WDD/03_Quality/acceptance-criteria.md` -> `docs/setup/tv-first-preflight.md` -> `docs/setup/windows11-kinect-v1.md` if touching the Kinect backend.

## Change protocol / WDD-first

- Choose **one phase-sized issue** from `WDD/04_Delivery/roadmap.md` and scope one PR to one issue. For a local repository without GitHub issues, write the chosen task ID in the branch/PR description and do not pretend an issue exists.
- Before implementation, record the affected requirement IDs, interfaces, tests, touched modules, risks and explicit **out of scope**. If behavior/architecture changes, update WDD in the same PR before code.
- Do not copy or fork entire third-party repositories; use a narrow integration with verified licenses and documented versions. Do not modify the OS USB driver automatically without adult consent.
- Build the smallest vertical slice. Avoid feature expansion, unnecessary abstractions, multiple parallel implementations and speculative frameworks.
- Test without hardware using synthetic fixtures; test on real Kinect before claiming hardware acceptance. A hardware-blocked phase is `BLOCKED`, not `DONE`.
- Review changes **once** with a distinct reviewer/agent, address actionable feedback, then run final verification; a second review is reserved for substantial unresolved defects. Do not create infinite review loops.
- Before every PR, refresh from latest main/master and check for conflicting open PRs. Never force-push someone else's branch. Do not merge without explicitly authorized instruction.
- Keep a short handoff: changed files, decisions, tests run/results, limitations, next issue. Never fabricate benchmarks or physical device results.

## Definition of done

Relevant WDD change + code + tests + acceptance evidence (automated or explicitly marked manual/pending) + no regression in core child UX. Unit and integration checks pass. Rendering is visibly evaluated (recorded demo is acceptable **only with synthetic data**, unless the operator explicitly permits live capture). Hardware results require operator observation.

## Stop conditions

Stop and report instead of guessing when: hardware identifiers mismatch, driver operations require admin, a library license is incompatible, Kinect frame input cannot be verified, runtime exhibits persistent unsafe flicker, or a change violates a child UX invariant.

## Commands (to be created by implementation)

`python -m magic_rain --demo` (explicit simulator); `python -m magic_rain --doctor` (sensor check); `python -m magic_rain` (real sensor, graceful fault message). `pytest -q`; `ruff check .`. These are **target interfaces**, not commands that work in this specification-only repository.
