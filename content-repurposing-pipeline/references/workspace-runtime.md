# Workspace Runtime

Use the process working directory as the single content workspace. The workspace stores personal content and state; reusable code, templates, and the dashboard stay inside the Skill. The workspace does not need to be a Git repository.

## Workspace Resolution

Before reading or writing content, set the command working directory to the exact content workspace root. The bundled scripts resolve `Path.cwd()` and accept no workspace or configuration arguments.

Do not:

- read a Skill-local workspace configuration;
- use an environment variable to select a workspace;
- search parent, sibling, home, or neighboring repository directories;
- run a bundled script from an article subdirectory or from the Skill directory;
- ask the user to supply command-line workspace options.

Reject a filesystem root and any directory inside the Skill. If the active directory is clearly not the intended content workspace, stop before reading sources or writing files and ask the user to open the task from the content workspace.

## Initialization

From the new content workspace directory, run:

```text
python -B <skill-directory>/scripts/init_workspace.py
```

This creates only `articles/`, `platforms/`, `shared/`, and `dashboard/data.json`. It does not initialize Git, copy dashboard code, or overwrite existing state.

## Dashboard

From the content workspace root, run:

```text
python -B <skill-directory>/scripts/serve_dashboard.py
```

The server binds to loopback and exposes only the bundled dashboard plus workspace files below `dashboard/data.json`, `articles/`, `platforms/`, and `shared/`. The AI may select another local port with `--port` when the default is occupied; this does not change workspace resolution.

## Validation

From the content workspace root, run:

```text
python -B <skill-directory>/scripts/validate_pipeline.py
```

The validator reads only the current workspace and does not inspect or require Git.

## Privacy And Portability

Installing or junctioning the whole Skill directory brings the workflow rules, templates, dashboard, and scripts to another machine. Open the user's content directory as the active workspace on that machine; never place personal articles under the Skill directory.

Git, a private remote, cloud sync, or another backup method may be used for the workspace, but none is required by the Skill. When a remote stores personal notes, keep it private. Never place credentials or access tokens in the workspace.
