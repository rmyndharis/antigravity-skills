const test = require('node:test');
const assert = require('node:assert');
const { scoreSkill } = require('../bin/cli.js');
const { tokenize, unique } = require('../lib/skill-utils');

function score(skill, query) {
  return scoreSkill(skill, unique(tokenize(query)));
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

test('scoreSkill matches whole words, not fragments of longer words', () => {
  const airflow = { id: 'airflow-dag-patterns', name: 'airflow-dag-patterns', description: 'Build Apache Airflow DAGs.', tags: ['airflow'] };
  const django = { id: 'django-pro', name: 'django-pro', description: 'Master Django with async views.', tags: ['django'] };
  const golang = { id: 'golang-pro', name: 'golang-pro', description: 'Master Go concurrency.', tags: ['golang'] };
  assert.strictEqual(score(airflow, 'ai'), 0);
  assert.strictEqual(score(django, 'go'), 0);
  assert.ok(score(golang, 'go') > 0);
  assert.strictEqual(score(golang, '++'), 0);
});

test('scoreSkill matches word prefixes only for tokens of four or more characters', () => {
  const skill = { id: 'k8s-manifest-generator', name: 'k8s-manifest-generator', description: 'Create Kubernetes manifests.', tags: [] };
  assert.ok(score(skill, 'kube') > 0);
  assert.strictEqual(score(skill, 'kub'), 0);
});
