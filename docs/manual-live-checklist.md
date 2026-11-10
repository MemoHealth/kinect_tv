# Print-friendly acceptance checklist for the owner

Record which results came from a local device check and which came from
physical observation on the target Kinect and TV.

## Hardware

- [ ] Kinect v1 with correct power and USB adapter is physically connected.
- [x] The target PC sees Kinect v1 camera `045E:02AE` after the owner installed Microsoft Kinect SDK 1.8 (1.8.0.595). Any later driver change requires approval and a rollback record.
- [x] Local `--doctor` test on 2026-11-10 received 1,798 depth-only frames at 320 × 240 in 60.0 s (29.9 FPS). Two frame numbers were skipped, the longest interval was 94 ms, and 19.3% of depth pixels had valid values in the current view.
- [x] A separate single-frame check reopened the SDK stream after the 60 s test.
- [x] After the owner physically reconnected USB, Windows showed the camera as started. A new SDK session read 129 real depth frames in five seconds with advancing timestamps and valid depth.
- [x] A local six-second run of the live scene completed calibration and rendered 356 frames using a virtual display on the target PC.
- [ ] Verify physical USB disconnect and reconnect during capture.
- [ ] Measure depth coverage in the actual play zone and motion-to-screen latency.

## Whole-room play

- [x] The Windows launcher listed the available display. Automated tests verified full-frame 3840 × 2160 and letterboxed 1024 × 768 output.
- [x] A 60-second synthetic scenario kept three moving obstacles and 1,500 bounded particles active with 4K presentation checks.
- [ ] Run fullscreen over HDMI on the TCL 75MQLED85K. Record the actual signal mode and check that the full 16:9 scene is visible without clipping. Confirm calm motion and visible rain in the room.
- [ ] Enter field -> rain interacts without pressing start.
- [ ] Head/arms/torso visibly deflect water; rapid arm sweep produces nearby drift.
- [ ] Mirror directions feel natural.
- [ ] Stationary or seated participant can influence rain.
- [ ] Three people can affect the rain at the same time when in view. Check partial overlap and verify that the rain still responds to the visible silhouettes.
- [ ] Use one or more silhouettes to fill the bowl with rain and then snow. Verify an empty play zone leaves the bowl unchanged.
- [ ] Select Ljusmåleri and check that movements from three people leave visible fading rainbow trails.
- [ ] Select each Lustiga huset lens on a free Kinect and verify the live color reflection. Leave the scene and verify depth-only play resumes.
- [ ] Child exits -> soft return to calm rain; no failure message.
- [ ] No scores, labels, gesture icons, tutorials, mandatory poses or achievements.
- [ ] Adults can open/close simple settings with keyboard; mild/mute options work.
- [x] Synthetic menu test verified Esc/F1, all four scene choices, both tilt inputs, the depth preview and exiting via Avsluta. A read-only SDK check reported the real camera angle at −17°.
- [ ] On the mounted Kinect, aim up and down using the adult depth view, close the menu with the play zone empty and verify that three outlines appear after recalibration.
- [ ] Cable routing safe; Kinect mounted stably; no hazardous movement demands.

## Fault tolerance and comfort

- [x] In a virtual-display test, an injected SDK disconnect error brought up the camera fault state. Automatic retry then reopened the real Kinect, recalibrated and returned to play.
- [ ] USB disconnect produces clear adult-level failure, not mock body tracking.
- [ ] Restart app; previously configured values persist.
- [x] Target PC live Kinect soak with virtual display and audio output on 2026-11-10. Ran for 1,800.2 s, rendered 109,142 frames, averaged 60.6 FPS and sustained at least 56.5 FPS across sampled 10-second intervals. Zero camera-fault frames. Sampled working set was 64.7 MiB at baseline and peaked at 67.0 MiB. The application exited cleanly.
- [ ] Confirm performance and comfort with the real HDMI display and three people in the room.
- [ ] No strobing, full-screen flashes, startling sounds or upsetting visuals.
- [ ] Runtime operates without internet and without recording children.

## Child observation (caregiver consent, no identity data)

- [ ] 2+ observed trials with different age/height; record first response, any instructions required, confusion points and comfort.
- [ ] If unsuccessful, tune natural visual response first rather than adding instructions.

**Date / PC / Kinect model / screen / observed issues:**
