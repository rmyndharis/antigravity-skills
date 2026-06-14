// One-shot fixer: removes lines that reference a backticked helper file
// (resources/ references/ assets/ scripts/) which does not exist in the skill's
// directory, and prunes a `## Resources` heading that becomes empty as a result.
const fs = require('fs');
const path = require('path');
const { listSkillIds } = require('../lib/skill-utils');

const ROOT = path.resolve(__dirname, '..');
const SKILLS_DIR = path.join(ROOT, 'skills');
const REF_RE = /`((?:resources|references|assets|scripts)\/[A-Za-z0-9._/-]+)`/g;

function lineReferencesMissingFile(line, skillDir) {
  REF_RE.lastIndex = 0;
  let match;
  let hasMissing = false;
  while ((match = REF_RE.exec(line)) !== null) {
    if (!fs.existsSync(path.join(skillDir, match[1]))) {
      hasMissing = true;
    }
  }
  return hasMissing;
}

function pruneEmptyResources(lines) {
  const out = [];
  for (let i = 0; i < lines.length; i += 1) {
    const line = lines[i];
    if (/^##\s+(?:resources?|reference\s+files?|references?)\s*$/i.test(line.trim())) {
      let j = i + 1;
      while (j < lines.length && lines[j].trim() === '') j += 1;
      const sectionEmpty = j >= lines.length || /^##\s/.test(lines[j].trim());
      if (sectionEmpty) {
        i = j - 1; // skip the heading and the trailing blank lines
        continue;
      }
    }
    out.push(line);
  }
  return out;
}

function run() {
  let fixedSkills = 0;
  let removedLines = 0;
  for (const skillId of listSkillIds(SKILLS_DIR)) {
    const dir = path.join(SKILLS_DIR, skillId);
    const mdPath = path.join(dir, 'SKILL.md');
    const content = fs.readFileSync(mdPath, 'utf8');
    const lines = content.split(/\r?\n/);
    const kept = lines.filter(line => !lineReferencesMissingFile(line, dir));
    const next = pruneEmptyResources(kept).join('\n');
    if (next === content) continue;
    fs.writeFileSync(mdPath, next);
    fixedSkills += 1;
    removedLines += lines.length - kept.length;
  }
  console.log(`Removed dangling references / pruned empty resource headings in ${fixedSkills} skills (${removedLines} ref lines removed).`);
}

run();
