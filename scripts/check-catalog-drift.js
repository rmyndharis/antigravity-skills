const fs = require('fs');
const path = require('path');
const { computeArtifacts } = require('./build-catalog');

const ROOT = path.resolve(__dirname, '..');

function readJson(file) {
  return JSON.parse(fs.readFileSync(path.join(ROOT, file), 'utf8'));
}

function readDiskArtifacts() {
  return {
    catalog: readJson('catalog.json'),
    bundles: readJson('bundles.json'),
    aliases: readJson('aliases.json'),
    catalogMarkdown: fs.readFileSync(path.join(ROOT, 'CATALOG.md'), 'utf8'),
  };
}

function stripGeneratedAt(obj) {
  const clone = JSON.parse(JSON.stringify(obj));
  delete clone.generatedAt;
  return JSON.stringify(clone);
}

function stripMarkdownTimestamp(md) {
  return md.replace(/^Generated at: .*$/m, 'Generated at: <timestamp>');
}

// Pure comparison: returns the list of artifact names that differ between the
// freshly computed artifacts and the on-disk ones, ignoring the generatedAt timestamp.
function findDrift(fresh, disk) {
  const checks = [
    ['catalog.json', stripGeneratedAt(fresh.catalog), stripGeneratedAt(disk.catalog)],
    ['bundles.json', stripGeneratedAt(fresh.bundles), stripGeneratedAt(disk.bundles)],
    ['aliases.json', stripGeneratedAt(fresh.aliases), stripGeneratedAt(disk.aliases)],
    ['CATALOG.md', stripMarkdownTimestamp(fresh.catalogMarkdown), stripMarkdownTimestamp(disk.catalogMarkdown)],
  ];
  const drift = [];
  for (const [name, freshValue, diskValue] of checks) {
    if (freshValue !== diskValue) drift.push(name);
  }
  return drift;
}

function run() {
  const fresh = computeArtifacts();
  const disk = readDiskArtifacts();
  const drift = findDrift(fresh, disk);
  if (drift.length) {
    for (const name of drift) {
      console.error(`Catalog drift detected in ${name}.`);
    }
    console.error('Run `npm run build:catalog` and commit the regenerated artifacts.');
    process.exit(1);
  }
  console.log('Catalog artifacts are in sync.');
}

if (require.main === module) {
  run();
}

module.exports = { findDrift, readDiskArtifacts, run };
