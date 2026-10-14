const fs = require('fs');
const path = require('path');

const ROOT = path.resolve(__dirname, '..');
const source = path.join(ROOT, 'skills', 'antigravity-skills-manager', 'SKILL.md');
const destination = path.join(ROOT, 'plugins', 'antigravity-skills-manager', 'skills', 'antigravity-skills-manager', 'SKILL.md');

try {
  const content = fs.readFileSync(source);
  if (process.argv.includes('--check')) {
    if (!fs.existsSync(destination) || !content.equals(fs.readFileSync(destination))) {
      throw new Error('Manager plugin skill is out of sync. Run `npm run build:catalog`.');
    }
    console.log('Manager plugin skill is in sync.');
  } else {
    fs.mkdirSync(path.dirname(destination), { recursive: true });
    fs.writeFileSync(destination, content);
    console.log('Updated manager plugin skill.');
  }
} catch (err) {
  console.error(err.message);
  process.exitCode = 1;
}
