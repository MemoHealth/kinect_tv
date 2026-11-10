# Journeys and application states

## State machine

`BOOT -> SENSOR_CHECK -> [CALIBRATE when needed] -> ATTRACT -> PLAY -> ATTRACT`. `SENSOR_CHECK -> ADULT_HELP` on sensor failure. `ATTRACT|PLAY -> PARENT_MENU -> previous state` by adult-only keyboard access. `--demo` explicitly substitutes synthetic sensor for real input; visible small *development mode* indicator is permitted in demo/testing only, not a normal-play HUD.

## First-time setup (adult only)

1. Adult plugs Kinect v1 with its proper power/USB adapter into the Windows PC; connects PC via HDMI to TV; places sensor securely, with clear view of play zone.
2. Adult runs setup/doctor (driver changes require explicit approval), verifies stable depth stream.
3. App prompts adult once for a clear, empty field-of-view reference if needed. Target: ~2–4 seconds of empty-area depth frames. If empty reference is impossible, provide a manual recalibrate key and a robust fallback; do not pretend the background is correct.
4. Fullscreen rain begins. Adult can adjust mirror, sensitivity, safe play-zone near/far bounds and volume via parent menu.
5. Persist only local non-sensitive settings. On later launches skip setup unless calibration is missing or camera position changes significantly.

## Returning use

- Auto-fullscreen attract scene with slow rainfall and ambient movement.
- A child enters the play zone. Valid mask for a short debounced interval (~0.3–0.7 s) ramps interaction in smoothly; no start press.
- Child can freely move; multi-person foreground silhouettes are treated as a combined obstacle and flow source (no identity resolution required).
- Child exits. Activity decays within ~2–4 s back to attract mode without abrupt blanking, countdown or attention-demanding message.

## Interruptions

- **USB lost:** fade particles to ambient loop; show a calm, simple *adult-level* connection notice only after a brief retry; do not display error codes in child mode.
- **Tracking jitter/occlusion:** maintain last stable mask for a very short time (~100–250 ms), then decay to fallback; never freeze a child's shadow indefinitely.
- **TV resolution changes:** preserve aspect ratio, letterbox if needed; do not stretch silhouettes.
- **App not focused:** pause expensive sensor acquisition if appropriate; never record into background.
- **Parent ESC:** show parent menu; resume without wiping the artwork unless intentionally reset.

## No-camera development journey

`python -m magic_rain --demo` opens the same art scene, driven by a simulated moving circle/silhouette controllable by mouse/keyboard. The UI or command line explicitly identifies simulation. This allows independent testing and cannot be used as real Kinect acceptance evidence.
