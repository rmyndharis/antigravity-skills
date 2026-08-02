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

- Execute commands via `skills_cli.py` or through `/skills-manager` (or `/skills`) slash commands in the CLI chat interface.
- Ensure skill installations save to `~/.gemini/antigravity/skills/<skill_id>/SKILL.md`.
- All underlying commands must use standard Python library features (`urllib.request`, `json`, `os`, `sys`) without third-party dependencies.

---

## Safety

- `install` writes instructions that every future Antigravity session loads automatically. Confirm the skill id with the user before installing, and show them what `search` returned rather than picking on their behalf.
- `install` replaces an existing installation of the same skill id, discarding local edits under that directory. Say so before overwriting.
- Never install a skill id the user did not ask for, and never install one that is absent from the catalog.
- `install` writes only under the global skills directory; report the exact path back to the user.

---

## Purpose

Provide a unified, lightweight, pure standard-library interface for managing Google Antigravity agent skills across platforms (Windows, macOS, Linux).

---

## Available Commands & Usage

### 1. List Catalog Skills
Lists catalog skills with their categories and descriptions. An unfiltered listing is capped at the first 40 entries with a count of the remainder; add a filter to see a complete result set:
```bash
python skills_cli.py list
```
*Slash command equivalent*: `/skills-manager list` (or `/skills list`)

### 2. Search Catalog Skills
Filters skills by matching keywords in skill id, name, description, category, tags, or triggers. Multi-word queries match skills containing every term, in any order, and results are never truncated:
```bash
python skills_cli.py search <term>
```
*Example*:
```bash
python skills_cli.py search flutter
```
*Slash command equivalent*: `/skills-manager search flutter` (or `/skills search flutter`)

### 3. Install Skill
Installs the whole skill folder into the global skills directory (`~/.gemini/antigravity/skills/<skill_id>/`), copying from the catalog shipped beside the script when present and downloading from GitHub otherwise. Any existing installation of the same id is replaced. Exits non-zero if some files could not be retrieved:
```bash
python skills_cli.py install <skill_id>
```
*Example*:
```bash
python skills_cli.py install flutter-expert
```
*Slash command equivalent*: `/skills-manager install flutter-expert` (or `/skills install flutter-expert`)

### 4. List Installed Skills
Inspects local `~/.gemini/antigravity/skills/` directory and lists installed skills:
```bash
python skills_cli.py installed
```
*Slash command equivalent*: `/skills-manager installed` (or `/skills installed`)

---

## Local Installation Storage Path

Skill files installed via this skill are placed in:
`~/.gemini/antigravity/skills/<skill_id>/SKILL.md`

On Windows: `C:\Users\<user>\.gemini\antigravity\skills\<skill_id>\SKILL.md`

Newly installed skills are automatically discovered by Google Antigravity upon session initialization or refresh.
