const fs = require('fs');
const path = require('path');
const {
  listSkillIds,
  readSkill,
  tokenize,
  unique,
  truncate,
} = require('../lib/skill-utils');

const ROOT = path.resolve(__dirname, '..');
const SKILLS_DIR = path.join(ROOT, 'skills');

const STOPWORDS = new Set([
  'a', 'an', 'and', 'are', 'as', 'at', 'be', 'but', 'by', 'for', 'from', 'has', 'have', 'in', 'into',
  'is', 'it', 'its', 'of', 'on', 'or', 'our', 'out', 'over', 'that', 'the', 'their', 'they', 'this',
  'to', 'use', 'when', 'with', 'you', 'your', 'will', 'can', 'if', 'not', 'only', 'also', 'more',
  'best', 'practice', 'practices', 'expert', 'specialist', 'focused', 'focus', 'master', 'modern',
  'advanced', 'comprehensive', 'production', 'production-ready', 'ready', 'build', 'create', 'deliver',
  'design', 'implement', 'implementation', 'strategy', 'strategies', 'patterns', 'pattern', 'workflow',
  'workflows', 'guide', 'template', 'templates', 'tool', 'tools', 'project', 'projects', 'support',
  'manage', 'management', 'system', 'systems', 'services', 'service', 'across', 'end', 'end-to-end',
  'using', 'based', 'ensure', 'help', 'needs', 'need', 'focuses', 'handles', 'builds', 'make',
]);

const TAG_STOPWORDS = new Set([
  'pro', 'expert', 'patterns', 'pattern', 'workflow', 'workflows', 'templates', 'template', 'toolkit',
  'tools', 'tool', 'project', 'projects', 'guide', 'management', 'engineer', 'architect', 'developer',
  'specialist', 'assistant', 'analysis', 'review', 'reviewer', 'automation', 'orchestration', 'scaffold',
  'scaffolding', 'implementation', 'strategy', 'context', 'feature', 'features', 'smart',
  'system', 'systems', 'design', 'development', 'test', 'testing',
]);

const CATEGORY_RULES = [
  {
    name: 'security',
    keywords: [
      'security', 'sast', 'privacy', 'threat', 'vulnerability', 'owasp', 'pci', 'gdpr',
      'secrets', 'malware', 'forensics', 'attack', 'auth', 'mtls', 'stride', 'reverse', 'firmware',
      'reversing', 'binary',
    ],
  },
  {
    name: 'infrastructure',
    keywords: [
      'kubernetes', 'k8s', 'helm', 'terraform', 'cloud', 'network', 'devops', 'gitops', 'prometheus',
      'grafana', 'observability', 'monitoring', 'logging', 'tracing', 'deployment', 'istio', 'linkerd',
      'mesh', 'slo', 'sre', 'oncall', 'handoff', 'incident', 'cicd', 'ci', 'cd',
    ],
  },
  {
    name: 'data-ai',
    keywords: [
      'data', 'database', 'db', 'sql', 'postgres', 'mysql', 'analytics', 'etl', 'warehouse', 'dbt',
      'ml', 'mlops', 'ai', 'llm', 'rag', 'vector', 'embedding', 'spark', 'airflow', 'cdc', 'pipeline',
      'postgresql', 'langchain', 'prompt', 'similarity',
    ],
  },
  {
    name: 'development',
    keywords: [
      'python', 'javascript', 'typescript', 'java', 'golang', 'go', 'rust', 'csharp', 'dotnet', 'php',
      'ruby', 'node', 'react', 'frontend', 'backend', 'mobile', 'ios', 'android', 'flutter', 'fastapi',
      'django', 'nextjs', 'vue', 'api', 'unity', 'unreal', 'godot', 'game', 'minecraft', 'swift',
      'kotlin', 'dart', 'elixir', 'haskell', 'julia', 'scala', 'cpp', 'bash', 'shell', 'memory',
      'code', 'codebase', 'refactoring', 'debug', 'debugging', 'diagnostics', 'deps', 'dependency',
      'framework', 'documentation', 'doc',
      'arm', 'cortex', 'error', 'git', 'tailwind', 'ui', 'ux', 'graphql', 'bazel',
    ],
  },
  {
    name: 'architecture',
    keywords: [
      'architecture', 'c4', 'microservices', 'event', 'cqrs', 'saga', 'domain', 'ddd',
      'decision', 'adr', 'monorepo',
    ],
  },
  {
    name: 'testing',
    keywords: ['testing', 'tdd', 'unit', 'e2e', 'qa', 'test'],
  },
  {
    name: 'business',
    keywords: [
      'business', 'market', 'sales', 'finance', 'startup', 'legal', 'hr', 'product', 'customer', 'seo',
      'marketing', 'marketer', 'kpi', 'contract', 'employment', 'quant', 'trading', 'portfolio', 'risk',
    ],
  },
  {
    name: 'workflow',
    keywords: ['workflow', 'orchestration', 'conductor', 'automation', 'process', 'collaboration'],
  },
];

// Hand-picked and small: every installed skill adds its metadata to each session.
// Language-specific skills are installed with --tag <language> instead.
const MAX_BUNDLE_SIZE = 10;
const BUNDLES = {
  'core-dev': {
    description: 'Language-agnostic development essentials: design, review, refactoring, debugging, testing, and Git. Add language skills with --tag <language>.',
    skills: [
      'api-design-principles', 'architecture-patterns', 'backend-architect', 'code-refactoring-refactor-clean',
      'code-review-excellence', 'debugger', 'error-handling-patterns', 'frontend-developer', 'git-advanced-workflows',
      'test-automator',
    ],
  },
  'security-core': {
    description: 'Security essentials: auditing, threat modeling, scanning, secrets, authentication, and secure coding.',
    skills: [
      'auth-implementation-patterns', 'backend-security-coder', 'frontend-security-coder', 'sast-configuration',
      'secrets-management', 'security-auditor', 'security-scanning-security-dependencies',
      'security-scanning-security-hardening', 'threat-modeling-expert',
    ],
  },
  'k8s-core': {
    description: 'Kubernetes essentials: architecture, manifests, Helm, security policies, GitOps, and service mesh.',
    skills: [
      'gitops-workflow', 'helm-chart-scaffolding', 'k8s-manifest-generator', 'k8s-security-policies',
      'kubernetes-architect', 'service-mesh-expert',
    ],
  },
  'data-core': {
    description: 'Data engineering, SQL, and database foundations.',
    skills: [
      'airflow-dag-patterns', 'data-engineer', 'data-quality-frameworks', 'database-architect',
      'database-migrations-sql-migrations', 'database-optimizer', 'dbt-transformation-patterns', 'postgresql',
      'spark-optimization', 'sql-pro',
    ],
  },
  'ai-core': {
    description: 'LLM application, retrieval, evaluation, and ML engineering essentials.',
    skills: [
      'ai-engineer', 'embedding-strategies', 'langchain-architecture', 'llm-evaluation', 'ml-engineer',
      'prompt-engineering-patterns', 'rag-implementation', 'vector-database-engineer',
    ],
  },
  'ops-core': {
    description: 'Operations essentials: observability, SLOs, incident response, deployment, and infrastructure as code.',
    skills: [
      'deployment-engineer', 'devops-troubleshooter', 'distributed-tracing', 'grafana-dashboards',
      'incident-responder', 'observability-engineer', 'postmortem-writing', 'prometheus-configuration',
      'slo-implementation', 'terraform-specialist',
    ],
  },
};

const CURATED_COMMON = [
  'bash-pro',
  'python-pro',
  'javascript-pro',
  'typescript-pro',
  'golang-pro',
  'rust-pro',
  'java-pro',
  'frontend-developer',
  'backend-architect',
  'nodejs-backend-patterns',
  'fastapi-pro',
  'api-design-principles',
  'sql-pro',
  'database-architect',
  'kubernetes-architect',
  'terraform-specialist',
  'observability-engineer',
  'security-auditor',
  'sast-configuration',
  'gitops-workflow',
];

function normalizeTokens(tokens) {
  return unique(tokens.map(token => token.toLowerCase())).filter(Boolean);
}

function deriveTags(skill) {
  let tags = Array.isArray(skill.tags) ? skill.tags : [];
  tags = tags.map(tag => tag.toLowerCase()).filter(Boolean);

  if (!tags.length) {
    tags = skill.id
      .split('-')
      .map(tag => tag.toLowerCase())
      .filter(tag => tag && !TAG_STOPWORDS.has(tag));
  }

  return normalizeTokens(tags);
}

function detectCategory(skill, tags) {
  if (['antigravity-skills-manager', 'context-driven-development', 'mermaid-expert'].includes(skill.id)) return 'workflow';
  if (skill.id.startsWith('c4-') || skill.id === 'architect-review') return 'architecture';
  if (skill.id === 'comprehensive-review-full-review') return 'development';
  if (skill.id.startsWith('startup-')) return 'business';
  // Prefer the skill's identity to incidental examples in its description.
  for (const tokens of [tokenize(skill.id), tags, tokenize(skill.description)]) {
    const haystack = new Set(tokens);
    for (const rule of CATEGORY_RULES) {
      if (rule.keywords.some(keyword => haystack.has(keyword))) return rule.name;
    }
  }

  return 'general';
}

function buildTriggers(skill, tags) {
  const tokens = tokenize(`${skill.name} ${skill.description}`)
    .filter(token => token.length >= 2 && !STOPWORDS.has(token));
  return unique([...tags, ...tokens]).slice(0, 12);
}

function buildAliases(skills) {
  const existingIds = new Set(skills.map(skill => skill.id));
  const aliases = {};
  const used = new Set();

  for (const skill of skills) {
    const tokens = skill.id.split('-').filter(Boolean);
    if (skill.id.length < 28 || tokens.length < 4) continue;

    const deduped = [];
    const tokenSeen = new Set();
    for (const token of tokens) {
      if (tokenSeen.has(token)) continue;
      tokenSeen.add(token);
      deduped.push(token);
    }

    const aliasTokens = deduped.length > 3
      ? [deduped[0], deduped[1], deduped[deduped.length - 1]]
      : deduped;
    const alias = unique(aliasTokens).join('-');

    if (!alias || alias === skill.id) continue;
    if (existingIds.has(alias) || used.has(alias)) continue;

    aliases[alias] = skill.id;
    used.add(alias);
  }

  return aliases;
}

function buildBundles(skills, definitions = BUNDLES) {
  const ids = new Set(skills.map(skill => skill.id));
  const bundles = {};

  for (const [bundleName, rule] of Object.entries(definitions)) {
    // Fail the build, and so the drift check, when a bundled skill is renamed or removed.
    const unknown = rule.skills.filter(skillId => !ids.has(skillId));
    if (unknown.length) {
      throw new Error(`Bundle '${bundleName}' lists unknown skills: ${unknown.join(', ')}`);
    }
    if (rule.skills.length > MAX_BUNDLE_SIZE) {
      throw new Error(`Bundle '${bundleName}' has ${rule.skills.length} skills; the limit is ${MAX_BUNDLE_SIZE}.`);
    }
    bundles[bundleName] = {
      description: rule.description,
      skills: [...rule.skills].sort(),
    };
  }

  const common = CURATED_COMMON.filter(skillId => ids.has(skillId));

  return { bundles, common };
}

function renderCatalogMarkdown(catalog) {
  const lines = [];
  lines.push('# Skill Catalog');
  lines.push('');
  lines.push(`Total skills: ${catalog.total}`);
  lines.push('');

  const categories = Array.from(new Set(catalog.skills.map(skill => skill.category))).sort();
  for (const category of categories) {
    const grouped = catalog.skills.filter(skill => skill.category === category);
    lines.push(`## ${category} (${grouped.length})`);
    lines.push('');
    lines.push('| Skill | Description | Tags | Triggers |');
    lines.push('| --- | --- | --- | --- |');

    for (const skill of grouped) {
      const description = truncate(skill.description, 160).replace(/\|/g, '\\|');
      const tags = skill.tags.join(', ');
      const triggers = skill.triggers.join(', ');
      lines.push(`| \`${skill.id}\` | ${description} | ${tags} | ${triggers} |`);
    }

    lines.push('');
  }

  return lines.join('\n');
}

function computeArtifacts() {
  const skillIds = listSkillIds(SKILLS_DIR);
  const skills = [];
  for (const skillId of skillIds) {
    const skill = readSkill(SKILLS_DIR, skillId);
    // Best-effort: warn but still include errored skills (with readSkill's safe defaults) so the catalog stays complete.
    if (skill.errors && skill.errors.length) {
      console.warn(`[build-catalog] Warning: ${skillId}: ${skill.errors.join('; ')}`);
    }
    skills.push(skill);
  }

  const catalogSkills = [];
  for (const skill of skills) {
    const tags = deriveTags(skill);
    const category = detectCategory(skill, tags);
    const triggers = buildTriggers(skill, tags);

    catalogSkills.push({
      id: skill.id,
      name: skill.name,
      description: skill.description,
      category,
      tags,
      triggers,
      path: path.relative(ROOT, skill.path).replace(/\\/g, '/'),
    });
  }

  // No build timestamp: identical inputs must produce identical bytes, or parallel branches conflict.
  const catalog = {
    total: catalogSkills.length,
    skills: catalogSkills.sort((a, b) => a.id.localeCompare(b.id)),
  };

  return {
    catalog,
    catalogMarkdown: renderCatalogMarkdown(catalog),
    bundles: buildBundles(catalog.skills),
    aliases: { aliases: buildAliases(catalog.skills) },
  };
}

function buildCatalog() {
  const artifacts = computeArtifacts();

  fs.writeFileSync(path.join(ROOT, 'catalog.json'), JSON.stringify(artifacts.catalog, null, 2));
  fs.writeFileSync(path.join(ROOT, 'CATALOG.md'), artifacts.catalogMarkdown);
  fs.writeFileSync(path.join(ROOT, 'bundles.json'), JSON.stringify(artifacts.bundles, null, 2));
  fs.writeFileSync(path.join(ROOT, 'aliases.json'), JSON.stringify(artifacts.aliases, null, 2));

  return artifacts.catalog;
}

if (require.main === module) {
  const catalog = buildCatalog();
  console.log(`Generated catalog for ${catalog.total} skills.`);
}

module.exports = {
  buildBundles,
  buildCatalog,
  computeArtifacts,
};
