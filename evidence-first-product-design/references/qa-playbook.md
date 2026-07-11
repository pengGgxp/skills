# Runtime UX QA Playbook

Runtime evidence must match the current source and the target platform. Static design review and source inspection are useful, but they do not prove interaction quality.

## Establish Provenance

Record the fields that apply:

- source or artifact identity, such as repository/branch/worktree/commit, design version, package version, binary hash, or firmware build;
- build or export command and whether the artifact reflects the latest change;
- runtime target and relevant local, service, hardware, network, model, or content dependencies;
- feature flags and relevant identity, role, permissions, locale, theme, and data context;
- device, simulator, browser, OS, viewport/window, scale, input method, and environmental conditions.

Reject screenshots from stale builds, mismatched services, hidden errors, corrupted fixtures, or unknown login/data state.

## Test The Workflow

Execute the affected user task as far as the user's authorization allows. Verify object identity and state after navigation, mode transitions, retries, authentication, backgrounding, and adaptive handoffs.

Use sandbox, test, preview, or reversible data by default. Do not send external messages, spend money, publish, destructively delete, mutate production, or change permissions without explicit user authority. When authority is absent, stop immediately before the committing action and document the untested step and expected evidence.

Cover relevant states:

```text
initial, loading, empty, partial, success, validation, permission denied,
recoverable error, permanent error, timeout, retry, cancel, degraded,
offline, interrupted, session expired, concurrent conflict, large data
```

Do not force irrelevant states. Explain which ones do not apply.

## Web

- Test representative wide, narrow, and mobile viewports based on the product's actual support matrix.
- Inspect page and internal-container overflow, focus order, keyboard traps, semantics, accessible names, contrast, zoom/text resize, reduced motion, and pointer/touch targets.
- Check console warnings/errors, framework overlays, failed requests, hydration, layout shifts, and stale assets.
- Use viewport screenshots for hierarchy; use full-page screenshots only as supplemental evidence.

## Native Mobile

- Test supported small and regular devices, orientations, safe areas, keyboard, Dynamic Type/font scale, dark mode, and reduced motion.
- Verify VoiceOver/TalkBack labels and order, non-gesture alternatives, target sizing, system back behavior, interruption/backgrounding, deep links, and state restoration.
- Distinguish iOS and Android conventions and evidence. Do not claim one simulator proves the other platform.

## Desktop

- Test minimum, typical, and large windows; resizing; display scaling; keyboard/menu access; focus; high contrast; screen reader; and multi-window or file behavior where relevant.
- Verify dense workflows with representative data volumes, partial failures, long-running actions, and permission differences.

## Other Interfaces

For TV, wearable, embedded, kiosk, voice, spatial, terminal, automotive, game, or other surfaces, build a platform capability matrix before testing:

- available input and output channels;
- focus, navigation, confirmation, escape, and recovery conventions;
- distance, environment, latency, connectivity, resource, and safety constraints;
- interruption, resume, multi-user, and privacy behavior;
- platform accessibility and alternative input requirements;
- available diagnostics, simulator/emulator, hardware, or test harness.

Use evidence appropriate to that platform. Do not force browser or smartphone criteria onto a different interaction model.

## Cross-Platform And Responsive

Verify that adaptation preserves the job and return path. Do not treat desktop columns stacked vertically as a mobile design, or a web screenshot as proof of a native surface.

## Content And Data

Test representative language scripts, long and short content, unbroken strings, rich text semantics, large collections, missing media, corrupted or unsupported data, and round-trip encoding where relevant.

Preview and summary transformers must not render canonical content unless their intentional loss is acceptable and tested.

## Severity

- **P0**: Blocks a critical task broadly, causes destructive loss/security/privacy harm, or makes the surface unusable.
- **P1**: Breaks a primary task, trust, accessibility, or content integrity for a significant path; required before delivery.
- **P2**: Material quality or efficiency issue with a workaround; schedule deliberately.
- **P3**: Minor polish, consistency, or low-frequency improvement.

Do not average severity into a score that hides critical findings. State evidence, affected users/path, reproduction, expected behavior, and acceptance condition for each issue.

## Completion Gate

Claim runtime QA completion or production readiness only when:

- required automated checks pass;
- required runtime paths have current evidence;
- P0/P1 is zero;
- approved design/spec differences are resolved or explicitly accepted;
- untested states and external dependencies are disclosed;
- evidence is stored according to the target project's conventions.

When the task is an implementation-only handoff and runtime access is unavailable, deliver the implementation with a clearly separated list of unverified paths, unavailable dependencies, and residual risk. Do not describe it as runtime-verified or production-ready.
