const test = require('node:test');
const assert = require('node:assert');
const { scoreSkill } = require('../bin/cli.js');
const { tokenize, unique } = require('../lib/skill-utils');

function score(skill, query) {
  const q = query.toLowerCase().trim();
  return scoreSkill(skill, q, unique(tokenize(q)));
}

test('scoreSkill matches via the triggers field', () => {
  const skill = {
    id: 'some-skill',
    name: 'Some Skill',
    description: 'Generic helper.',
    tags: [],
    triggers: ['kubernetes', 'helm'],
  };
  assert.ok(score(skill, 'kubernetes') > 0, 'trigger token should contribute to score');
});

test('scoreSkill is safe for a skill with no tags and no triggers', () => {
  const skill = { id: 'workflow-patterns', name: 'workflow-patterns', description: 'Patterns.' };
  assert.doesNotThrow(() => score(skill, 'patterns'));
});
