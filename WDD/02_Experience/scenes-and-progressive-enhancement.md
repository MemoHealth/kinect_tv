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

In Regn and Snö, the bowl fills only with precipitation redirected by a
silhouette. A subtle stream leads recent body contacts toward the bowl.
Collected water or snow stays visible until the scene changes, and the
rest of the precipitation recycles at the floor.

The two Lustiga huset scenes warp the existing depth mask after normal mirror
mapping. Konvex enlarges shapes near the center and Konkav compresses them.
The mapping stays inside the camera field and preserves the left-to-right
order of participants. Contours and decorative particles use the warped
mask, with a violet backdrop and no RGB camera image.

Ljusmåleri uses movement along the silhouettes as a brush. The colors cycle
through the rainbow and accumulate as a soft, fading long-exposure trail.
Each participant can contribute at once. Switching scenes clears the trail.

## Optional reliable skeleton feature gate

Pose magic is a separate feature flag (`pose_magic=false` initially). Requires simultaneous RGB+depth stability or proven single-stream human pose inference on real hardware; test with small children, different heights, occlusions, backlighting and overlap. If confidence is low, silently fall back to silhouette reactions. Any gesture must feel like an *amplification* of natural motion; avoid commands and tutorial overlays.

## Future game ideas (not implementation instructions)

Direct rain toward a blossom / spinning wheel, collaborative waterfall, rainbow canopy, underwater current, living star field. These are exploratory ideas only and not part of the current acceptance criteria. No achievements, score or instructions without a separate product decision and WDD update.
