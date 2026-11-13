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
- [x] Each of the six new modes completed 1,800 three-player updates and
  renders, representing 60 simulated seconds per mode. Checked storage bounds
  for fruits, fragments, reflection samples and dance segments throughout.
  This was an offline scenario, excluding camera capture and TV presentation.
- [ ] Certify stable native-TV frame rate for each new mode. CPU timings
  varied during local testing, with some samples over 33.3 ms, so the
  30 FPS minimum is not yet an accepted hardware result.
- [x] The obsolete convex/concave modules and their lens-specific tests are
  removed. Old saved lens names safely return to Regn.
- [ ] Test all new worlds with the real Kinect and three people on the TCL.
  Hardware is unavailable for this delivery. Fish targets and dance figures
  are derived from the visible contour; anatomical joint tracking is outside
  the delivered baseline.

## Noise and slicing follow-up

- [x] A 45-second real Kinect empty-room comparison completed without sensor
  faults, at 54.11 FPS average and 32 ms p95 frame interval. The old Fruit
  Ninja logic cut 25 fruits from room noise; the new logic cut zero.
  Spawn schedules differ, so this is an empty-room fault check, not a
  comparative success rate.
- [ ] The subsequent human run failed body acceptance. It averaged 41.28 FPS,
  but calibration included part of the person and the image clipped the head.
  The initial adaptive margin removed too much torso. The revised farther
  reference and bounded margin have synthetic crossing tests; repeat the
  human test before marking calibration or slicing sensitivity accepted.
- [x] Real game and adult-preview screenshots were saved locally with the
  owner's explicit request. They remain outside GitHub. The failed run is
  retained as evidence.

## Pearl rain graphics, 2026-11-13

- [x] Astra reviewed the wind-aligned drop sprites, soft tips, local contact
  light and explicit floor-impact rings. No blocking findings remain.
- [x] Compared old and new renderers with identical synthetic three-player
  masks and particle positions over 360 updates. The paired PNGs stay local.
  The new render path measured 8.34 ms median and 14.12 ms p95 at 1280 x 720.
  This excludes physics, camera capture and display presentation; it does not
  certify native 4K frame rate.
- [x] Ruff passes and all 72 automated tests pass, including rotated tip
  anchoring, bounded floor rings and no floor impacts from caught water.
- [ ] Human calibration, slicing sensitivity and new rain comfort on the
  actual TV remain pending. The owner chose graphics and automated testing
  instead of another camera run. No additional live images were captured.

## Stable silhouettes, 2026-11-13

- [x] The 240-frame synthetic three-player fixture retained 100% of the body
  pixels after entry. Four coherent 12 x 12 transient islands were injected
  every other frame, including near the play-zone edges. Maximum false
  foreground fell from 577 to 1 pixel (local hole repair), with no detached
  islands visible in the updated screenshot. This is a controlled fixture,
  not an observed real-room false-positive rate.
- [x] Automated cases cover one extra sensor-frame confirmation delay, duplicate
  timestamps, connected fast thin arms, three moving people, threshold
  hysteresis, invalid depth, flood rejection and stale/configuration resets.
  Drawing tests cover small-edge damping, fast movement, reentry and elapsed
  time at 30/60 FPS; display smoothing never changes the collision mask.
- [x] Astra approved the final synthetic contours and code for a draft PR, with the performance and physical acceptance gates still open.
- [x] Synthetic before/after graphics were saved locally. CPU cost was measured
  rather than inferred from appearance. One paired full logical rain step
  measured median/p95 35.77/59.00 ms before and 36.96/59.19 ms after. This
  includes mask, motion, two physics steps, rain drawing and outline, but
  excludes camera, audio, arm-water and TV presentation. Further samples
  varied substantially even for the old renderer. No sustained-FPS claim.
- [ ] The 33.3 ms frame budget is NOT accepted. Native-TV sustained performance
  and a real human tracking trial remain pending. The source and PR are
  software-ready, not a completed hardware release. No camera run was made.
- [ ] Persistent coherent room noise, or noise attached to a body, can still
  survive. This filter is not a person classifier. Check calibration and
  visible whole-body framing during the next operator-run trial.
## Stjärngas, 2026-11-13

- [x] Astra reviewed code and synthetic graphics. Its initial finding that
  alternating +/-2 raw-pixel noise could impart false velocity was reproduced
  and fixed using local multi-frame directional consistency. Both +/-1 and
  +/-2 regression cases pass. Milt now reduces visible particles and trails.
- [x] Ruff and all 91 tests pass. Gas coverage includes four directional
  slow/fast sweeps, stillness, jitter, acquisition/reentry, three bodies,
  swept thin-arm contact, wall energy loss, no gravity, mutual repulsion,
  minute-long decay/density spread, 20 Hz sensor delivery and equivalent 30/60 FPS fixed-step input.
- [x] Normal command entry point completed 75 simulated frames and exited
  cleanly. The adult panel opened and closed in a synthetic live-input
  fixture; no Kinect was opened and no user settings were overwritten.
- [x] The final 180-frame three-player scenario used 600 particles and measured
  18.07 ms median / 22.90 ms p95 for two fixed physics steps, scene drawing and
  the shared outline at logical 1280 x 720. Capture, foreground segmentation,
  audio and TV presentation are excluded. Initial unoptimized results missed
  the budget; profiling removed large temporary arrays and scalar rounding.
- [x] After the synthetic movement stopped, 60 seconds of simulation reduced
  RMS speed to 3.150 logical pixels/s, 7.01% of the 44.943 peak. The pool stayed
  at 600 particles, geometry history at eight or fewer and positions finite.
  The earlier stronger pressure/drag tuning did not meet the 10% target and
  was replaced with weaker repulsion and a 10-second velocity half-life.
  Screenshots of active, settled and Milt states remain local and synthetic.
- [ ] Real Kinect and native TV sustained performance, perceived contact
  latency, very slow hand motion, three-person play and comfort remain NOT
  TESTED. Logical timings are not a hardware release gate. Approximately
  133 ms of consistent motion at 30 Hz (200 ms at 20 Hz, excluding other latency) is needed to turn a new movement into a punch;
  direct obstacle displacement remains immediate.

## Child observation (caregiver consent, no identity data)

- [ ] 2+ observed trials with different age/height; record first response, any instructions required, confusion points and comfort.
- [ ] If unsuccessful, tune natural visual response first rather than adding instructions.

**Date / PC / Kinect model / screen / observed issues:**
