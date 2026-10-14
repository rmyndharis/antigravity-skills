const fs = require('fs');
const path = require('path');
const yaml = require('yaml');

function isPlainObject(value) {
  return value && typeof value === 'object' && !Array.isArray(value);
}

function truncate(value, limit) {
  if (!value || value.length <= limit) return value || '';
  return `${value.slice(0, limit - 3)}...`;
}

function stripCodeFences(content) {
  let fence = null;
  return content.split(/\r?\n/).map(line => {
    const match = /^ {0,3}(`{3,}|~{3,})(.*)$/.exec(line);
    if (match) {
      if (!fence && match[1][0] === '`' && match[2].includes('`')) return line;
      if (!fence) fence = match[1];
      else if (match[1][0] === fence[0] && match[1].length >= fence.length && !match[2].trim()) fence = null;
      return '';
    }
    return fence ? '' : line;
  }).join('\n');
}

function findHelperReferences(content) {
  const prose = stripCodeFences(content);
  const prefix = '(?:\\./)?(?:resources|references|assets|scripts|examples)/';
  const patterns = [
    new RegExp('`(' + prefix + '[^`\\s]+)(?:[ \\t]+[^`\\r\\n]*)?`', 'g'),
    new RegExp('\\*\\*(' + prefix + '[^*\\r\\n]+)\\*\\*', 'g'),
    new RegExp('\\[[^\\]\\r\\n]*\\]\\((' + prefix + '[^\\s)]+)(?:\\s+"[^"]*")?\\)', 'g'),
  ];
  const references = [];
  for (const pattern of patterns) {
    for (const match of prose.matchAll(pattern)) {
      const reference = match[1].split('#')[0];
      try {
        references.push(decodeURIComponent(reference));
      } catch {
        references.push(reference);
      }
    }
  }
  return unique(references);
}

function parseFrontmatter(content) {
  const sanitized = content.replace(/^\uFEFF/, '');
  const lines = sanitized.split(/\r?\n/);
  if (!lines.length || lines[0].trim() !== '---') {
    return { data: {}, body: content, errors: [], hasFrontmatter: false };
  }

  let endIndex = -1;
  for (let i = 1; i < lines.length; i += 1) {
    if (lines[i].trim() === '---') {
      endIndex = i;
      break;
    }
  }

  if (endIndex === -1) {
    return {
      data: {},
      body: content,
      errors: ['Missing closing frontmatter delimiter (---).'],
      hasFrontmatter: true,
    };
  }

  const errors = [];
  const fmText = lines.slice(1, endIndex).join('\n');
  let data = {};

  try {
    const doc = yaml.parseDocument(fmText, { prettyErrors: false });
    if (doc.errors && doc.errors.length) {
      errors.push(...doc.errors.map(error => error.message));
    }
    data = doc.toJS();
  } catch (err) {
    errors.push(err.message);
    data = {};
  }

  if (!isPlainObject(data)) {
    errors.push('Frontmatter must be a YAML mapping/object.');
    data = {};
  }

  const body = lines.slice(endIndex + 1).join('\n');
  return { data, body, errors, hasFrontmatter: true };
}

function tokenize(value) {
  if (!value) return [];
  return value
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, ' ')
    .split(' ')
    .map(token => token.trim())
    .filter(Boolean);
}

function unique(list) {
  const seen = new Set();
  const result = [];
  for (const item of list) {
    if (!item || seen.has(item)) continue;
    seen.add(item);
    result.push(item);
  }
  return result;
}

function readSkill(skillDir, skillId) {
  const skillPath = path.join(skillDir, skillId, 'SKILL.md');
  let content;
  try {
    content = fs.readFileSync(skillPath, 'utf8');
  } catch (err) {
    return {
      id: skillId,
      name: skillId,
      description: '',
      tags: [],
      path: skillPath,
      content: '',
      errors: [`Failed to read SKILL.md: ${err.message}`],
      missing: true,
    };
  }

  const { data, errors } = parseFrontmatter(content);
  const name = typeof data.name === 'string' && data.name.trim()
    ? data.name.trim()
    : skillId;
  const description = typeof data.description === 'string'
    ? data.description.trim()
    : '';

  const rawTags = Array.isArray(data.tags) || (typeof data.tags === 'string' && data.tags.trim())
    ? data.tags
    : (isPlainObject(data.metadata) ? data.metadata.tags : undefined);
  let tags = [];
  if (Array.isArray(rawTags)) {
    tags = rawTags.map(tag => String(tag).trim());
  } else if (typeof rawTags === 'string' && rawTags.trim()) {
    const parts = rawTags.includes(',')
      ? rawTags.split(',')
      : rawTags.split(/\s+/);
    tags = parts.map(tag => tag.trim());
  }

  tags = tags.filter(Boolean);

  return {
    id: skillId,
    name,
    description,
    tags,
    path: skillPath,
    content,
    errors: errors || [],
    missing: false,
  };
}

function listSkillIds(skillsDir) {
  return fs.readdirSync(skillsDir, { withFileTypes: true })
    .filter(entry => {
      if (entry.name.startsWith('.') || !entry.isDirectory()) return false;
      const skillPath = path.join(skillsDir, entry.name, 'SKILL.md');
      return fs.existsSync(skillPath) && fs.lstatSync(skillPath).isFile();
    })
    .map(entry => entry.name)
    .sort();
}

module.exports = {
  isPlainObject,
  truncate,
  stripCodeFences,
  findHelperReferences,
  listSkillIds,
  parseFrontmatter,
  readSkill,
  tokenize,
  unique,
};
