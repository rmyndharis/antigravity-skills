const test = require('node:test');
const assert = require('node:assert');
const fs = require('node:fs');
const path = require('node:path');
const { runCli, tmpDir, rmDir } = require('./helpers');

test('install a non-existent skill exits non-zero and prints no success', () => {
  const cwd = tmpDir();
  try {
    const r = runCli(['install', 'this-skill-does-not-exist'], { cwd });
    assert.strictEqual(r.code, 1);
    assert.ok(!/Installation complete/.test(r.stdout + r.stderr));
  } finally {
    rmDir(cwd);
  }
});

test('install a real skill copies it and reports success', () => {
  const cwd = tmpDir();
  try {
    const r = runCli(['install', 'python-pro'], { cwd });
    assert.strictEqual(r.code, 0);
    assert.ok(fs.existsSync(path.join(cwd, '.agent', 'skills', 'python-pro', 'SKILL.md')));
    assert.ok(/Installation complete/.test(r.stdout));
  } finally {
    rmDir(cwd);
  }
});

test('re-installing without --force skips and does not overwrite', () => {
  const cwd = tmpDir();
  try {
    runCli(['install', 'python-pro'], { cwd });
    const marker = path.join(cwd, '.agent', 'skills', 'python-pro', 'LOCAL_EDIT.txt');
    fs.writeFileSync(marker, 'mine');
    const r = runCli(['install', 'python-pro'], { cwd });
    assert.strictEqual(r.code, 0);
    assert.ok(/[Ss]kipped/.test(r.stdout + r.stderr));
    assert.ok(fs.existsSync(marker), 'local edit must survive a skip');
  } finally {
    rmDir(cwd);
  }
});

test('--force overwrites an existing install', () => {
  const cwd = tmpDir();
  try {
    runCli(['install', 'python-pro'], { cwd });
    const marker = path.join(cwd, '.agent', 'skills', 'python-pro', 'LOCAL_EDIT.txt');
    fs.writeFileSync(marker, 'mine');
    const r = runCli(['install', 'python-pro', '--force'], { cwd });
    assert.strictEqual(r.code, 0);
    assert.ok(!fs.existsSync(marker), 'force overwrite removes stray local files');
  } finally {
    rmDir(cwd);
  }
});
