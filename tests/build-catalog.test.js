const test = require('node:test');
const assert = require('node:assert');
const { buildBundles, computeArtifacts } = require('../scripts/build-catalog');

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

test('bundles stay small and focused on their domain', () => {
  const { bundles } = computeArtifacts().bundles;
  for (const [name, included, excluded] of [
    ['core-dev', ['api-design-principles', 'debugger'], ['python-pro', 'php-pro', 'legal-advisor']],
    ['k8s-core', ['kubernetes-architect', 'helm-chart-scaffolding'], ['legal-advisor', 'ios-developer']],
    ['data-core', ['data-engineer', 'sql-pro'], ['ml-engineer', 'content-marketer']],
    ['ai-core', ['rag-implementation', 'prompt-engineering-patterns'], ['data-engineer']],
    ['security-core', ['security-auditor', 'sast-configuration'], ['malware-analyst', 'risk-manager']],
    ['ops-core', ['observability-engineer', 'terraform-specialist'], ['flutter-expert', 'data-engineer']],
  ]) {
    for (const id of included) assert.ok(bundles[name].skills.includes(id), `${name} should include ${id}`);
    for (const id of excluded) assert.ok(!bundles[name].skills.includes(id), `${name} should exclude ${id}`);
  }
  for (const [name, bundle] of Object.entries(bundles)) assert.ok(bundle.skills.length <= 10, name);
});

test('a bundle naming an unknown skill or exceeding the size limit fails the build', () => {
  const skills = [{ id: 'known-skill' }];
  assert.throws(() => buildBundles(skills, { sample: { description: 'x', skills: ['known-skill', 'renamed-skill'] } }), /unknown skills: renamed-skill/);
  const many = Array.from({ length: 11 }, (_, i) => ({ id: `skill-${i}` }));
  assert.throws(() => buildBundles(many, { sample: { description: 'x', skills: many.map(s => s.id) } }), /limit is 10/);
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
