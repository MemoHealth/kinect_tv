# Acceptance criteria (canonical requirement IDs)

**Evidence types:** A = automated CI, S = local synthetic visual/interaction test, H = owner-run real Kinect + TV test, C = child observational session. Mark the verification type used and any limitations. **A/S evidence never substitutes for H.**

| ID | Requirement | Acceptance evidence |
|---|---|---|
| MR-UX-01 | Launch directly into ambient rain after prior setup, full screen | S + H: no Start step, no splash/menu barrier |
| MR-UX-02 | No child HUD or gesture instructions | S + H: normal-play screenshot has no text, score, icon, button or skeleton diagram, except MR-35's explicitly requested world portals and temporary hold feedback |
| MR-UX-03 | Natural entry/exit | S + H: movement enters play automatically and returns gradually on exit; no child action needed |
| MR-UX-04 | Mirror mapping | H: moving right hand to child's right corresponds to same-side visual movement in mirror perspective; tested explicitly |
| MR-UX-05 | Calm parent menu | S + H: F1 and Esc open or close the menu. The adult can exit, choose a scene, aim Kinect with a live preview and calibrate in the open menu. The preview marks when foreground reaches a play-zone boundary. Settings persist and support keyboard and mouse. No child gesture opens the panel. |
| MR-UX-06 | Readability-independent | C: 2+ trial participants of differing age/height can discover visible influence without explanation; note observed exceptions (not assumed pass) |
| MR-CV-01 | Real depth sensor | H: authentic Kinect v1 stream with confirmed units, timestamps, stable capture and reconnect behavior |
| MR-CV-02 | Depth-only baseline | A + S + H: play works with RGB=None and poses disabled |
| MR-CV-03 | Foreground and silhouette | S + H: one, two and three simultaneous people produce visible masks across the play zone. Partial occlusion preserves the visible foreground. Invalid depth does not fill the screen. |
| MR-CV-04 | Bad tracking fallback | A + S: stale/missing frames decay safely; no frozen body > configured hold; sensor fault apparent to adult |
| MR-ART-01 | Rain interacts with body | S + H: clear deflection/outline following for head, torso and arms; droplets do not simply pass through a broad solid mask |
| MR-ART-02 | Motion drives nearby field | S + H: arm sweep causes localized directional flow and decays smoothly; non-moving objects do not create large wind |
| MR-ART-03 | Quiet/motionless play | S + H: seated or stationary user still produces an interactive outline and subtle glimmer |
| MR-ART-04 | No required poses | S + H: at least all Tier A effects function without skeleton/MediaPipe |
| MR-ART-05 | Comfortable visuals and audio | S + H + C: no flash, no sudden loud cue, intensity/mute settings work; no rapid whole-screen inversions |
| MR-ART-06 | Natural posture expression without skeleton | S + H: reaching high or wide changes rainfall smoothly; no discrete pose success/fail and no dependency on RGB |
| MR-SYS-01 | Simulated dev mode | A + S: `--demo` launches without Kinect; mode clearly labeled to developer and not counted as hardware success |
| MR-SYS-02 | Fault transparency | A + H: missing or disconnected device shows calm adult message; no silent fake camera or crash |
| MR-SYS-03 | Offline/private | A + H: no runtime network use; no raw frame recordings; image saving disabled by default, explicitly enabled by adult only |
| MR-SYS-04 | Stable responsive runtime | S + H: performance budgets per `01_Architecture/performance.md`, sustained 30 min, log actual measured results |
| MR-SYS-05 | Safe hardware install | H: driver identity/approval and rollback documented; no automatic admin driver action |
| MR-SYS-06 | Maintainable boundaries | A: no sensor library imports outside `sensors/`; deterministic simulation unit-tested; schema/settings validated |
| MR-DEL-01 | Documentation / review | A + process: corresponding WDD updated, one focused PR per issue, one independent review and explicit test results |

## V1 release gate

Release requires MR-UX-01..05, MR-CV-01..04, MR-ART-01..06, MR-SYS-01..06, MR-DEL-01 verified with the evidence types listed. MR-UX-06 requires observational evidence before describing the product as intuitively validated; until then document it as pending rather than asserting it.

## Good enough ≠ perfect

A magical contour and responsive water motion are more important than fluid conservation, detailed fingers, precise joints or broad feature scope. Prefer stable Tier A over unreliable Tier B; track measured limitations.
