import contextlib
import importlib.util
import io
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import Mock, patch


ROOT = Path(__file__).resolve().parents[1]
OPTIMIZER_PATH = ROOT / 'skills/prompt-engineering-patterns/scripts/optimize-prompt.py'
API_PATH = ROOT / 'skills/api-design-principles/assets/rest-api-template.py'


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    previous = sys.dont_write_bytecode
    sys.dont_write_bytecode = True
    try:
        spec.loader.exec_module(module)
    finally:
        sys.dont_write_bytecode = previous
    return module


optimizer_module = load_module('prompt_optimizer_asset', OPTIMIZER_PATH)


class TestPromptOptimizer(unittest.TestCase):
    def make_optimizer(self, client=None, cases=None):
        if client is None:
            client = Mock(complete=Mock(return_value='correct'))
        if cases is None:
            cases = [optimizer_module.TestCase({'text': 'input'}, 'correct')]
        optimizer = optimizer_module.PromptOptimizer(client, cases)
        self.addCleanup(optimizer.shutdown)
        return optimizer

    def test_last_iteration_returns_best_evaluated_prompt(self):
        client = Mock()
        client.complete.side_effect = lambda prompt: 'correct' if 'clear, concise format' in prompt else 'wrong'
        optimizer = self.make_optimizer(client)
        with contextlib.redirect_stdout(io.StringIO()):
            result = optimizer.optimize('Classify: {text}', max_iterations=1)
        self.assertEqual(result['best_score'], 1.0)
        self.assertIn('clear, concise format', result['best_prompt'])

    def test_default_iteration_limit_keeps_final_improvement(self):
        optimizer = self.make_optimizer()
        def evaluate(prompt):
            return {'avg_accuracy': prompt.count('clear, concise format') / 10, 'avg_latency': 0.0}
        with patch.object(optimizer, 'evaluate_prompt', side_effect=evaluate), contextlib.redirect_stdout(io.StringIO()):
            result = optimizer.optimize('base')
        self.assertEqual(result['best_score'], 0.5)
        self.assertEqual(result['best_prompt'].count('clear, concise format'), 5)

    def test_concise_or_example_variation_can_win(self):
        for target in ('concise', 'example'):
            with self.subTest(target=target):
                client = Mock()
                if target == 'concise':
                    client.complete.side_effect = lambda prompt: 'correct' if 'in order to' not in prompt else 'wrong'
                else:
                    client.complete.side_effect = lambda prompt: 'correct' if 'Example:' in prompt else 'wrong'
                optimizer = self.make_optimizer(client)
                with contextlib.redirect_stdout(io.StringIO()):
                    result = optimizer.optimize('Read {text} in order to summarize it.', max_iterations=1)
                self.assertEqual(result['best_score'], 1.0)
                if target == 'concise':
                    self.assertNotIn('in order to', result['best_prompt'])
                else:
                    self.assertIn('Example:', result['best_prompt'])

    def test_export_includes_final_winner_without_an_extra_completion(self):
        client = Mock()
        client.complete.side_effect = lambda prompt: 'correct' if prompt.startswith('winner') else 'wrong'
        optimizer = self.make_optimizer(client)
        with patch.object(optimizer, 'generate_variations', return_value=['winner {text}']), contextlib.redirect_stdout(io.StringIO()):
            result = optimizer.optimize('base {text}', max_iterations=1)
        self.assertEqual(client.complete.call_count, 2)
        with tempfile.TemporaryDirectory() as directory:
            filename = Path(directory) / 'results.json'
            optimizer.export_results(filename)
            history = json.loads(filename.read_text())
        self.assertEqual(history[-1]['prompt'], result['best_prompt'])
        self.assertEqual(history[-1]['metrics']['avg_accuracy'], result['best_score'])
        self.assertEqual([entry['iteration'] for entry in history], [0, 1])

    def test_repeated_optimization_keeps_independent_run_histories(self):
        optimizer = self.make_optimizer()
        with contextlib.redirect_stdout(io.StringIO()):
            first = optimizer.optimize('first {text}')
        saved_first = json.loads(json.dumps(first))
        with contextlib.redirect_stdout(io.StringIO()):
            second = optimizer.optimize('second {text}')
        self.assertEqual(first, saved_first)
        self.assertIsNot(first['history'], second['history'])
        self.assertEqual([entry['prompt'] for entry in second['history']], ['second {text}'])

    def test_percentile_uses_linear_interpolation(self):
        cases = [optimizer_module.TestCase({'text': str(i)}, 'correct') for i in range(3)]
        optimizer = self.make_optimizer(cases=cases)
        optimizer.shutdown()
        optimizer.executor = ThreadPoolExecutor(max_workers=1)
        with patch.object(optimizer_module.time, 'time', side_effect=[0, 0, 0, 10, 0, 20]):
            metrics = optimizer.evaluate_prompt('{text}')
        self.assertEqual(metrics['avg_latency'], 10.0)
        self.assertAlmostEqual(metrics['p95_latency'], 19.0)
        self.assertEqual(metrics['avg_accuracy'], 1.0)
        self.assertEqual(metrics['success_rate'], 1.0)
        json.dumps(metrics, allow_nan=False)

    def test_single_sample_percentile(self):
        optimizer = self.make_optimizer()
        with patch.object(optimizer_module.time, 'time', side_effect=[0, 7]):
            metrics = optimizer.evaluate_prompt('{text}')
        self.assertEqual(metrics['p95_latency'], 7.0)

    def test_empty_test_cases_are_rejected(self):
        optimizer = self.make_optimizer()
        with self.assertRaisesRegex(ValueError, 'At least one test case'):
            optimizer.evaluate_prompt('{text}', test_cases=[])
        optimizer.test_suite = []
        with self.assertRaisesRegex(ValueError, 'At least one test case'):
            optimizer.evaluate_prompt('{text}')

    def test_invalid_iteration_limit_is_rejected(self):
        optimizer = self.make_optimizer()
        for value in (0, -1, 1.5):
            with self.subTest(value=value), self.assertRaisesRegex(ValueError, 'positive integer'):
                optimizer.optimize('{text}', max_iterations=value)

    def test_format_contract_preserves_escaping_and_format_specifiers(self):
        client = Mock(complete=Mock(return_value='correct'))
        optimizer = self.make_optimizer(client, [optimizer_module.TestCase({'number': 1.25}, 'correct')])
        optimizer.evaluate_prompt('Literal {{braces}}, value {number:.1f}')
        client.complete.assert_called_once_with('Literal {braces}, value 1.2')
        with self.assertRaises(KeyError):
            optimizer.evaluate_prompt('{missing}')
        self.assertEqual(client.complete.call_count, 1)

    def test_json_templates_render_with_the_bundled_optimizer(self):
        path = ROOT / 'skills/prompt-engineering-patterns/assets/prompt-template-library.md'
        content = path.read_text()
        for heading, variable, key in (
            ('Named Entity Recognition', 'text', 'persons'),
            ('Structured Data Extraction', 'posting', 'title'),
        ):
            with self.subTest(template=heading):
                template = re.search(r'### ' + heading + r'\n```\n([\s\S]*?)\n```', content).group(1)
                client = Mock(complete=Mock(return_value='correct'))
                optimizer = self.make_optimizer(client, [optimizer_module.TestCase({variable: 'Example'}, 'correct')])
                optimizer.evaluate_prompt(template)
                rendered = client.complete.call_args.args[0]
                payload = rendered[rendered.index('{'):]
                self.assertIn(key, json.loads(payload))

    def test_failed_responses_do_not_count_as_success(self):
        client = Mock(complete=Mock(return_value='   '))
        optimizer = self.make_optimizer(client)
        metrics = optimizer.evaluate_prompt('{text}')
        self.assertEqual(metrics['success_rate'], 0.0)
        self.assertEqual(metrics['avg_accuracy'], 0.0)
        client.complete.return_value = None
        with self.assertRaisesRegex(TypeError, 'must be strings'):
            optimizer.evaluate_prompt('{text}')
        client.complete.side_effect = RuntimeError('completion failed')
        with self.assertRaisesRegex(RuntimeError, 'completion failed'):
            optimizer.evaluate_prompt('{text}')

    def test_script_runs_without_site_packages_and_exports_json(self):
        with tempfile.TemporaryDirectory() as directory:
            result = subprocess.run([sys.executable, '-S', str(OPTIMIZER_PATH)], cwd=directory, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            history = json.loads((Path(directory) / 'optimization_results.json').read_text())
        self.assertEqual(history[0]['metrics']['avg_accuracy'], 1.0)


API_DEPENDENCIES_AVAILABLE = all(importlib.util.find_spec(name) is not None for name in ('fastapi', 'httpx', 'email_validator'))


@unittest.skipUnless(API_DEPENDENCIES_AVAILABLE, 'Install the FastAPI asset test dependencies to run API regressions')
class TestRestApiTemplate(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from fastapi.testclient import TestClient
        cls.api = load_module('rest_api_asset', API_PATH)
        cls.client = TestClient(cls.api.app)

    @classmethod
    def tearDownClass(cls):
        cls.client.close()

    def test_missing_user_error_contract_for_all_callers(self):
        for method in ('get', 'patch', 'delete'):
            with self.subTest(method=method):
                options = {'json': {}} if method == 'patch' else {}
                response = getattr(self.client, method)('/api/users/999', **options)
                self.assertEqual(response.status_code, 404)
                error = self.api.ErrorResponse.model_validate(response.json())
                self.assertEqual(error.message, 'User not found')
                self.assertEqual(error.details[0].field, 'id')
                self.assertEqual(error.details[0].code, 'NOT_FOUND')

    def test_existing_user_endpoints_preserve_success_responses(self):
        response = self.client.get('/api/users/123')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['id'], '123')
        response = self.client.patch('/api/users/123', json={'name': 'Updated'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['name'], 'Updated')
        self.assertEqual(self.client.delete('/api/users/123').status_code, 204)

    def test_patch_rejects_explicit_null_fields(self):
        for field in ('name', 'email', 'status'):
            with self.subTest(field=field):
                response = self.client.patch('/api/users/123', json={field: None})
                self.assertEqual(response.status_code, 422)
                self.assertEqual(response.json()['detail'][0]['loc'], ['body', field])

    def test_patch_preserves_omitted_fields_and_accepts_valid_updates(self):
        response = self.client.patch('/api/users/123', json={})
        self.assertEqual(response.status_code, 200)
        user = self.api.User.model_validate(response.json())
        self.assertEqual(user.name, 'User Name')
        self.assertEqual(user.email, 'user@example.com')
        self.assertEqual(user.status, self.api.UserStatus.ACTIVE)
        changes = {'name': 'Updated', 'email': 'updated@example.com', 'status': 'inactive'}
        response = self.client.patch('/api/users/123', json=changes)
        self.assertEqual(response.status_code, 200)
        for field, expected in changes.items():
            self.assertEqual(response.json()[field], expected)


if __name__ == '__main__':
    unittest.main()
