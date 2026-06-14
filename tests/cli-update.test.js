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
