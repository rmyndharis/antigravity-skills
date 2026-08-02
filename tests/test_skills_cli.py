import unittest
from unittest.mock import patch
import sys
import os
import io
import tempfile

# Ensure repository root is in sys.path
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

import skills_cli

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
        os.environ["GEMINI_SKILLS_DIR"] = self.temp_dir.name

    def tearDown(self):
        self.temp_dir.cleanup()
        if "GEMINI_SKILLS_DIR" in os.environ:
            del os.environ["GEMINI_SKILLS_DIR"]

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

if __name__ == '__main__':
    unittest.main()
