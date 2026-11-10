# Kinect v1 on Windows: safe hardware setup and troubleshooting

Use this protocol to verify the Kinect v1 on the target PC.

## Target PC

The owner's Microsoft Kinect SDK 1.8 (1.8.0.595) installation exposed the
`045E:02AE` camera on Windows 10 Pro 22H2. Use the installed Microsoft driver
and run the depth check below. The later driver-binding steps are an
alternative investigation for a PC where this path fails.

## Before touching Windows drivers

Read `docs/setup/tv-first-preflight.md`. The operator should first check the proper external Kinect power/USB adapter, Device Manager identifiers, HDMI TV setup, and safe camera distance. A development agent must not run installer scripts, modify drivers, disable Memory Integrity, or claim success solely because a GitHub README says Windows 11 is supported.

## Equipment

- Kinect v1 (Xbox 360 or Kinect for Windows v1), with correct **external power supply + USB adapter** where applicable.
- Target PC with Windows 10 Pro 22H2, USB port (try direct ports before hubs), and HDMI to TCL Google TV.
- Place Kinect securely at/near TV and clear a reasonably open play area. Sensor sightline should include children standing naturally, without pressing close to the TV. Practical working depth is limited; actual range varies by model/mode and environment.
- Keep keyboard available for parent/admin setup.

## Understand the driver risk

Microsoft's official Kinect for Windows SDK 1.8 lists Windows 7/8/8.1, **not Windows 11**, as supported operating systems (https://www.microsoft.com/en-us/download/details.aspx?id=40278). Kinect v1 may still be usable on modern Windows through community libraries, but this is a device- and driver-specific result, not guaranteed compatibility. Microsoft's old Kinect v1 Windows runtime/SDK is legacy. The preferred investigation is community-supported **libfreenect + libusb**, whose Windows README documents libusbK/Zadig for Kinect camera. A small Windows-11-focused repository, `kinect-senses`, publishes `setup.ps1`, `bind-drivers.ps1`, `doctor.ps1` and `streambench.py`, but has a limited track record and must not be treated as guaranteed compatibility. **It is a diagnostic reference, not an approved dependency to copy wholesale.**

Sources: https://github.com/OpenKinect/libfreenect and https://github.com/ovrsr/kinect-senses

## One-time hardware investigation (adult + Claude Code)

1. **No driver change yet.** Plug correct adapter and confirm visible Kinect devices and hardware IDs. Sensor models can differ. Make a note of current Windows device drivers.
2. Clone the community source and **inspect its scripts before execution** (e.g. `setup.ps1`, `bind-drivers.ps1`). Use an isolated directory outside Magic Rain repo; treat it as reference/diagnostic tool, not bundled code.
3. If the inspected instructions request a driver binding, verify device IDs. `kinect-senses` documents camera USB ID `045E:02AE` and `libusbK` for depth/RGB. **Never select unrelated USB hardware in Zadig.** Audio and motor bindings are not needed for this project by default.
4. Only after explicit operator approval, perform any driver change and retain a note of rollback steps (Device Manager -> remove/reinstall device driver as appropriate). No automatic elevation.
5. Run upstream health checks as documented, including a **depth-only** stream benchmark of 60 seconds. Record: version/commit, port/controller, fps, dropped packets, corrupt frames, disconnects. `kinect-senses` documents `./doctor.ps1 -Live` and `python streambench.py` for its own tree; verify their current usage before running.
6. Test whether a child-sized foreground object is distinguishable over room background, plus adult arms. Record screen mirror direction.
7. Implement Magic Rain sensor adapter against verified native ABI/ctypes or a small subprocess bridge if needed. The native USB API remains in `sensors/kinect_v1.py` and must release handles cleanly.
8. Do not test RGB+depth simultaneously until **after** depth-only experience is functional. Upstream reports simultaneous streaming may lose packets on certain Windows USB controllers; it is not required for v1.

## Magic Rain depth check

```powershell
# First ensure Python and app dependencies are installed, then:
python -m magic_rain --demo        # no real camera needed
python -m magic_rain --doctor      # 60-second real-depth health check
python -m magic_rain              # live fullscreen with empty-room calibration
```

The doctor check uses depth only and reports aggregate numbers.

## Common problem -> proper response

| Symptom | Investigation | Avoid |
|---|---|---|
| No Kinect device | adapter power, USB, Device Manager, model ID | coding around missing power |
| Only Xbox NUI Motor (`045E:02B0`) is listed | Check external adapter power and reseat the sensor connection. Try a direct USB port and look for the separate camera interface (`045E:02AE` or `045E:02BF`, depending on model). [OpenKinect USB IDs](https://github.com/OpenKinect/libfreenect/blob/master/src/freenect_internal.h) | Binding a depth driver to the motor |
| Device detected, no depth | driver binding, DLL loading, USB host controller | disabling Windows Memory Integrity by default |
| RGB+depth stutters | test depth alone; single-stream baseline | assuming a gaming GPU fixes USB packet loss |
| Freeze after minutes | USB capture diagnostics, native cleanup, queue size 1–2 | infinite queue buffering |
| Child shape not detected | distance, camera angle, empty-scene calibration | immediately adding AI skeleton model |
| Movement mirrors incorrectly | single mirror setting, screen mapping | ad-hoc flips in multiple modules |
| TV shows bars/stretch | logical 16:9 viewport, aspect ratio, HDMI display config | stretching depth image non-uniformly |
| Frame rate drops | reduce glow/particle count, inspect frame timing | immediate language/framework rewrite |

## Pass/Fail hardware report template

```text
Date:
Machine CPU/GPU, Windows version:
Kinect model and hardware ID:
Power + USB adapter / port/controller:
Driver binding and version:
Upstream diagnostic source/commit:
Depth stream: resolution / valid depth percentage / fps 60s / drops:
Near/far working range observed:
Latency observation:
Reconnection test:
Result: PASS / FAIL / BLOCKED
Known limitations / rollback steps:
```
