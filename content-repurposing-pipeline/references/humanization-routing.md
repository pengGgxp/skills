# Humanization Routing

Use this reference for Chinese master articles and Chinese platform versions. Humanization is an editorial quality pass inside the existing QA loop, not a separate publication stage and not an attempt to defeat AI detectors.

## Internal Dependency

| Skill | Installed version | Pinned source | Purpose |
| --- | --- | --- | --- |
| `humanizer-zh-next` | `1.2.0` | `Hyacehila/humanizer-zh-next@cf08ea33910a094f6738cec01ed9c6fc19acc2f9` | Chinese AI-pattern diagnosis, voice calibration, faithful rewrite, and final self-check |

The dependency is resolved by its installed Skill name, not by loading a network URL during article production. Routing is automatic from the parent pipeline; user prompts must not be required to mention or invoke this dependency. Do not copy its full rules into this Skill. If it is unavailable, keep the draft in `drafting` or `needs_changes`, record a concise blocker, and use only this file's fallback checklist until the dependency is restored.

`humanizer-zh-next` already incorporates fixed MIT-licensed ideas from `blader/humanizer`, `op7418/humanizer-zh`, and `hardikpandya/stop-slop`. Do not install or run `stop-slop` as a second full rewrite pass by default; overlapping rewrites can erase the author's voice and create contradictory style rules.

## When To Run

Run after the fact-supported draft is structurally complete and before the independent content reviewer. Run it again after material platform adaptation because each platform has a different acceptable rhythm, heading density, and degree of informality.

Skip only for non-prose artifacts, verbatim quotations, code, tables whose wording is fixed, or a user request to preserve exact wording. Do not rewrite a natural passage merely because it contains one possible signal. Act on clustered patterns that make the text empty, inflated, repetitive, uniformly paced, or unlike the supplied author sample.

## Input Contract

Provide the target text together with:

- genre and destination platform;
- intended reader and desired level of formality;
- authorized source summary and immutable facts;
- the user's own writing sample when one is available and authorized;
- protected elements: citations, links, code, commands, image references, financial or legal qualifiers, and intentional terminology.

Do not use another person's writing as a voice sample unless the user explicitly authorizes style analysis. A public style may inform high-level traits, but the rewrite must not impersonate a living author.

## Required Pass

1. Classify the genre using the indexed Skill's genre matrix.
2. Identify the strongest clustered patterns, especially generic guide openings, repeated transitions, abstract claims, uniform paragraph shapes, excessive three-part lists, duplicated conclusions, vague attribution, and repeated disclaimers.
3. Produce one faithful revision. Prefer concrete supplied details, direct subjects and verbs, meaningful paragraph variation, and explicit trade-offs. Keep useful lists in tutorials and reference material.
4. Ask what still makes the revision read like generic AI prose, then correct only those residual patterns.
5. Verify every sentence against the source. Restore any lost qualifier, citation, link, step, warning, or technical term.

One diagnosis, one revision, and one self-check is the default. Repeat only when the independent reviewer identifies a concrete remaining problem. Do not create an endless humanize-and-rehumanize loop.

## Hard Boundaries

- Never invent anecdotes, personal experience, emotions, numbers, dates, quotations, sources, causal explanations, or product behavior.
- Never claim that the result is undetectable or guaranteed to pass an AI detector.
- Do not force first-person language into technical, financial, legal, academic, or reference prose.
- Do not remove necessary risk disclosures merely because they repeat. Consolidate them only when meaning and placement remain adequate.
- Do not flatten deliberate author quirks, mixed feelings, uncertainty, humor, or domain vocabulary into generic clean prose.
- Do not treat correct grammar, formal vocabulary, Markdown headings, or a single connector as evidence of AI writing.

## Fallback Checklist

When the indexed Skill cannot be loaded, check only these six dimensions and record the dependency blocker:

1. Specificity: every broad judgment has supplied evidence or is removed.
2. Directness: subjects and actions are clear; meta-introductions are gone.
3. Rhythm: paragraph and sentence shapes vary because the content varies, not because randomness was added.
4. Voice: real judgments and uncertainty from the source remain visible.
5. Density: repeated summaries, filler transitions, and decorative conclusions are removed.
6. Fidelity: facts, qualifiers, citations, links, code, visuals, and instructions remain intact.
