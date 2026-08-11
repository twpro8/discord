#!/usr/bin/env node
// Computes the base X.Y.Z version an alpha/beta desktop-release build should
// use, given the last real stable version and the commits that would land
// on `main` if the target ref were merged today.
//
// Why this exists instead of shelling out to `release-please release-pr
// --dry-run`: that command answers "what's new since the last release
// *reachable from this branch's own history*", which only works when
// dry-running against the actual release branch (main) itself. Run against
// `dev` (or any branch that hasn't been merged back from main since the
// last release), it either finds no reachable release and falls back to
// that branch's own possibly-stale `.release-please-manifest.json`, or (in
// `--local` mode) force-resets to the real `origin/main`, discarding
// exactly the unmerged commits we're trying to evaluate. Verified against
// this repo's real state 2026-08-11: `dev`'s manifest still reads 0.1.0
// even though v0.2.0 has already shipped from `main`, and dry-running
// against `dev` silently proposed "0.2.0" again — a version that's already
// released. Neither of release-please's modes can be made to answer "what
// if these commits, which don't exist on `main` yet, were merged there."
//
// So this script applies release-please's *actual* bump rule directly,
// verified by loading its real compiled classes (release-please@17.11.1's
// `DefaultVersioningStrategy`/`parseConventionalCommits`) and testing every
// commit type this repo's commit-msg hook allows, rather than trusting
// prose docs — which turned out to matter: this repo's own development.md
// claims "chore/docs/ci/style/test-only commits produce no release," but
// release-please's real `determineReleaseType()` falls through to a PATCH
// bump for *any* commit that parses as a Conventional Commit and isn't
// `feat`/breaking — chore, docs, style, refactor, test, build, ci, and
// revert all bump patch too, confirmed by direct testing against the real
// classes. The only way to get "no release" is when nothing parses as a
// Conventional Commit at all (e.g. only merge commits, or zero commits).
// That means development.md is inaccurate for this project's actual
// release-please behavior — out of scope to fix here, but flagged
// separately since it affects how the *existing* automation behaves too,
// not just this new script.
//
// This does not reimplement release-please's changelog generation, PR
// management, or manifest bookkeeping — only this one bump rule, scoped
// solely to picking the base version alpha/beta tags build on, and kept
// aligned with this repo's own `bump-minor-pre-major: true`
// (release-please-config.json).
//
// Usage: git log origin/main..<sha> --format='%B%x1e' \
//          | node compute-prerelease-version.mjs <base-version>
// Prints the next base X.Y.Z version on success, or the literal string
// "none" (exit 0) if nothing in the given commits is releasable.

const RECORD_SEPARATOR = "\x1e";
// This repo's commit-msg hook (scripts/check-commit-msg.sh) only ever lets
// these 10 types reach a real commit, so restricting to them here is exactly
// equivalent to release-please's own parser (which doesn't validate type
// against a fixed enum at all) for every commit this repo can ever produce.
const CONVENTIONAL_COMMIT =
  /^(feat|fix|chore|docs|test|refactor|style|perf|build|ci|revert)(\([^)]+\))?(!)?:\s+.+/;
const BREAKING_FOOTER = /^BREAKING[ -]CHANGE:/m;

const baseVersion = process.argv[2];
if (!baseVersion) {
  fail("usage: compute-prerelease-version.mjs <base-version>");
}

const versionMatch = /^(\d+)\.(\d+)\.(\d+)$/.exec(baseVersion);
if (!versionMatch) {
  fail(`base version "${baseVersion}" is not a plain X.Y.Z semver`);
}
const [, majorStr, minorStr, patchStr] = versionMatch;
const base = {
  major: Number(majorStr),
  minor: Number(minorStr),
  patch: Number(patchStr),
};

const input = await readStdin();
const records = input.split(RECORD_SEPARATOR).map((r) => r.trim()).filter(Boolean);

let highestBump = "none"; // none < patch < minor < major
for (const record of records) {
  const subject = record.split("\n", 1)[0];
  const match = CONVENTIONAL_COMMIT.exec(subject);
  if (!match) continue; // not a conventional-commit subject (e.g. a merge commit) — not releasable on its own

  const [, type, , bang] = match;
  const isBreaking = Boolean(bang) || BREAKING_FOOTER.test(record);

  let bump;
  if (isBreaking) {
    bump = "major";
  } else if (type === "feat") {
    bump = "minor";
  } else {
    // Matches DefaultVersioningStrategy.determineReleaseType's fallthrough:
    // any other recognized, non-breaking, non-feat type still bumps patch.
    bump = "patch";
  }

  if (rank(bump) > rank(highestBump)) highestBump = bump;
}

if (highestBump === "none") {
  process.stdout.write("none\n");
  process.exit(0);
}

// bump-minor-pre-major: true (release-please-config.json) — prior to the
// project's first major release, a breaking change bumps minor, not major.
if (highestBump === "major" && base.major === 0) {
  highestBump = "minor";
}

const next =
  highestBump === "major"
    ? { major: base.major + 1, minor: 0, patch: 0 }
    : highestBump === "minor"
      ? { major: base.major, minor: base.minor + 1, patch: 0 }
      : { major: base.major, minor: base.minor, patch: base.patch + 1 };

process.stdout.write(`${next.major}.${next.minor}.${next.patch}\n`);

function rank(bump) {
  return { none: 0, patch: 1, minor: 2, major: 3 }[bump];
}

function fail(message) {
  console.error(`compute-prerelease-version: ${message}`);
  process.exit(1);
}

function readStdin() {
  return new Promise((resolve, reject) => {
    let data = "";
    process.stdin.setEncoding("utf8");
    process.stdin.on("data", (chunk) => (data += chunk));
    process.stdin.on("end", () => resolve(data));
    process.stdin.on("error", reject);
  });
}
