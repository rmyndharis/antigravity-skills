# Antigravity Skill Vault

[![Buy Me a Coffee](https://img.shields.io/badge/Buy_Me_a_Coffee-support-FFDD00?logo=buymeacoffee&logoColor=black)](https://buymeacoffee.com/rmyndharis)

A curated collection of **Agent Skills** for **Google Antigravity**, ported from the [Claude Code Agents](https://github.com/wshobson/agents) repository.

This vault transforms the extensive Claude Code ecosystem into **Antigravity Skills**, providing your agent with repeatable workflows, domain expertise, and specialized tools.

---

## 🚀 Overview

This repository contains **300+ specialized skills** across software development, operations, security, and business domains. Each skill is a directory-based package that teaches Antigravity's agent how to perform specific tasks.

### What's Included?

The skills are derived from three types of Claude Code components, all unified into the Antigravity Skill format:

1.  **Domain Skills** (e.g., `k8s-manifest-generator`, `async-python-patterns`): Specialized knowledge packages.
2.  **Specialist Agents** (e.g., `backend-architect`, `security-auditor`): Persona-based instruction sets for complex reasoning.
3.  **Commands & Workflows** (e.g., `full-stack-orchestration-full-stack-feature`, `conductor-implement`): Structured, multi-step procedures.

---

## 📂 Categories

Skills are flattened in the `skills/` directory, but cover these broad categories:

### 💻 Development & Languages
- **Python**: `python-pro`, `fastapi-pro`, `async-python-patterns`, `uv-package-manager`
- **JavaScript/TypeScript**: `typescript-pro`, `react-modernization`, `nextjs-app-router-patterns`
- **Systems**: `rust-pro`, `golang-pro`, `memory-safety-patterns`
- **Mobile**: `frontend-mobile-development-component-scaffold`, `react-native-architecture`

### ☁️ Infrastructure & Operations
- **Kubernetes**: `kubernetes-architect`, `helm-chart-scaffolding`, `gitops-workflow`
- **Cloud**: `cloud-architect`, `terraform-module-library`, `cost-optimization`
- **CI/CD**: `cicd-automation-workflow-automate`, `github-actions-templates`, `gitlab-ci-patterns`

### 🔒 Security & Quality
- **Security**: `security-auditor`, `sast-configuration`, `security-scanning-security-hardening`
- **Code Quality**: `code-review-ai-ai-review`, `code-refactoring-refactor-clean`, `codebase-cleanup-tech-debt`
- **Testing**: `unit-testing-test-generate`, `tdd-workflows-tdd-cycle`, `e2e-testing-patterns`

### 🔄 Workflows & Architecture
- **Conductor**: `conductor-implement`, `context-driven-development` (Context-Driven Development)
- **Architecture**: `c4-architecture-c4-architecture`, `microservices-patterns`, `api-design-principles`
- **Orchestration**: `full-stack-orchestration-full-stack-feature`, `incident-response-incident-response`

### 📊 Data & AI
- **Data Engineering**: `data-engineer`, `spark-optimization`, `dbt-transformation-patterns`
- **AI/ML**: `ml-pipeline-workflow`, `prompt-engineering-patterns`, `rag-implementation`

---

## 🎯 Install Strategically (Token Efficient)

Antigravity loads metadata (name + description) from every installed skill at session start. More skills means more token usage and a higher chance of irrelevant auto-activation. Prefer targeted installs via search, tags, or bundles. `install --all` is advanced and not recommended for most projects.

## 🧭 Catalog & Discovery

This repo ships a generated catalog for discovery:

- `CATALOG.md` (human-readable index)
- `catalog.json` (machine-readable index used by the CLI)
- `bundles.json` (curated bundles)
- `aliases.json` (short names that map to long skill IDs)

Regenerate after adding/editing skills. This also synchronizes the manager skill into the dedicated plugin package:

```bash
npm run build:catalog
```

## 🛠️ How to Use

When a conversation starts, Antigravity loads the **metadata** (name & description) from all skills.
ANTIGRAVITY automatically activates a skill when your request matches its description.

**Examples:**

*   *"Help me design a REST API for a user service"* → Activates `api-design-principles` and `backend-architect`.
*   *"Scaffold a new FastAPI project"* → Activates `python-development-python-scaffold`.
*   *"Review this PR for security issues"* → Activates `security-scanning-security-hardening` or `security-auditor`.
*   *"Start a new feature track for login"* → Activates `conductor-new-track`.

---

The npm CLI provides two default installation scopes:

-   **Workspace scope** (project-specific): `<workspace-root>/.agent/skills/`
-   **Global scope** (`--global`, legacy IDE location): `~/.gemini/antigravity/skills/`

`AG_SKILLS_DIR` overrides either destination and expands a leading `~`. Antigravity supports the CLI's `.agent/skills/` workspace path for backward compatibility; the current default is `.agents/skills/`. Global locations vary by host: Antigravity CLI uses `~/.gemini/antigravity-cli/skills/`, while the app and current IDE use `~/.gemini/config/skills/`. See the official [skill locations](https://www.antigravity.google/docs/skills/).

For example, select the current workspace convention or the Antigravity CLI global directory:

```bash
AG_SKILLS_DIR=.agents/skills npx @rmyndharis/antigravity-skills install bash-pro
AG_SKILLS_DIR="$HOME/.gemini/antigravity-cli/skills" npx @rmyndharis/antigravity-skills install bash-pro
```

Use the same override with `installed`, `update`, and `doctor` when inspecting or changing that installation.

### Using `npx` (Recommended)

Run the published npm CLI from your intended workspace. Node.js and npm are required; cloning this repository is optional.

To add the manager skill itself:

```bash
npx @rmyndharis/antigravity-skills install antigravity-skills-manager
npx @rmyndharis/antigravity-skills doctor
npx @rmyndharis/antigravity-skills installed
```

Start a new Antigravity session, then invoke `/antigravity-skills-manager` followed by your request. You can also use the CLI directly without installing the manager skill.

**1. Search skills (recommended first):**

```bash
npx @rmyndharis/antigravity-skills search <query>
# Example:
npx @rmyndharis/antigravity-skills search kubernetes
```

**2. List available skills:**

```bash
npx @rmyndharis/antigravity-skills list
```

**3. Install a specific skill to your current project:**

```bash
npx @rmyndharis/antigravity-skills install <skill-name>
# Example:
npx @rmyndharis/antigravity-skills install bash-pro
```

An existing skill directory is skipped. Add `--force` only to replace it, including any local edits:

```bash
npx @rmyndharis/antigravity-skills install bash-pro --force
```

**4. Install by tag or bundle (targeted sets):**

```bash
# By tag
npx @rmyndharis/antigravity-skills install --tag kubernetes

# By bundle
npx @rmyndharis/antigravity-skills install --bundle core-dev
```

Available bundles: `core-dev`, `security-core`, `k8s-core`, `data-core`, `ops-core`.

**5. Install a skill globally:**

```bash
npx @rmyndharis/antigravity-skills install <skill-name> --global
# Example:
npx @rmyndharis/antigravity-skills install bash-pro --global
```

**6. Check installed skills:**

```bash
# List local specific skills
npx @rmyndharis/antigravity-skills installed

# List globally installed skills
npx @rmyndharis/antigravity-skills installed --global
```

**7. Update installed skills:**

```bash
# Update a specific skill
npx @rmyndharis/antigravity-skills update <skill-name>

# Update ALL installed skills
npx @rmyndharis/antigravity-skills update

# Update global skills
npx @rmyndharis/antigravity-skills update --global
```

`update` and `install --force` replace each selected skill directory completely, removing files deleted upstream and discarding local edits. Back up custom changes before replacing a skill. Ordinary `install` preserves an existing directory by skipping it.

Each replacement is prepared before the previous directory is moved. Copy failures preserve the existing installation; activation failures attempt to restore it. If restoration fails, the error identifies the retained backup. Interrupted installations can leave a hidden `.<skill-id>.install-lock` and `.<skill-id>.install-*` recovery directory beside the skill. Inspect and preserve any backup before cleanup, and remove a stale lock only after confirming that no installer is running. File or symlink destinations, source symlinks, and overlapping source/destination paths are rejected.

**8. Doctor / stats:**

```bash
npx @rmyndharis/antigravity-skills doctor
npx @rmyndharis/antigravity-skills stats
```

**9. Install ALL skills (advanced, not recommended):**

```bash
# To your current workspace
npx @rmyndharis/antigravity-skills install --all

# Globally
npx @rmyndharis/antigravity-skills install --all --global
```

> **Note:** Installing all skills increases token usage and can trigger unrelated skills. Prefer targeted installs.

Aliases are supported via `aliases.json` (for long skill names).

Example:

```bash
npx @rmyndharis/antigravity-skills install full-stack-feature
```

### Installing the npm CLI globally

To make the `ag-skills` executable available on your PATH:

```bash
npm install --global @rmyndharis/antigravity-skills
ag-skills install antigravity-skills-manager
```

`npm install --global` installs the executable. It does not select a global skill destination. Use `ag-skills install <skill-name> --global` for the CLI's legacy global skill directory, or `AG_SKILLS_DIR` for the location used by your Antigravity host.

### Using a source checkout

To run unpublished checkout changes reliably, run `npm ci` in the repository root, then invoke its CLI from your intended workspace. A package-name `npx` command resolves an installed package or the published release; it does not explicitly select this checkout:

```bash
node /absolute/path/to/antigravity-skills/bin/cli.js install antigravity-skills-manager
node /absolute/path/to/antigravity-skills/bin/cli.js installed
```

### Using `agy plugin install` (experimental)

Local plugin installation, enable/disable, and manager invocation have been verified in the Antigravity app on macOS with `agy 1.3.3`. With an npm package packed from this checkout and installed into an isolated workspace, the manager searched the catalog, installed and listed a skill, preserved local files during an ordinary reinstall, and updated only the selected skill. These results apply to the checkout payload, not to an earlier npm release. The npm and Python CLIs can also be used independently.

The dedicated plugin contains only the manager skill. Install its directory following the official [plugin installation instructions](https://www.antigravity.google/docs/plugins?tab=cli):

```bash
git clone https://github.com/rmyndharis/antigravity-skills.git
agy plugin validate ./antigravity-skills/plugins/antigravity-skills-manager
agy plugin install ./antigravity-skills/plugins/antigravity-skills-manager
```

Do not package the repository root as a plugin. Plugin skill discovery would include the entire vault under its `skills/` directory. The root intentionally has no plugin manifest.

Inspect the manager in the app's Customizations view, then invoke its displayed command:

```text
/antigravity-skills-manager search flutter
/antigravity-skills-manager install flutter-expert into this workspace
/antigravity-skills-manager list installed skills
```

The manager uses the npm CLI commands above, so Node.js and npm must be available. The plugin does not bundle a Python executable or register separate command aliases. The package contains one skill, `antigravity-skills-manager`. On `agy 1.3.3`, `agy plugin list --json` lists imported plugins without component names or enabled state; use the Customizations view to inspect activation and command discovery.

### Using Python

The `skills_cli.py` entrypoint uses only the Python standard library and supports `list`, `search`, `install`, and `installed`. Run the script from a checkout or the installed npm package; it is not copied alongside an installed manager skill:

```bash
python3 /path/to/antigravity-skills/skills_cli.py search flutter
python3 /path/to/antigravity-skills/skills_cli.py install flutter-expert
python3 /path/to/antigravity-skills/skills_cli.py installed
```

Python defaults to `~/.gemini/antigravity/skills/`; use `AG_SKILLS_DIR` for the host-specific destinations described above. Its `install` command replaces an existing installation, including local edits, and recognizes catalog aliases. It copies the local vault when available. A standalone copy retrieves the catalog, aliases, and skill files from one GitHub commit per command and requires network access. Use the npm CLI's `update` command for updates by name or in bulk.

### Manual Installation

If you prefer to clone the repository:

**Option A — Install to a workspace**

```bash
mkdir -p .agent/skills
cp -R /path/to/antigravity-skills/skills/<skill-name> .agent/skills/
```

**Option B — Install globally**

```bash
mkdir -p ~/.gemini/antigravity/skills
cp -R /path/to/antigravity-skills/skills/<skill-name> ~/.gemini/antigravity/skills/
```

> **Note:** After copying skills, restart your agent session so Antigravity re-detects them.

---

## ➕ Adding New Skills

1.  Create a folder: `skills/<skill-name>/`
2.  Add `SKILL.md` (required)
3.  (Optional) Add helpers: `scripts/`, `references/`, `assets/`

### Development checks

Install the Node dependencies and Python test dependencies before running the complete checks:

```bash
npm ci
python3 -m venv .venv
. .venv/bin/activate
python3 -m pip install -r requirements-test-assets.txt
npm run build:catalog
npm test
npm run test:python
npm run validate:skills -- --strict
npm run check:catalog
```

`npm run test:python` includes tests for shipped helper scripts and requires the packages in `requirements-test-assets.txt`. `npm run test:assets` runs only those helper-script tests. The Python CLI itself still has no third-party runtime dependencies. Activate the virtual environment before running these commands; on Windows, use `.venv\Scripts\Activate.ps1` in PowerShell.

Edit the canonical manager skill at `skills/antigravity-skills-manager/SKILL.md`. `npm run build:catalog` copies it into `plugins/antigravity-skills-manager/skills/antigravity-skills-manager/SKILL.md`; `npm run check:catalog` checks that the copy is current without changing it.

### Authoring Guidelines

- Keep `SKILL.md` concise; move long examples to `resources/` or `examples/`.
- Use narrow descriptions (for example: "Use when you need to ...") and include "Do not use" to reduce over-activation.
- Add a "Safety" section for skills that propose terminal or infrastructure changes.
- Regenerate catalog files with `npm run build:catalog`, then run `npm run prepublishOnly` for the complete local gate. CI runs the same Node, Python, validation, and catalog checks.
- CI runs strict validation using `validation-baseline.json` for existing gaps; new skills must include the required sections outside code examples. Helper paths under `resources/`, `references/`, `assets/`, `scripts/`, and `examples/` are checked in every Markdown file, including links and bold paths. Use paths relative to the skill directory and include the referenced files.
- The baseline is intentionally empty. Refreshing it (`node scripts/validate-skills.js --write-baseline --yes`) grandfathers — and thus silences — current soft violations, so avoid it unless you truly need to; without `--yes` the command only previews what it would grandfather.

### SKILL.md Template

```markdown
---
name: <skill-name>
description: <one sentence describing when to use this skill>
---

# <Skill Title>

## Use this skill when
- ...

## Do not use this skill when
- ...

## Instructions
1. ...
2. ...
```

---

## 🔐 Security

See [SECURITY.md](SECURITY.md) for safety expectations when writing skills that touch terminals or infrastructure.

---

## ☕ Support

If this vault saves you time, you can support its maintenance by buying me a coffee.

<a href="https://buymeacoffee.com/rmyndharis"><img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me a Coffee" height="50"/></a>

---

## 📜 License

MIT License. See [LICENSE](LICENSE) file for details.

Original content © [Claude Code Agents](https://github.com/wshobson/agents).
Ported to Antigravity Skills.
