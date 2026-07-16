# Feishu Review Workspace

Use this reference only for an explicitly authorized Feishu review sync. The private run remains authoritative.

## Preconditions

Require all of the following before any external write:

1. The material visibility is `public` or `public_after_redaction`; never sync `private` material.
2. The current master has completed redaction and `disclosure_approved=approved`.
3. The disclosure approval SHA-256 equals the current master SHA-256.
4. A non-expired, non-revoked workspace authorization permits the requested operation.
5. The authorization is bound to the selected Feishu `account_id`, Bitable resources, folder, and ACL policy.
6. A stable operation ID has been written to the private run outbox before the API call.

`claims_verified` is also required before creating an audit snapshot or requesting factual review. `draft_approved` is required before treating a reviewed master as eligible for platform adaptation. Neither gate authorizes publication.

## Persistent Workspace Authorization

Copy `content-hub/templates/pipeline/feishu-review-workspace.yaml` to `<private-pipeline-root>/authorizations/<authorization_id>.yaml` and fill it only after explicit authorization. Keep this filled record outside Git and Feishu. Store resource identifiers, never credentials such as app secrets, access tokens, refresh tokens, or private keys.

Record:

- authorization ID, status, authorizer, time, scope, persistence, expiry, and revocation;
- Feishu `account_id` and optional tenant label;
- Bitable `app_token`, topic `table_id`, review-version `table_id`, folder token, and guide document ID;
- document ACL, link-sharing policy, and allowed reviewer identities.

For a one-run authorization, still use the same record shape, set `persistence: one_run`, and list the exact run in `authorized_run_ids`. Do not reuse it for another run.

## Source Of Truth And ACL

- Keep the private `master-article.md` and `run-record.yaml` authoritative.
- Publish only redacted, restricted read/comment mirrors to Feishu. Create a new immutable mirror for each source SHA-256 and move the topic-row pointer; never update an existing document body in place.
- Disable public link sharing. Grant the smallest reviewer set that satisfies the recorded scope.
- Store the effective ACL with each mirror and snapshot. Treat an unknown or widened ACL as a blocking disclosure risk.
- If the remote document revision differs from the recorded revision, set `drift_status: detected`, enqueue no further writes, and ask an operator to choose whether to discard the remote edit or manually apply an approved change to the private master.
- Require the Feishu tool to verify inherited ACL before writing content into a newly created empty document. If ACL cannot be read and confirmed, leave the document empty, record the failure, and stop.
- Use revision/ETag preconditions for any mutable Bitable pointer update. If the tool cannot perform a conditional update, never overwrite a document; serialize the run to one designated sync worker and stop on any concurrent or ambiguous table state.
- After any private-master edit, recalculate SHA-256 and invalidate affected approvals and all downstream review snapshots.

## Bitable Model

Use two tables so current status and immutable history are not conflated.

### Topic Table

Use one row per sanitized run, keyed by immutable `run_id`. Include:

- `选题`
- `运行 ID`
- `文章 ID`
- `状态`
- `可见性`
- `母稿镜像链接`
- `当前母稿 SHA-256`
- `最新审核版链接`
- `最新审核结论`
- `待确认项`
- `当前版本`
- `最后更新时间`
- `同步状态`
- `同步租约持有者`
- `同步租约过期时间`

Use topic statuses `草稿中`, `待审核`, `待确认`, `已通过`, and `已归档`. `已通过` means only that the recorded review version received favorable feedback.

### Review-Version Table

Append one row per immutable snapshot, keyed by `run_id + version + snapshot_sha256`. Include:

- `运行 ID`
- `版本`
- `审核目标类型`
- `Artifact ID`
- `平台`
- `源 Artifact SHA-256`
- `审核快照 SHA-256`
- `审核版链接`
- `远端 Revision`
- `审核结论`
- `审核人`
- `审核时间`
- `待确认项`
- `ACL`
- `Supersedes 版本`
- `创建时间`

Use `master` or `platform` as the review target type. A platform target is allowed only after the master gates permit adaptation; bind it to the platform manifest SHA-256. Never update an old review conclusion in place. Append a correction and set `Supersedes 版本` to the earlier immutable version.

## Version And Concurrency Rules

- Format versions as `v0001`, `v0002`, and so on. Start at `v0001`, allocate `max(recorded versions) + 1`, and never reuse a number after failure or cancellation.
- Acquire a per-run sync lease before allocating a version or changing the topic pointer. Store the opaque worker ID and an explicit expiry in the topic row using a conditional update. Renew only while the same worker still owns it.
- If conditional lease updates are unavailable, permit only the single worker named by the operator for that run. Detect another active operation or an ambiguous topic row and stop for manual reconciliation.
- Name documents deterministically with opaque identifiers, for example `review-<run_id>-<version>-<sha12>`. Do not put a private topic in the title.
- If document creation may have succeeded but the response or returned `doc_id` was lost, do not retry creation. Mark the outbox item `failed`, scan only the authorized folder for the exact deterministic title and creation window, and require manual reconciliation when the match is not unique.

## Idempotent Synchronization

Build operation IDs as:

```text
feishu:<action>:<run_id>:<artifact_sha256>:<version>
```

Before a call, append an outbox item with `status: pending`. After a resource is created, persist its returned record or document ID before making the next call. On retry, reuse the same operation ID and query by the immutable key before creating anything. Record `attempts`, `last_attempt_at`, `completed_at`, `remote_revision`, and the redacted error summary.

Use the outbox `action` as an exact authorization-scope value, and keep it identical to the action segment in `operation_id`. Also record `artifact_sha256` and `version` as separate fields so validation can compare them with the operation ID. When drift is detected, move active operations to `blocked_drift` before any further external call.

Supported outbox states are `pending`, `in_progress`, `completed`, `failed`, `blocked_drift`, and `cancelled`.

## Review Decisions

Bind feedback to the exact snapshot SHA-256 and record reviewer identity and time. A favorable Feishu review may inform a human approval, but it does not directly mutate `claims_verified`, `disclosure_approved`, `draft_approved`, or `publish_approved`. Record any gate decision separately in the private run with approver, time, scope, notes, and the applicable artifact SHA-256.

Never publish, send, commit, push, or broaden visibility as a side effect of review synchronization.

Keep authorization IDs, remote resource IDs, reviewer identities, ACL membership, revisions, version history, and outbox operations out of sanitized Content Hub records. Export only `feishu_review.status: redacted` with empty operational fields when a public audit record needs to indicate that a private projection exists.
