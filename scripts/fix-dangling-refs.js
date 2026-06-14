// One-shot fixer: removes lines that reference a backticked helper file
// (resources/ references/ assets/ scripts/ examples/) which does not exist in the
// skill's directory, and prunes a `## Resources` or `### Reference Files` heading
// that becomes empty as a result. Skips lines inside fenced code blocks.
const fs = require('fs');
const path = require('path');
const { listSkillIds } = require('../lib/skill-utils');

const ROOT = path.resolve(__dirname, '..');
const SKILLS_DIR = path.join(ROOT, 'skills');
const REF_RE = /`((?:resources|references|assets|scripts|examples)\/[A-Za-z0-9._/-]+)`/g;

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
    const headingMatch = /^(#{2,3})\s+(?:\w+\s+)*(?:resources?|reference\s+files?|references?|examples?|example\s+files?)\s*$/i.exec(line.trim());
    if (headingMatch) {
      const level = headingMatch[1].length;
      let j = i + 1;
      while (j < lines.length && lines[j].trim() === '') j += 1;
      let sectionEmpty = j >= lines.length;
      if (!sectionEmpty) {
        const nextHeading = /^(#{1,6})\s/.exec(lines[j].trim());
        if (nextHeading && nextHeading[1].length <= level) sectionEmpty = true;
      }
      if (sectionEmpty) {
        i = j - 1;
        continue;
      }
    }
    out.push(line);
  }
  return out;
}

function cleanLines(lines, skillDir) {
  const kept = [];
  let inFence = false;
  for (const line of lines) {
    if (/^```/.test(line.trim())) { inFence = !inFence; kept.push(line); continue; }
    if (!inFence && lineReferencesMissingFile(line, skillDir)) continue;
    kept.push(line);
  }
  return kept;
}

function run() {
  let fixedSkills = 0;
  let removedLines = 0;
  for (const skillId of listSkillIds(SKILLS_DIR)) {
    const dir = path.join(SKILLS_DIR, skillId);
    const mdPath = path.join(dir, 'SKILL.md');
    const content = fs.readFileSync(mdPath, 'utf8');
    const lines = content.split(/\r?\n/);
    const kept = cleanLines(lines, dir);
    const prunedLines = pruneEmptyResources(kept);
    const changed = kept.length !== lines.length || prunedLines.length !== kept.length;
    let next = prunedLines.join('\n');
    if (changed) next = next.replace(/\n{3,}/g, '\n\n');
    if (next === content) continue;
    fs.writeFileSync(mdPath, next);
    fixedSkills += 1;
    removedLines += lines.length - kept.length;
  }
  console.log(`Removed dangling references / pruned empty resource headings in ${fixedSkills} skills (${removedLines} ref lines removed).`);
}

run();
