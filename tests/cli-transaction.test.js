const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('fs-extra');
const path = require('node:path');
const { installSkill } = require('../lib/install-skill');
const { tmpDir, rmDir } = require('./helpers');

function fixture(t) {
  const root = tmpDir();
  t.after(() => rmDir(root));
  const source = path.join(root, 'source', 'sample');
  const destination = path.join(root, 'target', 'sample');
  fs.ensureDirSync(source);
  fs.ensureDirSync(destination);
  fs.writeFileSync(path.join(source, 'SKILL.md'), 'new version');
  fs.writeFileSync(path.join(destination, 'SKILL.md'), 'old version');
  fs.writeFileSync(path.join(destination, 'obsolete.txt'), 'old file');
  return { root, source, destination };
}

function assertOldInstallation(destination) {
  assert.equal(fs.readFileSync(path.join(destination, 'SKILL.md'), 'utf8'), 'old version');
  assert.equal(fs.readFileSync(path.join(destination, 'obsolete.txt'), 'utf8'), 'old file');
  assert.deepEqual(fs.readdirSync(path.dirname(destination)), ['sample']);
}

test('replacement removes obsolete files and preserves executable modes', async t => {
  const { source, destination } = fixture(t);
  fs.writeFileSync(path.join(source, 'run.sh'), '#!/bin/sh\nexit 0\n', { mode: 0o755 });
  assert.equal(await installSkill(source, destination, true), true);
  assert.equal(fs.readFileSync(path.join(destination, 'SKILL.md'), 'utf8'), 'new version');
  assert.equal(fs.existsSync(path.join(destination, 'obsolete.txt')), false);
  if (process.platform !== 'win32') {
    assert.equal(fs.statSync(path.join(destination, 'run.sh')).mode & 0o777, 0o755);
  }
  assert.deepEqual(fs.readdirSync(path.dirname(destination)), ['sample']);
});

test('install without overwrite preserves the existing directory', async t => {
  const { source, destination } = fixture(t);
  assert.equal(await installSkill(source, destination), false);
  assertOldInstallation(destination);
});

test('failed staging preserves the complete previous installation', async t => {
  const { source, destination } = fixture(t);
  t.mock.method(fs, 'copySync', (_source, staged) => {
    fs.ensureDirSync(staged);
    fs.writeFileSync(path.join(staged, 'partial.txt'), 'partial copy');
    throw new Error('copy failed');
  });
  await assert.rejects(installSkill(source, destination, true), /copy failed/);
  assertOldInstallation(destination);
});

test('failed backup rename preserves the complete previous installation', async t => {
  const { source, destination } = fixture(t);
  const rename = fs.rename;
  t.mock.method(fs, 'rename', async (from, to) => {
    if (from.endsWith(`${path.sep}sample`)) throw new Error('backup rename failed');
    return rename(from, to);
  });
  await assert.rejects(installSkill(source, destination, true), /backup rename failed/);
  assertOldInstallation(destination);
});

test('failed activation restores the complete previous installation', async t => {
  const { source, destination } = fixture(t);
  const rename = fs.rename;
  t.mock.method(fs, 'rename', async (from, to) => {
    if (path.basename(from) === 'staged') throw new Error('activation failed');
    return rename(from, to);
  });
  await assert.rejects(installSkill(source, destination, true), /activation failed/);
  assertOldInstallation(destination);
});

test('failed restoration retains and reports the previous installation backup', async t => {
  const { source, destination } = fixture(t);
  const rename = fs.rename;
  t.mock.method(fs, 'rename', async (from, to) => {
    if (['staged', 'backup'].includes(path.basename(from))) throw new Error('rename failed');
    return rename(from, to);
  });
  let backup;
  await assert.rejects(installSkill(source, destination, true), err => {
    assert.match(err.message, /restoration failed/);
    backup = err.message.split('Previous installation retained at: ')[1];
    return Boolean(backup);
  });
  assert.equal(fs.readFileSync(path.join(backup, 'SKILL.md'), 'utf8'), 'old version');
  assert.equal(fs.readFileSync(path.join(backup, 'obsolete.txt'), 'utf8'), 'old file');
  assert.equal(fs.existsSync(destination), false);
  assert.equal(fs.existsSync(path.join(path.dirname(destination), '.sample.install-lock')), false);
});

test('cleanup failure warns without reporting a successful replacement as failed', async t => {
  const { source, destination } = fixture(t);
  const warnings = [];
  t.mock.method(console, 'warn', warning => warnings.push(warning));
  t.mock.method(fs, 'remove', async () => { throw new Error('cleanup failed'); });
  assert.equal(await installSkill(source, destination, true), true);
  assert.equal(fs.readFileSync(path.join(destination, 'SKILL.md'), 'utf8'), 'new version');
  assert.ok(warnings.some(warning => /temporary files at .*cleanup failed/.test(warning)));
  assert.equal(fs.existsSync(path.join(path.dirname(destination), '.sample.install-lock')), false);
});

test('lock cleanup failure reports the stale lock after a successful replacement', async t => {
  const { source, destination } = fixture(t);
  const warnings = [];
  t.mock.method(console, 'warn', warning => warnings.push(warning));
  t.mock.method(fs, 'rmdir', async () => { throw new Error('lock cleanup failed'); });
  assert.equal(await installSkill(source, destination, true), true);
  assert.equal(fs.readFileSync(path.join(destination, 'SKILL.md'), 'utf8'), 'new version');
  assert.ok(warnings.some(warning => /installation lock at .*\.sample\.install-lock/.test(warning)));
  assert.equal(fs.existsSync(path.join(path.dirname(destination), '.sample.install-lock')), true);
});

test('failed first installation leaves no partially installed skill', async t => {
  const { source, destination } = fixture(t);
  fs.removeSync(destination);
  t.mock.method(fs, 'rename', async () => { throw new Error('activation failed'); });
  await assert.rejects(installSkill(source, destination), /activation failed/);
  assert.equal(fs.existsSync(destination), false);
  assert.deepEqual(fs.readdirSync(path.dirname(destination)), []);
});

test('overlapping source and destination paths are rejected before writing', async t => {
  const { source } = fixture(t);
  for (const destination of [source, path.dirname(source), path.join(source, 'nested')]) {
    await assert.rejects(installSkill(source, destination, true), /must not overlap/);
    assert.equal(fs.readFileSync(path.join(source, 'SKILL.md'), 'utf8'), 'new version');
    assert.deepEqual(fs.readdirSync(source), ['SKILL.md']);
  }
});

test('source overlap through a destination parent symlink is rejected', async t => {
  const { root, source } = fixture(t);
  const alias = path.join(root, 'alias');
  fs.symlinkSync(path.dirname(source), alias, 'junction');
  await assert.rejects(installSkill(source, path.join(alias, 'sample'), true), /must not overlap/);
  assert.equal(fs.readFileSync(path.join(source, 'SKILL.md'), 'utf8'), 'new version');
});

test('a safe destination parent symlink resolves to the same installation and lock', async t => {
  const { root, source, destination } = fixture(t);
  const alias = path.join(root, 'alias');
  fs.symlinkSync(path.dirname(destination), alias, 'junction');
  assert.equal(await installSkill(source, path.join(alias, 'sample'), true), true);
  assert.equal(fs.readFileSync(path.join(destination, 'SKILL.md'), 'utf8'), 'new version');
  assert.deepEqual(fs.readdirSync(path.dirname(destination)), ['sample']);
});

test('a destination parent changed during staging is rejected before activation', async t => {
  const { root, source, destination } = fixture(t);
  const alias = path.join(root, 'alias');
  const other = path.join(root, 'other');
  fs.mkdirSync(other);
  fs.symlinkSync(path.dirname(destination), alias, 'junction');
  const copy = fs.copySync;
  t.mock.method(fs, 'copySync', (...args) => {
    copy(...args);
    fs.unlinkSync(alias);
    fs.symlinkSync(other, alias, 'junction');
  });
  await assert.rejects(installSkill(source, path.join(alias, 'sample'), true), /destination changed/);
  assertOldInstallation(destination);
  assert.deepEqual(fs.readdirSync(other), []);
});

test('a regular-file destination is preserved and rejected even with overwrite', async t => {
  const { source, destination } = fixture(t);
  fs.removeSync(destination);
  fs.writeFileSync(destination, 'keep this file');
  await assert.rejects(installSkill(source, destination, true), /real directory/);
  assert.equal(fs.readFileSync(destination, 'utf8'), 'keep this file');
});

test('a symlink destination and its target are preserved and rejected', async t => {
  const { root, source, destination } = fixture(t);
  const linked = path.join(root, 'linked');
  fs.renameSync(destination, linked);
  fs.symlinkSync(linked, destination, 'junction');
  await assert.rejects(installSkill(source, destination, true), /real directory/);
  assert.equal(fs.lstatSync(destination).isSymbolicLink(), true);
  assert.equal(fs.readFileSync(path.join(linked, 'SKILL.md'), 'utf8'), 'old version');
});

test('a missing or non-file SKILL.md leaves the previous installation untouched', async t => {
  const { source, destination } = fixture(t);
  fs.unlinkSync(path.join(source, 'SKILL.md'));
  await assert.rejects(installSkill(source, destination, true), /regular SKILL.md/);
  fs.mkdirSync(path.join(source, 'SKILL.md'));
  await assert.rejects(installSkill(source, destination, true), /regular SKILL.md/);
  assertOldInstallation(destination);
});

test('an empty source SKILL.md leaves the previous installation untouched', async t => {
  const { source, destination } = fixture(t);
  fs.writeFileSync(path.join(source, 'SKILL.md'), '');
  await assert.rejects(installSkill(source, destination, true), /nonempty regular SKILL.md/);
  assertOldInstallation(destination);
});

test('an invalid staged SKILL.md never replaces the previous installation', async t => {
  const { source, destination } = fixture(t);
  const copy = fs.copySync;
  for (const state of ['empty', 'missing', 'directory']) {
    t.mock.method(fs, 'copySync', (...args) => {
      copy(...args);
      const stagedSkill = path.join(args[1], 'SKILL.md');
      fs.unlinkSync(stagedSkill);
      if (state === 'empty') fs.writeFileSync(stagedSkill, '');
      if (state === 'directory') fs.mkdirSync(stagedSkill);
    });
    await assert.rejects(installSkill(source, destination, true), /nonempty regular SKILL.md/);
    assertOldInstallation(destination);
    t.mock.restoreAll();
  }
});

test('a source symlink is rejected before replacing an installation', async t => {
  const { root, source, destination } = fixture(t);
  const alias = path.join(root, 'source-alias');
  fs.symlinkSync(source, alias, 'junction');
  await assert.rejects(installSkill(alias, destination, true), /regular SKILL.md/);
  assertOldInstallation(destination);
});

test('a symlink inside the source is rejected without changing its target or installation', async t => {
  const { source, destination } = fixture(t);
  fs.symlinkSync(destination, path.join(source, 'linked'), 'junction');
  await assert.rejects(installSkill(source, destination, true), /must not contain symlinks/);
  assertOldInstallation(destination);
});

test('an existing installation lock is left intact', async t => {
  const { source, destination } = fixture(t);
  const lock = path.join(path.dirname(destination), '.sample.install-lock');
  fs.mkdirSync(lock);
  fs.writeFileSync(path.join(lock, 'owner'), 'other installer');
  await assert.rejects(installSkill(source, destination, true), /Another installation may be in progress/);
  assert.equal(fs.readFileSync(path.join(lock, 'owner'), 'utf8'), 'other installer');
  assert.equal(fs.readFileSync(path.join(destination, 'SKILL.md'), 'utf8'), 'old version');
});

test('concurrent installers cannot replace the same destination', async t => {
  const { source, destination } = fixture(t);
  const rename = fs.rename;
  let release;
  let entered;
  const paused = new Promise(resolve => { release = resolve; });
  const ready = new Promise(resolve => { entered = resolve; });
  t.mock.method(fs, 'rename', async (from, to) => {
    if (path.basename(from) === 'sample') {
      entered();
      await paused;
    }
    return rename(from, to);
  });
  const first = installSkill(source, destination, true);
  try {
    await ready;
    await assert.rejects(installSkill(source, destination, true), /Another installation may be in progress/);
  } finally {
    release();
    await first;
  }
  assert.equal(fs.readFileSync(path.join(destination, 'SKILL.md'), 'utf8'), 'new version');
  assert.deepEqual(fs.readdirSync(path.dirname(destination)), ['sample']);
});
