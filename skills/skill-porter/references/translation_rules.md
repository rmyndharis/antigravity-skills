# Translation & Optimization Reference

This document catalogs the exact translation rules and semantic upgrades performed when porting external agent skills to Google Antigravity.

---

## 1. Tool Mapping Table

| Claude / Generic Tool | Antigravity Native Tool | Description / Behavioral Note |
| :--- | :--- | :--- |
| `Bash` | `run_command` | Shell execution. Antigravity uses PowerShell (`pwsh`) on Windows and Bash on Unix. Background execution emits task notifications. |
| `Glob` | `find_by_name` | Fast file finding via `fd`. Uses `Pattern` and `SearchDirectory`. |
| `Grep` | `grep_search` | Pattern matching via ripgrep (`Query` and `SearchPath`). |
| `Read` / `cat` | `view_file` | Read files with exact line ranges (`StartLine`, `EndLine`). Truncates beyond 800 lines/46KB safely. |
| `Edit` / `StrReplace` | `replace_file_content` | Precision chunk replacement with exact character matching. |
| `Write` | `write_to_file` | File writing with artifact support and metadata schemas. |
| Subagents | `invoke_subagent` | Parallel array dispatch: `{ "Subagents": [ ... ] }`. Supports Reactive Wakeup. |

---

## 2. Context & Config File Mapping

| External Path | Antigravity Native Equivalent | Purpose |
| :--- | :--- | :--- |
| `CLAUDE.md`, `claude.md` | `GEMINI.md`, `AGENTS.md` | Workspace instructions and project architecture rules. |
| `.claude/rules/*.md` | `.agents/rules/*.md` | Granular hierarchical rules. |
| `.claude/skills/` | `.agents/skills/` (Workspace) or `~/.gemini/config/plugins/` (Global) | Custom skill storage locations. |

---

## 3. Execution Model Upgrades

### Single-Agent to Multi-Agent Parallelism
- **Sequential Spawning in Claude**: Claude skills often run subagents sequentially in chat loops.
- **Antigravity Array Dispatch**: Antigravity can dispatch an array of 5+ subagents simultaneously in a single tool call (`invoke_subagent`), cutting total latency dramatically.
- **Reactive Wakeup**: The primary agent does not poll. It ends its tool call and Antigravity awakens the agent automatically upon completion.

### Artifacts vs. Temp Files
- Instead of asking agents to dump logs or HTML files into arbitrary project directories, Antigravity uses structured markdown artifacts in `<appDataDir>\brain\<conversation-id>\...` created via `write_to_file`.
