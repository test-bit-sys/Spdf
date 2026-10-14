"""
Script to:
1. Commit and push updated screenshot and trademark-free files to GitHub.
2. Set repository topics on GitHub for enhanced search discovery.
3. Create GitHub Release v1.0.0 and optionally attach the Windows binary zip.
"""

import subprocess
import urllib.request
import json
import os
import sys

def get_git_credentials():
    p = subprocess.Popen(['git', 'credential', 'fill'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
    out, _ = p.communicate(input='protocol=https\nhost=github.com\n\n')
    username = None
    token = None
    for line in out.splitlines():
        if line.startswith('username='):
            username = line.split('=', 1)[1]
        elif line.startswith('password='):
            token = line.split('=', 1)[1]
    return username, token


def push_updates(token, username):
    base_dir = os.path.abspath(os.path.dirname(__file__))

    def run_cmd(cmd):
        print(f"Running: {' '.join(cmd)}")
        res = subprocess.run(cmd, cwd=base_dir, capture_output=True, text=True)
        return res

    run_cmd(["git", "add", "."])
    st = run_cmd(["git", "status", "--porcelain"])
    if st.stdout.strip():
        run_cmd(["git", "commit", "-m", "fix: remove all trademark references, update official screenshot and branding"])
        auth_remote = f"https://{username}:{token}@github.com/{username}/Spdf.git"
        run_cmd(["git", "remote", "set-url", "origin", auth_remote])
        push_res = run_cmd(["git", "push", "origin", "main"])
        clean_url = f"https://github.com/{username}/Spdf.git"
        run_cmd(["git", "remote", "set-url", "origin", clean_url])
        if push_res.returncode == 0:
            print("[SUCCESS] Pushed updated files to GitHub.")
        else:
            print("[ERROR] Push failed:", push_res.stderr)


def set_repo_topics(token, username, repo_name="Spdf"):
    url = f"https://api.github.com/repos/{username}/{repo_name}/topics"
    topics = [
        "pdf",
        "pdf-reader",
        "pdf-editor",
        "pdf-viewer",
        "pyside6",
        "qt6",
        "pymupdf",
        "desktop-app",
        "python",
        "annotations",
        "digital-signature",
        "open-source"
    ]
    payload = {"names": topics}
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "Spdf-Publisher/1.0"
    }
    req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers=headers, method="PUT")
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode())
            print(f"[SUCCESS] Repository topics set to: {data.get('names')}")
    except Exception as e:
        print(f"[ERROR] Setting topics failed: {e}")


def create_release(token, username, repo_name="Spdf", tag="v1.0.0"):
    url = f"https://api.github.com/repos/{username}/{repo_name}/releases"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "Spdf-Publisher/1.0"
    }
    
    release_notes = (
        "## Spdf v1.0.0 — Initial Official Release\n\n"
        "Welcome to the first official release of **Spdf**, a modern, high-performance desktop PDF reader, editor, and organizer built natively with Python, PySide6, and PyMuPDF.\n\n"
        "### 🚀 Key Highlights\n"
        "- **Modern Obsidian Dark UI**: Deep charcoal canvas with gold (#E5A93C) and crimson accents.\n"
        "- **High-DPI Page Canvas**: Asynchronous vector page rendering with smooth scrolling, zoom presets, and drop shadows.\n"
        "- **Rich Annotations**: Highlighting, underlines, strikethroughs, Bezier-smoothed ink pen, text overlays, and sticky notes.\n"
        "- **Document Organizer**: Merge multiple PDFs, split by custom range/burst, extract pages, rotate CW/CCW, and delete.\n"
        "- **Security & Privacy**: AES-256 encryption, password protection, interactive digital signature pad, and permanent redactions.\n"
        "- **Export & Print**: Native Windows printing (Ctrl+P) and multi-format conversion (PNG/JPG/TIFF/TXT).\n"
        "- **Windows Installer & Standalone Executable**: Instant one-click installation with desktop shortcuts.\n"
    )

    payload = {
        "tag_name": tag,
        "target_commitish": "main",
        "name": f"Spdf {tag} — Official Release",
        "body": release_notes,
        "draft": False,
        "prerelease": False
    }

    req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode())
            release_id = data.get("id")
            html_url = data.get("html_url")
            upload_url = data.get("upload_url").split("{?")[0]
            print(f"[SUCCESS] Release created: {html_url}")
            return release_id, upload_url, html_url
    except urllib.error.HTTPError as e:
        if e.code == 422:
            print(f"[INFO] Release {tag} already exists.")
            # Fetch existing release
            req_get = urllib.request.Request(f"{url}/tags/{tag}", headers=headers)
            with urllib.request.urlopen(req_get) as resp_get:
                data = json.loads(resp_get.read().decode())
                return data.get("id"), data.get("upload_url").split("{?")[0], data.get("html_url")
        else:
            print(f"[ERROR] Release creation failed: {e.read().decode()}")
            raise


if __name__ == "__main__":
    user, tok = get_git_credentials()
    if not tok:
        print("No GitHub token found.")
        sys.exit(1)

    print(f"Authenticated as: {user}")
    print("1. Pushing cleaned files to GitHub...")
    push_updates(tok, user)

    print("\n2. Setting repository search topics...")
    set_repo_topics(tok, user, "Spdf")

    print("\n3. Creating GitHub Release...")
    rel_id, up_url, rel_url = create_release(tok, user, "Spdf", "v1.0.0")

    print(f"\nAll operations completed! Release URL: {rel_url}")
