# Art direction, motion language and sound

## Artistic direction

A premium, calm, magical installation rather than an arcade: deep navy, blue-lilac and turquoise rain, translucent luminous droplets, pearlescent ripples, soft volumetric fog faked with gradients, occasional warm gold glints. Luminous water around silhouette and hand/arm movements. Dark background makes particles legible at daylight TV brightness.

## Animation grammar

- MR-16 draws three stable visual depth layers for rain. Distant drops
  stay short and subdued. Near drops have a brighter tip and a tapered,
  darker tail. A subtle ground haze adds depth, while body impacts remain
  the brightest local accent.
- Persistent idle rain with believable gravity and gentle drift.
- Droplets collide with contour; rain peels away and travels tangentially along body boundary.
- Faster motion causes locally increased flow and short-lived sparkles, but not a white flash or visually opaque flood.
- Strength ramps continuously. Soft color and density changes over ~0.5–2 s.
- The child is not displayed as a live RGB video, avatar or labeled skeleton by default.
- Transition between ambient and active states is gradual; no visible mode switch.

## Performance-conscious effects

Start with pygame-ce/NumPy particles at logical 1280x720; draw size, glow and trails conservatively. Pre-render static blur sprites or use additive layers sparingly. Use no expensive pixel-by-pixel CPU blur each frame at full resolution. If profiling shows effects too heavy, reduce bloom before sacrificing frame responsiveness.

## Audio

- MR-01 generates a seamless low-volume rain bed in memory and fades it in over two seconds. Playback is optional when a Windows audio output is unavailable.
- Short calm water droplets/chimes and a subtle continuous rain bed, **low by default**, with an immediate parent mute option. Never auto-raise system volume.
- No speech, prompts, jump-scare stingers, sudden loud effects, copyright-sensitive music, mandatory microphone recording or voice recognition.
- Movement can gently alter volume/pitch/timbre under hard caps; avoid a per-particle sound (sound spam).
- Mute works instantly and persists.
- Audio assets: original/appropriately licensed, documented provenance, or generate procedural rain textures locally. Prefer deterministic procedural ambient if assets unavailable.

## Visual accessibility and comfort

- No strobing, rapidly cycling large-area light changes or high-contrast blinking. No flashing fullscreen effect even for an impact or celebratory gesture.
- No mandatory jumping, squatting, one-legged balance, touching TV or extended arm holding. Children can participate from a seated position if visible to sensor.
- Limit moving elements and volume through parent intensity setting: Milt / Normalt / Livligt. `Milt` is a legitimate sensory-friendly mode.
- No punishment or timed objectives; optional gameplay later must preserve art mode.
