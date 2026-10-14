"""
GitHub Repository Creation and Direct Push Automation for Spdf.
Uses the stored credentials from Windows Git Credential Manager to create the
repository via GitHub API and push the repository cleanly to GitHub.
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


def create_github_repo(username, token, repo_name="Spdf", description="A modern, high-performance desktop PDF reader, editor, and organizer built with PySide6 and PyMuPDF."):
    url = "https://api.github.com/user/repos"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "Spdf-Publisher/1.0"
    }
    payload = {
        "name": repo_name,
        "description": description,
        "private": False,
        "has_issues": True,
        "has_projects": True,
        "has_wiki": False
    }
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req) as resp:
            res_data = json.loads(resp.read().decode())
            print(f"[SUCCESS] Repository '{repo_name}' created on GitHub: {res_data.get('html_url')}")
            return res_data.get('html_url'), res_data.get('clone_url')
    except urllib.error.HTTPError as e:
        if e.code == 422:
            print(f"[INFO] Repository '{repo_name}' already exists on GitHub for user '{username}'.")
            return f"https://github.com/{username}/{repo_name}", f"https://github.com/{username}/{repo_name}.git"
        else:
            err_msg = e.read().decode()
            print(f"[ERROR] Failed to create repository: {e.code} - {err_msg}")
            raise


def git_commit_and_push(remote_url, token, username):
    base_dir = os.path.abspath(os.path.dirname(__file__))

    def run_cmd(cmd):
        print(f"Running: {' '.join(cmd)}")
        res = subprocess.run(cmd, cwd=base_dir, capture_output=True, text=True)
        if res.returncode != 0:
            print(f"Stdout: {res.stdout}")
            print(f"Stderr: {res.stderr}")
        return res

    # 1. Initialize git repository if needed
    if not os.path.exists(os.path.join(base_dir, ".git")):
        run_cmd(["git", "init", "-b", "main"])

    # 2. Stage files
    run_cmd(["git", "add", "."])

    # 3. Check status
    st = run_cmd(["git", "status", "--porcelain"])
    if st.stdout.strip():
        run_cmd([
            "git", "commit", "-m",
            "feat: initial release of Spdf - Professional Desktop PDF Suite v1.0.0\n\n"
            "- Modern luxury obsidian dark theme UI\n"
            "- High-DPI page canvas with asynchronous rendering\n"
            "- Complete annotation suite (Highlights, Underline, Ink pen, Text overlays, Sticky notes)\n"
            "- Document organizer (Merge, Split, Extract, Rotate, Delete pages)\n"
            "- Security & Encryption (AES-256, Password protection, Digital signature pad, Redaction)\n"
            "- Native printing (Ctrl+P) and Multi-format export (PNG/JPG/TIFF/TXT)\n"
            "- Windows installer and standalone executable builder"
        ])

    # 4. Set remote URL
    # Embed token for authenticated push without interactive prompts
    auth_remote = remote_url.replace("https://", f"https://{username}:{token}@")
    
    # Check if remote origin already exists
    remotes = run_cmd(["git", "remote"]).stdout.splitlines()
    if "origin" in remotes:
        run_cmd(["git", "remote", "set-url", "origin", auth_remote])
    else:
        run_cmd(["git", "remote", "add", "origin", auth_remote])

    # 5. Push to GitHub
    print("\nPushing to GitHub...")
    push_res = run_cmd(["git", "push", "-u", "origin", "main", "--force"])
    
    # Reset origin to clean URL without embedded token for security
    clean_url = f"https://github.com/{username}/Spdf.git"
    run_cmd(["git", "remote", "set-url", "origin", clean_url])

    if push_res.returncode == 0:
        print("\n" + "=" * 60)
        print(f"PUSH SUCCESSFUL! Repository is live at: https://github.com/{username}/Spdf")
        print("=" * 60)
        return True
    else:
        print("\nPush failed:", push_res.stderr)
        return False


if __name__ == "__main__":
    print("Fetching GitHub credentials from Windows Credential Manager...")
    user, tok = get_git_credentials()
    if not tok:
        print("Error: No GitHub token found in Git Credential Manager.")
        sys.exit(1)
    print(f"Authenticated as: {user}")

    html_url, clone_url = create_github_repo(user, tok, "Spdf")
    success = git_commit_and_push(clone_url, tok, user)
    if not success:
        sys.exit(1)
