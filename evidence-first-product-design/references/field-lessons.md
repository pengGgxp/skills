# Field Lessons

These reusable failure modes were distilled from production UI work. Apply them as questions, not as universal bans.

## 1. A Historical Artifact Becomes The Current Truth

Old specifications, screenshots, prototypes, and implementation notes often conflict. Record source class, date, approval state, build provenance, and what superseded what. Do not silently blend incompatible generations.

## 2. Roadmap Capability Leaks Into The Current Product

Visual ambition can smuggle future features into current navigation and copy. Establish version scope and explicit exclusions before designing. Protect important boundaries with tests where appropriate.

## 3. Surface-First Work Produces Generic Dashboards

When objects and task priority are unresolved, design tools fill the gap with equal cards, panels, and buttons. Resolve the model and primary job, then make hierarchy work in grayscale.

## 4. A Vague Container Absorbs Unrelated Objects

Labels such as “studio,” “hub,” or “control center” can hide missing object boundaries. Name the actual objects, modes, inputs, outputs, states, and destinations before creating a permanent container.

## 5. Mobile Becomes Desktop Columns Stacked Vertically

Responsive design is a change in places, priority, navigation, and input, not only dimensions. Decide what becomes a new screen, drawer, sheet, tab, or deferred action. Avoid proving mobile with an extremely long page.

## 6. Screenshots Pass While The Workflow Loses State

Static appearance cannot prove selection, navigation handoff, retry, focus, or persisted work. Exercise the task and verify the final object and state after every transition.

## 7. Historical Technology Becomes A Current Assumption

Old filenames and screenshots can outlive a framework or component library. Read manifests, imports, entry points, lockfiles, and tests before proposing implementation. Never infer a stack from visual appearance.

## 8. Global Overrides Become The Design System

Repeated selector overrides and `!important` layers create route and breakpoint regressions. Prefer scoped ownership, shared tokens, and component variants. Re-test every affected surface after a global change.

## 9. JSX Or Markup Extraction Pretends To Be Architecture

Moving visual markup without separating state, data, actions, and domain boundaries leaves the original monolith intact. Extract behavior and ownership, not only presentation.

## 10. Prototype Data Becomes A Production Claim

Example answers, metrics, generated artifacts, permissions, and selections are not implemented capabilities. Map every production claim to a real contract or label it clearly as a concept, disabled state, or roadmap item.

## 11. Errors Or Stale Builds Are Hidden For Screenshots

Do not hide error banners, use an old build, or point at a mismatched service to obtain a clean image. Prove commit/worktree, build command, URL, service target, account, data state, diagnostics, and recovery.

## 12. Trust Is Reduced To A Decorative Label

Labels such as “ready,” “secure,” “verified,” or “AI grounded” must map to current data, permissions, and behavior. Unknown state stays unknown; confidence does not become a fabricated percentage.

## 13. A Reading Or Public Surface Turns Into An Admin Or Social Dashboard

Protect the visitor's primary job and information boundary. Keep private navigation, internal identifiers, debug state, operational controls, and secondary engagement from competing with the main content.

## 14. Test Data Is Corrupted Before It Reaches The Product

Shell encodings, fixture pipelines, locale transforms, and serialization can corrupt multilingual content before the application receives it. Round-trip representative data through the real API/storage path before using it as visual evidence.

## 15. Ideal Content Passes While Real Boundaries Fail

Long titles, long unbroken words, rich text, large lists, partial errors, offline work, interruption, session expiry, and concurrent edits belong in the specification. Hardening is design input, not final polish.

## 16. A Full-Page Screenshot Replaces First-Viewport Judgment

Use viewport evidence for hierarchy and primary-task assessment. Use full-page captures only as supplemental evidence for page continuity, not as proof of usable interaction.

## 17. A Preview Transformer Is Reused As The Canonical Renderer

Summary, truncation, sanitization, or search-snippet helpers intentionally discard content. Do not use them to render canonical documents, messages, receipts, or records. Test semantic content such as links, images, ordered lists, code, tables, and long blocks end to end.

