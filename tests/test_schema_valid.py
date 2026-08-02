import unittest
import os
import json
import re

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class TestSchemaValid(unittest.TestCase):
    def test_plugin_json_schema(self):
        plugin_path = os.path.join(REPO_ROOT, "plugin.json")
        self.assertTrue(os.path.exists(plugin_path), "plugin.json does not exist at repo root")
        
        with open(plugin_path, "r", encoding="utf-8") as f:
            content = f.read()

        data = json.loads(content)
        self.assertIsInstance(data, dict, "plugin.json must contain a JSON object")

        # Validate name
        self.assertIn("name", data, "plugin.json missing 'name'")
        self.assertIsInstance(data["name"], str)
        self.assertTrue(re.match(r"^[a-z0-9]+(?:-[a-z0-9]+)*$", data["name"]), f"Invalid plugin name format: {data['name']}")

        # Validate version
        self.assertIn("version", data, "plugin.json missing 'version'")
        self.assertIsInstance(data["version"], str)
        self.assertTrue(re.match(r"^\d+\.\d+\.\d+$", data["version"]), f"Invalid semantic version: {data['version']}")

        # Validate description
        self.assertIn("description", data, "plugin.json missing 'description'")
        self.assertIsInstance(data["description"], str)
        self.assertTrue(len(data["description"].strip()) > 0, "description cannot be empty")
        self.assertLessEqual(len(data["description"]), 256, "description exceeds 256 chars")

        # Validate entry
        self.assertIn("entry", data, "plugin.json missing 'entry'")
        self.assertEqual(data["entry"], "skills_cli.py")

        # Validate skills list
        self.assertIn("skills", data)
        self.assertIsInstance(data["skills"], list)
        self.assertIn("skills/antigravity-skills-manager/SKILL.md", data["skills"])

        # Validate commands
        self.assertIn("commands", data)
        self.assertIsInstance(data["commands"], list)
        self.assertTrue(len(data["commands"]) > 0)
        skills_cmd = data["commands"][0]
        self.assertEqual(skills_cmd.get("name"), "skills")
        self.assertIn("subcommands", skills_cmd)
        sub_names = [sc["name"] for sc in skills_cmd["subcommands"]]
        self.assertIn("list", sub_names)
        self.assertIn("search", sub_names)
        self.assertIn("install", sub_names)
        self.assertIn("installed", sub_names)

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
