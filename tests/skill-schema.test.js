const test = require('node:test');
const assert = require('node:assert');
const schema = require('../lib/skill-schema');

test('skill-schema exposes the closed allowed field set', () => {
  assert.ok(schema.ALLOWED_FIELDS instanceof Set);
  for (const f of ['name', 'description', 'license', 'compatibility', 'metadata', 'allowed-tools']) {
    assert.ok(schema.ALLOWED_FIELDS.has(f), `missing ${f}`);
  }
  assert.strictEqual(schema.ALLOWED_FIELDS.has('tags'), false);
});

test('skill-schema exposes ordering, limits, and name pattern', () => {
  assert.deepStrictEqual(schema.FIELD_ORDER, ['name', 'description', 'license', 'compatibility', 'allowed-tools', 'metadata']);
  assert.strictEqual(schema.LIMITS.name, 64);
  assert.strictEqual(schema.LIMITS.description, 1024);
  assert.strictEqual(schema.LIMITS.compatibility, 500);
  assert.strictEqual(schema.LIMITS.license, 128);
  assert.strictEqual(schema.LIMITS.skillLines, 500);
  assert.ok(schema.NAME_PATTERN.test('tdd-workflows-tdd-cycle'));
  assert.strictEqual(schema.NAME_PATTERN.test('Bad_Name'), false);
});
