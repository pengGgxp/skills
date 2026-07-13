import { strict as assert } from "node:assert";
// Modified from heygen-com/hyperframes v0.7.55: tests the no-bundled-SFX fallback behavior.
import { test } from "node:test";
import { mkdtempSync, rmSync, existsSync } from "node:fs";
import { join, dirname } from "node:path";
import { tmpdir } from "node:os";
import { fileURLToPath } from "node:url";
import { resolveSfx } from "./lib/sfx.mjs";

// This adapted bundle intentionally omits the upstream standalone MP3 files.
// The default no-credential path must skip cues without dangling metadata.

const HERE = dirname(fileURLToPath(import.meta.url));
const sfxLibDir = join(HERE, "..", "assets", "sfx"); // same offset the engine uses

test("default install omits SFX assets and unresolved cues have no dangling entry", async () => {
  assert.ok(!existsSync(join(sfxLibDir, "manifest.json")), "manifest is intentionally absent");
  const dir = mkdtempSync(join(tmpdir(), "mu-audio-"));
  try {
    const { sfx, anomalies } = await resolveSfx({
      cues: [{ id: "1", name: "whoosh" }],
      heygenOK: false,
      hyperframesDir: dir,
      sfxLibDir,
    });
    assert.equal(sfx.length, 0);
    assert.ok(anomalies.some((a) => /no HeyGen credential and no local SFX library/.test(a)));
    assert.ok(!existsSync(join(dir, "assets", "sfx", "whoosh.mp3")));
  } finally {
    rmSync(dir, { recursive: true, force: true });
  }
});

test("missing local library is quiet when no SFX cues were requested", async () => {
  const dir = mkdtempSync(join(tmpdir(), "mu-audio-"));
  try {
    const { sfx, anomalies } = await resolveSfx({
      cues: [],
      heygenOK: false,
      hyperframesDir: dir,
      sfxLibDir,
    });
    assert.equal(sfx.length, 0);
    assert.deepEqual(anomalies, []);
  } finally {
    rmSync(dir, { recursive: true, force: true });
  }
});
