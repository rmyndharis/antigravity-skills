const test = require('node:test');
const assert = require('node:assert');
const fs = require('node:fs');
const path = require('node:path');
const { runCli, tmpDir, rmDir } = require('./helpers');

test('update with no installation dir exits non-zero', () => {
  const cwd = tmpDir();
  try {
    const r = runCli(['update'], { cwd });
    assert.strictEqual(r.code, 1);
    assert.ok(/No installation found/.test(r.stdout + r.stderr));
  } finally {
    rmDir(cwd);
  }
});

test('update a not-installed skill exits non-zero', () => {
  const cwd = tmpDir();
  try {
    runCli(['install', 'python-pro'], { cwd }); // create the dir with something
    const r = runCli(['update', 'golang-pro'], { cwd });
    assert.strictEqual(r.code, 1);
    assert.ok(/is not installed/.test(r.stdout + r.stderr));
  } finally {
    rmDir(cwd);
  }
});

test('update an invalid skill name exits non-zero', () => {
  const cwd = tmpDir();
  try {
    runCli(['install', 'python-pro'], { cwd });
    const r = runCli(['update', '../evil'], { cwd });
    assert.strictEqual(r.code, 1);
  } finally {
    rmDir(cwd);
  }
});

test('update replaces the installed directory and removes obsolete files', () => {
  const cwd = tmpDir();
  try {
    assert.strictEqual(runCli(['install', 'python-pro'], { cwd }).code, 0);
    const skill = path.join(cwd, '.agent', 'skills', 'python-pro');
    fs.writeFileSync(path.join(skill, 'obsolete.txt'), 'old file');
    fs.writeFileSync(path.join(skill, 'SKILL.md'), 'old version');
    const r = runCli(['update', 'python-pro'], { cwd });
    assert.strictEqual(r.code, 0);
    assert.match(r.stdout, /Updated: 1, skipped: 0, failed: 0/);
    assert.strictEqual(fs.existsSync(path.join(skill, 'obsolete.txt')), false);
    assert.strictEqual(fs.readFileSync(path.join(skill, 'SKILL.md'), 'utf8'),
      fs.readFileSync(path.join(__dirname, '..', 'skills', 'python-pro', 'SKILL.md'), 'utf8'));
  } finally {
    rmDir(cwd);
  }
});

test('explicit update of a retired skill fails without reporting completion', () => {
  const cwd = tmpDir();
  try {
    const skill = path.join(cwd, '.agent', 'skills', 'retired-skill');
    fs.mkdirSync(skill, { recursive: true });
    fs.writeFileSync(path.join(skill, 'SKILL.md'), 'keep this skill');
    const r = runCli(['update', 'retired-skill'], { cwd });
    assert.strictEqual(r.code, 1);
    assert.match(r.stdout, /Updated: 0, skipped: 0, failed: 1/);
    assert.doesNotMatch(r.stdout, /Update complete/);
    assert.strictEqual(fs.readFileSync(path.join(skill, 'SKILL.md'), 'utf8'), 'keep this skill');
  } finally {
    rmDir(cwd);
  }
});

test('batch update reports retired skills as skipped without claiming completion', () => {
  const cwd = tmpDir();
  try {
    const target = path.join(cwd, '.agent', 'skills');
    fs.mkdirSync(path.join(target, 'retired-skill'), { recursive: true });
    fs.mkdirSync(path.join(target, '.hidden'));
    fs.writeFileSync(path.join(target, 'notes.txt'), 'keep');
    const r = runCli(['update'], { cwd });
    assert.strictEqual(r.code, 0);
    assert.match(r.stdout, /Updating 1 skills/);
    assert.match(r.stdout, /Updated: 0, skipped: 1, failed: 0/);
    assert.doesNotMatch(r.stdout, /Update complete|notes.txt|\.hidden/);
  } finally {
    rmDir(cwd);
  }
});

test('batch update does not normalize an installed directory into a different destination', () => {
  const cwd = tmpDir();
  try {
    const skill = path.join(cwd, '.agent', 'skills', 'Python-Pro');
    fs.mkdirSync(skill, { recursive: true });
    fs.writeFileSync(path.join(skill, 'SKILL.md'), 'local instructions');
    const r = runCli(['update'], { cwd });
    assert.strictEqual(r.code, 0);
    assert.match(r.stdout, /Updated: 0, skipped: 1, failed: 0/);
    assert.strictEqual(fs.readFileSync(path.join(skill, 'SKILL.md'), 'utf8'), 'local instructions');
    assert.deepStrictEqual(fs.readdirSync(path.dirname(skill)), ['Python-Pro']);
  } finally {
    rmDir(cwd);
  }
});

// Isolated, in-process: verify loadJson warns (not silently degrades) on a corrupt
// file when given a label. Does NOT touch the repo's real bundles.json, so it is
// safe under node --test's concurrent file execution.
test('loadJson warns on a corrupt file when given a label', () => {
  const { loadJson } = require('../bin/cli.js');
  const dir = tmpDir();
  const file = path.join(dir, 'bundles.json');
  fs.writeFileSync(file, '{ not valid json');
  const warnings = [];
  const originalWarn = console.warn;
  console.warn = (msg) => warnings.push(String(msg));
  try {
    const result = loadJson(file, 'bundles.json');
    assert.strictEqual(result, null);
    assert.ok(warnings.some(w => /could not be parsed/.test(w)), 'expected a parse warning');
  } finally {
    console.warn = originalWarn;
    rmDir(dir);
  }
});

test('loadJson does NOT warn on a corrupt file when no label is given', () => {
  const { loadJson } = require('../bin/cli.js');
  const dir = tmpDir();
  const file = path.join(dir, 'thing.json');
  fs.writeFileSync(file, '{ not valid json');
  const warnings = [];
  const originalWarn = console.warn;
  console.warn = (msg) => warnings.push(String(msg));
  try {
    const result = loadJson(file, undefined);
    assert.strictEqual(result, null);
    assert.strictEqual(warnings.length, 0);
  } finally {
    console.warn = originalWarn;
    rmDir(dir);
  }
});
