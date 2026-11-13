# Interaction design: natural magic, invisible interface

## Primary rule

**The child-facing screen is the world itself.** No instruction banners, hand icons, progress indicators, score, buttons, gesture charts or long pauses. The system rewards exploration, not performance of commands. MR-35 is an explicit owner-requested exception for two discreet world-switch portals with temporary dwell feedback; baseline play still requires no gesture.

## Visual composition

- Fullscreen 16:9 soft dark-blue/purple space with slow atmospheric layered rain, mild depth gradient and discreet luminous water highlights. No UI chrome.
- Show a soft, continuously visible outline of each silhouette, including when a person stands still. Use the same field placement as the weather response and leave the interior transparent.
- MR-15 filters the visual outline from subpixel mask coverage and uses smooth presentation scaling. The gameplay mask and collision geometry retain the original sensor resolution.
- Windows display selection uses physical pixels under per-monitor DPI awareness. A 4K TV remains selectable when Windows scales its desktop UI.
- Mirror body movement left/right; child's screen silhouette maps intuitively.
- Keep center of scene uncluttered; avoid an ever-present fake character.

## Discoverable interaction tiers

| Tier | Child action | World response | Required data |
|---|---|---|---|
| A | Stands in view | Rain separates and traces body outline | depth silhouette |
| A | Raises an arm, spreads arms | Droplets divert along raised outline, forming streams | depth silhouette |
| A | Sweeps side to side | Local gust/whirlpool follows moving silhouette | depth mask temporal change |
| A | Stands still | Rain softly accumulates and shimmers at shoulders/upper contour | depth silhouette |
| A | Reaches higher or stretches wider | Sky and flow strengthen *continuously* according to silhouette height/width (not exact required poses) | depth silhouette geometry |
| A | Leaves camera zone | Return smoothly to gentle rain | active foreground |
| B (optional) | Reaches high with both hands | More rain and diffuse stars fade in | reliable pose capability |
| B (optional) | Hands joined | Glowing orb visual illusion grows between hands | reliable pose capability |
| B (optional) | T-shape pose | Gentle rainbow palette shift | reliable pose capability |

Tier A includes two **pose-like qualities** measurable without a skeleton: relative reach (height of upper contour above head/torso baseline) and spread (horizontal extent of upper-body mask). Normalize against recent personal silhouette/scene bounds, smooth to avoid jitter, and map continuously to visual intensity; when unreliable, use only direct collision. Do not require the child to know a pose name. Tier A alone must be delightful and meet MVP. For Tier B, do not require exact posture or a tutorial; smooth activation over ~0.5 s with hysteresis and a cooldown before retrigger. Disable if 3D pose tracking is unreliable for small children.

## Do not accidentally build a gesture-command game

- In the first live version, interaction is **continuous physical cause and effect**: body as obstacle, arm as moving deflector, motion as gentle wind. No pose recognition must be necessary for visible action.
- Attract mode has raindrops even when no one is present. First detected foreground visibly bends a **local** stream immediately and remains calm for an idle child. A positive response must not depend on jumping, clapping or hitting an invisible target.
- MR-04 captures depth on a worker with one replaceable frame. The display starts with ambient rain while the adult clears the camera view for the in-memory reference. The notice disappears when calibration completes. Occupancy changes drive local wind and a gradual reach/spread response.
- Real body-to-screen latency must be measured; when the sensor loses confidence, the world gently returns to ambient rain instead of producing imaginary gestures.
- The child must never have to come close enough to touch the TV. The parent chooses a safe operating zone; no splash effect should encourage collisions with furniture or the display.

## Multiple children

Multiple foreground shapes influence the same rain naturally. No player IDs, markers, selection icons, score or color per person. If silhouettes overlap, treat them as one continuous physical object. Do not promise a unique magic power for each child.

## Parent menu

- Hidden in normal play. `F1` or `Esc` opens or closes the adult panel. The panel has actions for leaving play, switching scenes and tilting Kinect with the left/right arrows or the two angle buttons. No tracked movement opens it.
- Clear, simple **Swedish** text for adults, at most one screen, no nested submenu maze. Suggested layout:

```text
          MAGISKT REGN

       [ Fortsätt leka ]

       Ljud          [ Av / Lågt / Normal ]
       Regnets styrka [ Milt / Normalt / Livligt ]
       Spegelbild     [ På / Av ]
       Kamera         [ Kontrollera / Kalibrera ]
       Spara bild     [ Av (standard) / På ]

       [ Avsluta ]
```

- The parent UI is not the game UI. Scene continues gently in background or pauses subtle movement.
- A `--doctor` screen may show technical details, but never during child play.
- On next launch, start attract mode automatically; **no Start button** after one-time setup. The word 'Fortsätt leka' in the parent menu is permitted.
- The panel offers presets for volume, intensity, mirror, horizontal zone, and distance. Only these settings go into the Windows user's local application data. The empty-room reference stays in memory and refreshes at startup and after reconnection.
- The adult panel shows depth, the current silhouette and the playable frame. An amber edge indicates where the silhouette reaches the frame. Tilt moves in 5° steps within the SDK range with a cooldown. After aiming, the adult can select calibration and step aside during a countdown while the panel stays open.
- Color assistance defaults to on. The menu shows whether registration is active, and the adult can disable it. Spegelstudio displays the actual color image when the adult selects that scene.
- No gestures open or navigate the adult menu. Adults use keyboard/mouse.

## Optional body world switching (MR-35)

The owner requested hands-free scene selection. Two small portals sit inside
the camera field, at 16%/84% width and 32% height. A lateral upper-body tip
from a coherent person can hold either portal for 1.8 seconds to go to the
previous/next world. A local ring and temporary destination name show progress.
This is a silhouette approximation, not anatomical hand tracking. Reject
short disconnected objects, torso/head-only occupancy and merged identities.

Require a 0.4-second release before arming, stable tip position and fresh
samples throughout the hold. Brief dropouts pause; longer loss resets. After
switching, require release and a cooldown; never repeatedly cycle a held hand.
Disable during camera notices/faults, the adult panel or the adult option
Kroppsstyrt byte = Av. No gestures quit, save, tilt or calibrate. Mirror color
display remains adult opt-in each session, so body cycling skips Spegelstudio
until an adult selects it once. Hold only generated Paint Explosion artwork
in memory when leaving that world, so body navigation does not erase it.
Hardware reachability, accidental switching and accessibility remain pending.

## First-run calibration

The camera calibrates with an empty play area at startup. For manual setup, the adult panel shows the countdown, progress and completion. The depth and color references stay in memory and are refreshed after camera movement.

## Failure UX

If device unavailable, after short retry show calm adult message (in Swedish) on low-contrast background: 'Kinect-kameran hittades inte. Kontrollera ström och USB.' with 'Försök igen' and 'Avsluta'; do **not** silently launch fake working play or present a terminal stack trace.

## Usability test

Give a child no explanation other than 'Gå fram till TV:n och titta'. Observe first interaction, whether movement feels like a mirror, whether an adult intervenes, and if children intuit that arms/body control rain. Adjust physics and feedback, not instructions, first.
