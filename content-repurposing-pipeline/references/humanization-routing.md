# Chinese Prose Editing Route

Use this reference for Chinese master articles and Chinese platform versions. Natural Chinese is an editorial quality target inside the existing QA loop, not a separate publication stage and not an attempt to defeat AI detectors.

## Route Internally

The user invokes `$content-repurposing-pipeline`. The pipeline internally uses `$edit-article-spine`; do not require the user to name, index, or separately invoke it.

This route is the Chinese configuration of that one editorial pass. Do not run another full-text humanizer before or after it. Overlapping rewrites can erase the author's choices, move factual qualifiers, and make every platform sound alike.

Run it after the fact-supported master is structurally complete and before independent master review. Run one `targeted` pass after each material Chinese platform adaptation because destination rhythm, heading density, formality, and link behavior differ.

Skip verbatim quotations, code, commands, fixed tables, metadata, and text the user asks to preserve exactly. Do not rewrite an already natural passage because it contains one possible signal. Act only on clustered patterns that make the prose empty, inflated, repetitive, uniformly paced, or unlike an authorized user sample.

## Input Contract

Provide:

- the exact target text and whether it is a master or a named platform version;
- intended reader, genre, destination profile, and desired formality;
- verified source summary and the temporary semantic boundary;
- an authorized sample of the user's own writing when available;
- protected facts, numbers, quotations, citations, links, code, commands, image references, terminology, legal meaning, and material uncertainty.

Do not use another person's prose as a voice sample unless the user explicitly authorizes style analysis. High-level traits may inform the edit, but do not impersonate a living author.

## One Editing Pass

1. Diagnose the strongest clustered problems. When AI-like prose is part of the request or clearly material, load `$edit-article-spine`'s `references/ai-patterns.md`. Check especially generic openings, repeated conclusions, abstract importance claims, vague attribution, uniform paragraph shapes, excessive symmetric lists, mechanical transitions, and repeated disclaimers.
2. Choose the editing mode from the text, not from a fixed recipe. Use `rebuild` when the central claim, progression, or section order is broken; use `targeted` when the spine is sound or the text has already been adapted for a platform.
3. Produce one faithful revision. Prefer supplied specifics, direct subjects and verbs, meaningful paragraph variation, and explicit trade-offs. Keep lists when they genuinely help scanning or execution.
4. Ask what still reads like interchangeable template prose, then correct only those residual patterns.
5. Verify every sentence against the protected elements. Restore any lost qualifier, citation, link, step, warning, technical term, or intentional image reference.

One diagnosis, one revision, and one self-check is the default. Repeat only when the independent reviewer identifies a concrete remaining defect. The reviewer remains the single existing QA reviewer; this route does not create another review layer.

## Six-Dimension Self-Check

- **Specificity**: broad judgments have supplied evidence or are removed.
- **Directness**: subjects and actions are clear; meta-introductions do not delay the point.
- **Rhythm**: sentence and paragraph shapes vary because the content varies, not because randomness was added.
- **Voice**: real judgments, uncertainty, vocabulary, and quirks from authorized material remain visible.
- **Density**: repeated summaries, filler transitions, and decorative conclusions are removed.
- **Fidelity**: facts, qualifiers, citations, links, code, visuals, and instructions remain intact.

## Hard Boundaries

- Never invent anecdotes, experience, emotions, numbers, dates, quotations, sources, causal explanations, or product behavior.
- Never claim the result is undetectable or guaranteed to pass an AI detector.
- Do not force first-person language into technical, financial, legal, academic, or reference prose.
- Do not remove necessary risk disclosures merely because they repeat. Consolidate them only when meaning and placement remain adequate.
- Do not flatten deliberate author quirks, mixed feelings, uncertainty, humor, or domain vocabulary into generic clean prose.
- Do not treat correct grammar, formal vocabulary, Markdown headings, or a single connector as evidence of AI writing.

## Bounded Fallback

If `$edit-article-spine` cannot be loaded, apply the input contract, clustered-pattern diagnosis, one revision, six-dimension self-check, and factual regression directly. Then send the exact current draft to the normal independent reviewer.

Do not add a stage or JSON field for this fallback, and do not block only because the helper Skill is missing. When a concrete defect remains after review, keep a master at `article.stage: drafting_master` with `master.status: drafting` and `qa.master: needs_changes`; keep a platform version at `article.stage: adapting` with that platform's `status: drafting` and `qa.platforms.<platform>: needs_changes`. Record only the concrete defect in `blockers`.
