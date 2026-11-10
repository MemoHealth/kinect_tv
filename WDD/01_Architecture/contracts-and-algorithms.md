# Canonical contracts and core algorithms

All algorithms are implementation proposals; the **input/output contracts and user-visible invariants** are mandatory. Numeric tuning values are initial hypotheses, requiring profiling and live validation.

## SensorFrame contract

```python
@dataclass(frozen=True)
class SensorFrame:
    timestamp_monotonic_s: float
    depth_mm: np.ndarray  # (H,W), uint16, 0 denotes invalid
    rgb: np.ndarray | None  # optional (H,W,3), uint8; not required for play
    width: int
    height: int
    source: Literal["kinect_v1", "simulation"]
    dropped_frames_total: int | None = None
```

`SensorAdapter.start()`, `.read_latest(timeout_s) -> SensorFrame | None`, `.health() -> SensorHealth`, `.stop()`. Use explicit statuses (`OK`, `NO_DEVICE`, `DRIVER_ERROR`, `NO_FRAMES`, `UNSTABLE_STREAM`) rather than empty arrays presented as success. Time is monotonic; consumer drops stale frames > ~250 ms.

## Foreground contract

```python
@dataclass(frozen=True)
class Foreground:
    mask: np.ndarray  # (H,W) bool, true=player/foreground
    confidence: float  # 0..1 data quality heuristic, not human identity confidence
    timestamp_monotonic_s: float
    active: bool
```

- Depth-only segmentation: stable empty-room depth reference; foreground if current valid distance is significantly **closer** than registered reference; reject invalid/hole pixels.
- Initial working thresholds: 80–160 mm closer than background, morphological closing/opening, temporal smoothing, minimum component size calibrated to range. These are **not fixed universal constants**.
- Bound active zone by near/far and adjustable left/right crop; mask must support children and adults, varying body sizes, multiple connected components, and partial occlusion.
- Confidence decreases with excessive missing-depth pixels, unrealistically sparse mask, or stale frames; low confidence reduces dynamics gracefully.
- On mask lost, decay rather than abrupt snap; never extrapolate indefinite limbs from stale data.

## Geometry and fluid illusion

Work in a logical 2D scene (suggest 1280x720) independent of display resolution. Depth frame and logical scene are mapped once.

- Use an obstacle mask from the foreground; compute a low-resolution signed-distance/edge gradient (OpenCV distance transform or equivalent) per new sensor frame; avoid expensive per-particle search of all contour points.
- Particle update on fixed time steps (~1/60 s): `velocity += (gravity + wind + flow_field) * dt`; cap speed; integrate and check **swept path** or subdivide updates to prevent tunneling through thin arms.
- If rain intersects an obstacle, reposition outside mask and remove/reflect inward normal component; bias tangential motion downhill along the outline. Spawn small splashes and soft glow at impact, but cap event rate.
- Motion flow from smoothed mask displacement / local temporal differences and/or foreground center-of-mass movement; apply decaying nearby forces; do not assume skeletal joints.
- **Response hierarchy:** first make a standing body visibly interrupt the falling rain; next make sweeping arms redirect nearby drops. Do not prioritize hidden discrete pose classifiers over these immediately discoverable actions. A child should not have to learn a gesture to see a result.
- Continuous posture-like measures can be estimated from silhouette occupancy (vertical reach; lateral spread), with temporal smoothing and confidence gates; map them to rain intensity and width. Never require discrete pose recognition for first interaction.
- Do not promise that real droplets will physically pool inside palms with this algorithm. A convincing *water orb* is an **optional authored effect** gated on reliable pose tracking, not real liquid conservation.
- Manage lifetime, respawn at top, bounded particle pool, deterministic random generator for tests. Do not spawn unbounded particles.

## Simulation and timing

- Separate sensor frame rate (~30 fps nominal) from rendering (target 60 fps); reuse/interpolate last stable mask.
- Fixed timestep accumulator, clamp dt after pause/focus loss (e.g. 50 ms maximum on resume), max substeps per frame; avoid spiral of death.
- Apply smooth interpolation/hysteresis to all reactive strengths (0.15–0.5 s transitions) and never flash or instantly invert the screen.
- Mirror by default: moving physically left should move silhouette to the same screen side as a mirror. Provide parent toggle if needed; test with a real child.
- Kinect depth frames are typically 4:3 while TV output is 16:9. Preserve human proportions: map foreground into an aspect-preserving central zone with ambient rain across full width, **or** use a configured crop. Never stretch the silhouette to fill widescreen. Test the resulting mapping with an actual user.

## Low-quality fallback ladder

1. Silhouette + flow + impacts (preferred).
2. Silhouette + simple collision (when flow tracking noisy).
3. Motion-centroid soft force (when mask fragmented).
4. Ambient rain only with calm adult connection/quality guidance if sensor truly unavailable.

No silent switch from real mode into synthetic child tracking. Never fake sensor health.
