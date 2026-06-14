// Single source of truth for SKILL.md frontmatter rules.
// Imported by scripts/validate-skills.js and scripts/normalize-frontmatter.js.

const ALLOWED_FIELDS = new Set([
  'name',
  'description',
  'license',
  'compatibility',
  'metadata',
  'allowed-tools',
]);

// Canonical key order used when rewriting frontmatter.
const FIELD_ORDER = ['name', 'description', 'license', 'compatibility', 'allowed-tools', 'metadata'];

const LIMITS = {
  name: 64,
  description: 1024,
  license: 128,
  compatibility: 500,
  skillLines: 500,
};

const NAME_PATTERN = /^[a-z0-9]+(?:-[a-z0-9]+)*$/;

module.exports = { ALLOWED_FIELDS, FIELD_ORDER, LIMITS, NAME_PATTERN };
