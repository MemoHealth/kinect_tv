# Magic Rain

**Specifikation v1.1 (2026-11-10) · TV-first.** Målmiljön är den befintliga datorn med Windows 10 Pro 22H2, Kinect v1 och en [TCL 75MQLED85K, 75 tum, 4K QD-Mini LED (2025)](https://www.tcl.com/se/sv/tvs/75mqled85k?customerModel=75MQLED85K) via HDMI.

A Kinect v1-powered, TV-sized, interactive art installation for children. It is an **experience**, not a game to learn: stand in front of the TV and let magical rain flow around your silhouette and move with your body. No scores, buttons, symbols or instructions during play.

**Status:** Developer demo with synthetic depth and a separate live Kinect depth check. **Runtime:** fully offline, no account, no telemetry. **Primary audience:** young children with adult setup.

## Run the developer demo

From this directory in PowerShell with Python 3.11 or 3.12:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
.\.venv\Scripts\python.exe -m magic_rain --demo --windowed
```

The synthetic obstacle moves on its own. Hold the left mouse button within the
central camera area to move it by hand. F11 switches between window and
fullscreen, and Esc exits the demo. Launch with just `--demo` for fullscreen
on the primary display. The terminal and window title identify simulation.
After installation, demo and tests run offline.

```powershell
.\.venv\Scripts\python.exe -m ruff check .
.\.venv\Scripts\python.exe -m pytest -q
```

MR-00 covers MR-SYS-01 and MR-SYS-06 with an installable package, a typed
depth-frame contract, aspect-preserving mapping, and a deterministic demo
loop. The circular obstacle and simple deflection are developer fixtures.
## Check the real Kinect

On the target PC with Microsoft Kinect SDK 1.8 installed and Kinect connected:

```powershell
.\.venv\Scripts\python.exe -m magic_rain --doctor
```

The check reads depth for 60 seconds and prints frame rate, valid depth
coverage, gaps in the frame counter, and the longest frame interval. Depth
images stay in memory. Launch the live scene with `python -m magic_rain` and
leave the play area empty while it calibrates. For a window, add `--windowed`.
The scene then reacts to all visible foreground regions. Physical
three-person play remains an acceptance check.

## Start here

- For Claude Code or Codex: read [`AGENTS.md`](AGENTS.md), [`CLAUDE.md`](CLAUDE.md), and [`WDD/README.md`](WDD/README.md), then use [`docs/claude/FIRST_PROMPT.md`](docs/claude/FIRST_PROMPT.md).
- **Working Design Document (WDD)** is the source of truth for product behavior and technical interfaces; see [`WDD/README.md`](WDD/README.md).
- [`WDD/04_Delivery/roadmap.md`](WDD/04_Delivery/roadmap.md) defines the build order and gates.
- [`docs/setup/windows11-kinect-v1.md`](docs/setup/windows11-kinect-v1.md) explains the hardware risk and how to validate it without guessing.
- [`docs/setup/tv-first-preflight.md`](docs/setup/tv-first-preflight.md) is a short, **non-invasive** preflight checklist before buying hardware or changing USB drivers.

## Intended end-user experience

Power on PC -> launch app -> fullscreen living rain scene -> child enters camera zone -> the rain reacts immediately. A parent-only settings panel is hidden behind a keyboard shortcut. First-time camera setup is guided for adults only. The game never requires reading, pressing a button, making a prescribed pose, or navigating a menu.

## Boundaries

No Switch 2/PS5 connection, no projector/interactive wall/climbing-wall/ball tracking in v1, no cloud AI, no network calls at runtime, no face recognition, no speech recognition, no image saving by default, no real-time video recording. No physics-engine overbuild. No dependency on GPU, multi-camera tracking or precise hand pose for the first usable version.

## Status and ownership

The demo and live depth check target this PC. The hardware checklist covers
remaining physical checks, including HDMI output to the TCL TV.
