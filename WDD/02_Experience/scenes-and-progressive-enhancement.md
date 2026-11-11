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

The two Lustiga huset scenes warp the live Kinect color image. Konvex
enlarges shapes near the center and Konkav compresses them. The mapping
stays inside the camera field and preserves participant order. If fresh
color is unavailable, the same lens warps the existing depth outlines.
The adult selects color explicitly for each session.

Ljusmåleri uses movement along the silhouettes as a brush. The colors cycle
through the rainbow and accumulate as a soft, fading long-exposure trail.
Each participant can contribute at once. Switching scenes clears the trail.

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

## Optional reliable skeleton feature gate

Pose magic is a separate feature flag (`pose_magic=false` initially). Requires simultaneous RGB+depth stability or proven single-stream human pose inference on real hardware; test with small children, different heights, occlusions, backlighting and overlap. If confidence is low, silently fall back to silhouette reactions. Any gesture must feel like an *amplification* of natural motion; avoid commands and tutorial overlays.

## Future game ideas (not implementation instructions)

Direct rain toward a blossom / spinning wheel, collaborative waterfall, rainbow canopy, underwater current, living star field. These are exploratory ideas only and not part of the current acceptance criteria. No achievements, score or instructions without a separate product decision and WDD update.
