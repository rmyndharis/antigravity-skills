---
name: skill-porter
description: >-
  Imports, converts, and optimizes external agent skills (written for Claude Code, Cursor, or generic LLMs) into native Google Antigravity plugins and skills. Translates legacy tool references, adapts subagents to Antigravity's parallel invoke_subagent arrays, and bundles plugin manifests. Use when the user asks to "import skill", "convert skill", "port skill", "optimize skill for antigravity", or provides a GitHub URL to a Claude Code skill.
---

# Antigravity Skill Porter & Optimizer

The **Skill Porter** autonomously bridges external agent ecosystems (Claude Code, Cursor, generic LLM agents) into native **Google Antigravity (AGY)** skills and plugins.

While platforms like Claude Code and Antigravity share the basic directory/`SKILL.md` layout, external skills typically contain hardcoded legacy tool names, single-agent sequential assumptions, and Claude-specific files. The Skill Porter translates these affordances and optimizes skills to leverage Antigravity's multi-agent runtime.

---

## Core Capabilities

1. **Direct GitHub Ingestion**:
   - Ingests public GitHub repositories (e.g. `https://github.com/owner/repo`) or local directories.
   - Automatically discovers `SKILL.md` and preserves auxiliary files (`references/`, `scripts/`, `examples/`).

2. **Deterministic Tool & Convention Mapping**:
   - Context files: `CLAUDE.md` / `claude.md` $\rightarrow$ `GEMINI.md`, `AGENTS.md`, `.agents/rules/`.
   - Command line: `Bash` $\rightarrow$ `run_command`.
   - File inspection: `Read` $\rightarrow$ `view_file`.
   - File search: `Glob` $\rightarrow$ `find_by_name`, `Grep` $\rightarrow$ `grep_search`.
   - File editing: `StrReplaceEditor` / `Edit` $\rightarrow$ `replace_file_content`.
   - Artifacts: File dumping $\rightarrow$ Antigravity markdown artifacts (`write_to_file`).

3. **Multi-Agent & Subagent Up-Leveling**:
   - Detects subagent workflows and injects Antigravity's parallel `invoke_subagent` batch arrays with Reactive Wakeup mechanics.

4. **Automated Plugin Packaging**:
   - Generates `plugin.json` manifests so imported skills can be turned on/off in the Antigravity settings UI.
   - Dual-installs to both `~/.gemini/config/plugins/<name>/` and `~/.gemini/config/skills/<name>/`.

5. **Diff & Verification (Dry-Run)**:
   - Evaluates changes and outputs an interactive unified diff before applying.

---

## Usage Instructions for the Agent

When the user asks to import or convert a skill from a URL or directory:

### Step 1: Preview with Dry Run
Execute the porter script with `--dry-run`:
```bash
python scripts/port_skill.py <url-or-path> --dry-run
```
Review the diff to ensure domain logic is preserved while tool references and scaffolding are properly upgraded.

### Step 2: Install the Skill
Run the command without `--dry-run`:
```bash
python scripts/port_skill.py <url-or-path>
```
To install into the current project workspace instead of globally, append `--workspace`.

### Step 3: Validate Installation
Verify the generated files:
- Manifest: `~/.gemini/config/plugins/<name>/plugin.json`
- Instructions: `~/.gemini/config/plugins/<name>/skills/<name>/SKILL.md`
Inform the user that the skill is ready to be invoked immediately.
