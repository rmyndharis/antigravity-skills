---
name: antigravity-skills-manager
description: Searches, installs, updates, and lists skills from the Antigravity Skill Vault. Use when choosing or managing workspace or global skills through the npm CLI.
---

# Antigravity Skills Manager

Manage selected skills from `@rmyndharis/antigravity-skills` using Node.js and npm. This skill can be invoked as `/antigravity-skills-manager`, followed by a request such as `search flutter`.

## Use this skill when

- Finding skills for a specific language, framework, or workflow.
- Installing a requested skill or curated bundle into a workspace or global directory.
- Listing installed skills or updating an existing installation.

## Do not use this skill when

- Performing the development task described by another skill.
- Configuring unrelated plugins, model providers, or user credentials.

## Instructions

1. Identify the requested operation and installation scope. Run workspace commands from the intended project directory, not from this plugin's directory.
2. Use the npm CLI commands below. Node.js and npm must be available; `npx` may download the package when it is not cached.
3. Search when the user has described a need without selecting a skill. Show relevant IDs and descriptions so the user can choose. An explicitly requested skill or bundle already establishes the selection.
4. Check the resolved destination with `doctor` and list existing skills before replacing them. Apply `AG_SKILLS_DIR` consistently to discovery of installed skills, installation, and updates.
5. Report the command's actual installed, updated, skipped, and failed counts and the destination path. Do not report success after a nonzero exit status.

## Commands

List or search the catalog:

```bash
npx @rmyndharis/antigravity-skills list
npx @rmyndharis/antigravity-skills search flutter
```

Install a selected skill or bundle into the current workspace:

```bash
npx @rmyndharis/antigravity-skills install flutter-expert
npx @rmyndharis/antigravity-skills install --bundle core-dev
```

Inspect or update installed skills:

```bash
npx @rmyndharis/antigravity-skills doctor
npx @rmyndharis/antigravity-skills installed
npx @rmyndharis/antigravity-skills update flutter-expert
```

`install` skips an existing directory. `install --force` and `update` replace the entire selected skill directory, including local edits and files removed upstream. `update` without a skill name updates all recognized installed skills. Use replacement only when the user has authorized it.

## Installation scope

- The default workspace destination is `<current-directory>/.agent/skills/`. Antigravity also supports `.agents/skills/`; set `AG_SKILLS_DIR` to select it explicitly.
- `--global` selects `~/.gemini/antigravity/skills/`, the legacy global location supported by the standalone Antigravity IDE. Use the same flag with `installed` and `update` for that scope.
- `AG_SKILLS_DIR` overrides both workspace and global destinations. A leading `~` is expanded. Antigravity CLI uses `~/.gemini/antigravity-cli/skills/`; the app and current IDE use `~/.gemini/config/skills/`.

For example, install and inspect a global skill for Antigravity CLI:

```bash
AG_SKILLS_DIR="$HOME/.gemini/antigravity-cli/skills" npx @rmyndharis/antigravity-skills install flutter-expert
AG_SKILLS_DIR="$HOME/.gemini/antigravity-cli/skills" npx @rmyndharis/antigravity-skills installed
```

## Safety

- Install only skills or bundles requested by the user. Prefer a small relevant selection; `install --all` loads unnecessary metadata and can cause unrelated activation.
- Explain that replacement discards local edits before proceeding unless the user has already authorized that replacement. An ordinary install preserves existing directories by skipping them.
- Keep the destination separate from the package's source skills. File or symlink destinations and source overlap are rejected.
- Failed copies leave the previous installation intact. If activation or restoration fails, follow the reported recovery path and preserve any backup. Remove a stale installation lock only after verifying that no installer is running.
- The plugin contains this skill's instructions only. Use the npm commands above; do not assume that `skills_cli.py` or another executable is beside this file.

See the official [skill locations](https://www.antigravity.google/docs/skills/) and [plugin documentation](https://www.antigravity.google/docs/plugins?tab=cli) when selecting the host-specific scope.
