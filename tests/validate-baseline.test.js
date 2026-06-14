const test = require('node:test');
const assert = require('node:assert');
const { spawnSync } = require('node:child_process');
const fs = require('node:fs');
const path = require('node:path');

const ROOT = path.resolve(__dirname, '..');
const VALIDATOR = path.join(ROOT, 'scripts', 'validate-skills.js');
const BASELINE = path.join(ROOT, 'validation-baseline.json');

function runValidator(args) {
  const result = spawnSync('node', [VALIDATOR, ...args], { encoding: 'utf8', cwd: ROOT });
  return { code: result.status || 0, out: (result.stdout || '') + (result.stderr || '') };
}

test('--write-baseline without --yes does NOT write the baseline file', () => {
  const before = fs.readFileSync(BASELINE, 'utf8');
  const r = runValidator(['--write-baseline']);
  const after = fs.readFileSync(BASELINE, 'utf8');
  assert.strictEqual(after, before, 'baseline must be unchanged without --yes');
  assert.ok(/not written/i.test(r.out), 'should explain it was not written');
  assert.ok(/grandfather/i.test(r.out), 'should mention grandfathering');
});
