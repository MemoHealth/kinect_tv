# Product vision, scope and principles

## The promise

A child stands in front of a TV. A beautiful, gently falling stream of magical rain is already on screen. As the child moves, particles visibly curve around the silhouette, cascade along the outline, and react to sweeping arms, tilts and changes of posture. **No explanation is required**. The child can discover cause and effect in under seconds, including very young children who cannot read.

## Audience and context

Primarily children roughly preschool through primary school age with adult supervision, in a typical living room. Multiple children may be present. Older adults are the setup operators. Console controllers are not necessary. The sensor is Kinect v1, the owner's existing Windows 10 Pro 22H2 PC processes input, and the TCL Google TV displays output over HDMI.

## Priority order

1. Immediate and delightful cause/effect.
2. Robustness, even with imperfect sensor input, small children, overlapping silhouettes and occasional occlusion.
3. Low cognitive load and low physical demand.
4. Low-cost, offline, small hardware footprint.
5. Expandability without destabilizing the basic interaction.

## Immutable design principles

- **Zero-HUD child experience:** no score, lives, instructions, labels, glyphs or progress bars in normal play.
- **Progressive magic:** any movement is useful; intentional poses only amplify effects, never gate them.
- **No fail state:** no wrong gesture, timer, lives, waiting for calibration or punishment.
- **No hard start/stop ritual:** entering the zone starts interaction; departing returns to calm rain.
- **No startling effects:** soft sound, bounded visual intensity, no rapid flashes, explosions or loud sudden audio.
- **No surveillance product:** no recognition, tracking individuals by identity, cloud processing or data collection.
- **Sensor independence:** creative rendering is not tightly coupled to a specific camera API.

## Deployment boundary: TV first

The v1 display is the **TCL 75MQLED85K**, a 75-inch 4K QD-Mini LED TV (2025), connected over HDMI. Render to the existing 1280 × 720 logical scene and preserve its 16:9 aspect ratio at the TV's actual HDMI mode. Test the PC's negotiated resolution and refresh rate, rain visibility and motion comfort on the physical screen. Compute body motion with Kinect v1 in a safe living-room play zone. Projected and touch surfaces belong to separate product work.

## Must-have v1 outcome

A single magic-rain scene in fullscreen, depth-derived body silhouette, silhouette-rain interaction, soft motion-driven flow, seamless attract/idle behavior, parental setup, graceful sensor failure, explicit simulation mode, tests and performance controls.

## Deliberately excluded from v1

Mario/console control, projector/wall/climbing-wall/ball modes, full fluid dynamics (Navier-Stokes/SPH), face tracking, speech commands, smartphone pairing, complex menu, achievements, voice assistant, multiplayer identity tracking, online features, accounts, automated AI generation, mandatory pose recognition, saving children's camera imagery.

## Success definition

An unfamiliar child can create a visible change by moving without instruction, and can continue playing for 5 minutes with no intervention. This is a **usability target** requiring observed tests, not a claimed measured result.
