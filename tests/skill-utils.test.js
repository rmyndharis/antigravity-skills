const test = require('node:test');
const assert = require('node:assert');
const fs = require('node:fs');
const path = require('node:path');
const { tmpDir, rmDir } = require('./helpers');
const { listSkillIds, readSkill, parseFrontmatter } = require('../lib/skill-utils');

test('listSkillIds skips directories without a SKILL.md', () => {
  const root = tmpDir();
  try {
    fs.mkdirSync(path.join(root, 'good'));
    fs.writeFileSync(path.join(root, 'good', 'SKILL.md'), '---\nname: good\ndescription: x\n---\nbody');
    fs.mkdirSync(path.join(root, 'no-skill-md'));
    fs.mkdirSync(path.join(root, '.hidden'));
    assert.deepStrictEqual(listSkillIds(root), ['good']);
  } finally {
    rmDir(root);
  }
});

test('readSkill returns an error marker instead of throwing on a missing file', () => {
  const root = tmpDir();
  try {
    const skill = readSkill(root, 'does-not-exist');
    assert.strictEqual(skill.missing, true);
    assert.ok(Array.isArray(skill.errors) && skill.errors.length > 0);
    assert.strictEqual(skill.id, 'does-not-exist');
  } finally {
    rmDir(root);
  }
});

test('readSkill surfaces frontmatter parse errors', () => {
  const root = tmpDir();
  try {
    fs.mkdirSync(path.join(root, 'broken'));
    fs.writeFileSync(path.join(root, 'broken', 'SKILL.md'), '---\nname: [unterminated\n---\nbody');
    const skill = readSkill(root, 'broken');
    assert.ok(skill.errors.length > 0);
  } finally {
    rmDir(root);
  }
});

test('dead exports are removed', () => {
  const utils = require('../lib/skill-utils');
  assert.strictEqual(utils.parseInlineList, undefined);
  assert.strictEqual(utils.stripQuotes, undefined);
});
