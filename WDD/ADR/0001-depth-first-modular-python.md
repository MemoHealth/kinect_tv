# ADR-0001: Depth-first modular Python with optional pose layer

**Status:** Accepted for initial implementation (design decision; unverified on owner's device). **Date:** 2026-11-08.

## Context

The goal is a child-first Kinect v1 interactive rain installation on the owner's existing PC with HDMI TV output. The owner confirmed the deployment machine, which runs Windows 10 Pro 22H2. Camera compatibility on that PC still requires a live test. Kinect v1 simultaneous RGB and depth streaming can be bandwidth-sensitive. The interaction relies on silhouettes and is accessible without pose commands.

## Decision

Use Python + NumPy + pygame-ce and a replaceable Kinect v1 adapter. The [Kinect backend decision](../01_Architecture/kinect-backend.md) records the installed SDK selected for MR-02. Base gameplay on a depth-derived foreground mask. 2D particle physics creates convincing water motion. A simulation adapter enables code and test progress without the device.

## Alternatives considered

- **Unity / Unreal:** good rendering but higher integration/setup burden and risk of over-engineering.
- **TouchDesigner:** excellent visuals but licensing/runtime/distribution and custom sensor integration are larger questions; reconsider only after a measured prototype.
- **Web browser + JS:** good UI but native Windows Kinect v1 driver/USB access still needs bridging, adding runtime processes.
- **libfreenect:** alternative Kinect v1 backend if the installed SDK fails the hardware gate.
- **True fluid simulation:** more CPU/GPU and complexity than visual value for first build.

## Consequences

Positive: simple AI-code workflow, no powerful GPU requirement for first prototype, deterministic tests, easy sensor isolation. Negative: pygame CPU drawing can cap quality; Kinect DLL setup remains a real physical/human gate. Reassess renderer if profiling violates performance targets; do not rewrite preemptively.

## Revisit if

Real-device driver impossible on Windows; sustained 30 fps target unattainable after quality ladder; user explicitly asks for projector/3D advanced installation; pose gestures prove essential in observed child play.
