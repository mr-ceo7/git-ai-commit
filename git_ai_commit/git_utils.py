"""
Git utility functions for git-ai-commit.
"""

import subprocess
from typing import List, Optional, Tuple


def run_git(args: List[str]) -> Tuple[int, str, str]:
    """Execute a git command and return (returncode, stdout, stderr)."""
    try:
        proc = subprocess.run(
            ["git"] + args,
            capture_output=True,
            text=True,
            check=False
        )
        return proc.returncode, proc.stdout, proc.stderr
    except FileNotFoundError:
        return 127, "", "git command not found in PATH"


def is_git_repository() -> bool:
    """Check if the current working directory is inside a git repository."""
    code, out, _ = run_git(["rev-parse", "--is-inside-work-tree"])
    return code == 0 and out.strip() == "true"


def get_git_root() -> Optional[str]:
    """Return the absolute path of the top-level repository directory."""
    code, out, _ = run_git(["rev-parse", "--show-toplevel"])
    return out.strip() if code == 0 else None


def get_current_branch() -> str:
    """Return the name of the current git branch."""
    code, out, _ = run_git(["branch", "--show-current"])
    if code == 0 and out.strip():
        return out.strip()
    code, out, _ = run_git(["rev-parse", "--abbrev-ref", "HEAD"])
    return out.strip() if code == 0 else "HEAD"


def has_remotes() -> bool:
    """Check if remote repositories are configured."""
    code, out, _ = run_git(["remote"])
    return code == 0 and bool(out.strip())


def has_staged_changes() -> bool:
    """Check if there are already staged changes."""
    code, _, _ = run_git(["diff", "--staged", "--quiet"])
    return code != 0


def get_unstaged_files() -> List[str]:
    """
    Get list of unstaged or untracked files from git status.
    Respects porcelain format entries.
    """
    code, out, _ = run_git(["status", "--porcelain"])
    if code != 0 or not out.strip():
        return []

    unstaged_files = []
    for line in out.strip().split("\n"):
        if not line.strip():
            continue
        # Porcelain status has 2 chars for index/working tree status, followed by space
        # e.g. ' M file', '?? file', ' M file -> file2'
        status = line[:2]
        filepath = line[3:].strip()
        # If unstaged modification, deletion, or untracked
        if status[1] != " " or status == "??" or status[0] == "?":
            if " -> " in filepath:
                filepath = filepath.split(" -> ")[1].strip()
            unstaged_files.append(filepath)
    return unstaged_files


def stage_files(files: List[str]) -> Tuple[bool, str]:
    """Stage specific files."""
    if not files:
        return True, ""
    code, out, err = run_git(["add"] + files)
    return code == 0, err or out


def stage_all() -> Tuple[bool, str]:
    """Stage all tracked and untracked changes."""
    code, out, err = run_git(["add", "-A"])
    return code == 0, err or out


def get_staged_diff() -> Optional[str]:
    """Get the diff of currently staged files."""
    code, out, _ = run_git(["diff", "--staged"])
    if code != 0:
        return None
    return out


def commit_changes(message: str) -> Tuple[bool, str]:
    """Commit staged changes with message."""
    code, out, err = run_git(["commit", "-m", message])
    return code == 0, err or out


def push_changes() -> Tuple[bool, str]:
    """Push commits to the current remote branch."""
    code, out, err = run_git(["push"])
    return code == 0, err or out
