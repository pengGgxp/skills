# Pipeline Contract

This contract defines the lightweight personal workflow stored in `dashboard/data.json`.

The file paths in this contract are relative to the user-selected content workspace. The Skill directory contains reusable rules, templates, scripts, and dashboard code only; it must never contain the user's articles or workflow state. A workspace may use Git, but Git is optional.

## Source Scope

- A source supplied in the current request or explicitly named by the user is authorized for that task.
- Ask before reading unrelated repositories, accounts, messages, logs, tickets, or saved data.
- Do not maintain expiring authorization records for ordinary local work.
- Never record secret values. Generalize sensitive details before external search or image generation.

## Article IDs And Paths

Use lowercase ASCII slugs. A date prefix is recommended for publishable articles:

```text
article_id: 2026-07-27-example-topic
master:     articles/2026-07-27-example-topic/master.md
platform:   platforms/blog/drafts/2026-07-27-example-topic/index.md
```

Use local timestamps with an explicit timezone when known.

## Dashboard Data

The top-level shape is:

```json
{
  "schema_version": "1.0",
  "updated_at": "2026-07-27T12:00:00+08:00",
  "articles": []
}
```

Each article uses:

```json
{
  "article_id": "2026-07-27-example-topic",
  "title": "Example title",
  "stage": "awaiting_master_review",
  "current_task": "Review the current mother draft.",
  "master": {
    "path": "articles/2026-07-27-example-topic/master.md",
    "status": "awaiting_review",
    "revision": 2,
    "approved_revision": null,
    "reviewed_at": ""
  },
  "qa": {
    "master": "passed",
    "visuals": "passed",
    "platforms": {}
  },
  "selected_platforms": [],
  "platforms": {},
  "visuals": {
    "status": "passed",
    "runtime_demo": "not_required",
    "note": ""
  },
  "blockers": [],
  "updated_at": "2026-07-27T12:00:00+08:00"
}
```

Optional `visuals.assets` items may record `{path, role, origin, source_url, rights, inspection, note}`. Keep this lightweight and include it only when it helps explain selected assets.

## Allowed States

Article stage:

- `idea`
- `drafting_master`
- `awaiting_master_review`
- `adapting`
- `awaiting_publish_review`
- `ready_to_publish`
- `published`
- `paused`
- `archived`

Master status:

- `drafting`
- `awaiting_review`
- `changes_requested`
- `approved`
- `rejected`

Platform status:

- `drafting`
- `awaiting_review`
- `changes_requested`
- `approved`
- `published`
- `skipped`

QA status:

- `not_run`
- `passed`
- `needs_changes`
- `not_recorded` for imported legacy work only

## State Transitions

```text
idea -> drafting_master -> awaiting_master_review
awaiting_master_review -> drafting_master          when changes are requested
awaiting_master_review -> adapting                 when approved and platforms are selected
adapting -> awaiting_publish_review                after platform QA
awaiting_publish_review -> adapting                when changes are requested
awaiting_publish_review -> ready_to_publish        when a current platform revision is approved
ready_to_publish -> published                      only after explicit publication
```

`paused` and `archived` may be entered from any non-published stage when accurately explained.

## Revision Semantics

- Start at revision `1`.
- Increment after a material body or selected-image edit.
- `approved_revision` must equal the current revision only while the item remains approved.
- A material edit clears stale approval and returns the item to review.
- Small metadata corrections that do not affect the reviewed content do not require a revision bump.

The revision is a personal workflow aid, not a cryptographic audit claim.

## Internal QA And Human Review

Use one independent review subagent by default at the master stage and a fresh one at the platform stage. Add a separate visual review only when image authenticity, privacy, or rights require specialist attention.

Review agents may recommend changes but may not create human decisions. Resolve actionable findings, rerun the reviewer, and store only the current `qa` result and concise blockers in JSON.

Human activity has two review moments:

1. Review the master. Approval may include platform selection.
2. Review each finished platform version for publication.

Platform selection is a production choice, not a third approval gate. Publication is a separate explicit action, not an approval side effect.

The bundled static dashboard may fetch and render the exact current Markdown referenced by `master.path` and each platform `path` for read-only inspection. Do not duplicate article bodies into workflow JSON, and do not treat opening or reading a preview as a decision. Use the Skill's `serve_dashboard.py` so the bundled interface and workspace files share one loopback origin; record a decision only after the user explicitly states it.

## Platform Versions

Each selected platform version contains `index.md`, `meta.yaml`, and `images/`. Start new versions from the Skill's `assets/templates/` files. `meta.yaml` stores descriptive and publication metadata only; workflow state stays in JSON.

Do not require an artifact manifest or publication checklist. Platform QA should still confirm:

- body and local images exist;
- links and commands are correct;
- title and structure fit the platform;
- product claims have an authentic relevant screenshot;
- selected images are legible and publishable;
- metadata and dashboard state agree.

## Stop Conditions

Record a blocker and stop the affected article or platform version when:

- the user has not authorized a required source;
- a material claim remains unsupported;
- credentials or confidential values cannot be removed;
- a required runtime demonstration is unavailable;
- an image does not match the function described;
- web-image publication rights are unknown;
- internal QA still has actionable findings;
- the current revision is not the approved revision;
- the user requests cancellation or pause.

Do not soften or hide a blocker merely to advance the status.
