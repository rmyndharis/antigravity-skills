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

Skills are flattening into the `skills/` directory, but cover these broad categories:

### 💻 Development & Languages
- **Python**: `python-pro`, `fastapi-pro`, `async-python-patterns`, `uv-package-manager`
- **JavaScript/TypeScript**: `typescript-pro`, `react-modernization`, `nextjs-app-router-patterns`
- **Systems**: `rust-pro`, `golang-pro`, `memory-safety-patterns`
- **Mobile**: `frontend-mobile-development`, `react-native-architecture`

### ☁️ Infrastructure & Operations
- **Kubernetes**: `kubernetes-architect`, `helm-chart-scaffolding`, `gitops-workflow`
- **Cloud**: `cloud-infrastructure`, `terraform-module-library`, `cost-optimization`
- **CI/CD**: `cicd-automation`, `github-actions-templates`, `gitlab-ci-patterns`

### 🔒 Security & Quality
- **Security**: `security-auditor`, `sast-configuration`, `owasp-prevention`
- **Code Quality**: `code-review-ai`, `code-refactoring`, `technical-debt-management`
- **Testing**: `unit-testing`, `tdd-workflows`, `e2e-testing-patterns`

### 🔄 Workflows & Architecture
- **Conductor**: `conductor-implement`, `context-driven-development` (Context-Driven Development)
- **Architecture**: `c4-architecture`, `microservices-patterns`, `api-design-principles`
- **Orchestration**: `full-stack-orchestration`, `incident-response`

### 📊 Data & AI
- **Data Engineering**: `data-engineer`, `spark-optimization`, `dbt-transformation-patterns`
- **AI/ML**: `ml-pipeline-workflow`, `prompt-engineering-patterns`, `rag-implementation`

---

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

**1. List available skills:**

Check which skills are available in the vault before installing:

```bash
npx @rmyndharis/antigravity-skills list
```

**2. Install a specific skill to your current project:**

```bash
npx @rmyndharis/antigravity-skills install <skill-name>
# Example:
npx @rmyndharis/antigravity-skills install bash-pro
```

**3. Install a skill globally:**

```bash
npx @rmyndharis/antigravity-skills install <skill-name> --global
# Example:
npx @rmyndharis/antigravity-skills install bash-pro --global
```

**4. Check installed skills:**

```bash
# List local specific skills
npx @rmyndharis/antigravity-skills installed

# List globally installed skills
npx @rmyndharis/antigravity-skills installed --global
```

**5. Update installed skills:**

```bash
# Update a specific skill
npx @rmyndharis/antigravity-skills update <skill-name>

# Update ALL installed skills
npx @rmyndharis/antigravity-skills update

# Update global skills
npx @rmyndharis/antigravity-skills update --global
```

**6. Install ALL skills:**

```bash
# To your current workspace
npx @rmyndharis/antigravity-skills install --all

# Globally
npx @rmyndharis/antigravity-skills install --all --global
```

### Manual Installation

If you prefer to clone the repository:

**Option A — Install to a workspace**

```bash
mkdir -p .agent/skills
cp -R /path/to/antigravity-skill-vault/skills/<skill-name> .agent/skills/
```

**Option B — Install globally**

```bash
mkdir -p ~/.gemini/antigravity/skills
cp -R /path/to/antigravity-skill-vault/skills/<skill-name> ~/.gemini/antigravity/skills/
```

> **Note:** After copying skills, restart your agent session so Antigravity re-detects them.

---

## ➕ Adding New Skills

1.  Create a folder: `skills/<skill-name>/`
2.  Add `SKILL.md` (required)
3.  (Optional) Add helpers: `scripts/`, `references/`, `assets/`

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

## 📜 License

MIT License. See [LICENSE](LICENSE) file for details.

Original content © [Claude Code Agents](https://github.com/wshobson/agents).
Ported to Antigravity Skills.
