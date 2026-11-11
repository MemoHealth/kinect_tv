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
- [ ] Hold both arms to form a cup. Verify water and snow rise inside the shape, overflow at the lower arm and fall when the arms open.
- [ ] Select Ljusmåleri and check that movements from three people leave visible fading rainbow trails.
- [ ] Select Spegelstudio and verify Eko and Kalejdoskop with the live color reflection. Leave the scene and verify silhouette play resumes.
- [x] Local hardware smoke test received 300 depth frames and 295 nonempty color frames in 10 s. An integrated virtual-display run rendered 45 frames of the real color mirror and cleared the color image on return to depth-only play. No images were saved.
- [ ] Child exits -> soft return to calm rain; no failure message.
- [ ] No scores, labels, gesture icons, tutorials, mandatory poses or achievements.
- [ ] Adults can open/close simple settings with keyboard; mild/mute options work.
- [x] Synthetic menu test verified Esc/F1, all four scene choices, both tilt inputs, the depth preview and exiting via Avsluta. A read-only SDK check reported the real camera angle at −17°.
- [ ] On the mounted Kinect, aim up and down using the menu preview. Select **Kalibrera kameran**, step out of view and wait for **Kalibrering klar**. Return and confirm head, hands and feet fit inside the frame. Move to an edge and verify the correct amber marker. Repeat with three people.
- [ ] Compare **Färgstöd** on and off with a player safely inside the frame. Check that small gaps improve without leaving false contours, and that movement still feels responsive.
- [ ] Calibrate with a distant area that appears black in the empty-room preview. When a player enters that area at normal play distance, check that the silhouette follows the measured body continuously across the dark background and the measured floor.
- [x] Local Kinect SDK test received 295 depth frames in 10 s. It mapped 259 synchronized color/depth pairs and captured a color calibration reference in memory. No images were saved.
- [ ] Cable routing safe; Kinect mounted stably; no hazardous movement demands.

## Fault tolerance and comfort

- [x] In a virtual-display test, an injected SDK disconnect error brought up the camera fault state. Automatic retry then reopened the real Kinect, recalibrated and returned to play.
- [ ] USB disconnect produces clear adult-level failure, not mock body tracking.
- [ ] Restart app; previously configured values persist.
- [x] Target PC live Kinect soak with virtual display and audio output on 2026-11-10. Ran for 1,800.2 s, rendered 109,142 frames, averaged 60.6 FPS and sustained at least 56.5 FPS across sampled 10-second intervals. Zero camera-fault frames. Sampled working set was 64.7 MiB at baseline and peaked at 67.0 MiB. The application exited cleanly.
- [ ] Confirm performance and comfort with the real HDMI display and three people in the room.
- [x] A 20-second live Rain trial on the TCL used 3840 × 2160 at 59 Hz and rendered
  857 frames at 42.8 FPS (p95 frame interval 47 ms). Calibration completed and
  there was no sensor fault. Capture delivered 552 depth frames and 1 registered
  color pair in this run, so the result mainly exercised the depth fallback.
  This was neither a three-person playtest nor a 30-minute soak.
- [ ] No strobing, full-screen flashes, startling sounds or upsetting visuals.
- [ ] Runtime operates without internet and without recording children.

## New-world software checks, 2026-11-11

- [x] Paint Explosion, Galaxy Mirror, Living Aquarium, Dansspegel,
  Spegelstudio and Fruit Ninja have each been reviewed by Astra before
  their PR. The shared contour change was also reviewed.
- [x] Synthetic fixtures exercise three figures, separated colors and short
  merges, local stardust, fish attraction, jellyfish avoidance and both dance
  styles. The source mask remains unchanged by display smoothing.
- [x] Paint export is explicit and uses the generated artwork surface. Tests
  compare the PNG to that surface after a separate UI surface is overwritten.
  Elapsed-time fade is checked at 30 and 60 updates per second.
- [x] All nine active scenes completed 75 frames and a clean exit through
  the normal simulated command entry point. The six new modes also passed
  opening and closing the adult panel with a synthetic live-input fixture.
- [x] The obsolete convex/concave modules and their lens-specific tests are
  removed. Old saved lens names safely return to Regn.
- [ ] Test all new worlds with the real Kinect and three people on the TCL.
  Hardware is unavailable for this delivery. Fish targets and dance figures
  are derived from the visible contour; anatomical joint tracking is outside
  the delivered baseline.

## Child observation (caregiver consent, no identity data)

- [ ] 2+ observed trials with different age/height; record first response, any instructions required, confusion points and comfort.
- [ ] If unsuccessful, tune natural visual response first rather than adding instructions.

**Date / PC / Kinect model / screen / observed issues:**
