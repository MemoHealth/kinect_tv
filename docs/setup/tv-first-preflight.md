# TV-first preflight — Kinect v1 on the target PC

This is a **read-only checklist for the owner**, not an invitation to install drivers. A checked box does not mean Kinect streaming is verified.

## Equipment and room

- [ ] Identify Kinect v1 model (Xbox 360 1414/1473 or Kinect for Windows 1517, if labeling allows). Record exactly what is printed rather than guessing.
- [ ] Confirm the correct **external Kinect power + USB adapter** for this sensor is physically available. Kinect USB alone may not power an Xbox 360 unit.
- [ ] The target PC has an available direct USB port, power supply, and HDMI to the TCL TV. Prefer direct USB over hubs.
- [ ] Sensor sits on a stable, child-proof mount with safe cable routing. There is room to move without reaching/touching TV, tripping, or jumping near furniture.
- [ ] Select the active HDMI input on the TCL 75MQLED85K. Record the actual resolution and refresh rate shown by Windows. Check a 3840 × 2160 signal if available, 16:9 geometry, visible edges and the TV's low-latency setting.

## Read-only device and scene checks

- [ ] Record Windows version and the reported Kinect device names/VID:PID from Device Manager **without replacing drivers**.
- [ ] Assess whether children of different heights will fit in view at a safe distance. The sensor has a limited field of view and working depth; camera tilt/placement must be tested physically, not assumed from nominal specs.
- [ ] Note interfering direct sunlight or reflective surfaces; these can disturb depth tracking.
- [ ] Determine whether the adult is willing to authorize an inspected driver change later **only if needed**. No modification in preflight.

## Operator handoff (fill in when available)

```text
Sensor model / photo of label (optional):
Power+USB adapter present: YES / NO / UNKNOWN
Laptop Windows version:
Port used (direct/hub):
HDMI-to-TCL works: YES / NO / UNKNOWN
Safe play-zone size and approximate viewing distance:
Device Manager names / hardware IDs (if plugged in):
Driver change authorized now? NO — ask separately at MR-02
Readiness: READY FOR NON-INVASIVE CHECK / NEEDS ADAPTER / NOT YET TESTED
```

## Important ordering

1. **MR-00** can be coded with simulated silhouettes even if the sensor is not yet connected.
2. **MR-02** is the next priority once the operator has the camera and adapter: identify hardware, inspect third-party scripts, ask before changing drivers, and measure real depth streaming.
3. Only after genuine Kinect frames are measured should development proceed to live masking, latency, and child usability claims. A fancy demo is not proof the sensor works.

No projector, wall mapping, climbing-wall, or throw detection belongs in this TV-first stage.
