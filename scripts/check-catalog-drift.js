const fs = require('fs');
const path = require('path');
const { computeArtifacts } = require('./build-catalog');

const ROOT = path.resolve(__dirname, '..');

function readJson(file, root) {
  return JSON.parse(fs.readFileSync(path.join(root, file), 'utf8'));
}

function readDiskArtifacts(root = ROOT) {
  try {
    return {
      catalog: readJson('catalog.json', root),
      bundles: readJson('bundles.json', root),
      aliases: readJson('aliases.json', root),
      catalogMarkdown: fs.readFileSync(path.join(root, 'CATALOG.md'), 'utf8'),
    };
  } catch (err) {
    throw new Error(`check-catalog-drift: failed to read a catalog artifact (${err.message}). Run \`npm run build:catalog\` to generate them.`, { cause: err });
  }
}

// Windows checkouts may convert CATALOG.md to CRLF.
function toLf(md) {
  return md.replace(/\r\n/g, '\n');
}

// Pure comparison: returns the list of artifact names that differ between the
// freshly computed artifacts and the on-disk ones.
function findDrift(fresh, disk) {
  const checks = [
    ['catalog.json', JSON.stringify(fresh.catalog), JSON.stringify(disk.catalog)],
    ['bundles.json', JSON.stringify(fresh.bundles), JSON.stringify(disk.bundles)],
    ['aliases.json', JSON.stringify(fresh.aliases), JSON.stringify(disk.aliases)],
    ['CATALOG.md', toLf(fresh.catalogMarkdown), toLf(disk.catalogMarkdown)],
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
