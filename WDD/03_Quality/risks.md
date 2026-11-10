# Risk register (lean)

| ID | Risk / failure | Likelihood / severity | Mitigation / decision gate |
|---|---|---|---|
| R-01 | Kinect v1 may be unstable on the target PC's USB controller | Medium / High | Depth-only adapter, doctor for 60 s, isolated backend, alternate USB port, hardware gate MR-02 |
| R-02 | Incorrect USB driver binding causes other device trouble | Low–medium / High | USB ID verification, adult approval, rollback instructions, never run install automatically |
| R-03 | Background segmentation fails with clutter/movement | Medium / High | Empty-room reference, valid depth mask, quality score, reset/calibration, smooth fallback |
| R-04 | Small children / multiple kids not reliably skeleton tracked | High / Medium | Silhouette-only core, no skeleton dependencies for MVP |
| R-05 | Particle engine too slow on laptop or TV | Medium / Medium | 720p logical engine, frame profiling, adaptive quality ladder, no 4K physics |
| R-06 | Delayed or jittery rain feels disconnected | Medium / High | Latest-frame queues, no heavy per-frame blur, short sensor->visual latency target, smooth filtering |
| R-07 | Children need instructions / gestural commands | Medium / High | No commands, respond to all movements, observe play without explanation |
| R-08 | Sensory overload, physical hazards | Medium / High | Soft visuals/audio, no demanded jump, caregiver oversight, secure cables/sensor |
| R-09 | Privacy leak through debugging screenshots, audio or MCP | Low–medium / High | No capture/telemetry by default, synthetic fixtures, adult-only optional screenshot |
| R-10 | Third-party lib breaks, is unmaintained or has incompatible redistribution terms | Medium / Medium | Narrow adapters, pinned commits, licensing notes, no automatic runtime downloads |

## Review trigger

Revisit when a risk is observed in live testing, when new drivers/dependencies are added or when requirements for raw camera/microphone recording change. No separate risk database needed.
