# Kinect v1 hardware integration on the target PC

## Verified reference points, not claims of device success

- OpenKinect `libfreenect`: https://github.com/OpenKinect/libfreenect (Kinect v1 RGB/depth and USB support on Windows; libusbK via Zadig is documented).
- Windows 11-oriented community project `kinect-senses`: https://github.com/ovrsr/kinect-senses (setup.ps1, doctor.ps1, camera/DLL handling; one small third-party project, not an established compatibility guarantee).
- The latter documents that **simultaneous RGB and depth streaming can lose packets substantially** on some USB host controllers, whereas single stream is much better. Measure locally instead of assuming 30 fps dual stream.

## Backend on the target PC

Run **depth-only** to reduce USB load and limit camera data to what the experience uses. The owner's installed Microsoft Kinect SDK 1.8 (1.8.0.595) on Windows 10 Pro 22H2 exposes the `045E:02AE` camera and returned a native depth frame. MR-02 uses the existing `Kinect10.dll` through a narrow Python adapter. Microsoft lists older operating systems for the SDK. Local verification is specific to this PC. Keep libfreenect as an investigation path if this setup fails its streaming gate.

## Hardware prerequisites

Kinect v1 sensor; model and USB identity checked before driver changes. Proper power adapter + USB adapter (some Xbox 360 configurations have proprietary connector/power); a stable shelf below/above TV; laptop with an available USB port, adult keyboard and HDMI. Adult must approve any admin/driver installation.

MR-11 reads and sets the camera angle through the installed SDK on the
capture worker. An explicit adult action requests a 5° step. Requests are
bounded to ±27°, separated by at least 2.5 seconds and paused for 20 seconds
after 12 attempts. Camera motion invalidates the empty-room reference.
See the [Microsoft SDK interface](https://learn.microsoft.com/en-us/previous-versions/windows/kinect-1.8/hh855326(v=ieb.10)).

## Verification gate (ISSUE MR-02)

1. Check device identity and USB devices; do **not** install a driver on an unrelated USB device.
2. Use the owner's installed Microsoft camera binding. Any alternative driver binding requires separate verification and authorization. Record the driver version and any approved changes.
3. Run hardware doctor: one depth frame and 60 s stable depth stream, track timestamps, effective fps, dropped packets, frame freeze events and USB disconnects. No RGB required.
4. Confirm foreground movement at realistic TV distances, at least adult and child-size targets; assess near/far range and mounting angle.
5. Record camera resolution, image orientation, depth units and mirror mapping. Store findings in hardware verification notes, never invented numbers.
6. Verify app exits cleanly and releases USB handles; allow reconnection without reboot if possible.

## Fallbacks and exclusions

If Windows USB capture cannot be stabilized, create an isolated Linux/libfreenect adapter on a spare PC **only after comparing measured effort**; do not change the entire art software. Never purchase a mini-PC or Chromebook before validating with current laptop. Do not disable Windows security features to accommodate old drivers without a dedicated security review; prefer libusb approach.

## Third-party source policy

Document commits/versions and licenses in dependency notes before bundling; link upstream, reuse minimum needed, do not assume source snippets are redistribution-friendly. Hardware driver scripts are inspected before running with admin privileges. Never run auto installer silently.
