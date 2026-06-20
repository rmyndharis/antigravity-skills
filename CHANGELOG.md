# Changelog

All notable changes to this project are documented here. This project adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]

## [1.2.0] - 2026-06-21

### Added
- `article-illustrations` skill — generates hand-drawn 16:9 article illustrations in the Grav whiteboard-sketch style, turning article concepts into memorable visuals with a recurring floating character, sparse annotations, and absurd metaphors. (Contributed via #8.)

## [1.1.0] - 2026-06-14

### Added
- `search`, `doctor`, and `stats` commands now reach `npx` users (the initial `1.0.0` build shipped without them).
- `install --force` to overwrite already-installed skills.
- `AG_SKILLS_DIR` environment variable to override the install destination for `install`/`installed`/`update`/`doctor` (expands a leading `~`; `doctor` reports the resolved override).
- `node:test` suite covering the CLI, skill parsing, catalog generation, and the drift guard (`npm test`), wired into CI.
- `lib/skill-schema.js` as the single source of frontmatter field rules.
- `scripts/check-catalog-drift.js` (`npm run check:catalog`) — fails if the committed catalog artifacts are stale; runs in CI.
- Validator now checks that backticked referenced files (`resources/`, `references/`, `assets/`, `scripts/`, `examples/`) exist; illustrative paths inside fenced code blocks are ignored.
- `SECURITY.md` private vulnerability disclosure channel.
- This `CHANGELOG.md`.

### Changed
- `install` skips already-installed skills by default (use `--force` to overwrite) and prints an honest installed/skipped/failed summary; it now exits non-zero on any failure.
- `update` exits non-zero on real failures (no installation found, invalid name, not installed).
- `installed` labels its output as an `AG_SKILLS_DIR override` when that environment variable is set.
- Search scoring now also matches the catalog `triggers` field.
- Corrupt `bundles.json`/`aliases.json` now produce an explicit warning instead of degrading silently.
- `detectCategory` no longer treats a generic "compliance" mention as `security` (re-categorized 5 skills).
- `--write-baseline` now requires an explicit `--yes` and prints what it would grandfather.
- CI runs `npm test`, `STRICT=1 npm run validate:skills`, and `npm run check:catalog` (with npm dependency caching).

### Fixed
- `listSkillIds`/`readSkill` no longer crash on a skill directory missing `SKILL.md`; `build-catalog` surfaces frontmatter parse warnings instead of swallowing them.
- Removed all dangling helper-file references (including `examples/`) across the skill corpus and pruned the empty resource/example headings left behind.
- `normalize-frontmatter` deduplicates metadata at token granularity (no duplicates for comma-containing values); `validate-skills` and `normalize-frontmatter` now share a single frontmatter field-set.
- Removed dead code: the `parseInlineList`/`stripQuotes` exports and the unreachable `name !== id` alias branch.

[Unreleased]: https://github.com/rmyndharis/antigravity-skills/compare/v1.2.0...HEAD
[1.2.0]: https://github.com/rmyndharis/antigravity-skills/releases/tag/v1.2.0
[1.1.0]: https://github.com/rmyndharis/antigravity-skills/releases/tag/v1.1.0
