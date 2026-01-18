# Antigravity Skill Vault

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

Regenerate after adding/editing skills:

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

You can install skills in **two scopes**:

-   **Workspace scope** (project-specific): `<workspace-root>/.agent/skills/`
-   **Global scope** (available in all projects): `~/.gemini/antigravity/skills/`

### Using `npx` (Recommended)

You can easily install skills directly from the repository without cloning it manually.

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

### Authoring Guidelines

- Keep `SKILL.md` concise; move long examples to `resources/` or `examples/`.
- Use narrow descriptions (for example: "Use when you need to ...") and include "Do not use" to reduce over-activation.
- Add a "Safety" section for skills that propose terminal or infrastructure changes.
- Regenerate catalog files with `npm run build:catalog` and validate with `npm run validate:skills`.
- CI runs strict validation using `validation-baseline.json` for existing gaps; new skills must include the required sections.
- If you backfill existing skills, refresh the baseline with `node scripts/validate-skills.js --write-baseline`.

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

## 📜 License

MIT License. See [LICENSE](LICENSE) file for details.

Original content © [Claude Code Agents](https://github.com/wshobson/agents).
Ported to Antigravity Skills.
