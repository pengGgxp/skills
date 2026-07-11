# Context Discovery

Discover the target project before deciding what its interface should be. Do not rely on filename conventions alone, and do not ask the user for facts already available in the workspace.

## Evidence Classes

Classify sources by the truth they can support.

| Class | Examples | Can establish | Cannot establish alone |
|---|---|---|---|
| User authority | Current request, explicit approvals, constraints | Requested scope, authorization, current choices | Product history or implementation state |
| Normative intent | PRD, policy, requirements, roadmap, ADR | Intended users, rules, version boundaries, obligations | Whether the feature actually works |
| Implementation | Code, schema, API client, types, tests, manifests | Existing capability, data shape, stack, permission enforcement | Whether the implemented product is desirable |
| Approved design | Accepted spec, design system, Figma, decision log | Settled interaction and visual decisions | Current implementation fidelity |
| Observational evidence | Research, analytics, support cases, usability results | What happened, frequency, user language | Causality without sufficient study |
| Runtime evidence | Current build, device, browser, logs, screenshots | What the tested version does now | Broader user behavior or untested states |
| Inspiration | Competitors, galleries, generated concepts | Candidate patterns and visual language | Product truth, scope, or feasibility |

Resolve conflicts within the relevant class. A newer production test can supersede an old screenshot; an implementation cannot silently overrule a current policy; a roadmap cannot be presented as shipped behavior.

## Discovery Order

1. Read the current user request and all repository instruction files in scope.
2. Locate product intent: PRDs, briefs, issue descriptions, policies, ADRs, roadmaps, and explicit exclusions.
3. Locate durable design context: audience, brand, design principles, tokens, component docs, Figma links, accepted concepts, and prior QA.
4. Inspect implementation truth: manifests, route or screen entry points, models, schemas, types, API clients, permissions, state stores, tests, and feature flags.
5. Inspect observational evidence: research, analytics definitions, support reports, interview notes, and usability findings.
6. Inspect current runtime evidence when the task concerns an existing interface.
7. Mark older prototypes, screenshots, generated concepts, and superseded specs as historical rather than current.

Use fast repository search first. Common starting points include:

```text
AGENTS.md, CONTRIBUTING.md, README, PRD*, docs/, design/, decisions/, ADR*
package manifests, build files, lockfiles, route/screen directories
schema, models, types, API clients, permissions, feature flags, tests
tokens, themes, Storybook, screenshots, QA reports, Figma/Code Connect files
```

These are search hints, not required names.

## Existing Product Versus Greenfield

For an existing product:

- Treat actual code and runtime as implementation truth.
- Identify compatibility, migration, and regression constraints.
- Preserve existing system patterns unless the task justifies changing them.
- Compare the newest approved design with the current implementation.

For greenfield work:

- Ask for the minimum missing product choices: target users, core job, product boundary, platform, and constraints.
- Label market, behavior, frequency, and preference statements as hypotheses until researched.
- Avoid choosing architecture or a design system before the task requires it.

For a design-only artifact with no repository:

- Build the Context Map from user-provided sources.
- State what implementation, contract, and runtime evidence is unavailable.
- Do not claim production feasibility or successful QA.

## Context Map

Capture only what affects the current task.

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

Record consequential facts and unresolved decisions.

- **Fact**: directly supported by a cited source.
- **Observation**: recorded behavior without an assumed cause.
- **Inference**: reasoned conclusion based on stated evidence.
- **Assumption**: necessary but unverified input.
- **Proposal**: a design choice awaiting approval.
- **Decision**: explicitly approved or already normative.
- **Gap**: required information or capability that does not exist.

## Ask Only When Needed

Ask the user when a missing answer would materially change product scope, audience, platform, policy, irreversible architecture, or a new visual direction. Continue with labeled assumptions when the choice is reversible and low risk.

Do not infer brand personality or audience only from code. First follow the repository's own documentation conventions and look for an established design-context source. Files such as `.better-web-ui.md` are only ecosystem-specific examples. If context is absent and visual work needs it, use an available setup/context skill or ask a focused question.

## Project Memory Boundary

Store durable findings in the target project, using its existing documentation conventions. A project may keep a product-design context file, but this skill must not require a specific filename.

Never copy project-specific facts back into the global skill. Generic improvements belong here; client facts, incidents, and decisions belong in the project.
