<!-- Modified from heygen-com/hyperframes v0.7.55: documented the excluded SFX bundle and safe explicit local-library behavior. -->

# Sound effects (SFX)

Named sound effects are resolved by the shared audio engine (`scripts/audio.mjs` -> `scripts/lib/sfx.mjs`). The engine selects one provider for the whole request:

- **HeyGen credential present -> retrieve every cue** from HeyGen's audio library (`/v3/audio/sounds`, `type=sound_effects`, `min_score=0.4`). This is search-and-download, not generation. A local library is not consulted.
- **No credential and `--sfx-lib <dir>` provided -> use that local library.** The directory must contain a `manifest.json` and every audio file named by the manifest.
- **Neither available -> skip every cue.** Each skipped cue is recorded as a non-fatal anomaly, and no missing file is written to `audio_meta.json`.

This adapted bundle intentionally ships no SFX audio or manifest. See [`../assets/sfx/CREDITS.md`](../assets/sfx/CREDITS.md) for the redistribution decision. There is no `npx hyperframes sfx` command, and SFX is never generated.

## Cues — request → meta

Each line names the effects it wants: `lines[].sfx: ["whoosh", "ui click"]`. The engine flattens these into cues, resolves them per the switch, dedupes identical `(id, name)` pairs (the same effect named twice downloads/copies once), and writes `audio_meta.sfx[]`:

```jsonc
{
  "id": "3",                       // joins the cue to the caller's model (frame / scene / segment)
  "name": "whoosh",
  "file": "assets/sfx/whoosh.mp3", // downloaded or copied from a supplied library
  "source": "heygen" | "local",    // which route resolved it
  "offset_s": 0,                   // delay from the line's start
  "duration_s": 0.57,
  "volume": 0.35                   // SFX sit UNDER voice + BGM
}
```

A cue that matches nothing is **skipped** (recorded as an anomaly); SFX never blocks a render.

## HeyGen retrieval (credentialed)

`searchSounds(name, "sound_effects", { limit: 3, minScore: 0.4 })` → top hit → `assets/sfx/<slug>.mp3`. Results are ranked by `score` (each carries a presigned `audio_url`, `duration`, `description`). The floor is **0.4** because good SFX hits score ~0.5–0.67 — below the API's default `0.7`, which would silently drop most named cues (only whoosh/swoosh-family clears 0.7). `duration_s` comes from the result (else 1.0). Name effects concretely (`glass shatter`, not `dramatic sound`); a vague query returns a poor match.

## Optional local library (no credential)

Pass `--sfx-lib <dir>` to `audio/scripts/audio.mjs`. The directory must contain a manifest with this shape and the corresponding licensed files:

```json
{
  "whoosh": {
    "file": "whoosh.mp3",
    "duration": 0.8,
    "description": "Short transition"
  }
}
```

A cue resolves by manifest key, file basename, or slug. Each `file` must be a basename with a supported audio extension (`.flac`, `.m4a`, `.mp3`, `.ogg`, or `.wav`); absolute paths, traversal, nested paths, Windows device names, and unsafe filename characters are rejected. Before adding an entry to `audio_meta.json`, the engine verifies that the source file exists and copies it into the project's `assets/sfx/`. A missing manifest, missing file, malformed manifest, invalid entry, or unknown cue produces an anomaly and no dangling entry. The caller is responsible for ensuring that every supplied file may be used and redistributed in the rendered output.

## Rules

- **Volume ~0.35.** SFX must sit under narration and BGM, not fight them.
- **No match → skip, don't fail.** A missing effect logs an anomaly and moves on; never a render blocker.
- **Retrieval or an explicit local library - never generation.** Search HeyGen by text, or match a name against the caller-supplied manifest.
- **One asset per distinct name.** Reuse across lines is deduped to a single download/copy, many cues.
- **The switch is global, not per cue.** With a credential, retrieval handles every cue. Without one, only entries in an explicitly supplied local library can resolve.
