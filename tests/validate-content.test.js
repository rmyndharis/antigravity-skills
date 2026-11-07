const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const { spawnSync } = require('node:child_process');
const { tmpDir, rmDir } = require('./helpers');
const { stripCodeFences, findHelperReferences } = require('../lib/skill-utils');
const { normalizeSkill } = require('../scripts/normalize-frontmatter');

const ROOT = path.resolve(__dirname, '..');
const BODY = '\n## Use this skill when\nA task.\n## Do not use this skill when\nAnother task.\n## Instructions\nFollow the steps.\n';

function fixture(t, content) {
  const root = tmpDir();
  t.after(() => rmDir(root));
  for (const file of ['scripts/validate-skills.js', 'lib/skill-utils.js', 'lib/skill-schema.js']) {
    const dest = path.join(root, file);
    fs.mkdirSync(path.dirname(dest), { recursive: true });
    fs.copyFileSync(path.join(ROOT, file), dest);
  }
  const skill = path.join(root, 'skills', 'sample');
  fs.mkdirSync(skill, { recursive: true });
  fs.writeFileSync(path.join(skill, 'SKILL.md'), content);
  return { root, skill, run() {
    const env = { ...process.env, STRICT: '1', NODE_PATH: path.join(ROOT, 'node_modules') };
    delete env.WRITE_BASELINE;
    delete env.WRITE_BASELINE_YES;
    return spawnSync(process.execPath, [path.join(root, 'scripts', 'validate-skills.js')], { env, encoding: 'utf8' });
  } };
}

test('a skill without name uses its folder name and passes strict validation', t => {
  const f = fixture(t, '---\ndescription: A complete description.\n---\n' + BODY);
  const result = f.run();
  assert.equal(result.status, 0, result.stderr);
});

test('required headings inside fenced examples do not satisfy strict validation', t => {
  const f = fixture(t, '---\nname: sample\ndescription: Example.\n---\n````markdown\n```\n' + BODY + '\n```\n````\n');
  const result = f.run();
  assert.equal(result.status, 1);
  assert.match(result.stderr, /Missing "Instructions"/);
});

test('helper links are validated in entrypoints and nested playbooks', t => {
  const f = fixture(t, '---\nname: sample\ndescription: Example.\n---\n' + BODY + '\n- [Guide](references/missing.md)\n');
  fs.mkdirSync(path.join(f.skill, 'resources'));
  fs.writeFileSync(path.join(f.skill, 'resources', 'playbook.md'), '- **assets/missing.json**\n- `scripts/missing.py`\n');
  const result = f.run();
  assert.equal(result.status, 1);
  for (const ref of ['references/missing.md', 'assets/missing.json', 'scripts/missing.py']) assert.ok(result.stderr.includes(ref), result.stderr);
});

test('existing root-relative helpers pass and fenced illustrative paths are ignored', t => {
  const f = fixture(t, '---\nname: sample\ndescription: Example.\n---\n' + BODY + '\n- [Guide](resources/guide.md#setup)\n');
  fs.mkdirSync(path.join(f.skill, 'resources'));
  fs.mkdirSync(path.join(f.skill, 'assets'));
  fs.writeFileSync(path.join(f.skill, 'assets', 'example.json'), '{}');
  fs.writeFileSync(path.join(f.skill, 'resources', 'guide.md'), '- **assets/example.json**\n~~~markdown\n- `scripts/illustration.py`\n~~~\n');
  const result = f.run();
  assert.equal(result.status, 0, result.stderr);
});

test('commands, encoded links and inline code preserve valid Markdown content', t => {
  const f = fixture(t, '---\nname: sample\ndescription: Example.\n---\n```inline code```\n'
    + BODY.replace(/^## (.+)$/gm, '  ## $1 ##')
    + '\nRun `scripts/check.sh --strict`. Read [setup](resources/setup%20guide.md#setup).\n');
  fs.mkdirSync(path.join(f.skill, 'scripts'));
  fs.mkdirSync(path.join(f.skill, 'resources'));
  fs.writeFileSync(path.join(f.skill, 'scripts', 'check.sh'), 'exit 0\n');
  fs.writeFileSync(path.join(f.skill, 'resources', 'setup guide.md'), '# Setup\n');
  const result = f.run();
  assert.equal(result.status, 0, result.stderr);
});

test('helper references cannot traverse outside their skill', t => {
  const f = fixture(t, '---\nname: sample\ndescription: Example.\n---\n' + BODY + '\n- `assets/../../outside.md`\n');
  fs.writeFileSync(path.join(f.root, 'skills', 'outside.md'), 'outside');
  assert.equal(f.run().status, 1);
  fs.writeFileSync(path.join(f.skill, 'SKILL.md'), '---\ndescription: Example.\n---\n' + BODY
    + '\n[Outside](assets/%2e%2e/%2e%2e/outside.md)\n');
  assert.equal(f.run().status, 1);
});

test('fence parsing respects delimiter type, length and unclosed blocks', () => {
  assert.equal(stripCodeFences('before\n````md\n```\nnot prose\n```\n````\nafter'), 'before\n\n\n\n\n\nafter');
  assert.deepEqual(findHelperReferences('```\n`assets/example.json`\n~~~\n`assets/still-code.json`'), []);
  assert.deepEqual(findHelperReferences('See [guide](https://example.com/assets/example.json).'), []);
});

test('normalizing invalid frontmatter leaves the original bytes unchanged', t => {
  const f = fixture(t, '---\nname: [broken\ntools: Read\n---\nOriginal body.\n');
  const file = path.join(f.skill, 'SKILL.md');
  const before = fs.readFileSync(file);
  assert.throws(() => normalizeSkill('sample', path.join(f.root, 'skills')), /Cannot normalize/);
  assert.deepEqual(fs.readFileSync(file), before);
});
