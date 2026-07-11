---
name: evidence-first-product-design
description: Orchestrate evidence-first product, UX, and UI work from context discovery and product truth through conceptual modeling, interaction flows, screen specifications, visual direction, implementation, and runtime QA. Use when Codex needs to design or redesign product surfaces, define information architecture or UI states, produce implementation-ready UX specifications, implement an approved interface, translate work to or from Figma, or audit usability, responsiveness, accessibility, resilience, and visual quality in any project. Adapt to the target domain, platform, stack, design system, and maturity instead of assuming a framework or product model.
---

# Evidence-First Product Design

Treat design as a traceable set of decisions, not a styling pass. Discover the target project's truth, resolve the lowest uncertain product layer, specify behavior before appearance, then verify the real experience on its actual platform.

## Load References

1. Always read [context-discovery.md](references/context-discovery.md) before making product or interface decisions.
2. Read [skill-routing.md](references/skill-routing.md) before selecting supporting skills. Load only the smallest useful set.
3. Read [field-lessons.md](references/field-lessons.md) for redesigns, implementation, and audits, or whenever the project has legacy surfaces.
4. Read [deliverable-templates.md](references/deliverable-templates.md) when producing formal design artifacts.
5. Read [qa-playbook.md](references/qa-playbook.md) before implementation verification or a production audit.

Keep product-specific facts in the target project. Never add a client's objects, routes, stack, tokens, or incidents to this installed skill.

## Choose Work Depth

Do not run the full workflow mechanically.

- **Discovery, research, or strategy**: stop at the relevant foundation layer. Do not invent screens.
- **New product flow or major redesign**: run Stages 0-6.
- **Targeted change inside an established pattern**: check Stages 0-2 quickly, then focus on Stages 3, 5, and 6.
- **Design or UX review**: establish evidence in Stage 0, audit the relevant layers, and do not change code unless the user asks.
- **Accessibility, resilience, responsive, or performance fix**: preserve the existing product contract, then focus on Stages 3, 5, and 6.
- **Visual concept or Figma-only request**: complete enough of Stages 0-3 to prevent the visual artifact from inventing behavior.
- **Implementation of an approved design**: verify approval, context, and contracts, then execute Stages 5-6 without reopening settled direction.

Escalate a local change to deeper product work if it changes a primary object, vocabulary, permission, state model, main task, or cross-surface navigation.

Respect authorization boundaries. A request to review, explain, or diagnose does not authorize code edits, external writes, or product scope changes.

## Stage 0: Context And Product Truth

Inspect the current task, repository instructions, product sources, implementation, design system, research, analytics, and runtime evidence. Follow [context-discovery.md](references/context-discovery.md).

Build two distinct views:

- **Product truth**: intended users, jobs, product promise, version scope, policy, and explicit exclusions.
- **Implementation truth**: capabilities that actually exist, data contracts, permissions, states, dependencies, tests, and runtime behavior.

Classify evidence instead of forcing every source into one precedence list. Requirements can define intent without proving implementation; code can prove implementation without proving the intended experience.

Produce a concise Context Map and Truth Ledger with scope, non-scope, facts, conflicts, assumptions, gaps, and evidence locations. Ask only for high-impact information that cannot be discovered safely.

**Gate**: Do not place unsupported roadmap capabilities, fabricated data, or assumed permissions in the core experience.

## Stage 1: Opportunity And Conceptual Model

Resolve only the foundation that is uncertain:

- Distinguish observed behavior from stakeholder belief and design assumption.
- Clarify the domain vocabulary before creating product vocabulary.
- Define user needs and the strategy choices that decide which needs to serve.
- Define user-meaningful objects, relationships, actions, states, permissions, and one term per concept.
- Keep transient queries, views, filters, and context values from becoming unnecessary first-class objects.

Load `layers-intro` before any other `layers-*` skill. Use `layers-orient` when the bottleneck is unclear and `layers-conceptual-model` when nouns, boundaries, or states are unstable.

**Gate**: Every primary noun and action maps to a justified model; assumptions and provisional objects are labeled.

## Stage 2: Interaction Flow And State

Create a breadboard for the current user, situation, and job. For each place, state what it shows, what the user can do, where each action goes, and how the user returns.

Cover relevant paths:

- happy, empty, loading, validation, error, degraded, and permission denied;
- cancel, retry, timeout, offline, interruption, and concurrent conflict;
- post-action feedback and preservation of user work;
- platform-specific navigation, input, window, gesture, and background behavior.

Use a state machine when behavior is asynchronous, multi-mode, permission-sensitive, or difficult to describe without impossible states. Every state needs a visible representation and an exit.

**Gate**: Every affordance has a destination; failure, cancellation, recovery, and platform transitions have no dead ends.

## Stage 3: Implementation-Ready Specification

Write the behavioral specification before high-fidelity visuals. Include:

- user and situation, primary job, and primary object;
- content and action priority, information architecture, and progressive disclosure;
- real copy or contract-valid examples;
- control semantics, state, focus, keyboard, pointer, touch, gesture, and assistive behavior;
- responsive, adaptive, window, orientation, and input-method changes relevant to the platform;
- data source, API or local model mapping, permission, validation, and unsupported claims;
- empty, slow, error, degraded, offline, conflict, long-content, and localization behavior;
- observable acceptance criteria.

Use domain methods such as `search-ux`, `form-design`, `state-machine`, or `responsive-design` only when the task needs them.

**Gate**: Another designer or engineer can implement correct behavior without guessing from a picture.

## Stage 4: Visual Direction And Design System

Start only after the relevant product and interaction decisions are stable.

- Reuse the target project's approved design system, tokens, components, platform conventions, and brand context.
- For a materially new direction, explore complete representative surfaces and critical states, not a hero or isolated card.
- Record typography, color roles, spacing, density, container model, interaction states, motion, imagery, and responsive rules.
- Keep hierarchy effective in grayscale before relying on color or effects.
- Treat generated images as visual references, never as behavior, data, accessibility, or implementation proof.
- Treat an explicit design-and-build request as authorization to proceed within its stated scope. Pause for acceptance only when the user requested staged approval, several materially different directions require a consequential choice, or the choice would be irreversible or expand scope. Existing approved patterns do not need repeated approval for scoped changes.

**Gate**: The visual direction solves identified product or hierarchy problems and does not imply unsupported capability.

## Stage 5: Implementation

Read the actual code, manifests, component library, conventions, contracts, and tests before editing.

- Preserve the discovered framework and platform. Do not default to React, web, Tailwind, a component library, or a new dependency.
- Reuse tokens, primitives, components, state models, and API clients.
- Keep page or screen composition separate from domain state, data orchestration, and reusable interaction behavior.
- Update affected types, contracts, tests, copy, error handling, analytics, and accessibility together.
- Use semantic controls and familiar platform patterns. Give icon-only actions an accessible name and discoverable explanation where needed.
- Avoid one-off override layers, duplicated state, fake success, hidden errors, internal identifiers, and prototype-only data in production.
- Keep changes within the user's requested scope and the project's ownership boundaries.

Load stack-specific implementation skills only after discovering the stack. For example, use React guidance only for a React codebase and SwiftUI/Figma guidance only for the relevant direction and platform.

## Stage 6: Runtime UX QA

Verify the current implementation on its real or equivalent target environment. Follow [qa-playbook.md](references/qa-playbook.md).

At minimum, where applicable:

- prove the source or artifact identity, current build, runtime target and dependencies, and relevant identity, permission, and data context;
- test the affected primary workflow and state transitions, not only static screenshots;
- test relevant devices, viewports, windows, orientations, themes, input methods, and assistive settings;
- cover keyboard or switch access, focus, semantics, contrast, text scaling, reduced motion, and target sizing;
- exercise empty, slow, error, degraded, offline, interruption, conflict, long content, localization, and large data as relevant;
- inspect platform diagnostics such as browser console, runtime logs, error overlays, layout overflow, crashes, or accessibility warnings;
- compare approved specification or concept with the implementation in a Fidelity Ledger.

Use sandbox, test, preview, or reversible data by default. Runtime QA does not authorize external communication, payment, publication, destructive deletion, production mutation, or permission changes. Perform those effects only with explicit user authority; otherwise stop before the committing action and record the untested boundary.

Record findings as P0-P3. Do not claim runtime verification or production readiness while P0/P1 remains, the tested artifact is stale, or a required path lacks runtime evidence. An implementation-only handoff may still be delivered when runtime access is unavailable, but it must name every unverified path and residual risk.

## Preserve Project Memory

Write durable product decisions, project context, contracts, unresolved assumptions, and QA evidence into the target repository's existing documentation system when the task authorizes changes. Prefer established files such as project instructions, PRDs, design context, ADRs, issue docs, or QA records.

Do not mutate this installed skill to remember a project. On the next project, discover context again.

## Output Discipline

- Use the user's and product's language, vocabulary, and level of detail.
- Separate fact, observation, inference, assumption, proposal, and approved decision.
- Attach evidence to consequential claims and state confidence where evidence is incomplete.
- Produce only artifacts needed for the current decision or delivery stage.
- Never fabricate user research, analytics, APIs, permissions, content, or test results.
- Surface source conflicts, stale artifacts, and residual risk instead of silently blending them.
- Stop at the user's requested boundary: design-only, review-only, implementation, or verification.
