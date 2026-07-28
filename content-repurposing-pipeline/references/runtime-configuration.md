# Runtime Configuration

Use one user-selected content workspace. The workspace stores personal content and state; reusable code, templates, and the dashboard stay inside the Skill. The workspace does not need to be a Git repository.

## Workspace Selection

Resolve the workspace in this order:

1. A workspace path explicitly supplied in the current request or through `--workspace`.
2. A configuration path explicitly supplied in the current request or through `--config`.
3. `<skill-directory>/.content-pipeline.yaml`.
4. `CONTENT_PIPELINE_CONFIG` only when the Skill-local file is absent.

Do not guess a workspace from the current directory, neighboring repositories, runtime workspaces, or home folders.

The tracked `.content-pipeline.example.yaml` is a template. Create the machine-specific `.content-pipeline.yaml` beside `SKILL.md`; it remains ignored by Git.

If neither an explicit workspace nor a complete configuration exists, stop and say:

```text
Content pipeline is not configured. Provide a content workspace or create
<skill-directory>/.content-pipeline.yaml from <skill-directory>/.content-pipeline.example.yaml
and set content_workspace.
```

## Schema

```yaml
schema_version: "3.0"
content_workspace: "D:/path/to/content-workspace"
```

Resolve a relative `content_workspace` against the configuration file directory. Reject placeholders, filesystem roots, and any workspace inside the Skill directory.

The runtime scripts temporarily accept the previous `schema_version: "2.0"` and its `content_repository` path so an existing installation can migrate without interruption. Do not create new version 2 configurations, and do not require its old repository identity fields.

## Initialization

Initialize a new workspace with:

```text
python -B scripts/init_workspace.py --workspace <path>
```

This creates only `articles/`, `platforms/`, `shared/`, and `dashboard/data.json`. It does not initialize Git, copy dashboard code, or overwrite existing state.

## Dashboard

Start the bundled read-only dashboard with:

```text
python -B scripts/serve_dashboard.py --workspace <path> --port 4174
```

The server binds to loopback and exposes only the bundled dashboard plus workspace files below `dashboard/data.json`, `articles/`, `platforms/`, and `shared/`.

## Privacy And Portability

Installing or junctioning the whole Skill directory brings the workflow rules, templates, dashboard, and scripts to another machine. Configure or explicitly select a user-owned workspace on that machine; never place personal articles under the Skill directory.

Git, a private remote, cloud sync, or another backup method may be used for the workspace, but none is required by the Skill. When a remote stores personal notes, keep it private. Never put credentials or access tokens in configuration.
