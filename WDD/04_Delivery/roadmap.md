# Implementation roadmap — one issue / one PR

Do **not** assign phase completion before proof. Suggested names (`MR-xx`) are local planned task IDs, **not** already-created GitHub issues. Create GitHub issues when a remote repository exists; check open PRs before duplicate work.

## Before or alongside MR-00 — Non-invasive operator preflight

**No coding issue and no driver changes.** Use `docs/setup/tv-first-preflight.md` to check sensor model, external power/USB adapter, free USB port, HDMI display and safe camera placement. Record unknowns; do not block simulated development if the operator has not connected hardware yet. Device detection and depth streaming are separate checks.

## MR-00 — Repository bootstrap + developer harness

**Goal:** installable Python package and explicit `--demo` window with synthetically moving obstacles and basic full-screen transition; no Kinect integration. Scope: pyproject, src layout, Ruff/Pytest, simple CI, config, simulation adapter, coordinate contract, docs. **Gate:** CLI works on the target PC, tests run offline, demo visibly identifies simulation to developer. No user-facing false hardware success. **Requirements:** MR-SYS-01, 06.

## MR-01 — Magical rain renderer and standalone deterministic physics

**Goal:** polished but minimal animated rain scene with gravity, trails, glow, soft ambient audio, basic obstacle collision using synthetic shape. Include particle cap, fixed step, unit tests, performance baseline. **Gate:** visually attractive on TV without sensor, single synthetic obstacle causes convincing deflection, no text/HUD. **Requirements:** MR-UX-02, MR-ART-01, 05, MR-SYS-04. **Dependency:** MR-00.

## MR-02 — Real Kinect v1 depth adapter / Windows hardware gate

**Goal:** driver instructions, doctor, depth-only stream adapter and disconnect handling. **Gate:** owner logs authentic depth capture and 60 seconds of timestamp and frame-rate health from Kinect v1 on the target PC; no silent demo fallback; no automatic admin driver changes. **Requirements:** MR-CV-01, 02, MR-SYS-02, 05. **Dependency:** MR-00; may be developed while MR-01 is separate, but merge conflict check mandatory.

## MR-03 — Foreground mask and mirror alignment

**Goal:** background calibration, body segmentation, confidence, image coordinate mapping, multiple silhouettes and fading on occlusion. **Gate:** synthetic fixtures and real Kinect verify adult and child silhouettes, three simultaneous people, partial overlap, mirror behavior and absence of full-screen false foreground. **Requirements:** MR-CV-03, 04, MR-UX-04. **Dependency:** MR-02.

## MR-04 — Reactive rain / flow field / continuous play

**Goal:** combine live silhouette, motion-derived localized wind, water contour reactions, idle-to-active transition and calming exit. **Gate:** child can approach screen and immediately influence rainfall without explanations or specific poses; 5-minute manual test documented. **Requirements:** MR-UX-01, 03, MR-ART-01, 02, 03, 04, 06. **Dependency:** MR-01 + MR-03.

## MR-05 — Parent menu / first-time setup / resilience

**Goal:** single Swedish parent menu, keyboard access, persisted settings, calibration/retry, sensor error UX, mute/mild controls. **Gate:** repeat launch needs no start click, disconnect produces calm truthful message, menu remains hidden to child, config recovery works. **Requirements:** MR-UX-01, 05, MR-SYS-02, 03. **Dependency:** MR-04.

## MR-06 — Polish, packaging and real-world test

**Goal:** simple Windows launcher/packaging (no silent driver installer), accessibility audit, child usability observations, 30min soak and documented hardware performance. **Gate:** measured acceptance checklist completed with truthfully pending entries; local Windows launch from one icon or simple command, full-screen on intended TV. **Requirements:** all outstanding in acceptance table; MR-UX-06 observational evidence. **Dependency:** MR-05.

The launcher prefers a connected 3840 × 2160 desktop and exposes a display
list and an explicit override. The physical HDMI gate is the TCL 75MQLED85K.
Record its actual signal mode and test three visible people together.

## MR-07 (optional, conditional) — Pose-powered water orb

**Only open after:** depth-only core feels excellent and real RGB+depth benchmark is sufficiently stable. Implement opt-in pose capability, confidence gate and fallbacks. First pose spell: two hands close creates a softly glowing ball, never mandatory for interaction. **Gate:** observed stability on children and no degradation of baseline latency. **Dependency:** MR-06. **Do not start by default.**

## Priority / critical path

### User-requested scene and camera updates

- MR-08 adds outlines for visible players.
- MR-09 adds the Snö weather scene and persistent scene selection.
- MR-10 adds two Lustiga huset variants with warped depth silhouettes.
- MR-11 adds direct Esc/F1 menu access, manual camera tilt and depth preview.
- MR-12 adds a bowl filled by body-directed rain and snow.
- MR-13 adds rainbow long-exposure painting from the depth silhouettes.
- MR-14 adds opt-in live color to the two funhouse lenses.
- MR-15 smooths outlines and uses the TV's physical resolution.
- MR-16 layers rain with tapered streaks and brighter contact highlights.
- MR-17 replaces the fixed bowl with water and snow held by the arm silhouette.

**After MR-00, prioritize MR-02 (real sensor) when the owner has the Kinect and adapter available.** Confirm the hardware before investing in elaborate particles. If hardware cannot be tested yet, MR-01 may progress with simulation, but do not mark a hardware-dependent feature as done.

`MR-00 -> MR-02 -> MR-03` and `MR-00 -> MR-01` converge at `MR-04 -> MR-05 -> MR-06`. If real hardware is blocked, continue improving demo only but **never label the live product complete**. No projector/klättervägg, ball tracking, console connection, or optional scenes until MR-06 acceptance is met; any projection prototype gets a **separate future scope decision**.

## PR checklist

One issue, one purpose; requirements/test IDs listed; relevant WDD updated; unit/integration tests; visual assessment; physical hardware result or explicit NOT TESTED; no additional recording/camera imports; one review; refreshed from main; known limitations and rollback notes.
