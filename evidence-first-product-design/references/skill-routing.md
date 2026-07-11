# Supporting Skill Routing

Load only skills that resolve the current uncertainty. Availability varies by host; if a named skill is unavailable, apply the same method directly and record the missing tooling. Never run the whole catalog for appearance of rigor.

## Foundation Layers

Load `layers-intro` before any other `layers-*` skill.

| Uncertainty | Preferred skill | Boundary |
|---|---|---|
| Which product layer is the bottleneck? | `layers-orient` | Keep the diagnostic short and choose one focus |
| What do users actually do? | `layers-observed-behaviour` | Plan or synthesize evidence; never invent research |
| Which domain concepts and terms matter? | `layers-domain` | Separate domain, user, product, and engineering language |
| Which needs or jobs matter? | `layers-user-needs`, `jobs-to-be-done` | Mark frequency and priority assumptions |
| Which needs should the product serve? | `layers-product-strategy` | Clarify bets and exclusions; do not overwrite requirements |
| What objects, relations, states, and terms exist? | `layers-conceptual-model` | Stay independent of UI and database schema |
| How do places, actions, and recovery connect? | `layers-interaction-flow` | Breadboard the job and edge paths |
| Are words, hierarchy, feedback, and accessibility coherent? | `layers-surface` | Use only after lower-layer decisions are stable enough |

## Focused UX Methods

| Problem | Preferred skill | Common companions |
|---|---|---|
| Navigation, taxonomy, wayfinding | `information-architecture` | conceptual model, user vocabulary |
| Search, filters, suggestions, zero results | `search-ux` | IA, state machine, density critique |
| Async or multi-mode behavior | `state-machine` | interaction flow, error handling |
| Forms and validation | `form-design` | error handling, accessibility |
| Prevention, errors, and recovery | `error-handling-ux` | state machine, loading states |
| Loading and progressive reveal | `loading-states` | performance evidence, error recovery |
| Cross-size or cross-input adaptation | `responsive-design` | platform conventions, interaction tests |
| Priority and action hierarchy | `visual-hierarchy` | grayscale scan, content priority |
| Cognitive load and density | `critique-information-density` | IA, progressive disclosure |
| Acceptance coverage | `design-qa-checklist` | runtime QA playbook |
| Tradeoff principles | `design-principles` | use only when principles resolve real conflicts |
| Competitive patterns | `competitive-analysis` | borrow patterns, not unsupported features or styling |
| Research validation | `usability-test-plan` | test open assumptions with representative tasks |

## Visual, Implementation, And Review

| Need | Possible skill | Use only when |
|---|---|---|
| Shared visual context and production UI | `frontend-design`, `setup` | The project lacks or needs current design context |
| Complete web concept and implementation | `build-web-apps:frontend-app-builder` | The target is web and behavioral specification is stable |
| React/Next.js performance patterns | `build-web-apps:react-best-practices` | The discovered codebase is React or Next.js |
| Web browser debugging and visual QA | `build-web-apps:frontend-testing-debugging`, `browser:control-in-app-browser` | A current runnable web surface exists |
| Holistic UX critique | `critique` | The user wants experience quality, hierarchy, IA, or cognitive-load findings |
| Measurable technical UI audit | `audit` | The user wants accessibility, responsive, theming, performance, or anti-pattern evidence |
| Focused accessibility remediation | `a11y` | Keyboard, screen reader, semantics, contrast, or motion needs changes |
| Resilience and edge cases | `harden` | Long content, localization, slow/offline, conflict, or large data can break the flow |
| Copy, motion, or performance | `clarify`, `animate`, `optimize` | The corresponding problem is demonstrated; these are not default phases |
| Bitmap visual exploration | `imagegen` | A complete visual reference is useful after behavioral decisions |

Do not use web skills for a native product, React guidance for Vue/Angular/Svelte, or browser checks as proof of native behavior. Use the target platform's tools, simulator, accessibility inspector, test framework, and design conventions.

## Figma

Use Figma only when the user requests a Figma artifact or supplies an authoritative Figma design.

- Write an approved screen or composed view: `figma:figma-generate-design` + `figma:figma-use`.
- Build variables, tokens, components, or variants: `figma:figma-generate-library` + `figma:figma-use`.
- Implement from Figma: `figma:figma-design-to-code`.
- Maintain component mappings: `figma:figma-code-connect`.
- Create a new file only after loading `figma:figma-create-new-file`.
- For SwiftUI in either direction, use `figma:figma-swiftui` with the direction-specific prerequisites.

If the host exposes different canonical identifiers, resolve the current skill catalog first. Never shorten a name in a way that skips a mandatory prerequisite.

Figma engineering does not validate product decisions. Stabilize the relevant model, flow, and specification first.

## Minimal Recipes

- New cross-surface flow: `layers-intro` + `layers-orient` + one bottleneck-layer skill + one domain method.
- Search: interaction flow + IA + `search-ux` + state machine.
- Complex form: conceptual model if needed + `form-design` + error handling + accessibility.
- Async AI or automation: conceptual model + interaction flow + state machine + error handling + hardening.
- Existing product review: context discovery + `critique` or `audit`, then only the focused methods needed by findings.
- Production web QA: critique + audit/hardening as relevant + browser testing.
- Native mobile redesign: interaction flow + state machine + responsive/adaptive thinking + platform-native accessibility and simulator QA.
