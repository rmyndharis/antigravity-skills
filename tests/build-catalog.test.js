const test = require('node:test');
const assert = require('node:assert');
const { computeArtifacts } = require('../scripts/build-catalog');

test('computeArtifacts returns all four artifacts without writing files', () => {
  const a = computeArtifacts();
  assert.ok(a.catalog && Array.isArray(a.catalog.skills));
  assert.strictEqual(a.catalog.total, a.catalog.skills.length);
  assert.ok(typeof a.catalogMarkdown === 'string' && a.catalogMarkdown.length > 0);
  assert.ok(a.bundles && a.bundles.bundles);
  assert.ok(a.aliases && a.aliases.aliases);
});

test('accessibility/compliance skill is no longer mis-categorized as security', () => {
  const a = computeArtifacts();
  const skill = a.catalog.skills.find(s => s.id === 'accessibility-compliance-accessibility-audit');
  assert.ok(skill, 'skill must exist');
  // Pinned to the correct category: previously mis-tagged 'security' via the 'compliance' keyword.
  assert.strictEqual(skill.category, 'general');
});

test('categories follow the skill domain before incidental description words', () => {
  const { catalog } = computeArtifacts();
  const categories = new Map(catalog.skills.map(skill => [skill.id, skill.category]));
  for (const [id, category] of Object.entries({
    'flutter-expert': 'development',
    'unity-developer': 'development',
    'database-migration': 'data-ai',
    'machine-learning-ops-ml-pipeline': 'data-ai',
    'legal-advisor': 'business',
    'quant-analyst': 'business',
    'risk-manager': 'business',
    'content-marketer': 'business',
    'startup-metrics-framework': 'business',
    'documentation-generation-doc-generate': 'development',
    'c4-code': 'architecture',
    'e2e-testing-patterns': 'testing',
    'context-driven-development': 'workflow',
    'antigravity-skills-manager': 'workflow',
    'architect-review': 'architecture',
    'arm-cortex-expert': 'development',
    'binary-analysis-patterns': 'security',
    'error-handling-patterns': 'development',
  })) assert.strictEqual(categories.get(id), category, id);
});

test('bundles include their domain skills without incidental description matches', () => {
  const { bundles } = computeArtifacts().bundles;
  for (const [name, included, excluded] of [
    ['core-dev', ['python-pro', 'dotnet-backend-patterns'], ['legal-advisor']],
    ['k8s-core', ['kubernetes-architect', 'helm-chart-scaffolding'], ['legal-advisor', 'ios-developer', 'unity-developer']],
    ['data-core', ['data-engineer', 'machine-learning-ops-ml-pipeline'], ['content-marketer', 'legal-advisor', 'ios-developer']],
    ['security-core', ['security-auditor', 'sast-configuration'], ['risk-manager', 'accessibility-compliance-accessibility-audit']],
    ['ops-core', ['observability-engineer', 'terraform-specialist'], ['flutter-expert', 'data-engineer', 'unity-developer']],
  ]) {
    for (const id of included) assert.ok(bundles[name].skills.includes(id), `${name} should include ${id}`);
    for (const id of excluded) assert.ok(!bundles[name].skills.includes(id), `${name} should exclude ${id}`);
  }
});

test('public skill IDs remain available without duplicating equivalent bundle instructions', () => {
  const { catalog, bundles } = computeArtifacts();
  const ids = new Set(catalog.skills.map(skill => skill.id));
  const pairs = [
    ['code-documentation-doc-generate', 'documentation-generation-doc-generate'],
    ['code-refactoring-context-restore', 'context-management-context-restore'],
    ['code-refactoring-tech-debt', 'codebase-cleanup-tech-debt'],
    ['error-debugging-error-analysis', 'error-diagnostics-error-analysis'],
    ['error-debugging-multi-agent-review', 'performance-testing-review-multi-agent-review'],
    ['debugging-toolkit-smart-debug', 'error-diagnostics-smart-debug'],
  ];
  for (const [first, second] of pairs) {
    assert.ok(ids.has(first) && ids.has(second));
    for (const bundle of Object.values(bundles.bundles)) {
      assert.ok(!(bundle.skills.includes(first) && bundle.skills.includes(second)));
    }
  }
});
