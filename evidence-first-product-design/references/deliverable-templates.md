# Deliverable Templates

Use only the artifacts required by the current task. Keep evidence links close to consequential claims and distinguish facts from proposals.

## Contents

1. Context Map
2. Truth Ledger
3. Conceptual Model
4. Breadboard
5. State Matrix
6. Screen Specification
7. Decision Log
8. Fidelity Ledger
9. Runtime QA Record

## Context Map

```markdown
| Area | Current truth | Evidence class | Source | Confidence/conflict |
|---|---|---|---|---|
| User and job | | | | |
| Product/version scope | | | | |
| Domain vocabulary | | | | |
| Existing capability | | | | |
| Data and permissions | | | | |
| Platform and stack | | | | |
| Design system/brand | | | | |
| Research/analytics | | | | |
| Runtime baseline | | | | |
| Authorization boundary | | | | |
```

## Truth Ledger

```markdown
| Claim or decision | Type | Evidence | Confidence | Impact if wrong | Next action |
|---|---|---|---|---|---|
| | fact/observation/inference/assumption/proposal/decision/gap | | | | |

Conflicts:
- [Source A] and [Source B] disagree about [topic]. They establish different evidence classes / [source] supersedes [source] because [reason].

In scope:
-

Explicitly out of scope:
-
```

## Conceptual Model

```markdown
| Object | User definition | Important attributes | Relationships | Actions | States | Permissions |
|---|---|---|---|---|---|---|

Not first-class objects:
- [Query/view/transient context]: [why it should not persist].

Vocabulary mapping:
| Product term | Domain term | Engineering term | Deprecated/ambiguous term | Reason |
|---|---|---|---|---|
```

## Breadboard

```text
Place: [user-meaningful name]
- [affordance] -> [destination place/state]
- [affordance] -> [destination place/state]
[content: information needed for the job]

Failure or interruption: [condition]
- Visible feedback:
- Preserved work/context:
- Recovery action -> [destination/state]
```

## State Matrix

```markdown
| State | Entry event | Visible representation | Available actions | Exit event | Side effect/audit | Test |
|---|---|---|---|---|---|---|
| idle | | | | | | |
| loading/working | | | | | | |
| empty | | | | | | |
| success | | | | | | |
| validation/error | | | | | | |
| degraded | | | | | | |
| permission/session | | | | | | |
| offline/interrupted/conflict | | | | | | |
```

## Screen Specification

```markdown
# [Place / Route / Screen]

- User and situation:
- Primary job:
- Primary object:
- Product/version scope:
- Data/model/API and permissions:
- Unsupported claims:

## Information And Action Order
1.
2.
3.

## Controls
| Control | Semantics | States | Keyboard/focus | Touch/gesture/pointer | Result |
|---|---|---|---|---|---|

## Adaptation
| Device/window/input/context | Structure | Moved/deferred content | Navigation and return | Overflow/interruption strategy |
|---|---|---|---|---|

## Edge Conditions
- Empty:
- Loading/slow:
- Error/retry/cancel:
- Degraded/offline:
- Permission/session expiry:
- Conflict/concurrent change:
- Localization/long content/text scaling:
- Large data/performance:

## Acceptance
- [Observable, repeatable assertion]
```

## Decision Log

```markdown
| Decision | Alternatives | Evidence and tradeoff | Approval status | Owner/date | Revisit trigger |
|---|---|---|---|---|---|
```

## Fidelity Ledger

```markdown
| Comparison point | Approved specification/concept | Implementation | Difference | Severity | Resolution |
|---|---|---|---|---|---|
| Container/structure | | | | P0-P3 | |
| Information/action order | | | | P0-P3 | |
| Interaction/state | | | | P0-P3 | |
| Copy/data/permissions | | | | P0-P3 | |
| Adaptive behavior | | | | P0-P3 | |
| Accessibility | | | | P0-P3 | |
```

## Runtime QA Record

```markdown
- Source/artifact/build identity (where applicable):
- Runtime target and dependency versions:
- Platform/browser/device/OS:
- Identity, role, permission, and data context (where applicable):
- Sizes, viewports, windows, orientations, and themes:
- Primary interaction proof:
- Empty/error/degraded/recovery proof:
- Keyboard/focus/screen reader/text scaling/reduced motion:
- Diagnostics, logs, console, overlay, crash, and overflow:
- Screenshots or recordings:
- Commands and automated tests:
- Side-effect boundary and any commit action intentionally not executed:
- P0/P1 remaining:
- P2/P3 tradeoffs and untested risk:
```
