const test = require('node:test');
const assert = require('node:assert');

test('cli.js can be required without executing the program', () => {
  const cli = require('../bin/cli.js');
  assert.strictEqual(typeof cli.sanitizeSkillId, 'function');
  assert.strictEqual(typeof cli.resolveSkillId, 'function');
  assert.strictEqual(typeof cli.resolveSkillPath, 'function');
  assert.strictEqual(typeof cli.scoreSkill, 'function');
});

test('sanitizeSkillId accepts kebab-case and rejects junk', () => {
  const { sanitizeSkillId } = require('../bin/cli.js');
  assert.strictEqual(sanitizeSkillId('Python-Pro'), 'python-pro');
  assert.strictEqual(sanitizeSkillId('../evil'), null);
  assert.strictEqual(sanitizeSkillId('a b'), null);
  assert.strictEqual(sanitizeSkillId(''), null);
});

test('resolveSkillId applies alias map after sanitize', () => {
  const { resolveSkillId } = require('../bin/cli.js');
  const aliases = { 'full-stack-feature': 'full-stack-orchestration-full-stack-feature' };
  assert.strictEqual(resolveSkillId('full-stack-feature', aliases), 'full-stack-orchestration-full-stack-feature');
  assert.strictEqual(resolveSkillId('python-pro', aliases), 'python-pro');
  assert.strictEqual(resolveSkillId('../x', aliases), null);
});

test('resolveSkillPath rejects path traversal', () => {
  const { resolveSkillPath } = require('../bin/cli.js');
  assert.strictEqual(resolveSkillPath('..'), null);
  assert.notStrictEqual(resolveSkillPath('python-pro'), null);
});
