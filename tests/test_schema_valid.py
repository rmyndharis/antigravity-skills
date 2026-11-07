import unittest
import os
import json
import shutil
import subprocess
import tempfile
from pathlib import Path

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PLUGIN_ROOT = Path(REPO_ROOT, "plugins", "antigravity-skills-manager")

class TestSchemaValid(unittest.TestCase):
    def test_plugin_json_schema(self):
        data = json.loads((PLUGIN_ROOT / "plugin.json").read_text(encoding="utf-8"))
        self.assertIsInstance(data, dict)
        self.assertEqual(set(data), {"name", "description"})
        self.assertIsInstance(data["name"], str)
        self.assertRegex(data["name"], r"^[a-zA-Z0-9_-]+$")
        self.assertEqual(data["name"], PLUGIN_ROOT.name)
        self.assertIsInstance(data["description"], str)
        self.assertTrue(data["description"].strip())

    def test_repository_root_is_not_a_plugin(self):
        self.assertFalse(Path(REPO_ROOT, "plugin.json").exists())

    def test_plugin_contains_only_the_synchronized_manager_skill(self):
        skills = sorted(path.relative_to(PLUGIN_ROOT).as_posix() for path in PLUGIN_ROOT.rglob("SKILL.md"))
        self.assertEqual(skills, ["skills/antigravity-skills-manager/SKILL.md"])
        canonical = Path(REPO_ROOT, "skills", "antigravity-skills-manager", "SKILL.md")
        self.assertEqual((PLUGIN_ROOT / skills[0]).read_bytes(), canonical.read_bytes())
        content = canonical.read_text(encoding="utf-8")
        self.assertIn("/antigravity-skills-manager", content)
        self.assertIn("npx @rmyndharis/antigravity-skills", content)
        self.assertNotRegex(content, r"(?<![\w-])/skills(?:-manager)?\b")

    def test_plugin_build_sync_and_read_only_check(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            script = root / "scripts" / "build-plugin.js"
            script.parent.mkdir()
            shutil.copyfile(Path(REPO_ROOT, "scripts", "build-plugin.js"), script)
            canonical = root / "skills" / "antigravity-skills-manager" / "SKILL.md"
            canonical.parent.mkdir(parents=True)
            canonical.write_text("first version\n", encoding="utf-8")
            destination = root / "plugins" / "antigravity-skills-manager" / "skills" / "antigravity-skills-manager" / "SKILL.md"

            def run(*args):
                return subprocess.run(["node", str(script), *args], cwd=root, capture_output=True, text=True)

            self.assertEqual(run("--check").returncode, 1)
            self.assertFalse(destination.exists())
            self.assertEqual(run().returncode, 0)
            self.assertEqual(destination.read_bytes(), canonical.read_bytes())
            self.assertEqual(run("--check").returncode, 0)
            canonical.write_text("second version\n", encoding="utf-8")
            self.assertEqual(run("--check").returncode, 1)
            self.assertEqual(destination.read_text(encoding="utf-8"), "first version\n")
            self.assertEqual(run().returncode, 0)
            self.assertEqual(destination.read_bytes(), canonical.read_bytes())

    def test_skill_md_schema(self):
        skill_md_path = os.path.join(REPO_ROOT, "skills", "antigravity-skills-manager", "SKILL.md")
        self.assertTrue(os.path.exists(skill_md_path), f"SKILL.md missing at {skill_md_path}")

        with open(skill_md_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        self.assertLessEqual(len(lines), 500, "SKILL.md exceeds 500 lines limit")

        content = "".join(lines)
        self.assertTrue(content.startswith("---"), "SKILL.md must start with YAML frontmatter delimiter '---'")

        # Extract frontmatter
        parts = content.split("---", 2)
        self.assertGreaterEqual(len(parts), 3, "SKILL.md must have valid closing YAML frontmatter delimiter '---'")
        frontmatter_raw = parts[1]

        # Parse key-values from frontmatter
        allowed_fields = {"name", "description", "license", "compatibility", "allowed-tools", "metadata"}
        fm_keys = set()
        for raw_line in frontmatter_raw.splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue
            if ":" in line:
                key = line.split(":", 1)[0].strip()
                if not raw_line.startswith(" ") and not raw_line.startswith("\t"):
                    fm_keys.add(key)

        for k in fm_keys:
            self.assertIn(k, allowed_fields, f"Disallowed key '{k}' found in SKILL.md frontmatter")

        self.assertIn("name", fm_keys, "Frontmatter missing 'name'")
        self.assertIn("description", fm_keys, "Frontmatter missing 'description'")

        # Section headers check
        self.assertIn("## Use this skill when", content)
        self.assertTrue("## Do not use" in content or "## Do not use this skill when" in content)
        self.assertIn("## Instructions", content)

if __name__ == '__main__':
    unittest.main()
