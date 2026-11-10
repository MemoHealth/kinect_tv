# Privacy, accessibility and physical safety

## Privacy architecture

- All sensing and computation **local on Windows PC**. After installation the app should work unplugged from internet.
- Raw depth frames, RGB, joint estimates, masks and microphone data are **not recorded or transmitted** by default. Prefer depth-only capture; disable microphone interface entirely.
- MR-14 opens RGB only while a Lustiga huset scene is selected by the adult.
  The game starts in Regn if a previous setting names either color mirror.
  Only the latest fresh color image is displayed in memory. Leaving the
  scene clears the image and returns capture to depth-only.
- `Spara bild` is **disabled by default**. If adult enables manual still capture later, save only art render without raw RGB and show a clear parent confirmation/destination. No automatic saving.
- No identity/facial recognition, biometrics, profiles, analytics, crash uploads, advertisement SDK or telemetry.
- Logging may include non-identifying performance counters/error codes but never body masks, camera imagery or identifiers.
- Any optional MCP/server connection is a separate developer workflow; not available in child runtime.

## Physical/sensory safety

- Secure Kinect so it cannot fall; keep cables/power adapter out of walking paths and away from water; no free-running motor tilt in play.
- Mark or supervise a safe standing area with adequate distance from the TV and furniture. Children should not need to touch the screen or jump. Don't request prolonged tiring poses.
- Provide muted/mild mode and restrained particle density. No flashes, rapid full-screen flicker, fear effects, harsh impacts or sudden loud audio.
- Allow seated use when within camera view, multiple kids sharing view, and a parent easy exit.
- The installation is a creative toy, **not** a clinical/rehabilitation measurement product; do not state that it diagnoses movement or measures performance.

## Operating system changes

Driver binding changes (e.g. via Zadig) require positive adult approval and exact USB identity check. Do not ask for security controls to be disabled as a default fix. Provide restoration instructions and avoid installing audio-device drivers when only depth is needed.

## Licensing

Review dependency and artwork/audio licenses before redistribution, especially libfreenect's dual-license terms and other native libraries. Do not copy external project content wholesale without license checks.
