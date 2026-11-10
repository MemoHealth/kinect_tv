# Print-friendly acceptance checklist for the owner

Record which results came from a local device check and which came from
physical observation on the target Kinect and TV.

## Hardware

- [ ] Kinect v1 with correct power and USB adapter is physically connected.
- [x] The target PC sees Kinect v1 camera `045E:02AE` after the owner installed Microsoft Kinect SDK 1.8 (1.8.0.595). Any later driver change requires approval and a rollback record.
- [x] Local `--doctor` test on 2026-11-10 received 1,798 depth-only frames at 320 × 240 in 60.0 s (29.9 FPS). Two frame numbers were skipped, the longest interval was 94 ms, and 19.3% of depth pixels had valid values in the current view.
- [x] A separate single-frame check reopened the SDK stream after the 60 s test.
- [ ] Verify physical USB disconnect and reconnect during capture.
- [ ] Measure depth coverage in the actual play zone and motion-to-screen latency.

## Whole-room play

- [ ] Run fullscreen over HDMI on the TCL 75MQLED85K. Record the actual signal mode and check that the full 16:9 scene is visible without clipping. Confirm calm motion and visible rain in the room.
- [ ] Enter field -> rain interacts without pressing start.
- [ ] Head/arms/torso visibly deflect water; rapid arm sweep produces nearby drift.
- [ ] Mirror directions feel natural.
- [ ] Stationary or seated participant can influence rain.
- [ ] Three people can affect the rain at the same time when in view. Check partial overlap and verify that the rain still responds to the visible silhouettes.
- [ ] Child exits -> soft return to calm rain; no failure message.
- [ ] No scores, labels, gesture icons, tutorials, mandatory poses or achievements.
- [ ] Adults can open/close simple settings with keyboard; mild/mute options work.
- [ ] Cable routing safe; Kinect mounted stably; no hazardous movement demands.

## Fault tolerance and comfort

- [ ] USB disconnect produces clear adult-level failure, not mock body tracking.
- [ ] Restart app; previously configured values persist.
- [ ] 30-minute runtime stable; log fps and memory measurement.
- [ ] No strobing, full-screen flashes, startling sounds or upsetting visuals.
- [ ] Runtime operates without internet and without recording children.

## Child observation (caregiver consent, no identity data)

- [ ] 2+ observed trials with different age/height; record first response, any instructions required, confusion points and comfort.
- [ ] If unsuccessful, tune natural visual response first rather than adding instructions.

**Date / PC / Kinect model / screen / observed issues:**
