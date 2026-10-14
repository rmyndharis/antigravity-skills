#!/usr/bin/env python3
"""
Antigravity Skill Porter & Optimizer (port_skill.py)
Imports, translates, and optimizes agent skills (from Claude Code, Cursor, etc.)
into native Google Antigravity plugins and skills.
"""

import argparse
import difflib
import json
import os
import re
import shutil
import sys
import urllib.request
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Deterministic tool and context replacement mapping
TOOL_REPLACEMENTS = [
    # Context files
    (r"\bCLAUDE\.md\b", "GEMINI.md"),
    (r"\bclaude\.md\b", "gemini.md"),
    (r"\.claude/rules\b", ".agents/rules"),
    (r"\.claude/skills\b", ".agents/skills"),
    (r"\.claude\b", ".agents"),
    # Platform / Agent Branding in instructions
    (r"\bClaude Code\b", "Google Antigravity (AGY)"),
    (r"\bClaude Cowork\b", "Google Antigravity 2.0"),
    (r"\bclaude\.ai\b", "Antigravity IDE"),
    (r"\bClaude\b", "Antigravity"),
    # Core Tools
    (r"`Bash`", "`run_command`"),
    (r"\bBash tool\b", "`run_command` tool"),
    (r"`Glob`", "`find_by_name`"),
    (r"\bGlob tool\b", "`find_by_name` tool"),
    (r"`Grep`", "`grep_search`"),
    (r"\bGrep tool\b", "`grep_search` tool"),
    (r"`Read`", "`view_file`"),
    (r"\bRead tool\b", "`view_file` tool"),
    (r"`Edit`", "`replace_file_content`"),
    (r"\bEdit tool\b", "`replace_file_content` tool"),
    (r"`StrReplaceEditor`", "`replace_file_content`"),
    (r"`Write`", "`write_to_file`"),
    (r"\bWrite tool\b", "`write_to_file` tool"),
]

def fetch_github_file(raw_url: str) -> str:
    """Fetches text content from a raw GitHub URL."""
    req = urllib.request.Request(
        raw_url,
        headers={"User-Agent": "Antigravity-Skill-Porter/1.0"}
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        return resp.read().decode("utf-8")

def resolve_source(source: str) -> Tuple[str, Optional[Path], Dict[str, str]]:
    """
    Resolves input source (URL or local path) into:
    (skill_md_content, base_local_dir_or_none, auxiliary_files_dict)
    """
    auxiliary_files = {}

    # Check if GitHub URL
    if source.startswith("http://") or source.startswith("https://") or ("github.com" in source):
        # Normalize GitHub URL to raw URL for SKILL.md
        # Handles:
        # 1. https://github.com/owner/repo/tree/branch/subpath
        # 2. https://github.com/owner/repo/blob/branch/subpath/SKILL.md
        # 3. https://github.com/owner/repo
        tree_match = re.search(r"github\.com/([^/]+)/([^/]+)/(?:tree|blob)/([^/]+)/(.+)$", source)
        base_match = re.search(r"github\.com/([^/]+)/([^/]+)/?$", source)

        if tree_match:
            owner, repo, branch, subpath = tree_match.group(1), tree_match.group(2), tree_match.group(3), tree_match.group(4)
            repo = repo.replace(".git", "")
            subpath = subpath.strip("/")
            if not subpath.lower().endswith(".md"):
                subpath = f"{subpath}/SKILL.md"
            raw_skill_url = f"https://raw.githubusercontent.com/{owner}/{repo}/{branch}/{subpath}"
            print(f"[+] Fetching SKILL.md from GitHub: {raw_skill_url}")
            content = fetch_github_file(raw_skill_url)
            return content, None, auxiliary_files
        elif base_match:
            owner, repo = base_match.group(1), base_match.group(2)
            repo = repo.replace(".git", "")
            raw_skill_url = f"https://raw.githubusercontent.com/{owner}/{repo}/main/SKILL.md"
            print(f"[+] Fetching SKILL.md from GitHub: {raw_skill_url}")
            try:
                content = fetch_github_file(raw_skill_url)
            except Exception:
                fallback_url = f"https://raw.githubusercontent.com/{owner}/{repo}/master/SKILL.md"
                print(f"[*] Retrying with master branch: {fallback_url}")
                content = fetch_github_file(fallback_url)
            return content, None, auxiliary_files
        else:
            content = fetch_github_file(source)
            return content, None, auxiliary_files

    # Local Path
    local_path = Path(source).resolve()
    if local_path.is_file() and local_path.name.lower() in ("skill.md", "skill.markdown"):
        content = local_path.read_text(encoding="utf-8")
        parent = local_path.parent
        # Load auxiliary files if present
        for subfolder in ("references", "scripts", "examples", "resources"):
            folder_path = parent / subfolder
            if folder_path.is_dir():
                for f in folder_path.rglob("*"):
                    if f.is_file():
                        rel = str(f.relative_to(parent))
                        auxiliary_files[rel] = f.read_text(encoding="utf-8", errors="ignore")
        return content, parent, auxiliary_files

    if local_path.is_dir():
        skill_file = local_path / "SKILL.md"
        if not skill_file.exists():
            skill_file = local_path / "skill.md"
        if not skill_file.exists():
            raise FileNotFoundError(f"No SKILL.md found in directory: {local_path}")
        content = skill_file.read_text(encoding="utf-8")
        for subfolder in ("references", "scripts", "examples", "resources"):
            folder_path = local_path / subfolder
            if folder_path.is_dir():
                for f in folder_path.rglob("*"):
                    if f.is_file():
                        rel = str(f.relative_to(local_path))
                        auxiliary_files[rel] = f.read_text(encoding="utf-8", errors="ignore")
        return content, local_path, auxiliary_files

    raise ValueError(f"Cannot resolve source: {source}")

def extract_frontmatter(content: str) -> Tuple[Dict[str, str], str]:
    """Extracts and parses YAML frontmatter from markdown."""
    pattern = r"^---\s*\n(.*?)\n---\s*\n(.*)$"
    match = re.search(pattern, content, re.DOTALL)
    if not match:
        return {}, content

    yaml_block = match.group(1)
    body = match.group(2)

    metadata = {}
    name_match = re.search(r"^name:\s*([^\n]+)", yaml_block, re.MULTILINE)
    if name_match:
        metadata["name"] = name_match.group(1).strip().strip("\"'")

    # Extract description supporting double quotes, single quotes, or multiline YAML blocks
    desc_match = re.search(
        r"^description:\s*(?:>-\s*|\|-?\s*)?\s*(?:\"([^\"]+)\"|'([^']+)'|([^\n]+(?:\n(?:\s{2,}|\t)[^\n]+)*))",
        yaml_block,
        re.MULTILINE
    )
    if desc_match:
        desc_text = (desc_match.group(1) or desc_match.group(2) or desc_match.group(3) or "").strip()
        desc_text = re.sub(r"\s+", " ", desc_text)
        metadata["description"] = desc_text

    return metadata, body

def optimize_for_antigravity(raw_content: str, metadata: Dict[str, str]) -> Tuple[str, Dict[str, str]]:
    """Applies deterministic & structural optimizations for Antigravity."""
    updated = raw_content

    # 1. Apply regex tool and convention replacements
    for pattern, replacement in TOOL_REPLACEMENTS:
        updated = re.sub(pattern, replacement, updated)

    # 2. Extract or synthesize metadata
    skill_name = metadata.get("name", "imported-skill").lower()
    skill_name = re.sub(r"[^a-z0-9_-]", "-", skill_name).strip("-")
    description = metadata.get("description", "")
    if not description:
        # Generate description from body title or first sentence
        first_p = re.search(r"#+\s*([^\n]+)", updated)
        description = f"Autonomous skill for {first_p.group(1) if first_p else skill_name}. Optimized for Google Antigravity."

    # Update description if it mentions Claude
    for pattern, replacement in TOOL_REPLACEMENTS:
        description = re.sub(pattern, replacement, description)

    # 3. Enhance with Antigravity multi-agent and reactive execution notes if subagents are detected
    has_subagents = bool(re.search(r"\bsub-?agents?\b", updated, re.IGNORECASE))
    if has_subagents:
        subagent_hint = (
            "\n\n> [!NOTE]\n"
            "> **Antigravity Multi-Agent Execution**:\n"
            "> When spawning subagents, dispatch them in parallel within a single `invoke_subagent` call:\n"
            "> ```json\n"
            '> { "Subagents": [ { "TypeName": "self", "Role": "...", "Prompt": "..." } ] }\n'
            "> ```\n"
            "> Do not poll or loop. Antigravity will automatically resume via **Reactive Wakeup** once subagents complete.\n"
        )
        if "> **Antigravity Multi-Agent Execution**" not in updated:
            updated = re.sub(r"(###?\s*step\s*\d+.*?(?:sub-?agent|parallel).*?\n)", r"\1" + subagent_hint, updated, flags=re.IGNORECASE)

    # 4. Construct clean optimized frontmatter
    optimized_frontmatter = (
        f"---\n"
        f"name: {skill_name}\n"
        f"description: >-\n"
        f"  {description}\n"
        f"---\n\n"
    )

    # Rebuild complete document
    _, body = extract_frontmatter(updated)
    optimized_doc = optimized_frontmatter + body.lstrip()

    metadata["name"] = skill_name
    metadata["description"] = description
    return optimized_doc, metadata

def show_diff(original: str, modified: str):
    """Prints a colorized or unified diff of changes."""
    diff = list(difflib.unified_diff(
        original.splitlines(keepends=True),
        modified.splitlines(keepends=True),
        fromfile="Original (Source)",
        tofile="Optimized (Antigravity)",
        n=3
    ))
    if not diff:
        print("[*] No textual changes needed; format is already standard.")
        return

    print("=" * 60)
    print("DIFF: Optimizations applied for Google Antigravity")
    print("=" * 60)
    for line in diff[:60]:  # Limit output to 60 lines for scannability
        sys.stdout.write(line)
    if len(diff) > 60:
        print(f"\n... and {len(diff) - 60} more diff lines.")
    print("=" * 60)

def install_skill(
    skill_name: str,
    optimized_content: str,
    description: str,
    auxiliary_files: Dict[str, str],
    global_install: bool = True,
    workspace_install: bool = False,
    workspace_root: Optional[Path] = None
):
    """Installs the optimized skill into Antigravity plugin and skill directories."""
    installed_paths = []
    user_home = Path(os.path.expanduser("~"))

    # 1. Global Plugin and Skill Paths
    if global_install:
        config_dir = user_home / ".gemini" / "config"
        plugin_dir = config_dir / "plugins" / skill_name
        plugin_skill_dir = plugin_dir / "skills" / skill_name
        global_skill_dir = config_dir / "skills" / skill_name

        plugin_skill_dir.mkdir(parents=True, exist_ok=True)
        global_skill_dir.mkdir(parents=True, exist_ok=True)

        # plugin.json
        manifest = {
            "name": skill_name,
            "description": description
        }
        (plugin_dir / "plugin.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
        installed_paths.append(str(plugin_dir / "plugin.json"))

        # SKILL.md
        (plugin_skill_dir / "SKILL.md").write_text(optimized_content, encoding="utf-8")
        installed_paths.append(str(plugin_skill_dir / "SKILL.md"))

        (global_skill_dir / "SKILL.md").write_text(optimized_content, encoding="utf-8")
        installed_paths.append(str(global_skill_dir / "SKILL.md"))

        # Auxiliary files
        for rel_path, fcontent in auxiliary_files.items():
            dest_plugin = plugin_skill_dir / rel_path
            dest_global = global_skill_dir / rel_path
            dest_plugin.parent.mkdir(parents=True, exist_ok=True)
            dest_global.parent.mkdir(parents=True, exist_ok=True)
            dest_plugin.write_text(fcontent, encoding="utf-8")
            dest_global.write_text(fcontent, encoding="utf-8")
            installed_paths.append(str(dest_plugin))

    # 2. Workspace Install
    if workspace_install:
        root = workspace_root or Path.cwd()
        ws_skill_dir = root / ".agents" / "skills" / skill_name
        ws_skill_dir.mkdir(parents=True, exist_ok=True)
        (ws_skill_dir / "SKILL.md").write_text(optimized_content, encoding="utf-8")
        installed_paths.append(str(ws_skill_dir / "SKILL.md"))
        for rel_path, fcontent in auxiliary_files.items():
            dest_ws = ws_skill_dir / rel_path
            dest_ws.parent.mkdir(parents=True, exist_ok=True)
            dest_ws.write_text(fcontent, encoding="utf-8")
            installed_paths.append(str(dest_ws))

    return installed_paths

def port_plugin_repo(repo_path: Path, dry_run: bool = False, workspace: bool = False, no_global: bool = False):
    """Ports a repository containing multiple skills into an Antigravity plugin and skills."""
    claude_plugin_json = repo_path / ".claude-plugin" / "plugin.json"
    plugin_name = repo_path.name
    plugin_desc = f"Antigravity plugin ported from {repo_path.name}"

    if claude_plugin_json.exists():
        try:
            data = json.loads(claude_plugin_json.read_text(encoding="utf-8"))
            plugin_name = data.get("name", plugin_name)
            plugin_desc = data.get("description", plugin_desc)
        except Exception:
            pass

    for pattern, replacement in TOOL_REPLACEMENTS:
        plugin_desc = re.sub(pattern, replacement, plugin_desc)

    skills_dir = repo_path / "skills"
    skill_dirs = [d for d in skills_dir.iterdir() if d.is_dir()]
    print(f"[+] Found multi-skill plugin repository: '{plugin_name}' with {len(skill_dirs)} skills.")

    user_home = Path(os.path.expanduser("~"))
    plugin_dir = user_home / ".gemini" / "config" / "plugins" / plugin_name
    global_skills_dir = user_home / ".gemini" / "config" / "skills"

    if not dry_run and not no_global:
        plugin_dir.mkdir(parents=True, exist_ok=True)
        manifest = {
            "name": plugin_name,
            "description": plugin_desc
        }
        (plugin_dir / "plugin.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    all_installed = []
    for sdir in sorted(skill_dirs):
        skill_file = sdir / "SKILL.md"
        if not skill_file.exists():
            skill_file = sdir / "skill.md"
        if not skill_file.exists():
            continue

        content = skill_file.read_text(encoding="utf-8")
        meta, body = extract_frontmatter(content)
        if "name" not in meta:
            meta["name"] = sdir.name

        opt_content, opt_meta = optimize_for_antigravity(content, meta)
        sname = opt_meta["name"]
        print(f"  [+] Optimized skill: {sname}")

        if not dry_run and not no_global:
            # Install into plugin
            target_plugin_skill = plugin_dir / "skills" / sname
            target_plugin_skill.mkdir(parents=True, exist_ok=True)
            (target_plugin_skill / "SKILL.md").write_text(opt_content, encoding="utf-8")
            all_installed.append(str(target_plugin_skill / "SKILL.md"))

            # Install into global skills root
            target_global = global_skills_dir / sname
            target_global.mkdir(parents=True, exist_ok=True)
            (target_global / "SKILL.md").write_text(opt_content, encoding="utf-8")
            all_installed.append(str(target_global / "SKILL.md"))

    if dry_run:
        print(f"\n[+] Dry run complete for {len(skill_dirs)} skills in '{plugin_name}'. No files written.")
    else:
        print(f"\n[V] Successfully installed Antigravity plugin '{plugin_name}' with {len(skill_dirs)} skills!")
        print(f"  Plugin Manifest: {plugin_dir / 'plugin.json'}")
        print(f"  Plugin Skills: {plugin_dir / 'skills'}")
        print(f"  Global Skills: {global_skills_dir}")

def main():
    parser = argparse.ArgumentParser(description="Antigravity Skill Porter & Optimizer")
    parser.add_argument("source", help="Source path (directory, SKILL.md, or GitHub repo URL)")
    parser.add_argument("--name", help="Override skill name")
    parser.add_argument("--dry-run", action="store_true", help="Preview optimizations and diff without installing")
    parser.add_argument("--workspace", action="store_true", help="Install into current workspace (.agents/skills/)")
    parser.add_argument("--no-global", action="store_true", help="Do not install into global ~/.gemini/config")
    args = parser.parse_args()

    print(f"[*] Reading source: {args.source}")

    # Check for multi-skill local directory
    if Path(args.source).is_dir() and (Path(args.source) / "skills").is_dir():
        port_plugin_repo(Path(args.source), dry_run=args.dry_run, workspace=args.workspace, no_global=args.no_global)
        return

    # Check for whole GitHub repo (without specific tree path)
    if ("github.com" in args.source) and ("/tree/" not in args.source) and ("/blob/" not in args.source):
        import tempfile, subprocess
        with tempfile.TemporaryDirectory() as tmpdir:
            print(f"[*] Cloning repository to inspect structure: {args.source}...")
            res = subprocess.run(["git", "clone", "--depth=1", args.source, tmpdir], capture_output=True, text=True)
            if res.returncode == 0 and (Path(tmpdir) / "skills").is_dir():
                port_plugin_repo(Path(tmpdir), dry_run=args.dry_run, workspace=args.workspace, no_global=args.no_global)
                return

    try:
        raw_content, local_base, aux_files = resolve_source(args.source)
    except Exception as e:
        print(f"[-] Error reading source: {e}", file=sys.stderr)
        sys.exit(1)

    metadata, body = extract_frontmatter(raw_content)
    if args.name:
        metadata["name"] = args.name

    print(f"[+] Optimizing skill '{metadata.get('name', 'unnamed')}' for Antigravity...")
    optimized_doc, updated_metadata = optimize_for_antigravity(raw_content, metadata)

    show_diff(raw_content, optimized_doc)

    if args.dry_run:
        print("[+] Dry run complete. No files written.")
        return

    skill_name = updated_metadata["name"]
    desc = updated_metadata["description"]
    print(f"[+] Installing skill '{skill_name}'...")
    installed = install_skill(
        skill_name=skill_name,
        optimized_content=optimized_doc,
        description=desc,
        auxiliary_files=aux_files,
        global_install=not args.no_global,
        workspace_install=args.workspace,
        workspace_root=Path.cwd()
    )

    print("\n[V] Successfully installed Antigravity Skill & Plugin:")
    for path in installed:
        print(f"  - {path}")
    print("\n[+] Done! You can now invoke this skill in Antigravity.")

if __name__ == "__main__":
    main()
