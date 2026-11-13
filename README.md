# Magic Rain

**Specifikation v1.1 (2026-11-10) · TV-first.** Målmiljön är den befintliga datorn med Windows 10 Pro 22H2, Kinect v1 och en [TCL 75MQLED85K, 75 tum, 4K QD-Mini LED (2025)](https://www.tcl.com/se/sv/tvs/75mqled85k?customerModel=75MQLED85K) via HDMI.

A Kinect v1-powered, TV-sized, interactive art installation for children. It is an **experience**, not a game to learn: stand in front of the TV and let magical rain flow around your silhouette and move with your body. No scores, buttons, symbols or instructions during play.

**Status:** Live Kinect play and synthetic developer demo. Physical release checks are tracked in the acceptance checklist. **Runtime:** fully offline, no account, no telemetry. **Primary audience:** young children with adult setup.

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
using the same display selection as live play. The terminal and window title
identify simulation.
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

Esc or F1 opens and closes the Swedish adult panel. Choose **Avsluta** to quit.
Under **Bana**, choose the weather, painting, galaxy, aquarium, dance or
mirror scenes. Regn now uses soft silver-blue droplets, wind-aligned tails, local contact light and subtle floor ripples. In Regn and Snö, shape your arms like a cup to collect water or snow.
The level rises inside your silhouette until it spills over the lower arm.
Opening your arms releases it. In Ljusmåleri, movement leaves rainbow trails
that slowly fade.
Paint Explosion adds local sprays, three player colors and an adjustable fade.
In that scene, the adult panel offers **Färgens toning**, **Spelarfärger** and
**Spara tavla**. Opening the panel holds the artwork. Saving writes the
generated artwork as a PNG in `Pictures/Magic Rain` inside the Windows user
profile. The exported image excludes the menu and camera pixels.
Galaxy Mirror turns the silhouettes into glowing constellations. Moving
arms scatter a bounded cloud of stardust.
Living Aquarium adds fish that approach the silhouette's upper outer points
and jellyfish that drift away. Hand following is approximated from the
silhouette and works with three visible players without pose tracking.
Dansspegel turns the silhouettes into softly drawn stick figures. Choose
**Figur → Skelett** in the adult panel for a friendly skeleton look.
The lines are derived from the visible silhouette, so hidden limbs and
precise anatomical joints are outside this mode's current tracking.
**Färgens toning** also works in Ljusmåleri. Contours and paint trails use a
small display filter for smoother edges.
Spegelstudio offers **Eko** and **Kalejdoskop**. It displays live color when
available and colored silhouettes otherwise. Choose it each session to
display the live reflection. The former convex/concave lenses are removed.
Fruit Ninja brings faster fruit from above and in upward arcs. Use a
clear hand or arm sweep to split it. Small contour jitter and initial
silhouette acquisition do not count as a cut. Up to three visible players
share the field.
Stjärngas adds a shared cloud of gravity-free light particles. Slow body
movements gently push them aside; consistent faster sweeps send them away
with short warm trails. Walls and bodies absorb some energy at each bounce.
Weak repulsion and time-based damping spread and quiet the cloud after play.
Milt shows 300 dimmer particles with fewer trails; Normalt and Livligt show
600. The same bounded physics pool remains active when intensity changes.
**Kameravinkel** uses the left/right keys or the −/+ buttons. Aim with the live
view in the menu, choose **Kalibrera kameran**, then step aside during the
three-second countdown. Keep the area empty until the menu reads
**Kalibrering klar**. Step back in and check that your teal silhouette fits.
Amber marks the edge it reaches. **Spelzon → Bred** uses the full depth image.

**Färgstöd** is on by default. It uses registered color to help fill small
gaps next to the depth silhouette. The menu shows when depth and color are
available. The depth tracker also recognizes a player standing against a
distant background that gave no depth during calibration. Parts outside the
camera view still require a different angle or more room. Camera frames stay
in memory. Only preferences are saved in the Windows user's local application
data.
Calibration now prefers the farther room surface if someone briefly crosses
the view, and filters small disconnected noise regions. The play area still
needs to be clear while the room reference is captured. New disconnected shapes now need confirmation in two distinct depth frames; established connected arms respond immediately. Small depth hysteresis reduces edge flicker, while the drawn contour uses adaptive smoothing and a soft luminous core. Persistent room objects still require a clear calibration.

## Windows launcher and TCL TV

Double-click `Start-Magic-Rain.cmd` on the existing PC. For a fresh checkout,
run `Setup-Magic-Rain.cmd` once with Python 3.11 or 3.12 installed. Setup
installs the Python package and its dependencies. Kinect uses the existing
Microsoft SDK 1.8 installation.

Connect the TCL 75MQLED85K via HDMI and select that input. In Windows display
settings, use Extend to address the TV independently and verify the signal
mode. The launcher prefers a connected 3840 × 2160 desktop. To choose manually:

```powershell
.\Start-Magic-Rain.cmd --displays
.\Start-Magic-Rain.cmd --display 2
```

The number comes from the displayed list. The scene keeps a 16:9 viewport
at the negotiated output resolution. The physical TV and three-person
checks are recorded in the [acceptance checklist](docs/manual-live-checklist.md).

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
