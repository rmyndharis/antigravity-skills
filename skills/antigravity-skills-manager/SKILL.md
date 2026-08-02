---
name: antigravity-skills-manager
description: Global skills manager for Google Antigravity. Explore, search, install, and manage 300+ agent skills from the rmyndharis/antigravity-skills catalog using pure stdlib CLI tools.
metadata:
  model: inherit
---

# 📦 Antigravity Skills Manager (`rmyndharis/antigravity-skills`)

The `antigravity-skills-manager` skill empowers Google Antigravity agents and users to discover, search, install, and manage over **300+ agent skills** from the open-source repository [`rmyndharis/antigravity-skills`](https://github.com/rmyndharis/antigravity-skills).

---

## Use this skill when

- Searching or exploring available agent skills in the `antigravity-skills` catalog.
- Installing a new skill into the global Antigravity configuration directory (`~/.gemini/antigravity/skills/<skill_id>/`).
- Listing locally installed skills to check system capabilities.
- Managing skill updates or auditing active agent tools.

## Do not use this skill when

- Performing general domain coding tasks that do not involve discovering or managing skills.
- Working on tasks outside the scope of Antigravity skill management.

---

## Instructions

- Prefer the `/skills-manager` (or `/skills`) slash commands. They work wherever the plugin is registered and need no path resolution.
- **`skills_cli.py` does not sit next to this file.** Installing this skill copies only `SKILL.md` into the skills directory; the script lives at the root of the checkout or npm package it came from — `agy plugin install` clones the repo, so it is at the clone root, and the npm package puts it at `node_modules/@rmyndharis/antigravity-skills/skills_cli.py`. Locate it before invoking it, and run it from there; `python3 skills_cli.py <cmd>` from this skill's own directory will not find it.
- If neither the repo nor the npm package is on disk, use `npx @rmyndharis/antigravity-skills` (the `ag-skills` CLI) instead — it covers the same four operations.
- Ensure skill installations save to `~/.gemini/antigravity/skills/<skill_id>/SKILL.md`, or to `AG_SKILLS_DIR` when that is set.
- All underlying commands must use standard Python library features (`urllib.request`, `json`, `os`, `sys`) without third-party dependencies.

---

## Safety

- `install` writes instructions that every future Antigravity session loads automatically. Confirm the skill id with the user before installing, and show them what `search` returned rather than picking on their behalf.
- `install` replaces an existing installation of the same skill id, discarding local edits under that directory. Say so before overwriting.
- Never install a skill id the user did not ask for, and never install one that is absent from the catalog.
- `install` writes under the resolved skills directory — `AG_SKILLS_DIR` when set, otherwise `~/.gemini/antigravity/skills`. Report the exact path back to the user rather than assuming the default.

---

## Purpose

Provide a unified, lightweight, pure standard-library interface for managing Google Antigravity agent skills across platforms (Windows, macOS, Linux).

---

## Available Commands & Usage

### 1. List Catalog Skills
Lists catalog skills with their categories and descriptions. An unfiltered listing is capped at the first 40 entries with a count of the remainder; add a filter to see a complete result set:
```bash
python3 skills_cli.py list
```
*Slash command equivalent*: `/skills-manager list` (or `/skills list`)

### 2. Search Catalog Skills
Filters skills by matching keywords in skill id, name, description, category, tags, or triggers. Multi-word queries match skills containing every term, in any order, and results are never truncated:
```bash
python3 skills_cli.py search <term>
```
*Example*:
```bash
python3 skills_cli.py search flutter
```
*Slash command equivalent*: `/skills-manager search flutter` (or `/skills search flutter`)

### 3. Install Skill
Installs the whole skill folder into the global skills directory (`~/.gemini/antigravity/skills/<skill_id>/`), copying from the catalog shipped beside the script when present and downloading from GitHub otherwise. Any existing installation of the same id is replaced. Exits non-zero if some files could not be retrieved:
```bash
python3 skills_cli.py install <skill_id>
```
*Example*:
```bash
python3 skills_cli.py install flutter-expert
```
*Slash command equivalent*: `/skills-manager install flutter-expert` (or `/skills install flutter-expert`)

### 4. List Installed Skills
Inspects local `~/.gemini/antigravity/skills/` directory and lists installed skills:
```bash
python3 skills_cli.py installed
```
*Slash command equivalent*: `/skills-manager installed` (or `/skills installed`)

---

## Local Installation Storage Path

Skill files installed via this skill are placed in:
`~/.gemini/antigravity/skills/<skill_id>/SKILL.md`

On Windows: `C:\Users\<user>\.gemini\antigravity\skills\<skill_id>\SKILL.md`

Newly installed skills are automatically discovered by Google Antigravity upon session initialization or refresh.
