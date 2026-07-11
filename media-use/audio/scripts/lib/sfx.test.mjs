// Modified from heygen-com/hyperframes v0.7.52: tests the explicit local SFX library and its safety checks.
import { test } from "node:test";
import assert from "node:assert/strict";
import { mkdtempSync, mkdirSync, writeFileSync, existsSync, rmSync } from "node:fs";
import { join } from "node:path";
import { tmpdir } from "node:os";
import { resolveSfx } from "./sfx.mjs";

// A caller-supplied local library must include both its manifest and audio files.
// These tests lock in the safe behavior: a present file is copied and referenced;
// malformed metadata, missing files, and path traversal yield anomalies without
// dangling or out-of-directory writes.

async function withDirs(fn) {
  const root = mkdtempSync(join(tmpdir(), "hf-sfx-"));
  const libDir = join(root, "lib");
  const projDir = join(root, "proj");
  mkdirSync(libDir, { recursive: true });
  mkdirSync(projDir, { recursive: true });
  try {
    // `await` is load-bearing: without it the finally cleanup runs before the
    // async test body resolves, deleting the temp dir mid-assertion.
    return await fn({ libDir, projDir });
  } finally {
    rmSync(root, { recursive: true, force: true });
  }
}

test("local library: copies and references a present licensed file", async () => {
  await withDirs(async ({ libDir, projDir }) => {
    writeFileSync(
      join(libDir, "manifest.json"),
      JSON.stringify({ whoosh: { file: "whoosh.mp3", duration: 0.8 } }),
    );
    writeFileSync(join(libDir, "whoosh.mp3"), "ID3-fake-bytes");
    const { sfx, anomalies } = await resolveSfx({
      cues: [{ id: "s1", name: "whoosh" }],
      heygenOK: false,
      hyperframesDir: projDir,
      sfxLibDir: libDir,
    });
    assert.equal(sfx.length, 1);
    assert.equal(sfx[0].file, "assets/sfx/whoosh.mp3");
    assert.equal(sfx[0].source, "local");
    assert.ok(existsSync(join(projDir, "assets/sfx/whoosh.mp3")), "mp3 copied into project");
    assert.equal(anomalies.length, 0);
  });
});

test("local library: a matched-but-missing file yields an anomaly and no dangling entry", async () => {
  await withDirs(async ({ libDir, projDir }) => {
    // Manifest names whoosh.mp3, but the mp3 was never shipped (the reported bug).
    writeFileSync(
      join(libDir, "manifest.json"),
      JSON.stringify({ whoosh: { file: "whoosh.mp3", duration: 0.8 } }),
    );
    const { sfx, anomalies } = await resolveSfx({
      cues: [{ id: "s1", name: "whoosh" }],
      heygenOK: false,
      hyperframesDir: projDir,
      sfxLibDir: libDir,
    });
    assert.equal(sfx.length, 0, "no dangling entry for a file that was never copied");
    assert.equal(anomalies.length, 1);
    assert.match(anomalies[0], /missing from the local SFX library/);
    assert.ok(!existsSync(join(projDir, "assets/sfx/whoosh.mp3")), "nothing copied");
  });
});

test("local library: a non-object manifest yields an anomaly instead of throwing", async () => {
  await withDirs(async ({ libDir, projDir }) => {
    writeFileSync(join(libDir, "manifest.json"), "null");
    const { sfx, anomalies } = await resolveSfx({
      cues: [{ id: "s1", name: "whoosh" }],
      heygenOK: false,
      hyperframesDir: projDir,
      sfxLibDir: libDir,
    });
    assert.equal(sfx.length, 0);
    assert.deepEqual(anomalies, ["local SFX manifest must be a JSON object - all cues dropped"]);
  });
});

test("local library: traversal paths are rejected and never copied", async () => {
  await withDirs(async ({ libDir, projDir }) => {
    const outside = join(libDir, "..", "outside.mp3");
    writeFileSync(outside, "ID3-outside");
    writeFileSync(
      join(libDir, "manifest.json"),
      JSON.stringify({ whoosh: { file: "../outside.mp3", duration: 0.8 } }),
    );
    const { sfx, anomalies } = await resolveSfx({
      cues: [{ id: "s1", name: "whoosh" }],
      heygenOK: false,
      hyperframesDir: projDir,
      sfxLibDir: libDir,
    });
    assert.equal(sfx.length, 0);
    assert.ok(anomalies.some((message) => /manifest entry "whoosh" is invalid/.test(message)));
    assert.ok(!existsSync(join(projDir, "assets", "outside.mp3")));
    assert.ok(!existsSync(join(projDir, "outside.mp3")));
  });
});

test("local library: coercible duration strings are rejected without throwing", async () => {
  await withDirs(async ({ libDir, projDir }) => {
    writeFileSync(
      join(libDir, "manifest.json"),
      JSON.stringify({ whoosh: { file: "whoosh.mp3", duration: "0.8" } }),
    );
    writeFileSync(join(libDir, "whoosh.mp3"), "ID3-fake-bytes");
    const { sfx, anomalies } = await resolveSfx({
      cues: [{ id: "s1", name: "whoosh" }],
      heygenOK: false,
      hyperframesDir: projDir,
      sfxLibDir: libDir,
    });
    assert.equal(sfx.length, 0);
    assert.ok(anomalies.some((message) => /manifest entry "whoosh" is invalid/.test(message)));
  });
});
