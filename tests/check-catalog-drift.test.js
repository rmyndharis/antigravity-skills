const test = require('node:test');
const assert = require('node:assert');
const { execFileSync } = require('node:child_process');
const path = require('node:path');
const { findDrift, readDiskArtifacts } = require('../scripts/check-catalog-drift');
const { computeArtifacts } = require('../scripts/build-catalog');
const { tmpDir, rmDir } = require('./helpers');

const ROOT = path.resolve(__dirname, '..');
const SCRIPT = path.join(ROOT, 'scripts', 'check-catalog-drift.js');

function runScript() {
  try {
    const stdout = execFileSync('node', [SCRIPT], { encoding: 'utf8', cwd: ROOT });
    return { code: 0, out: stdout };
  } catch (err) {
    return { code: err.status || 1, out: (err.stdout || '') + (err.stderr || '') };
  }
}

test('check:catalog passes when artifacts are in sync (real run)', () => {
  const r = runScript();
  assert.strictEqual(r.code, 0, r.out);
  assert.ok(/in sync/.test(r.out));
});

test('findDrift returns empty when fresh equals disk', () => {
  const fresh = computeArtifacts();
  const disk = readDiskArtifacts();
  assert.deepStrictEqual(findDrift(fresh, disk), []);
});

test('findDrift detects a drifting artifact without touching any file', () => {
  const fresh = computeArtifacts();
  const disk = readDiskArtifacts();
  const tampered = JSON.parse(JSON.stringify(disk));
  tampered.catalog.skills[0].description = 'TAMPERED IN MEMORY';
  const drift = findDrift(fresh, tampered);
  assert.ok(drift.includes('catalog.json'), `expected catalog.json drift, got ${JSON.stringify(drift)}`);
});

test('findDrift ignores the generatedAt timestamp', () => {
  const fresh = computeArtifacts();
  const disk = readDiskArtifacts();
  const tampered = JSON.parse(JSON.stringify(disk));
  tampered.catalog.generatedAt = '1999-01-01T00:00:00.000Z';
  tampered.bundles.generatedAt = '1999-01-01T00:00:00.000Z';
  tampered.aliases.generatedAt = '1999-01-01T00:00:00.000Z';
  assert.deepStrictEqual(findDrift(fresh, tampered), []);
});

test('findDrift detects CATALOG.md drift (markdown path)', () => {
  const fresh = computeArtifacts();
  const disk = readDiskArtifacts();
  const tampered = JSON.parse(JSON.stringify(disk));
  const before = tampered.catalogMarkdown;
  tampered.catalogMarkdown = before.replace('# Skill Catalog', '# Skill Catalog TAMPERED');
  assert.notStrictEqual(tampered.catalogMarkdown, before, 'replace was a no-op — the header string changed; update this test');
  assert.ok(findDrift(fresh, tampered).includes('CATALOG.md'), 'markdown tamper should be detected');
});

test('readDiskArtifacts throws a helpful error when artifacts are missing', () => {
  const dir = tmpDir(); // empty: no catalog.json etc.
  try {
    assert.throws(() => readDiskArtifacts(dir), /failed to read a catalog artifact|build:catalog/i);
  } finally {
    rmDir(dir);
  }
});
