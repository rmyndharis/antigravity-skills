const { spawnSync } = require('node:child_process');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');

const CLI = path.resolve(__dirname, '..', 'bin', 'cli.js');

function runCli(args, opts = {}) {
  const res = spawnSync('node', [CLI, ...args], {
    encoding: 'utf8',
    env: { ...process.env, ...(opts.env || {}) },
    cwd: opts.cwd || process.cwd(),
  });
  return {
    code: res.status == null ? 1 : res.status,
    stdout: res.stdout || '',
    stderr: res.stderr || '',
  };
}

function tmpDir() {
  return fs.mkdtempSync(path.join(os.tmpdir(), 'agskills-'));
}

function rmDir(dir) {
  fs.rmSync(dir, { recursive: true, force: true });
}

module.exports = { runCli, tmpDir, rmDir, CLI };
