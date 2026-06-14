const test = require('node:test');
const assert = require('node:assert');
const fs = require('node:fs');
const path = require('node:path');
const { runCli, tmpDir, rmDir } = require('./helpers');

test('AG_SKILLS_DIR overrides the install destination', () => {
  const dest = tmpDir();
  const cwd = tmpDir();
  try {
    const r = runCli(['install', 'python-pro'], { cwd, env: { AG_SKILLS_DIR: dest } });
    assert.strictEqual(r.code, 0);
    assert.ok(fs.existsSync(path.join(dest, 'python-pro', 'SKILL.md')));
    assert.ok(!fs.existsSync(path.join(cwd, '.agent', 'skills', 'python-pro')));
  } finally {
    rmDir(dest);
    rmDir(cwd);
  }
});

test('installed lists from AG_SKILLS_DIR', () => {
  const dest = tmpDir();
  const cwd = tmpDir();
  try {
    runCli(['install', 'python-pro'], { cwd, env: { AG_SKILLS_DIR: dest } });
    const r = runCli(['installed'], { cwd, env: { AG_SKILLS_DIR: dest } });
    assert.ok(/python-pro/.test(r.stdout));
  } finally {
    rmDir(dest);
    rmDir(cwd);
  }
});

test('doctor reports the AG_SKILLS_DIR override when set', () => {
  const dest = tmpDir();
  try {
    const r = runCli(['doctor'], { env: { AG_SKILLS_DIR: dest } });
    assert.ok(/AG_SKILLS_DIR override/.test(r.stdout));
    assert.ok(r.stdout.includes(dest));
  } finally {
    rmDir(dest);
  }
});
