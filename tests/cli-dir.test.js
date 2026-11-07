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

test('--global installs where Antigravity reads global skills and points to the legacy directory', () => {
  const home = tmpDir();
  const cwd = tmpDir();
  const env = { HOME: home, USERPROFILE: home };
  try {
    assert.strictEqual(runCli(['install', 'python-pro', '--global'], { cwd, env }).code, 0);
    assert.ok(fs.existsSync(path.join(home, '.gemini', 'config', 'skills', 'python-pro', 'SKILL.md')));
    assert.doesNotMatch(runCli(['installed', '--global'], { cwd, env }).stdout, /earlier versions/);

    fs.mkdirSync(path.join(home, '.gemini', 'antigravity', 'skills'), { recursive: true });
    const installed = runCli(['installed', '--global'], { cwd, env });
    assert.match(installed.stdout, /earlier versions remain in .*antigravity/);
    assert.match(installed.stdout, /python-pro/);
    assert.match(runCli(['doctor'], { cwd, env }).stdout, /Legacy global dir/);
  } finally {
    rmDir(home);
    rmDir(cwd);
  }
});

test('resolveTargetDir expands a leading ~ in AG_SKILLS_DIR', () => {
  const os = require('node:os');
  const { resolveTargetDir } = require('../bin/cli.js');
  const saved = process.env.AG_SKILLS_DIR;
  try {
    process.env.AG_SKILLS_DIR = '~/agskills-tilde-test';
    assert.strictEqual(resolveTargetDir(false), path.join(os.homedir(), 'agskills-tilde-test'));
  } finally {
    if (saved === undefined) delete process.env.AG_SKILLS_DIR;
    else process.env.AG_SKILLS_DIR = saved;
  }
});

test('installed shows an override header when AG_SKILLS_DIR is set', () => {
  const dest = tmpDir();
  const cwd = tmpDir();
  try {
    runCli(['install', 'python-pro'], { cwd, env: { AG_SKILLS_DIR: dest } });
    const r = runCli(['installed'], { cwd, env: { AG_SKILLS_DIR: dest } });
    assert.ok(/override/i.test(r.stdout), 'installed header should indicate the AG_SKILLS_DIR override');
  } finally {
    rmDir(dest);
    rmDir(cwd);
  }
});

test('installed lists only visible real directories', () => {
  const dest = tmpDir();
  try {
    fs.mkdirSync(path.join(dest, 'sample'));
    fs.mkdirSync(path.join(dest, '.hidden'));
    fs.writeFileSync(path.join(dest, 'notes.txt'), 'notes');
    fs.symlinkSync(path.join(dest, 'sample'), path.join(dest, 'linked'), 'junction');
    const r = runCli(['installed'], { env: { AG_SKILLS_DIR: dest } });
    assert.strictEqual(r.code, 0);
    assert.match(r.stdout, /- sample/);
    assert.doesNotMatch(r.stdout, /notes.txt|\.hidden|linked/);
  } finally {
    rmDir(dest);
  }
});

test('runCli isolates inherited AG_SKILLS_DIR while permitting explicit overrides', () => {
  const dest = tmpDir();
  const cwd = tmpDir();
  const saved = process.env.AG_SKILLS_DIR;
  try {
    fs.mkdirSync(path.join(dest, 'golang-pro'));
    const sentinel = path.join(dest, 'golang-pro', 'SKILL.md');
    fs.writeFileSync(sentinel, 'local instructions');
    process.env.AG_SKILLS_DIR = dest;
    const r = runCli(['install', 'python-pro'], { cwd });
    assert.strictEqual(r.code, 0);
    assert.ok(fs.existsSync(path.join(cwd, '.agent', 'skills', 'python-pro', 'SKILL.md')));
    assert.strictEqual(runCli(['update', 'golang-pro'], { cwd }).code, 1);
    assert.strictEqual(fs.readFileSync(sentinel, 'utf8'), 'local instructions');
    assert.deepStrictEqual(fs.readdirSync(dest), ['golang-pro']);
    assert.match(runCli(['installed'], { cwd, env: { AG_SKILLS_DIR: dest } }).stdout, /golang-pro/);
  } finally {
    if (saved === undefined) delete process.env.AG_SKILLS_DIR;
    else process.env.AG_SKILLS_DIR = saved;
    rmDir(dest);
    rmDir(cwd);
  }
});
