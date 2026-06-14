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
