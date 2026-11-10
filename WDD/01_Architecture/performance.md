# Performance and observability budgets

Performance is primarily a **perceived latency** problem: children must experience an immediate reaction between body movement and moving rain, not simply high frame rate.

## Initial targets (validation goals, not established measurements)

| Metric | Target | Minimum acceptable | Method |
|---|---:|---:|---|
| Render | 60 FPS @ logical 1280x720 | stable >=30 FPS | frame-time instrumentation |
| Depth capture | near sensor nominal 30 FPS | >=20 stable FPS | monotonic frame timestamps |
| Body-to-reactive visual onset | <150 ms median | <250 ms p95 | camera/phone slow-motion comparative measurement |
| Enter zone to visible response | <0.8 s | <1.5 s | live observation |
| Exit to calm rain | ~2–4 s | no abrupt stop | observed |
| Visible interactive particles | begin 1,500–3,000 | adaptive lower bound | real PC profiling |
| Runtime stability | 30 min | no crash, USB hang or unbounded memory | live soak |

These numbers are goals only; flag any unmet gate. 1080p/4K TV output is achieved by scaling the logical scene, **not** rendering 4K fluid simulation.

## Adaptive quality (in this order)

Lower particle count -> reduce per-particle glow and trail length -> use half-resolution force field -> cap splash events -> target 30 Hz render. Never skip sensor sampling merely to preserve cosmetic effects. Effects must degrade smoothly without visible jumps.

## Diagnostics

Developer-only overlay or `--doctor` logs: render FPS, sensor FPS, frame age, skipped frames, foreground confidence/area, scene particle count, simulation duration, memory consumption and source (`real`/`simulation`). No data should leave the machine. Default user-facing play screen must not show metrics.

## Benchmarks

Automated repeatable 60 s synthetic load with 1, 2, 3 simulated figures and worst-case heavy motion. Real Kinect 30 min test on user's Windows PC. Publish **measured** outputs with OS, CPU, GPU and date only after testing; no speculative benchmark claims.
