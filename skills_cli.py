import sys
import os
import re
import json
import shutil
import tempfile
import urllib.request
import urllib.error
import urllib.parse

# Reconfigure sys.stdout/stderr to UTF-8 for Windows terminal compatibility.
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

RAW_BASE_URL = "https://raw.githubusercontent.com/rmyndharis/antigravity-skills/"
API_BASE_URL = "https://api.github.com/repos/rmyndharis/antigravity-skills/contents/"
COMMIT_URL = "https://api.github.com/repos/rmyndharis/antigravity-skills/commits/main"
_remote_revision = None

GLOBAL_SKILLS_DIR = os.path.join(os.path.expanduser("~"), ".gemini", "antigravity", "skills")


# Mirrors resolveTargetDir() in bin/cli.js: AG_SKILLS_DIR overrides the destination and a
# leading ~ is expanded, so this CLI and ag-skills always agree on where skills live.
def get_skills_dir():
    override = os.environ.get("AG_SKILLS_DIR")
    if override:
        if override == "~" or override.startswith(("~/", "~\\")):
            override = os.path.expanduser("~") + override[1:]
        return os.path.abspath(override)
    return os.path.abspath(GLOBAL_SKILLS_DIR)


SKILL_ID_RE = re.compile(r'[a-z0-9-]+')


def validate_skill_id(skill_id):
    if not isinstance(skill_id, str) or not SKILL_ID_RE.fullmatch(skill_id):
        raise ValueError(f"invalid skill id: {skill_id!r}")
    return skill_id


def skill_folder_from_catalog(cat_path, skill_id):
    validate_skill_id(skill_id)
    candidate = cat_path or f"skills/{skill_id}/SKILL.md"
    if candidate != f"skills/{skill_id}/SKILL.md":
        raise ValueError(f"unsafe skill path in catalog entry: {candidate!r}")
    return candidate[:-len('/SKILL.md')]


# Check both path spelling and filesystem resolution before reading or writing.
def contained_join(base, *parts):
    base_abs = os.path.abspath(base)
    target = os.path.abspath(os.path.join(base_abs, *parts))
    base_real = os.path.realpath(base_abs)
    target_real = os.path.realpath(target)
    try:
        contained = (target != base_abs and os.path.commonpath([base_abs, target]) == base_abs
                     and target_real != base_real
                     and os.path.commonpath([base_real, target_real]) == base_real)
    except ValueError:
        contained = False
    if not contained:
        raise ValueError(f"refusing to write outside {base_abs}: {target}")
    current = base_abs
    for part in os.path.relpath(target, base_abs).split(os.sep):
        current = os.path.join(current, part)
        if os.path.islink(current):
            raise ValueError(f"refusing symbolic link: {current}")
    return target


# Stdlib urllib fetcher with user-agent and timeout handling.
def fetch_json(url):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "AntigravitySkillsInstaller/1.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode('utf-8'))
    except Exception as e:
        print(f"Error fetching {url}: {e}", file=sys.stderr)
        return None

# Stdlib binary fetcher for raw files.
def fetch_bytes(url):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "AntigravitySkillsInstaller/1.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            return resp.read()
    except Exception as e:
        print(f"Error downloading {url}: {e}", file=sys.stderr)
        return None


def get_remote_revision():
    global _remote_revision
    if _remote_revision is None:
        commit = fetch_json(COMMIT_URL)
        revision = commit.get('sha') if isinstance(commit, dict) else None
        if not isinstance(revision, str) or not re.fullmatch(r'[0-9a-f]{40}', revision):
            raise ValueError("could not resolve a verified commit for main")
        _remote_revision = revision
    return _remote_revision


def remote_file_url(relative_path):
    return RAW_BASE_URL + get_remote_revision() + '/' + urllib.parse.quote(relative_path, safe='/')

# Prefer the catalog.json shipped next to this script; fall back to raw GitHub.
def load_catalog():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    local_catalog = os.path.join(script_dir, "catalog.json")
    if os.path.exists(local_catalog):
        try:
            with open(local_catalog, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    try:
        return fetch_json(remote_file_url('catalog.json'))
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return None


def load_aliases(allow_remote=False):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    local_aliases = os.path.join(script_dir, "aliases.json")
    if os.path.exists(local_aliases) and _remote_revision is None:
        try:
            with open(local_aliases, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (OSError, ValueError) as e:
            print(f"Warning: could not read aliases.json: {e}", file=sys.stderr)
            return {}
    elif (allow_remote and (_remote_revision is not None
          or (not os.path.exists(os.path.join(script_dir, "catalog.json"))
              and not os.path.exists(os.path.join(script_dir, "skills"))))):
        data = fetch_json(remote_file_url('aliases.json'))
    else:
        return {}
    return data['aliases'] if isinstance(data, dict) and isinstance(data.get('aliases'), dict) else {}

def skill_matches(s, query):
    if not query:
        return True
    haystack = " ".join([
        s.get('id', ''),
        s.get('name', ''),
        s.get('description', ''),
        s.get('category', ''),
        " ".join(s.get('tags', [])),
        " ".join(s.get('triggers', [])),
    ]).lower()
    # Match on every whitespace-separated token rather than the whole string, so
    # "kubernetes helm" finds skills mentioning both instead of requiring that
    # exact adjacent phrase (which no catalog entry contains).
    return all(token in haystack for token in query.lower().split())

def cmd_list(category=None, query=None):
    global _remote_revision
    _remote_revision = None
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

    # Cap only the unfiltered listing; a filtered result set is small enough to show
    # in full, and truncating it would let a caller conclude a skill does not exist.
    limit = None if (category or query) else 40
    for s in (skills if limit is None else skills[:limit]):
        cat = f"[{s.get('category', 'general')}]"
        print(f"* {s.get('id', ''):<50} {cat:<12}")
        if s.get('description'):
            desc = s['description'][:80] + "..." if len(s['description']) > 80 else s['description']
            print(f"  └─ {desc}")
    if limit is not None and len(skills) > limit:
        print(f"\n... and {len(skills) - limit} more. Use --query <term> or search <term> to filter.")

def cmd_search(query):
    if not query or not query.strip():
        print("Usage: python skills_cli.py search <term>", file=sys.stderr)
        sys.exit(1)
    cmd_list(query=query.strip())

# Local source copy, used whenever the repo's skills/ tree sits beside this script.
def copy_folder_local(local_src, local_dst):
    if os.path.islink(local_src) or not os.path.isdir(local_src):
        raise ValueError(f"invalid skill source directory: {local_src}")

    def fail_walk(error):
        raise error

    os.makedirs(local_dst, exist_ok=True)
    for root, dirs, files in os.walk(local_src, onerror=fail_walk):
        rel_path = os.path.relpath(root, local_src)
        target_dir = local_dst if rel_path == "." else contained_join(local_dst, rel_path)
        os.makedirs(target_dir, exist_ok=True)
        for directory in dirs:
            contained_join(local_src, os.path.relpath(os.path.join(root, directory), local_src))
        for f in files:
            src_file = contained_join(local_src, os.path.relpath(os.path.join(root, f), local_src))
            if not os.path.isfile(src_file):
                raise ValueError(f"unsupported source file: {src_file}")
            dst_file = contained_join(target_dir, f)
            shutil.copy2(src_file, dst_file)
            print(f"  └─ Copied: {f}")
    return True


def safe_remote_name(name):
    return (isinstance(name, str) and name not in ('', '.', '..')
            and not any(char in name for char in '/\\%?#:')
            and not any(ord(char) < 32 or ord(char) == 127 for char in name))


# A complete directory listing is required before an installation can be activated.
def download_folder_recursive(remote_path, local_target_dir):
    parts = remote_path.split('/')
    if (len(parts) < 2 or parts[0] != 'skills'
            or not SKILL_ID_RE.fullmatch(parts[1])
            or not all(safe_remote_name(part) for part in parts[2:])):
        raise ValueError(f"unsafe remote skill path: {remote_path!r}")
    os.makedirs(local_target_dir, exist_ok=True)
    api_url = API_BASE_URL + urllib.parse.quote(remote_path, safe='/') + '?ref=' + get_remote_revision()
    items = fetch_json(api_url)
    if not items or not isinstance(items, list):
        print(f"  └─ Folder listing unavailable or empty: {remote_path}", file=sys.stderr)
        return False

    success = True
    seen = set()
    for item in items:
        if not isinstance(item, dict):
            success = False
            continue
        item_name = item.get('name', '')
        item_path = item.get('path', '')
        item_type = item.get('type', '')
        if (not safe_remote_name(item_name) or item_name in seen
                or item_path != remote_path + '/' + item_name):
            print(f"  └─ Invalid directory entry in {remote_path}: {item_path!r}", file=sys.stderr)
            success = False
            continue
        seen.add(item_name)
        target_item_path = contained_join(local_target_dir, item_name)

        if item_type == 'file':
            download_url = remote_file_url(item_path)
            if item.get('download_url') not in (None, download_url):
                print(f"  └─ Invalid download URL for: {item_path}", file=sys.stderr)
                success = False
                continue
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
        else:
            print(f"  └─ Unsupported directory entry type: {item_type!r}", file=sys.stderr)
            success = False

    return success


def check_install_paths(source, target):
    source_real = os.path.realpath(source)
    target_real = os.path.realpath(target)
    try:
        common = os.path.commonpath([source_real, target_real])
    except ValueError:
        common = None
    if common in (source_real, target_real):
        raise ValueError("skill source and installation destination must not overlap")
    for label, candidate in (('source', source), ('destination', target)):
        if os.path.islink(candidate):
            raise ValueError(f"refusing symbolic link {label}: {candidate}")
        if os.path.lexists(candidate) and not os.path.isdir(candidate):
            raise ValueError(f"skill {label} is not a directory: {candidate}")


def install_skill(remote_path, source, skills_dir, skill_id):
    target = contained_join(skills_dir, skill_id)
    check_install_paths(source, target)
    os.makedirs(skills_dir, exist_ok=True)
    lock = contained_join(skills_dir, f'.{skill_id}.install-lock')
    try:
        os.mkdir(lock)
    except FileExistsError:
        raise ValueError(f"another installation is active; lock exists: {lock}")

    transaction = None
    keep_backup = False
    activated = False
    try:
        transaction = tempfile.mkdtemp(prefix=f'.{skill_id}-', dir=skills_dir)
        staged = os.path.join(transaction, 'staged')
        backup = os.path.join(transaction, 'backup')
        if os.path.isdir(source):
            complete = copy_folder_local(source, staged)
        else:
            complete = download_folder_recursive(remote_path, staged)
        skill_md = os.path.join(staged, 'SKILL.md')
        if (not complete or not os.path.isfile(skill_md) or os.path.islink(skill_md)
                or os.path.getsize(skill_md) == 0):
            raise ValueError(f"Installation incomplete for '{skill_id}' - no complete skill was retrieved.")

        target = contained_join(skills_dir, skill_id)
        check_install_paths(source, target)
        replacing = os.path.isdir(target)
        if replacing:
            os.replace(target, backup)
        try:
            os.replace(staged, target)
            activated = True
        except BaseException as activation_error:
            if replacing:
                try:
                    os.replace(backup, target)
                except BaseException as rollback_error:
                    keep_backup = True
                    raise OSError(f"activation failed ({activation_error}); rollback failed "
                                  f"({rollback_error}); previous installation retained at {backup}") from rollback_error
            raise
    finally:
        if transaction and not activated and os.path.lexists(os.path.join(transaction, 'backup')):
            keep_backup = True
            print(f"Previous installation retained at {os.path.join(transaction, 'backup')}", file=sys.stderr)
        if transaction and not keep_backup:
            try:
                shutil.rmtree(transaction)
            except OSError as e:
                print(f"Warning: could not remove temporary installation files at {transaction}: {e}", file=sys.stderr)
        try:
            os.rmdir(lock)
        except OSError as e:
            print(f"Warning: could not remove installation lock {lock}: {e}", file=sys.stderr)

def cmd_install(skill_id):
    global _remote_revision
    _remote_revision = None
    if not skill_id or not skill_id.strip():
        print("Please specify skill name/id to install.", file=sys.stderr)
        sys.exit(1)

    skill_id_clean = skill_id.strip()
    catalog = load_catalog()
    if not isinstance(catalog, dict) or not isinstance(catalog.get('skills'), list):
        print("Failed to load catalog.", file=sys.stderr)
        sys.exit(1)

    def find_skill(query):
        for entry in catalog['skills']:
            if not isinstance(entry, dict):
                continue
            if any(isinstance(entry.get(key), str) and entry[key].lower() == query
                   for key in ('id', 'name')):
                return entry
        return None

    try:
        query = skill_id_clean.lower()
        aliases = load_aliases()
        alias = aliases.get(query)
        if alias is not None:
            validate_skill_id(query)
            query = validate_skill_id(alias)
        found = find_skill(query)
        if found is None and alias is None:
            alias = load_aliases(allow_remote=True).get(query)
            if alias is not None:
                validate_skill_id(query)
                found = find_skill(validate_skill_id(alias))
        if found is None:
            raise ValueError(f"Skill '{skill_id_clean}' not found in catalog.")

        skills_dir = get_skills_dir()
        remote_skill_path = skill_folder_from_catalog(found.get('path', ''), found.get('id'))
        target_skill_dir = contained_join(skills_dir, found['id'])
        script_dir = os.path.dirname(os.path.abspath(__file__))
        local_skill_src = contained_join(script_dir, remote_skill_path)
        print(f"[*] Installing skill '{found['id']}' into: {target_skill_dir}")
        install_skill(remote_skill_path, local_skill_src, skills_dir, found['id'])
    except (ValueError, OSError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"[OK] Successfully installed '{found['id']}'!")

def cmd_installed():
    skills_dir = get_skills_dir()
    if not os.path.exists(skills_dir):
        print("No skills currently installed.")
        return

    dirs = [d for d in os.listdir(skills_dir)
            if not d.startswith('.') and not os.path.islink(os.path.join(skills_dir, d))
            and os.path.isdir(os.path.join(skills_dir, d))]
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
