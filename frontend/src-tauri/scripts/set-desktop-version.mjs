#!/usr/bin/env node
// Ephemeral version patch used only by the desktop-release workflow's
// alpha/beta build legs to stamp a computed prerelease version (e.g.
// 1.5.0-alpha.2) into the desktop bundle metadata and UI version string
// before `tauri build` runs. Never committed back — it edits the CI
// runner's own checkout. Stable releases skip this entirely: the
// checked-out tag's files already carry the real, release-please-committed
// version.
//
// Patches exactly the three non-canonical files release-please itself
// keeps in sync (see release-please-config.json's "extra-files"), minus
// backend/pyproject.toml, which the desktop build never reads.
//
// Fails loudly rather than silently building the wrong artifact: refuses
// to write unless it can find a well-formed, non-empty current version at
// the expected location in every file, and re-reads each file after
// writing to confirm the new value landed exactly as requested.

import { readFileSync, writeFileSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const version = process.argv[2];
if (!version) {
  fail("usage: set-desktop-version.mjs <version>");
}

const scriptDir = path.dirname(fileURLToPath(import.meta.url));
const srcTauriDir = path.resolve(scriptDir, "..");
const frontendDir = path.resolve(srcTauriDir, "..");

const CARGO_VERSION_LINE =
  /^(\[package\][\s\S]*?^version\s*=\s*")([^"]+)(")/m;

const targets = [
  {
    file: path.join(frontendDir, "package.json"),
    field: '"version"',
    readVersion: (text) => JSON.parse(text).version,
    withVersion: (text) => {
      const json = JSON.parse(text);
      json.version = version;
      return `${JSON.stringify(json, null, 2)}\n`;
    },
  },
  {
    file: path.join(srcTauriDir, "tauri.conf.json"),
    field: '"version"',
    readVersion: (text) => JSON.parse(text).version,
    withVersion: (text) => {
      const json = JSON.parse(text);
      json.version = version;
      return `${JSON.stringify(json, null, 2)}\n`;
    },
  },
  {
    file: path.join(srcTauriDir, "Cargo.toml"),
    field: "[package].version",
    readVersion: (text) => CARGO_VERSION_LINE.exec(text)?.[2],
    withVersion: (text) => {
      if (!CARGO_VERSION_LINE.test(text)) {
        return null;
      }
      return text.replace(CARGO_VERSION_LINE, (_match, before, _old, after) => {
        return `${before}${version}${after}`;
      });
    },
  },
];

for (const target of targets) {
  let original;
  try {
    original = readFileSync(target.file, "utf8");
  } catch (error) {
    fail(`cannot read ${target.file}: ${error.message}`);
  }

  const currentVersion = safely(() => target.readVersion(original));
  if (!currentVersion || typeof currentVersion !== "string") {
    fail(
      `${target.file}: could not find an existing non-empty ${target.field}, refusing to guess`,
    );
  }

  const updated = safely(() => target.withVersion(original));
  if (!updated) {
    fail(`${target.file}: failed to patch ${target.field}`);
  }
  writeFileSync(target.file, updated);

  const rewritten = readFileSync(target.file, "utf8");
  const verified = safely(() => target.readVersion(rewritten));
  if (verified !== version) {
    fail(
      `${target.file}: verification failed after write — expected ${target.field} to be "${version}", found "${verified}"`,
    );
  }

  console.log(`set-desktop-version: ${target.file}: ${currentVersion} -> ${version}`);
}

console.log(`set-desktop-version: all files patched to ${version}`);

function safely(fn) {
  try {
    return fn();
  } catch {
    return null;
  }
}

function fail(message) {
  console.error(`set-desktop-version: ${message}`);
  process.exit(1);
}
