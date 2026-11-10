# Architecture, boundaries and runtime topology

## Decision

**Python 3.11/3.12 baseline + NumPy + pygame-ce (SDL2) + optional OpenCV** for a fast, understandable desktop prototype. Kinect v1 uses the dedicated SDK adapter described in [Kinect backend](kinect-backend.md). Keep graphics backend replaceable if profiling shows CPU limits. Do not build Unity or a browser client unless measurements justify it.

## Data flow

```text
Kinect v1 / simulated input
           |
           v
SensorAdapter --> SensorFrame (depth mm, timestamp, optional RGB)
           |
           v
Foreground segmenter --> binary person mask + confidence/quality
           |
           +--> shape/motion estimator --> flow field / optional gestures
           |                              |
           +------------------------------+
                                          v
                                  RainSimulation
                                          |
                                          v
                                  Renderer + audio
                                          |
                                          v
                                    HDMI -> TV
Adult keyboard -> UI state/settings -> all modules (controlled configuration only)
```

## Required modules and ownership

- `app.py`: lifecycle, window, state machine; no hardware code.
- `sensors/base.py`: typed interface, errors, timestamps, health.
- `sensors/kinect_v1.py`: only module allowed to import/call Kinect/native USB DLLs.
- `sensors/simulated.py`: deterministic synthetic frames/interactive mouse control.
- `vision/background.py`: static depth model with controlled recalibration.
- `vision/foreground.py`: depth mask, body-region filtering, holes and smooth edges.
- `interaction/field.py`: derive local forces and collisions from mask and its motion.
- `interaction/poses.py`: optional, disabled by default, capability-gated.
- `simulation/rain.py`: pure deterministic update step, fixed delta handling.
- `render/scene.py`: particles, glow, rain trails, background; parent menu is separate UI.
- `ui/parent.py`: adult-only settings and diagnostics; no normal-play HUD.
- `audio/ambient.py`: soft reactive ambience and mute.
- `config.py`: validated local settings, defaults and migration.
- `diagnostics.py`: health display, fps, packet losses outside child view.

## Proposed implementation file tree (do not create all empty folders prematurely)

```text
src/magic_rain/
  __main__.py   app.py    config.py    diagnostics.py
  sensors/{base.py,kinect_v1.py,simulated.py}
  vision/{background.py,foreground.py}
  interaction/{field.py,poses.py}
  simulation/rain.py
  render/scene.py
  ui/parent.py
  audio/ambient.py
assets/audio/       assets/fonts/       assets/shaders/ (only if needed)
tests/{unit,integration,fixtures}/
pyproject.toml       .gitignore       .github/workflows/check.yml
```

## Architectural constraints

- No circular import between `sensors`, `vision`, `interaction`, `simulation`, `render`.
- Capture can run off-main-thread if blocking; render/game loop stays responsive; bounded queue size 1–2 (drop stale frames, never accumulate latency).
- All coordinate mapping is centralized: sensor pixel -> normalized (0..1) -> logical scene -> displayed letterboxed coordinates, with mirror applied exactly once.
- Normal play never depends on RGB and never downloads a model.
- No persistence of `SensorFrame` or foreground masks; raw live frames remain memory-only.
- Avoid network access after setup; disable analytics, telemetry, update checks and auto-downloads.
- Dependencies pinned after a successful build/test; document license implications and platform-specific native DLL distribution.

## Build constraints

Provide command entry points `--demo`, `--doctor`, `--windowed` (dev), and default live fullscreen. Do not let hardware integration block simulated-mode CI. Prefer simple functions + type hints over dependency injection frameworks or ECS.
