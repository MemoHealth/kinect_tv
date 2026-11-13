# Scenes and progressive enhancement

## One scene first

**Only mandatory scene:** Magic Rain. Never let scene selection delay startup or distract a child. Attract and active are continuous intensity states within the same scene.

## Art behaviors for Magic Rain

1. **Ambient sky**: steady enchanted rainfall with layered speeds and gentle parallax. No person needed.
2. **Silhouette umbrella**: rain visibly changes direction and trickles around child's head, shoulders and arms.
3. **Motion gust**: fast lateral movement generates a soft directional field and trail of luminous droplets; fades quickly.
4. **Stillness glimmer**: holding still creates slower glints on top contours; no pose inference required.
5. **Soft splash**: when a lot of silhouette motion displaces rain, create limited small splash particles, no loud impact or flash.
6. **Reach and spread**: the higher/wider the child extends their silhouette, the more the sky opens and rain bends, via smooth shape metrics rather than discrete skeleton-required commands.

## Not in MVP

- Accurate hand-shaped bowls that physically accumulate water.
- Joint-based gestures or tracking a specific person.
- Gesture command lists (e.g. 'jump for splash') — these turn play into instruction following.
- Modes the child has to unlock or choose via controls.

## Optional scene variations, only after real playtest

The adult panel switches between Regn and Snö and remembers the selection.
Snow uses slow drifting flakes and an icy palette. Flakes react to all visible
depth silhouettes. The winter scene keeps the same outlines and plays quietly.

In Regn and Snö, a silhouette with an open top, two sides and a closed
bottom can hold precipitation. A horizontal fill line rises inside the
shape until it reaches the lower side. Additional precipitation spills
over that side. Opening the arms releases the accumulated water or snow.
Up to three separate shapes can collect independently.

Spegelstudio replaces the former convex and concave lenses. Eko leaves
short fading reflections of movement. Kalejdoskop combines a recognizable
central reflection with surrounding symmetric patterns. Camera pixels stay
in memory. With no fresh RGB, the same effects use colored silhouettes.
The adult selects the mirror scene explicitly for each session.

Ljusmåleri uses movement along the silhouettes as a brush. The colors cycle
through the rainbow and accumulate as a soft, fading long-exposure trail.
Each participant can contribute at once. Switching scenes clears the trail.
The adult can select the same Kort, Normal and Lång trail half-lives in
Ljusmåleri as in Paint Explosion. Existing settings retain the three-second
default and the rainbow rendering.

### Paint Explosion (MR-20)

Ordinary motion draws soft trails. Faster local movement releases short
sprays from the moving contour. Three separable players can paint in three
colors. A merged shape blends the visible colors while the previous slots
stay available for a short split. The adult panel offers three palettes
and three trail half-lives. Opening it holds the artwork for preview.
The adult can save just the generated artwork as a local PNG.

Requirements MR-UX-02/03/05/06, MR-CV-02–04, MR-ART-02/04–06,
MR-SYS-03/04/06. Settings and artwork export are scoped to Paint Explosion.
Tests cover three color slots, merging, elapsed-time fade, bounded spray,
and explicit export without camera, menu or diagnostic pixels. Risks include
temporary color reassignment after occlusion and TV frame budget. Raw image
capture, a pose dependency and automated saving are out of scope.

### Galaxy Mirror (MR-22)

A stationary silhouette contains a quiet glow and colored stars. Moving a
limb emits short-lived dust locally from that contour. Background stars stay
calm and all three visible players can contribute without RGB or joints.
The scene has a fixed particle budget and clears on exit.

Requirements MR-UX-02–04/06, MR-CV-02–04, MR-ART-03–05, MR-SYS-03/04.
Reuse the existing viewport, contour and cached sprite renderer. Tests cover
three stationary shapes, local moving emissions and empty-mask cleanup.
GPU compute, raw color display and volumetric rendering are out of scope.

### Living Aquarium (MR-23)

Three visible silhouettes can attract nearby fish toward their upper-body
outer points. This is a contour-based hand approximation. Hands need not
activate a gesture. Jellyfish drift away from the visible body. The school
returns to gentle motion when people leave.

Requirements MR-UX-02/03/06, MR-CV-02–04, MR-ART-02–05, MR-SYS-03/04/06.
Use 24 cached fish sprites, five animated jellyfish and bounded bubbles.
Tests cover three sets of targets, fish approach, jellyfish avoidance and
empty-scene recovery. Precise hand joints, identity tracking, new assets,
fluid simulation and RGB are out of scope.

### Dansspegel (MR-27)

The scene derives a central line from each visible silhouette and draws a
friendly colored stick figure. Up to three players can contribute. The
adult chooses Streck or Skelett. The skeleton look uses the same derived
geometry with ivory strokes, simple ribs and a friendly round head.
Lines render on a larger cached layer and scale down with antialiasing.

Requirements MR-UX-02–04/06, MR-CV-02–04, MR-ART-03–06, MR-SYS-04.
Tests cover three silhouettes, preservation of the source mask, a style
switch and clearing on loss. This is silhouette-derived geometry; it does
not supply anatomical joints or infer hidden limbs. Accurate SDK skeleton
tracking remains a separately gated enhancement.

### Spegelstudio delivery (MR-28)

Requirements MR-UX-02/04/05, MR-CV-02/04, MR-ART-05, MR-SYS-03/04/06.
Reuse the installed depth/RGB capture and the common viewport. Keep at most
four short-lived reflection samples and cache the kaleidoscope map.
Remove the old lens module, renderer and obsolete lens tests. Tests cover
horizontal mapping, both new styles, expiry of RGB history, depth fallback
and old settings recovery. New capture libraries, recording and a GPU
framework are out of scope.

### Fruit Ninja (MR-29)

Procedural fruit falls from above as well as rising in arcs from below.
About 65% spawns from above. Meaningful movement of any visible silhouette
can split a fruit, with two falling halves and a small splash.
Stationary silhouettes keep their outline. Uncut fruit falls away and new
fruit arrives continuously. Three players share the same fruit field.

The scene uses original sprites and a bounded simulation with at most ten
whole fruits, twenty fragments and 160 splash particles. A four-sensor-pixel
jitter band is excluded. New foreground must have nearby vacated foreground
before it can cut; acquisition and loss alone cannot slice fruit. Motion is
held for at most 65 ms and intersects the visible 22-pixel fruit radius.
New fruit arrives every 0.32–0.56 s. Tests cover three simultaneous cuts,
stationary-versus-moving input, continuous respawn and bounded storage.
The requirements and exclusions are recorded in the worlds proposal.
The experience has no score, timer, bomb, win state or required command.

### Stjärngas (MR-34)

A shared gravity-free cloud of 600 softly glowing particles. Slow silhouettes
gently push them aside; faster normal motion produces faster local bursts.
Speed adds short warm trails, never a full-screen flash. Silhouettes retain
the shared outline. Three people influence the same cloud without pose or RGB.
The adult chooses Stjärngas under Bana. No new child controls or score.

Use fixed arrays, a coarse bilinear density-pressure field for mutual
repulsion, inelastic reflection and weak elapsed-time drag. Pressure is a
bounded collective approximation, not an exact pairwise gas solver. Without
new movement the cloud should spread and become quiet in approximately a
minute. Measure decay and density relaxation separately. There is no ongoing
random energy source. First detection creates an obstacle without a punch.
Local motion is estimated over recent masks, with a two-sensor-pixel jitter
allowance and four consistent advancing intervals at the contact point.
Very slow movements still displace overlapping particles directly; velocity
impulses deliberately require sustained movement. At 30 Hz the confirmation
history adds roughly 133 ms before a new punch can transfer velocity.
No extrapolation from stale bodies. No driver or dependency changes.

The pressure field is 32 x 18. Velocity half-life is 10 seconds. Wall
restitution is 0.84; body restitution is 0.82 in the local moving frame.
Speed is capped at 480 logical pixels/s. Four swept samples per 1/60 s
substep protect thin arms. At most eight float32 geometry-history fields
are retained for at most 250 ms; velocity uses the latest four intervals.
This also supports slower 20 Hz delivery (about 200 ms confirmation).
Empty/reacquired bodies do not seed a punch.
Milt displays 300 evenly selected particles, dimmer cores and at most 48
trails; Normalt 600/120 and Livligt 600/200. Keep the same 600-particle physics
pool during intensity changes so the cloud does not suddenly reset.

Software acceptance: four directional contacts; fast sweeps transfer more
energy than slow ones; no energy injection by stillness or short jitter;
swept thin-arm collision; three simultaneous contacts; reentry without a
blast; bounded speed/storage; quieting after 60 seconds and density spread;
equivalent fixed-step results at 30/60 rendering FPS; synthetic graphics and
CPU timing reviewed by Astra. Kinect/TV comfort and native-display sustained
performance remain separate hardware gates.

## Optional reliable skeleton feature gate

Pose magic is a separate feature flag (`pose_magic=false` initially). Requires simultaneous RGB+depth stability or proven single-stream human pose inference on real hardware; test with small children, different heights, occlusions, backlighting and overlap. If confidence is low, silently fall back to silhouette reactions. Any gesture must feel like an *amplification* of natural motion; avoid commands and tutorial overlays.

## Future game ideas (not implementation instructions)

Direct rain toward a blossom / spinning wheel, collaborative waterfall, rainbow canopy, underwater current, living star field. These are exploratory ideas only and not part of the current acceptance criteria. No achievements, score or instructions without a separate product decision and WDD update.
