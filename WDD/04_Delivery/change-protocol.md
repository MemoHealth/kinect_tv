# Lightweight issue / PR / agent change protocol

## Source of truth

GitHub issue (task intent), WDD (approved design), PR (implementation review), tests (verification evidence). No separate task DB, duplicate design Wiki or giant AI-generated report. `WDD/04_Delivery/roadmap.md` acts as initial backlog until GitHub exists.

## Minimum issue body

- Task ID and title; motivation / observed issue.
- Scope and **out of scope**.
- Relevant requirement IDs and WDD links.
- Acceptance tests (automated, simulated, owner-hardware, child observations).
- Dependencies / existing PR conflict check.
- Risks, particularly hardware and privacy.

## Required PR summary (compact)

```text
Issue: MR-xx / #number (if issued)
Why: one sentence
Change: affected files/modules
Design impact: WDD files updated or 'none; no behavior change'
Requirements: MR-...
Verification: pytest ..., ruff ..., --demo ..., hardware: PASS/FAIL/NOT RUN
Review: one independent review + addressed findings
Out of scope: explicitly excluded work
Risks / limitations: ...
```

## Agent sequencing

1. Planner reads WDD and scope, checks current branch/main and open PRs, proposes bounded change.
2. Builder changes WDD first if necessary, implements minimal vertical slice and tests, records results.
3. Reviewer independently checks product invariants, architecture boundaries, privacy, acceptance evidence. **One review round by default**.
4. Builder fixes actionable issues, runs full targeted verification and records limitations.
5. PR opened only when gates satisfied or clearly labeled blocked; merge requires explicit maintainer approval.

## Handoff format

`DONE / BLOCKED / PARTIAL`, requirement IDs, changed files, test commands/results, measured performance (if any), pending hardware steps, recommended next issue. Under a page; avoid status chatter and long agent transcripts.

## Change categories

- Bug with no behavior change: tests + short PR, WDD update only if contract was incorrect.
- UX/behavior change: edit narrowest WDD spec + acceptance test in same PR.
- New subsystem or platform stack: ADR, risk review and targeted proof-of-concept before broader build.
- Device/driver change: stop for human confirmation.
