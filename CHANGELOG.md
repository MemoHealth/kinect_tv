# Specification changelog

## v1.1 — 2026-11-10 (TV-first readiness review)

- Kept Kinect v1 + Windows 11 laptop + HDMI TCL TV as the **only v1 target**; explicitly deferred projector, climbing-wall and ball-tracking experiments. No new speculative platform layers.
- Added short read-only device/room preflight. It checks power adapter, USB identifiers, TV, camera sightline and safe distance without touching drivers.
- Prioritized real Kinect depth-stream verification directly after bootstrap when hardware is available, rather than spending time polishing an unproven camera stack.
- Reinforced immediate, continuous visual cause-and-effect. Water must react to silhouette/motion without requiring any recognized pose.
- Clarified that Microsoft's legacy Kinect SDK 1.8 does **not** officially list Windows 11 support, and that open-source alternatives need owner-run hardware verification.
- Updated Claude/Codex entry points to keep the first task limited to MR-00.

## v1.0 — 2026-11-08

Original design package, WDD, agent instructions, staged roadmap and demo-first implementation plan. No application code included.
