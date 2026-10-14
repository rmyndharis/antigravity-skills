import unittest
from unittest.mock import patch
import sys
import os
import io
import json
import shutil
import stat
import tempfile
from pathlib import Path

# Ensure repository root is in sys.path
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

import skills_cli

TEST_REVISION = 'a' * 40
PINNED_RAW_BASE = skills_cli.RAW_BASE_URL + TEST_REVISION + '/'

MOCK_CATALOG = {
    "generatedAt": "2026-08-02T00:00:00.000Z",
    "total": 2,
    "skills": [
        {
            "id": "antigravity-skills-manager",
            "name": "antigravity-skills-manager",
            "description": "Global skills manager for Google Antigravity.",
            "category": "workflow",
            "tags": ["skills", "installer", "manager"],
            "triggers": ["skills", "skill"],
            "path": "skills/antigravity-skills-manager/SKILL.md"
        },
        {
            "id": "agent-orchestration-improve-agent",
            "name": "agent-orchestration-improve-agent",
            "description": "Systematic improvement of existing agents.",
            "category": "workflow",
            "tags": ["agent", "improve"],
            "triggers": ["agent", "improve"],
            "path": "skills/agent-orchestration-improve-agent/SKILL.md"
        }
    ]
}

class TestSkillsCLI(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.environment = patch.dict(os.environ, {"AG_SKILLS_DIR": self.temp_dir.name})
        self.environment.start()
        self.addCleanup(self.environment.stop)
        revision = patch.object(skills_cli, '_remote_revision', TEST_REVISION)
        revision.start()
        self.addCleanup(revision.stop)
        for name in ('fetch_json', 'fetch_bytes'):
            fetch = patch.object(skills_cli, name, side_effect=AssertionError('unexpected network request'))
            fetch.start()
            self.addCleanup(fetch.stop)

    def tearDown(self):
        self.temp_dir.cleanup()

    def run_cli(self, args):
        stdout_capture = io.StringIO()
        stderr_capture = io.StringIO()
        with patch.object(sys, 'argv', ['skills_cli.py'] + args):
            with patch('sys.stdout', stdout_capture), patch('sys.stderr', stderr_capture):
                exit_code = 0
                try:
                    skills_cli.main()
                except SystemExit as e:
                    exit_code = e.code if isinstance(e.code, int) else 1
        return exit_code, stdout_capture.getvalue(), stderr_capture.getvalue()

    # TC-CLI-LIST-01: List catalog skills
    def test_list_skills(self):
        code, out, err = self.run_cli(['list'])
        self.assertEqual(code, 0)
        self.assertIn("Found", out)

    # TC-CLI-LIST-02: Empty catalog handling
    @patch('skills_cli.load_catalog', return_value={'skills': []})
    def test_list_empty_catalog(self, mock_catalog):
        code, out, err = self.run_cli(['list'])
        self.assertEqual(code, 0)
        self.assertIn("Found 0 skill(s)", out)
        self.assertIn("No skills available in catalog", out)

    # TC-CLI-LIST-03: Malformed catalog error
    @patch('skills_cli.load_catalog', return_value=None)
    def test_list_malformed_catalog(self, mock_catalog):
        code, out, err = self.run_cli(['list'])
        self.assertEqual(code, 1)
        self.assertIn("Failed to load catalog", err)

    # TC-CLI-SEARCH-01: Match by ID/Name
    @patch('skills_cli.load_catalog', return_value=MOCK_CATALOG)
    def test_search_manager(self, mock_catalog):
        code, out, err = self.run_cli(['search', 'manager'])
        self.assertEqual(code, 0)
        self.assertIn("antigravity-skills-manager", out)

    # TC-CLI-SEARCH-02: Case-insensitive search
    @patch('skills_cli.load_catalog', return_value=MOCK_CATALOG)
    def test_search_case_insensitive(self, mock_catalog):
        code, out, err = self.run_cli(['search', 'MANAGER'])
        self.assertEqual(code, 0)
        self.assertIn("antigravity-skills-manager", out)

    # TC-CLI-SEARCH-03: Tag/Category match
    @patch('skills_cli.load_catalog', return_value=MOCK_CATALOG)
    def test_search_workflow(self, mock_catalog):
        code, out, err = self.run_cli(['search', 'workflow'])
        self.assertEqual(code, 0)
        self.assertIn("Found 2 skill(s)", out)

    # TC-CLI-SEARCH-04: No matching results
    @patch('skills_cli.load_catalog', return_value=MOCK_CATALOG)
    def test_search_no_match(self, mock_catalog):
        code, out, err = self.run_cli(['search', 'nonexistent_xyz_999'])
        self.assertEqual(code, 0)
        self.assertIn("Found 0 skill(s)", out)
        self.assertIn("No skills found matching filter", out)

    # TC-CLI-SEARCH-05: Missing search term
    def test_search_missing_term(self):
        code, out, err = self.run_cli(['search'])
        self.assertEqual(code, 1)
        self.assertIn("Usage:", err)

    # TC-CLI-INST-01: Valid skill installation
    @patch('skills_cli.load_catalog', return_value=MOCK_CATALOG)
    def test_install_valid_skill(self, mock_catalog):
        code, out, err = self.run_cli(['install', 'antigravity-skills-manager'])
        self.assertEqual(code, 0)
        self.assertIn("[OK] Successfully installed", out)
        installed_file = os.path.join(self.temp_dir.name, 'antigravity-skills-manager', 'SKILL.md')
        self.assertTrue(os.path.exists(installed_file))
        with open(installed_file, 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertIn("name: antigravity-skills-manager", content)

    # TC-CLI-INST-02: Re-installation / Overwrite
    @patch('skills_cli.load_catalog', return_value=MOCK_CATALOG)
    def test_install_overwrite(self, mock_catalog):
        code1, out1, err1 = self.run_cli(['install', 'antigravity-skills-manager'])
        self.assertEqual(code1, 0)
        code2, out2, err2 = self.run_cli(['install', 'antigravity-skills-manager'])
        self.assertEqual(code2, 0)
        self.assertIn("[OK] Successfully installed", out2)

    # TC-CLI-INST-03: Non-existent skill ID
    @patch('skills_cli.load_catalog', return_value=MOCK_CATALOG)
    def test_install_nonexistent_skill(self, mock_catalog):
        code, out, err = self.run_cli(['install', 'unknown-skill-999'])
        self.assertEqual(code, 1)
        self.assertIn("Skill 'unknown-skill-999' not found in catalog", err)

    # TC-CLI-INST-04: Unmocked skill installation from disk catalog.json
    def test_install_unmocked(self):
        code, out, err = self.run_cli(['install', 'antigravity-skills-manager'])
        self.assertEqual(code, 0, f"Unmocked install failed: {err}")
        self.assertIn("[OK] Successfully installed", out)
        installed_file = os.path.join(self.temp_dir.name, 'antigravity-skills-manager', 'SKILL.md')
        self.assertTrue(os.path.exists(installed_file))

    # TC-CLI-INSTD-01: Clean directory state
    def test_installed_empty(self):
        code, out, err = self.run_cli(['installed'])
        self.assertEqual(code, 0)
        self.assertIn("No skills currently installed", out)

    # TC-CLI-INSTD-02: Multiple installed skills
    @patch('skills_cli.load_catalog', return_value=MOCK_CATALOG)
    def test_installed_multiple(self, mock_catalog):
        self.run_cli(['install', 'antigravity-skills-manager'])
        code, out, err = self.run_cli(['installed'])
        self.assertEqual(code, 0)
        self.assertIn("antigravity-skills-manager", out)
        self.assertIn("[OK] SKILL.md", out)

    # TC-CLI-INSTD-03: Non-skill folder ignore/flag
    def test_installed_folder_without_skill_md(self):
        fake_folder = os.path.join(self.temp_dir.name, 'dummy-folder')
        os.makedirs(fake_folder, exist_ok=True)
        code, out, err = self.run_cli(['installed'])
        self.assertEqual(code, 0)
        self.assertIn("dummy-folder", out)
        self.assertIn("[X] No SKILL.md", out)

    # TC-CLI-DIR-01: Default destination is the same global dir bin/cli.js uses
    def test_default_skills_dir_matches_node_cli(self):
        del os.environ["AG_SKILLS_DIR"]
        expected = os.path.join(os.path.expanduser("~"), ".gemini", "antigravity", "skills")
        self.assertEqual(skills_cli.get_skills_dir(), os.path.abspath(expected))

    # TC-CLI-DIR-02: AG_SKILLS_DIR expands a leading ~, as bin/cli.js does
    def test_ag_skills_dir_expands_tilde(self):
        os.environ["AG_SKILLS_DIR"] = "~/some-skills-dir"
        resolved = skills_cli.get_skills_dir()
        self.assertEqual(resolved, os.path.join(os.path.expanduser("~"), "some-skills-dir"))
        self.assertNotIn("~", resolved)

    # TC-CLI-INST-05: A failed install must exit non-zero, not report soft success
    @patch('skills_cli.fetch_bytes', return_value=None)
    @patch('skills_cli.fetch_json', side_effect=[{'sha': TEST_REVISION}, None])
    @patch('skills_cli.load_catalog', return_value={'skills': [
        {'id': 'ghost-skill', 'name': 'ghost-skill', 'path': 'skills/ghost-skill/SKILL.md'}
    ]})
    def test_install_failure_exits_nonzero(self, mock_catalog, mock_json, mock_bytes):
        code, out, err = self.run_cli(['install', 'ghost-skill'])
        self.assertEqual(code, 1)
        self.assertIn("Installation incomplete", err)

    # TC-CLI-INST-06: A catalog id must not be able to write outside the skills dir
    @patch('skills_cli.load_catalog', return_value={'skills': [
        {'id': '../escaped', 'name': '../escaped', 'path': 'skills/api-design-principles/SKILL.md'}
    ]})
    def test_install_refuses_path_escape(self, mock_catalog):
        code, out, err = self.run_cli(['install', '../escaped'])
        self.assertEqual(code, 1)
        self.assertIn("invalid skill id", err)
        escaped = os.path.join(os.path.dirname(self.temp_dir.name), 'escaped')
        self.assertFalse(os.path.exists(escaped))

    # TC-CLI-INST-07: Reinstalling replaces the folder so upstream deletions do not survive
    @patch('skills_cli.load_catalog', return_value=MOCK_CATALOG)
    def test_reinstall_removes_stale_files(self, mock_catalog):
        self.run_cli(['install', 'antigravity-skills-manager'])
        stale = os.path.join(self.temp_dir.name, 'antigravity-skills-manager', 'stale-upstream-file.md')
        with open(stale, 'w', encoding='utf-8') as f:
            f.write('removed upstream')
        code, out, err = self.run_cli(['install', 'antigravity-skills-manager'])
        self.assertEqual(code, 0)
        self.assertFalse(os.path.exists(stale))

    # TC-CLI-INST-08: A catalog path must not read from outside the package
    @patch('skills_cli.load_catalog')
    def test_install_refuses_catalog_path_traversal(self, mock_catalog):
        secrets = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, secrets)
        with open(os.path.join(secrets, 'id_rsa'), 'w', encoding='utf-8') as f:
            f.write('private key material')
        with open(os.path.join(secrets, 'SKILL.md'), 'w', encoding='utf-8') as f:
            f.write('decoy')
        rel = os.path.relpath(secrets, REPO_ROOT).replace(os.sep, '/')
        mock_catalog.return_value = {'skills': [
            {'id': 'innocent', 'name': 'innocent', 'path': f'{rel}/SKILL.md'}
        ]}
        code, out, err = self.run_cli(['install', 'innocent'])
        self.assertEqual(code, 1)
        self.assertIn("unsafe skill path", err)
        self.assertFalse(os.path.exists(os.path.join(self.temp_dir.name, 'innocent', 'id_rsa')))

    # TC-CLI-INST-09: A catalog path must not walk the pinned repo prefix off the URL
    @patch('skills_cli.fetch_json')
    @patch('skills_cli.load_catalog')
    def test_install_refuses_url_repo_substitution(self, mock_catalog, mock_fetch):
        mock_catalog.return_value = {'skills': [{
            'id': 'innocent',
            'name': 'innocent',
            'path': 'skills/../../../../attacker-org/malicious-repo/contents/x/SKILL.md',
        }]}
        code, out, err = self.run_cli(['install', 'innocent'])
        self.assertEqual(code, 1)
        self.assertIn("unsafe skill path", err)
        mock_fetch.assert_not_called()

    # TC-CLI-INST-10: API items pointing outside the requested folder are skipped
    def test_download_skips_items_outside_requested_folder(self):
        target = os.path.join(self.temp_dir.name, 'out')
        items = [{'name': 'evil.md', 'path': 'skills/other-skill/evil.md', 'type': 'file'}]
        with patch('skills_cli.fetch_json', return_value=items), \
             patch('skills_cli.fetch_bytes', return_value=b'x') as mock_bytes:
            ok = skills_cli.download_folder_recursive('skills/innocent', target)
        self.assertFalse(ok)
        mock_bytes.assert_not_called()
        self.assertFalse(os.path.exists(os.path.join(target, 'evil.md')))

    # TC-CLI-SEARCH-06: Multi-word queries match on every term, not the exact phrase
    @patch('skills_cli.load_catalog', return_value=MOCK_CATALOG)
    def test_search_multi_word(self, mock_catalog):
        code, out, err = self.run_cli(['search', 'improve agent'])
        self.assertEqual(code, 0)
        self.assertIn("agent-orchestration-improve-agent", out)
        self.assertIn("Found 1 skill(s)", out)

    def install_fixture(self):
        package = Path(self.temp_dir.name) / 'package'
        source = package / 'skills' / 'sample'
        source.mkdir(parents=True)
        (source / 'SKILL.md').write_text('new instructions', encoding='utf-8')
        target = Path(self.temp_dir.name) / 'installed' / 'sample'
        target.mkdir(parents=True)
        (target / 'SKILL.md').write_text('old instructions', encoding='utf-8')
        (target / 'local.txt').write_text('local content', encoding='utf-8')
        os.environ['AG_SKILLS_DIR'] = str(target.parent)
        for name, value in (
            ('__file__', str(package / 'skills_cli.py')),
            ('load_catalog', lambda: {'skills': [{'id': 'sample', 'name': 'sample',
                                                 'path': 'skills/sample/SKILL.md'}]}),
        ):
            replacement = patch.object(skills_cli, name, value)
            replacement.start()
            self.addCleanup(replacement.stop)
        return source, target

    def assert_old_installation(self, target):
        self.assertEqual((target / 'SKILL.md').read_text(encoding='utf-8'), 'old instructions')
        self.assertEqual((target / 'local.txt').read_text(encoding='utf-8'), 'local content')

    def test_failed_download_preserves_existing_installation(self):
        source, target = self.install_fixture()
        shutil.rmtree(source)
        with patch.object(skills_cli, 'fetch_json', return_value=None):
            code, out, err = self.run_cli(['install', 'sample'])
        self.assertEqual(code, 1)
        self.assertNotIn('Successfully installed', out)
        self.assert_old_installation(target)
        self.assertEqual(list(target.parent.iterdir()), [target])

    def test_copy_failure_preserves_existing_installation(self):
        source, target = self.install_fixture()
        (source / 'asset.txt').write_text('required asset', encoding='utf-8')
        copy2 = shutil.copy2

        def fail_asset(src, dst):
            if Path(src).name == 'asset.txt':
                raise PermissionError('cannot read asset')
            return copy2(src, dst)

        with patch.object(shutil, 'copy2', side_effect=fail_asset):
            code, out, err = self.run_cli(['install', 'sample'])
        self.assertEqual(code, 1)
        self.assertIn('cannot read asset', err)
        self.assert_old_installation(target)
        self.assertEqual(list(target.parent.iterdir()), [target])

    def test_walk_error_does_not_report_complete_installation(self):
        source, target = self.install_fixture()

        def failing_walk(path, onerror):
            yield str(source), [], ['SKILL.md']
            onerror(PermissionError('cannot list assets'))

        with patch.object(os, 'walk', side_effect=failing_walk):
            code, out, err = self.run_cli(['install', 'sample'])
        self.assertEqual(code, 1)
        self.assertIn('cannot list assets', err)
        self.assertNotIn('Successfully installed', out)
        self.assert_old_installation(target)

    @unittest.skipIf(os.name == 'nt', 'Unix executable permissions')
    def test_local_install_preserves_executable_permissions(self):
        source, target = self.install_fixture()
        script = source / 'run.sh'
        script.write_text('#!/bin/sh\nexit 0\n', encoding='utf-8')
        script.chmod(0o755)
        code, out, err = self.run_cli(['install', 'sample'])
        self.assertEqual(code, 0, err)
        self.assertEqual(stat.S_IMODE((target / 'run.sh').stat().st_mode), 0o755)
        self.assertFalse((target / 'local.txt').exists())

    def test_swap_failure_restores_existing_installation(self):
        source, target = self.install_fixture()
        replace = os.replace

        def fail_activation(src, dst):
            if Path(src).name == 'staged':
                raise PermissionError('cannot activate installation')
            return replace(src, dst)

        with patch.object(os, 'replace', side_effect=fail_activation):
            code, out, err = self.run_cli(['install', 'sample'])
        self.assertEqual(code, 1)
        self.assertIn('cannot activate', err)
        self.assert_old_installation(target)
        self.assertEqual(list(target.parent.iterdir()), [target])

    def test_backup_move_failure_keeps_existing_installation(self):
        source, target = self.install_fixture()
        with patch.object(os, 'replace', side_effect=PermissionError('cannot move installation')):
            code, out, err = self.run_cli(['install', 'sample'])
        self.assertEqual(code, 1)
        self.assert_old_installation(target)
        self.assertEqual(list(target.parent.iterdir()), [target])

    def test_interrupted_activation_restores_existing_installation(self):
        source, target = self.install_fixture()
        replace = os.replace

        def interrupt_activation(src, dst):
            if Path(src).name == 'staged':
                raise KeyboardInterrupt()
            return replace(src, dst)

        with patch.object(os, 'replace', side_effect=interrupt_activation):
            with self.assertRaises(KeyboardInterrupt):
                self.run_cli(['install', 'sample'])
        self.assert_old_installation(target)
        self.assertEqual(list(target.parent.iterdir()), [target])

    def test_new_install_swap_failure_leaves_no_partial_installation(self):
        source, target = self.install_fixture()
        shutil.rmtree(target)
        with patch.object(os, 'replace', side_effect=PermissionError('cannot activate installation')):
            code, out, err = self.run_cli(['install', 'sample'])
        self.assertEqual(code, 1)
        self.assertFalse(target.exists())
        self.assertEqual(list(target.parent.iterdir()), [])

    def test_failed_rollback_retains_and_reports_backup(self):
        source, target = self.install_fixture()
        replace = os.replace

        def fail_activation_and_rollback(src, dst):
            if Path(src).name in ('staged', 'backup'):
                raise PermissionError('cannot rename')
            return replace(src, dst)

        with patch.object(os, 'replace', side_effect=fail_activation_and_rollback):
            code, out, err = self.run_cli(['install', 'sample'])
        self.assertEqual(code, 1)
        backups = list(target.parent.glob('.sample-*/backup'))
        self.assertEqual(len(backups), 1)
        self.assert_old_installation(backups[0])
        self.assertIn(str(backups[0]), err)
        self.assertFalse((target.parent / '.sample.install-lock').exists())

    def test_cleanup_failure_warns_after_successful_activation(self):
        source, target = self.install_fixture()
        with patch.object(shutil, 'rmtree', side_effect=PermissionError('cannot clean backup')):
            code, out, err = self.run_cli(['install', 'sample'])
        self.assertEqual(code, 0)
        self.assertIn('Successfully installed', out)
        self.assertIn('Warning:', err)
        self.assertEqual((target / 'SKILL.md').read_text(encoding='utf-8'), 'new instructions')
        backups = list(target.parent.glob('.sample-*/backup'))
        self.assertEqual(len(backups), 1)
        self.assert_old_installation(backups[0])

    def test_existing_installation_lock_prevents_changes(self):
        source, target = self.install_fixture()
        lock = target.parent / '.sample.install-lock'
        lock.mkdir()
        code, out, err = self.run_cli(['install', 'sample'])
        self.assertEqual(code, 1)
        self.assertIn('another installation is active', err)
        self.assertTrue(lock.is_dir())
        self.assert_old_installation(target)

    def test_source_destination_overlap_is_rejected_before_writing(self):
        source, target = self.install_fixture()
        for destination_root in (source.parent, source / 'nested'):
            with self.subTest(destination_root=destination_root):
                os.environ['AG_SKILLS_DIR'] = str(destination_root)
                code, out, err = self.run_cli(['install', 'sample'])
                self.assertEqual(code, 1)
                self.assertIn('must not overlap', err)
                self.assertEqual((source / 'SKILL.md').read_text(encoding='utf-8'), 'new instructions')
                self.assertFalse((source / 'nested').exists())
        with self.assertRaisesRegex(ValueError, 'must not overlap'):
            skills_cli.check_install_paths(str(source), str(source.parent))

    def test_catalog_ids_and_mismatched_paths_are_rejected(self):
        source, target = self.install_fixture()
        for skill_id in ('.', '..', '../sample', 'link/sample', '/sample', '', None):
            with self.subTest(skill_id=skill_id):
                catalog = {'skills': [{'id': skill_id, 'name': 'sample', 'path': 'skills/sample/SKILL.md'}]}
                with patch.object(skills_cli, 'load_catalog', return_value=catalog):
                    code, out, err = self.run_cli(['install', 'sample'])
                self.assertEqual(code, 1)
                self.assertIn('invalid skill id', err)
                self.assert_old_installation(target)
        catalog = {'skills': [{'id': 'sample', 'path': 'skills/other/SKILL.md'}]}
        with patch.object(skills_cli, 'load_catalog', return_value=catalog):
            code, out, err = self.run_cli(['install', 'sample'])
        self.assertEqual(code, 1)
        self.assertIn('unsafe skill path', err)
        self.assert_old_installation(target)

    @unittest.skipUnless(hasattr(os, 'symlink'), 'symbolic links unavailable')
    def test_source_tree_symlinks_are_rejected(self):
        source, target = self.install_fixture()
        outside = Path(self.temp_dir.name) / 'outside'
        outside.mkdir()
        (outside / 'data.txt').write_text('outside content', encoding='utf-8')
        for link_target in (outside, outside / 'data.txt'):
            with self.subTest(link_target=link_target):
                link = source / 'linked'
                link.symlink_to(link_target, target_is_directory=link_target.is_dir())
                try:
                    code, out, err = self.run_cli(['install', 'sample'])
                    self.assertEqual(code, 1)
                    self.assert_old_installation(target)
                    self.assertFalse((target / 'linked').exists())
                finally:
                    link.unlink()

    @unittest.skipUnless(hasattr(os, 'symlink'), 'symbolic links unavailable')
    def test_source_directory_symlink_is_rejected(self):
        source, target = self.install_fixture()
        outside = Path(self.temp_dir.name) / 'outside'
        source.rename(outside)
        source.symlink_to(outside, target_is_directory=True)
        code, out, err = self.run_cli(['install', 'sample'])
        self.assertEqual(code, 1)
        self.assert_old_installation(target)
        self.assertEqual((outside / 'SKILL.md').read_text(encoding='utf-8'), 'new instructions')

    @unittest.skipUnless(hasattr(os, 'symlink'), 'symbolic links unavailable')
    def test_destination_symlink_is_rejected_and_root_symlink_is_supported(self):
        source, target = self.install_fixture()
        outside = Path(self.temp_dir.name) / 'outside'
        outside.mkdir()
        (outside / 'marker').write_text('keep', encoding='utf-8')
        shutil.rmtree(target)
        target.symlink_to(outside, target_is_directory=True)
        code, out, err = self.run_cli(['install', 'sample'])
        self.assertEqual(code, 1)
        self.assertTrue(target.is_symlink())
        self.assertEqual((outside / 'marker').read_text(encoding='utf-8'), 'keep')
        target.unlink()
        linked_root = Path(self.temp_dir.name) / 'linked-root'
        linked_root.symlink_to(target.parent, target_is_directory=True)
        os.environ['AG_SKILLS_DIR'] = str(linked_root)
        code, out, err = self.run_cli(['install', 'sample'])
        self.assertEqual(code, 0, err)
        self.assertEqual((target / 'SKILL.md').read_text(encoding='utf-8'), 'new instructions')

    def test_non_directory_destination_is_preserved(self):
        source, target = self.install_fixture()
        shutil.rmtree(target)
        target.write_text('keep', encoding='utf-8')
        code, out, err = self.run_cli(['install', 'sample'])
        self.assertEqual(code, 1)
        self.assertIn('destination is not a directory', err)
        self.assertEqual(target.read_text(encoding='utf-8'), 'keep')

    def test_installed_ignores_hidden_directories(self):
        for name in ('.sample-backup', '.sample.install-lock', 'visible'):
            Path(self.temp_dir.name, name).mkdir()
        code, out, err = self.run_cli(['installed'])
        self.assertEqual(code, 0)
        self.assertIn('1 total', out)
        self.assertIn('visible', out)
        self.assertNotIn('.sample', out)

    @unittest.skipUnless(hasattr(os, 'symlink'), 'symbolic links unavailable')
    def test_installed_ignores_symbolic_link_directories(self):
        visible = Path(self.temp_dir.name, 'visible')
        visible.mkdir()
        (visible / 'SKILL.md').write_text('instructions', encoding='utf-8')
        Path(self.temp_dir.name, 'linked').symlink_to(visible, target_is_directory=True)
        code, out, err = self.run_cli(['installed'])
        self.assertEqual(code, 0)
        self.assertIn('1 total', out)
        self.assertIn('visible', out)
        self.assertNotIn('linked', out)

    def test_local_alias_install_resolves_canonical_skill(self):
        code, out, err = self.run_cli(['install', 'FULL-STACK-FEATURE'])
        self.assertEqual(code, 0, err)
        canonical = 'full-stack-orchestration-full-stack-feature'
        self.assertTrue(Path(self.temp_dir.name, canonical, 'SKILL.md').is_file())
        self.assertFalse(Path(self.temp_dir.name, 'full-stack-feature').exists())

    def test_unsafe_alias_is_rejected(self):
        source, target = self.install_fixture()
        aliases_path = source.parents[1] / 'aliases.json'
        for alias, skill_id in (('short', '../sample'), ('short', '.'), ('../short', 'sample')):
            with self.subTest(alias=alias, skill_id=skill_id):
                aliases_path.write_text(json.dumps({'aliases': {alias: skill_id}}), encoding='utf-8')
                code, out, err = self.run_cli(['install', alias])
                self.assertEqual(code, 1)
                self.assertIn('invalid skill id', err)
                self.assert_old_installation(target)

    def test_standalone_alias_fallback_fetches_only_when_needed(self):
        source, target = self.install_fixture()
        shutil.rmtree(source.parent)

        def fetch_json(url):
            if url == skills_cli.COMMIT_URL:
                return {'sha': TEST_REVISION}
            if url == PINNED_RAW_BASE + 'aliases.json':
                return {'aliases': {'short': 'sample'}}
            self.assertEqual(url, skills_cli.API_BASE_URL + 'skills/sample?ref=' + TEST_REVISION)
            return [{'name': 'SKILL.md', 'path': 'skills/sample/SKILL.md', 'type': 'file'}]

        with patch.object(skills_cli, 'fetch_json', side_effect=fetch_json) as fetch, \
                patch.object(skills_cli, 'fetch_bytes', return_value=b'remote instructions'):
            code, out, err = self.run_cli(['install', 'short'])
            self.assertEqual(code, 0, err)
            self.assertEqual(fetch.call_args_list[1].args[0], PINNED_RAW_BASE + 'aliases.json')
            fetch.reset_mock()
            code, out, err = self.run_cli(['install', 'sample'])
            self.assertEqual(code, 0, err)
            self.assertNotIn(PINNED_RAW_BASE + 'aliases.json', [call.args[0] for call in fetch.call_args_list])

    def test_standalone_install_pins_catalog_aliases_and_nested_files(self):
        package = Path(self.temp_dir.name) / 'standalone'
        package.mkdir()
        (package / 'aliases.json').write_text(json.dumps({'aliases': {'short': 'stale'}}), encoding='utf-8')
        install_root = Path(self.temp_dir.name) / 'installed'
        os.environ['AG_SKILLS_DIR'] = str(install_root)
        main_revision = TEST_REVISION
        fetched = []

        def fetch_json(url):
            nonlocal main_revision
            fetched.append(url)
            if url == skills_cli.COMMIT_URL:
                return {'sha': main_revision}
            if url == PINNED_RAW_BASE + 'catalog.json':
                main_revision = 'b' * 40
                return {'skills': [{'id': 'sample', 'path': 'skills/sample/SKILL.md'}]}
            if url == PINNED_RAW_BASE + 'aliases.json':
                return {'aliases': {'short': 'sample'}}
            if url == skills_cli.API_BASE_URL + 'skills/sample?ref=' + TEST_REVISION:
                return [
                    {'name': 'SKILL.md', 'path': 'skills/sample/SKILL.md', 'type': 'file',
                     'download_url': PINNED_RAW_BASE + 'skills/sample/SKILL.md'},
                    {'name': 'assets', 'path': 'skills/sample/assets', 'type': 'dir'},
                ]
            self.assertEqual(url, skills_cli.API_BASE_URL + 'skills/sample/assets?ref=' + TEST_REVISION)
            return [{'name': 'config.json', 'path': 'skills/sample/assets/config.json', 'type': 'file'}]

        def fetch_bytes(url):
            self.assertTrue(url.startswith(PINNED_RAW_BASE), url)
            return b'original revision'

        with patch.object(skills_cli, '__file__', str(package / 'skills_cli.py')), \
                patch.object(skills_cli, 'fetch_json', side_effect=fetch_json), \
                patch.object(skills_cli, 'fetch_bytes', side_effect=fetch_bytes):
            code, out, err = self.run_cli(['install', 'short'])
        self.assertEqual(code, 0, err)
        self.assertEqual(main_revision, 'b' * 40)
        self.assertEqual(fetched.count(skills_cli.COMMIT_URL), 1)
        self.assertIn(PINNED_RAW_BASE + 'catalog.json', fetched)
        self.assertIn(PINNED_RAW_BASE + 'aliases.json', fetched)
        self.assertEqual((install_root / 'sample/assets/config.json').read_bytes(), b'original revision')

    def test_invalid_remote_revision_never_falls_back_to_main(self):
        source, target = self.install_fixture()
        shutil.rmtree(source)
        for commit in (None, {'sha': 'main'}, {'sha': 'a' * 39}, {'sha': 'a' * 41}, {'sha': 1}):
            with self.subTest(commit=commit), patch.object(skills_cli, 'fetch_json', return_value=commit) as fetch, \
                    patch.object(skills_cli, 'fetch_bytes') as download:
                code, out, err = self.run_cli(['install', 'sample'])
                self.assertEqual(code, 1)
                self.assertIn('could not resolve a verified commit', err)
                fetch.assert_called_once_with(skills_cli.COMMIT_URL)
                download.assert_not_called()
                self.assert_old_installation(target)

    def test_remote_revision_cache_is_reset_for_each_command(self):
        package = Path(self.temp_dir.name) / 'standalone'
        package.mkdir()
        with patch.object(skills_cli, '__file__', str(package / 'skills_cli.py')), \
                patch.object(skills_cli, 'fetch_json', side_effect=[
                    {'sha': TEST_REVISION}, {'skills': []}, {'sha': 'b' * 40}, {'skills': []},
                ]) as fetch:
            self.assertEqual(self.run_cli(['list'])[0], 0)
            self.assertEqual(self.run_cli(['list'])[0], 0)
        self.assertEqual(fetch.call_args_list[1].args[0], PINNED_RAW_BASE + 'catalog.json')
        self.assertEqual(fetch.call_args_list[3].args[0], skills_cli.RAW_BASE_URL + 'b' * 40 + '/catalog.json')

    def test_remote_entries_must_be_immediate_pinned_children(self):
        root = 'skills/sample'
        entries = [
            {'name': name, 'path': root + '/' + name, 'type': 'file'}
            for name in ('', '.', '..', 'a/b', 'a\\b', '%2e%2e', 'x?raw', 'x#fragment', 'x:stream')
        ]
        entries.extend([
            {'name': 'x', 'path': root + '/nested/x', 'type': 'file'},
            {'name': 'x', 'path': root + '/../x', 'type': 'file'},
        ])
        for url in ('https://example.com/x', skills_cli.RAW_BASE_URL + '../x',
                    skills_cli.RAW_BASE_URL + 'main/' + root + '/x',
                    skills_cli.RAW_BASE_URL + root + '/%78'):
            entries.append({'name': 'x', 'path': root + '/x', 'type': 'file', 'download_url': url})
        for index, entry in enumerate(entries):
            with self.subTest(entry=entry), patch.object(skills_cli, 'fetch_json', return_value=[entry]), \
                    patch.object(skills_cli, 'fetch_bytes') as fetch:
                complete = skills_cli.download_folder_recursive(root, os.path.join(self.temp_dir.name, str(index)))
                self.assertFalse(complete)
                fetch.assert_not_called()

    def test_remote_listing_and_file_failures_are_incomplete(self):
        for listing in (None, [], {}, ['bad entry'],
                        [{'name': 'link', 'path': 'skills/sample/link', 'type': 'symlink'}]):
            with self.subTest(listing=listing), patch.object(skills_cli, 'fetch_json', return_value=listing), \
                    patch.object(skills_cli, 'fetch_bytes') as fetch:
                self.assertFalse(skills_cli.download_folder_recursive('skills/sample', self.temp_dir.name))
                fetch.assert_not_called()
        entry = {'name': 'SKILL.md', 'path': 'skills/sample/SKILL.md', 'type': 'file'}
        with patch.object(skills_cli, 'fetch_json', return_value=[entry]), \
                patch.object(skills_cli, 'fetch_bytes', return_value=None):
            self.assertFalse(skills_cli.download_folder_recursive('skills/sample', self.temp_dir.name))

    def test_incomplete_remote_subdirectory_preserves_existing_installation(self):
        source, target = self.install_fixture()
        shutil.rmtree(source)
        root_listing = [
            {'name': 'SKILL.md', 'path': 'skills/sample/SKILL.md', 'type': 'file'},
            {'name': 'assets', 'path': 'skills/sample/assets', 'type': 'dir'},
        ]
        with patch.object(skills_cli, 'fetch_json', side_effect=[{'sha': TEST_REVISION}, root_listing, []]), \
                patch.object(skills_cli, 'fetch_bytes', return_value=b'new instructions'):
            code, out, err = self.run_cli(['install', 'sample'])
        self.assertEqual(code, 1)
        self.assert_old_installation(target)

    def test_complete_remote_tree_preserves_file_bytes(self):
        source, target = self.install_fixture()
        shutil.rmtree(source)
        root_listing = [
            {'name': 'SKILL.md', 'path': 'skills/sample/SKILL.md', 'type': 'file'},
            {'name': 'assets', 'path': 'skills/sample/assets', 'type': 'dir'},
        ]
        nested_listing = [{'name': 'sample data.txt', 'path': 'skills/sample/assets/sample data.txt',
                           'type': 'file', 'download_url': PINNED_RAW_BASE
                           + 'skills/sample/assets/sample%20data.txt'}]
        with patch.object(skills_cli, 'fetch_json', side_effect=[{'sha': TEST_REVISION}, root_listing, nested_listing]), \
                patch.object(skills_cli, 'fetch_bytes', side_effect=[b'new instructions', b'']) as fetch:
            code, out, err = self.run_cli(['install', 'sample'])
        self.assertEqual(code, 0, err)
        self.assertEqual((target / 'SKILL.md').read_bytes(), b'new instructions')
        self.assertEqual((target / 'assets/sample data.txt').read_bytes(), b'')
        self.assertEqual(fetch.call_args.args[0], PINNED_RAW_BASE
                         + 'skills/sample/assets/sample%20data.txt')
        self.assertFalse((target / 'local.txt').exists())

    def test_duplicate_remote_entry_is_incomplete(self):
        entry = {'name': 'SKILL.md', 'path': 'skills/sample/SKILL.md', 'type': 'file'}
        with patch.object(skills_cli, 'fetch_json', return_value=[entry, entry]), \
                patch.object(skills_cli, 'fetch_bytes', return_value=b'instructions') as fetch:
            complete = skills_cli.download_folder_recursive('skills/sample', self.temp_dir.name)
        self.assertFalse(complete)
        self.assertEqual(fetch.call_count, 1)

    def test_missing_or_empty_skill_document_cannot_replace_existing_installation(self):
        source, target = self.install_fixture()
        (source / 'SKILL.md').unlink()
        for present in (False, True):
            with self.subTest(empty=present):
                if present:
                    (source / 'SKILL.md').write_bytes(b'')
                code, out, err = self.run_cli(['install', 'sample'])
                self.assertEqual(code, 1)
                self.assertIn('Installation incomplete', err)
                self.assert_old_installation(target)

if __name__ == '__main__':
    unittest.main()
