# Source references and dependency tracking

Magic Rain includes the original design specification and the MR-00 demo. The
demo installs its Python dependencies from PyPI. The live adapter loads
`Kinect10.dll` from the system installation on Windows.

## Primary sources (checked 2026-11-08)

- OpenKinect `libfreenect` — v1 driver, Windows and libusbK guidance: https://github.com/OpenKinect/libfreenect
- Community Windows 11 `kinect-senses` — depth/IR/RGB, setup/driver check, FPS warning: https://github.com/ovrsr/kinect-senses

## Per-dependency record required when code is introduced

| Dependency | Purpose | Version/commit | License reviewed? | Bundled/native DLLs? | Approval |
|---|---|---|---|---|---|
| pygame-ce | desktop rendering | 2.5.6 | LGPL-2.1 per wheel metadata | SDL and other components in upstream wheel | MR-00 local development |
| numpy | numerical/particle arrays | 2.2.6 | BSD-3-Clause, with additional notices in wheel | Native libraries in upstream wheel | MR-00 local development |
| pytest / Ruff | tests / lint | 8.4.2 / 0.14.0 | MIT / MIT | Development only | MR-00 local development |
| Microsoft Kinect SDK | depth capture on the target PC | 1.8.0.595 | Proprietary Microsoft SDK. [Publisher download](https://www.microsoft.com/en-us/download/details.aspx?id=40278) | Owner-installed runtime. Project ships no SDK binaries or headers. | MR-02 local integration |
| libfreenect/libusb | real Kinect capture | pending | pending | pending | pending |
| kinect-senses (if used) | reference only initially | pending | pending | **not bundled by default** | pending |

## Distribution

Local private experiment first. If distributing publicly, verify not just the Python code license but every native DLL, driver package, shader/font/sound asset and installation script. Audio/music/images must be original, properly licensed or public-domain. Do not copy copyrighted game art or music.
