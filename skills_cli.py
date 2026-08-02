import sys
import os
import json
import urllib.request
import urllib.error

# ponytail: reconfigure sys.stdout/stderr to UTF-8 for Windows terminal compatibility
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

CATALOG_URL = "https://raw.githubusercontent.com/rmyndharis/antigravity-skills/main/catalog.json"
BUNDLES_URL = "https://raw.githubusercontent.com/rmyndharis/antigravity-skills/main/bundles.json"
RAW_BASE_URL = "https://raw.githubusercontent.com/rmyndharis/antigravity-skills/main/"
API_BASE_URL = "https://api.github.com/repos/rmyndharis/antigravity-skills/contents/"

# ponytail: environment variable override allows isolated testing without polluting ~/.gemini/config/skills
def get_skills_dir():
    return os.environ.get("GEMINI_SKILLS_DIR") or os.path.abspath(os.path.join(os.path.expanduser("~"), ".gemini", "config", "skills"))

# ponytail: stdlib urllib fetcher with user-agent and timeout handling
def fetch_json(url):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "AntigravitySkillsInstaller/1.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode('utf-8'))
    except Exception as e:
        print(f"Error fetching {url}: {e}", file=sys.stderr)
        return None

# ponytail: stdlib binary fetcher for raw files
def fetch_bytes(url):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "AntigravitySkillsInstaller/1.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            return resp.read()
    except Exception as e:
        print(f"Error downloading {url}: {e}", file=sys.stderr)
        return None

# ponytail: prefer local catalog.json if available in script directory, fallback to raw github
def load_catalog():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    local_catalog = os.path.join(script_dir, "catalog.json")
    if os.path.exists(local_catalog):
        try:
            with open(local_catalog, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return fetch_json(CATALOG_URL)

def skill_matches(s, query):
    if not query:
        return True
    q = query.lower()
    if q in s.get('id', '').lower():
        return True
    if q in s.get('name', '').lower():
        return True
    if q in s.get('description', '').lower():
        return True
    if q in s.get('category', '').lower():
        return True
    if any(q in t.lower() for t in s.get('tags', [])):
        return True
    if any(q in tr.lower() for tr in s.get('triggers', [])):
        return True
    return False

def cmd_list(category=None, query=None):
    catalog = load_catalog()
    if catalog is None or 'skills' not in catalog:
        print("Failed to load catalog.", file=sys.stderr)
        sys.exit(1)

    skills = catalog['skills']
    if not skills:
        print("\n[+] Found 0 skill(s) in catalog:\n" + "-"*60)
        print("No skills available in catalog.")
        return

    if category:
        skills = [s for s in skills if s.get('category', '').lower() == category.lower()]
    if query:
        skills = [s for s in skills if skill_matches(s, query)]

    print(f"\n[+] Found {len(skills)} skill(s) in catalog:\n" + "-"*60)
    if not skills:
        print("No skills found matching filter.")
        return

    for s in skills[:40]:  # Limit display to 40 items
        cat = f"[{s.get('category', 'general')}]"
        print(f"* {s.get('id', ''):<50} {cat:<12}")
        if s.get('description'):
            desc = s['description'][:80] + "..." if len(s['description']) > 80 else s['description']
            print(f"  └─ {desc}")
    if len(skills) > 40:
        print(f"\n... and {len(skills) - 40} more. Use --query <term> or search <term> to filter.")

def cmd_search(query):
    if not query or not query.strip():
        print("Usage: python skills_cli.py search <term>", file=sys.stderr)
        sys.exit(1)
    cmd_list(query=query.strip())

# ponytail: local repo fallback for offline/test reliability
def copy_folder_local(local_src, local_dst):
    os.makedirs(local_dst, exist_ok=True)
    for root, dirs, files in os.walk(local_src):
        rel_path = os.path.relpath(root, local_src)
        target_dir = os.path.join(local_dst, rel_path) if rel_path != "." else local_dst
        os.makedirs(target_dir, exist_ok=True)
        for f in files:
            src_file = os.path.join(root, f)
            dst_file = os.path.join(target_dir, f)
            with open(src_file, "rb") as rf:
                content = rf.read()
            with open(dst_file, "wb") as wf:
                wf.write(content)
            print(f"  └─ Downloaded: {f}")
    return True

# ponytail: recursive directory fetcher using github api with raw fallback
def download_folder_recursive(remote_path, local_target_dir):
    os.makedirs(local_target_dir, exist_ok=True)
    api_url = API_BASE_URL + remote_path
    items = fetch_json(api_url)
    if not items or not isinstance(items, list):
        # ponytail: fallback to direct SKILL.md download if GitHub API fails or rate limited
        raw_url = RAW_BASE_URL + remote_path + "/SKILL.md"
        content = fetch_bytes(raw_url)
        if content:
            with open(os.path.join(local_target_dir, "SKILL.md"), "wb") as f:
                f.write(content)
            print("  └─ Downloaded: SKILL.md (fallback)")
            return True
        return False

    success = True
    for item in items:
        item_name = item.get('name', '')
        item_path = item.get('path', '')
        item_type = item.get('type', '')
        target_item_path = os.path.join(local_target_dir, item_name)

        if item_type == 'file':
            download_url = item.get('download_url') or (RAW_BASE_URL + item_path)
            data = fetch_bytes(download_url)
            if data is not None:
                with open(target_item_path, "wb") as f:
                    f.write(data)
                print(f"  └─ Downloaded: {item_name}")
            else:
                success = False
        elif item_type == 'dir':
            dir_ok = download_folder_recursive(item_path, target_item_path)
            if not dir_ok:
                success = False

    return success

def cmd_install(skill_id):
    if not skill_id or not skill_id.strip():
        print("Please specify skill name/id to install.", file=sys.stderr)
        sys.exit(1)

    skill_id_clean = skill_id.strip()
    catalog = load_catalog()
    if catalog is None or 'skills' not in catalog:
        print("Failed to load catalog.", file=sys.stderr)
        sys.exit(1)

    found = None
    for s in catalog['skills']:
        if s.get('id', '').lower() == skill_id_clean.lower() or s.get('name', '').lower() == skill_id_clean.lower():
            found = s
            break

    if not found:
        print(f"Error: Skill '{skill_id_clean}' not found in catalog.", file=sys.stderr)
        sys.exit(1)

    skills_dir = get_skills_dir()
    target_skill_dir = os.path.join(skills_dir, found['id'])
    print(f"[*] Installing skill '{found['id']}' into: {target_skill_dir}")

    cat_path = found.get('path', '')
    if cat_path and cat_path.endswith('/SKILL.md'):
        remote_skill_path = cat_path[:-len('/SKILL.md')]
    elif cat_path:
        remote_skill_path = os.path.dirname(cat_path)
    else:
        remote_skill_path = f"skills/{found['id']}"

    script_dir = os.path.dirname(os.path.abspath(__file__))
    local_skill_src = os.path.join(script_dir, remote_skill_path)

    if os.path.exists(local_skill_src) and os.path.isdir(local_skill_src):
        ok = copy_folder_local(local_skill_src, target_skill_dir)
    else:
        ok = download_folder_recursive(remote_skill_path, target_skill_dir)

    if ok and os.path.exists(os.path.join(target_skill_dir, "SKILL.md")):
        print(f"[OK] Successfully installed '{found['id']}'!")
    else:
        print(f"[!] Installation completed with potential missing files for '{found['id']}'.")

def cmd_installed():
    skills_dir = get_skills_dir()
    if not os.path.exists(skills_dir):
        print("No skills currently installed.")
        return

    dirs = [d for d in os.listdir(skills_dir) if os.path.isdir(os.path.join(skills_dir, d))]
    if not dirs:
        print("No skills currently installed.")
        return

    print(f"\n[*] Installed Skills in {skills_dir} ({len(dirs)} total):\n" + "-"*60)
    for d in sorted(dirs):
        skill_md = os.path.join(skills_dir, d, "SKILL.md")
        has_md = "[OK] SKILL.md" if os.path.exists(skill_md) else "[X] No SKILL.md"
        print(f"* {d:<50} {has_md}")

def main():
    if len(sys.argv) < 2:
        print("Usage: python skills_cli.py [list|search|install|installed] [args]")
        sys.exit(1)

    cmd = sys.argv[1].lower()
    if cmd == "list":
        cat = None
        q = None
        if len(sys.argv) > 2:
            if sys.argv[2] == "--category" and len(sys.argv) > 3:
                cat = sys.argv[3]
            elif sys.argv[2] == "--query" and len(sys.argv) > 3:
                q = sys.argv[3]
            else:
                q = sys.argv[2]
        cmd_list(category=cat, query=q)
    elif cmd == "search":
        q = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else ""
        cmd_search(q)
    elif cmd == "install":
        if len(sys.argv) < 3:
            print("Please specify skill name/id to install.", file=sys.stderr)
            sys.exit(1)
        cmd_install(sys.argv[2])
    elif cmd == "installed":
        cmd_installed()
    else:
        print(f"Unknown command: {cmd}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
