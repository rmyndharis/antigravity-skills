# Changelog

All notable changes to this project are documented here.

## [Unreleased]

### Added
- `node:test` test suite covering the CLI, skill parsing, catalog generation, and the drift guard (`npm test`).
- `lib/skill-schema.js` as the single source of frontmatter field rules.
- `scripts/check-catalog-drift.js` (`npm run check:catalog`) — CI fails if committed catalog artifacts are stale.
- `install --force` to overwrite already-installed skills.
- `AG_SKILLS_DIR` environment variable to override the install destination (reported by `doctor`).
- Validator now checks that backticked referenced files (`resources/`, `references/`, `assets/`, `scripts/`) exist.
- `SECURITY.md` private vulnerability disclosure channel.

### Changed
- `install` now skips already-installed skills by default (use `--force` to overwrite) and reports an honest installed/skipped/failed summary.
- `install` exits non-zero when nothing could be installed; no longer prints "Installation complete!" on total failure.
- `update` exits non-zero on real failures (no installation, invalid name, not installed).
- Search scoring now also matches the catalog `triggers` field.
- Corrupt `bundles.json`/`aliases.json` now produce an explicit warning instead of degrading silently.
- `detectCategory` no longer treats generic "compliance" as `security`.
- `--write-baseline` now requires `--yes` and prints what it would grandfather.

### Fixed
- `listSkillIds`/`readSkill` no longer crash on a skill directory missing `SKILL.md`; `build-catalog` surfaces frontmatter parse warnings.
- Removed 228 dangling helper-file references across 165 skills.
- Removed dead code: `parseInlineList`/`stripQuotes` exports and the unreachable `name !== id` alias branch.
