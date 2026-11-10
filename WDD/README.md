# Working Design Document (WDD) — index

WDD means **Working Design Document**: living, version-controlled decisions used before and during implementation. This is the **canonical source of truth** for the product. Each rule is documented once, and other docs link to it. Use English in engineering documents for agents; Swedish is the default language for adult-facing UI.

## Product (why / what)

- [`00_Product/vision-and-principles.md`](00_Product/vision-and-principles.md): experience, invariants, scope and non-goals.
- [`00_Product/user-journeys.md`](00_Product/user-journeys.md): first use, returning use, interruptions and caregiver setup.

## Engineering (how)

- [`01_Architecture/system-and-modules.md`](01_Architecture/system-and-modules.md): chosen stack, components and data flow.
- [`01_Architecture/contracts-and-algorithms.md`](01_Architecture/contracts-and-algorithms.md): frame contracts, mask, flow, particle collisions and update rules.
- [`01_Architecture/kinect-backend.md`](01_Architecture/kinect-backend.md): Kinect v1 on the target Windows PC, limitations, acceptance gate.
- [`../docs/setup/tv-first-preflight.md`](../docs/setup/tv-first-preflight.md): operator-facing hardware readiness without changing drivers.
- [`01_Architecture/performance.md`](01_Architecture/performance.md): budgets, adaptive quality and metrics.

## Experience (what children see and feel)

- [`02_Experience/interaction-and-menu.md`](02_Experience/interaction-and-menu.md): zero-HUD play, intuitive rules, caregiver controls.
- [`02_Experience/art-direction-and-sound.md`](02_Experience/art-direction-and-sound.md): rain aesthetic and sound envelope.
- [`02_Experience/scenes-and-progressive-enhancement.md`](02_Experience/scenes-and-progressive-enhancement.md): first scene, optional variations and pose gating.

## Quality / delivery

- [`03_Quality/acceptance-criteria.md`](03_Quality/acceptance-criteria.md): measurable requirements and exact pass criteria.
- [`03_Quality/test-plan.md`](03_Quality/test-plan.md): automated tests, hardware matrix and child usability.
- [`03_Quality/privacy-and-safety.md`](03_Quality/privacy-and-safety.md): offline operation and child safety.
- [`03_Quality/risks.md`](03_Quality/risks.md): risk register and mitigations.
- [`04_Delivery/roadmap.md`](04_Delivery/roadmap.md): issue-sized phases and dependencies.
- [`04_Delivery/worlds-feasibility.md`](04_Delivery/worlds-feasibility.md): proposed worlds, source and license review, and build gates.
- [`04_Delivery/change-protocol.md`](04_Delivery/change-protocol.md): workflow and traceability.
- [`ADR/0001-depth-first-modular-python.md`](ADR/0001-depth-first-modular-python.md): key architecture decision.

## Change discipline

Update the narrowest canonical document when changing behavior. New architectural decisions require a short ADR only when they affect multiple modules or introduce an irreversible dependency. Prefer **no new documents** for minor fixes. All acceptance claims must cite observed tests; unresolved hardware gates remain open.
