#!/usr/bin/env python3
"""Commit and push one Brain run's changes, and nothing else.

    publish.py baseline <brain_root>
    publish.py stage <brain_root> <changed_file>...   (paths relative to brain_root)
    publish.py commit <brain_root> --tree <sha> --message <text>

Each command prints one outcome line. Exit codes: 0 BASELINE, STAGED, or
PUSHED; 2 SKIP (no Git repository or no upstream); 3 HOLD (changes left
uncommitted); 4 PUSH_FAILED (commit kept local); 1 usage error.
"""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Sequence

STATE_NAME = "brain-publish-state.json"
VALIDATOR = Path(__file__).resolve().parent / "validate.py"
IN_PROGRESS = ("MERGE_HEAD", "CHERRY_PICK_HEAD", "REVERT_HEAD", "REBASE_HEAD", "rebase-merge", "rebase-apply")


class Outcome(Exception):
    def __init__(self, label: str, code: int, detail: str = ""):
        super().__init__(detail)
        self.label, self.code, self.detail = label, code, detail


def hold(detail: str) -> Outcome:
    return Outcome("HOLD", 3, detail)


def git(root: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess:
    result = subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True)
    if check and result.returncode != 0:
        raise hold(f"git {' '.join(args)} failed: {result.stderr.strip()}")
    return result


def out(root: Path, *args: str) -> str:
    return git(root, *args).stdout.strip()


def snapshot(root: Path) -> Dict[str, str]:
    """Content hash of every file under the Brain root, untracked ones included."""
    hashes = {}
    for directory, subdirectories, files in os.walk(root):
        subdirectories[:] = [name for name in subdirectories if name != ".git"]
        for name in files:
            path = Path(directory, name)
            hashes[path.relative_to(root).as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()
    return hashes


def repo_state(root: Path) -> dict:
    """Live facts the run's commit depends on; any change between steps holds the publish."""
    branch = git(root, "symbolic-ref", "-q", "HEAD", check=False).stdout.strip()
    if not branch:
        raise hold("HEAD is detached")
    for name in IN_PROGRESS:
        if Path(out(root, "rev-parse", "--path-format=absolute", "--git-path", name)).exists():
            raise hold(f"a Git operation is in progress ({name})")
    remote, _, remote_ref = out(
        root, "for-each-ref", "--format=%(upstream:remotename)%00%(upstream:remoteref)", branch
    ).partition("\0")
    return {"head": out(root, "rev-parse", "HEAD"), "branch": branch, "remote": remote, "remote_ref": remote_ref}


def state_path(root: Path) -> Path:
    return Path(out(root, "rev-parse", "--path-format=absolute", "--git-path", STATE_NAME))


def load(root: Path) -> dict:
    path = state_path(root)
    if not path.exists():
        raise hold("no baseline recorded for this run")
    state = json.loads(path.read_text())
    if state.get("skip"):
        raise Outcome("SKIP", 2, state["skip"])
    if state.get("hold"):
        raise hold(f"at baseline: {state['hold']}")
    live = repo_state(root)
    for key in ("head", "branch", "remote", "remote_ref"):
        if live[key] != state[key]:
            raise hold(f"{key} changed since the baseline ({state[key]} -> {live[key]})")
    return state


def baseline(root: Path) -> Outcome:
    if git(root, "rev-parse", "--is-inside-work-tree", check=False).returncode != 0:
        raise Outcome("SKIP", 2, "brain_root is not in a Git repository")
    path = state_path(root)
    prefix = out(root, "rev-parse", "--show-prefix")
    state: dict = {"prefix": prefix, "snapshot": snapshot(root)}
    try:
        state.update(repo_state(root))
        if not state["remote"]:
            state["skip"] = f"{state['branch']} has no upstream"
        elif out(root, "rev-parse", "@{upstream}") != state["head"]:
            state["hold"] = "the branch is ahead of or behind its upstream"
        elif git(root, "diff", "--cached", "--quiet", check=False).returncode:
            state["hold"] = "the index already has staged changes"
        else:
            status = git(root, "status", "--porcelain=v1", "-z", "--untracked-files=all", "--", ".").stdout
            state["dirty"] = [entry[3:] for entry in status.split("\0") if entry[:2].strip()]
    except Outcome as outcome:
        state["hold"] = outcome.detail
    path.write_text(json.dumps(state))
    return Outcome("BASELINE", 0, str(path))


def stage(root: Path, files: Sequence[str]) -> Outcome:
    state = load(root)
    if subprocess.run([sys.executable, str(VALIDATOR), str(root)], capture_output=True).returncode:
        raise hold("final validation has errors")
    claimed = {Path(os.path.relpath((root / name).resolve(), root.resolve())).as_posix() for name in files}
    current = snapshot(root)
    changed = {name for name in set(current) | set(state["snapshot"]) if current.get(name) != state["snapshot"].get(name)}
    if changed != claimed:
        raise hold(f"changed files differ from the run's files: unexpected {sorted(changed - claimed)}, unchanged {sorted(claimed - changed)}")
    repo_paths = sorted(state["prefix"] + name for name in claimed)
    preexisting = sorted(set(state["dirty"]) & set(repo_paths))
    if preexisting:
        raise hold(f"files had uncommitted edits before the run: {preexisting}")
    git(root, "add", "-A", "--", *(f":/{name}" for name in repo_paths))
    staged = set(filter(None, git(root, "diff", "--cached", "--name-only", "--no-renames", "-z").stdout.split("\0")))
    if staged != set(repo_paths):
        git(root, "reset", "-q", "--", *(f":/{name}" for name in repo_paths))
        raise hold(f"the index holds other changes: {sorted(staged - set(repo_paths))}")
    tree = out(root, "write-tree")
    print(out(root, "diff", "--no-renames", state["head"], tree))
    return Outcome("STAGED", 0, f"TREE {tree}")


def commit(root: Path, tree: str, message: str) -> Outcome:
    state = load(root)
    if out(root, "write-tree") != tree:
        raise hold("the index changed after it was reviewed")
    new = out(root, "commit-tree", tree, "-p", state["head"], "-m", message)
    git(root, "update-ref", "-m", "brain publish", state["branch"], new, state["head"])
    state_path(root).unlink()
    lease = f"--force-with-lease={state['remote_ref']}:{state['head']}"
    pushed = git(root, "push", lease, state["remote"], f"{new}:{state['remote_ref']}", check=False)
    if pushed.returncode:
        raise Outcome("PUSH_FAILED", 4, f"commit {new} stays local: {pushed.stderr.strip()}")
    return Outcome("PUSHED", 0, f"{new} to {state['remote']} {state['remote_ref']}")


def run(arguments: List[str]) -> Outcome:
    if len(arguments) >= 2 and arguments[0] == "baseline":
        return baseline(Path(arguments[1]))
    if len(arguments) >= 3 and arguments[0] == "stage":
        return stage(Path(arguments[1]), arguments[2:])
    if len(arguments) == 6 and arguments[0] == "commit" and arguments[2] == "--tree" and arguments[4] == "--message":
        return commit(Path(arguments[1]), arguments[3], arguments[5])
    return Outcome("USAGE", 1, "\n" + "\n".join(__doc__.strip().splitlines()[2:5]))


def main(argv: Optional[Sequence[str]] = None) -> int:
    try:
        outcome = run(list(sys.argv[1:] if argv is None else argv))
    except Outcome as raised:
        outcome = raised
    print(f"{outcome.label}: {outcome.detail}" if outcome.detail else outcome.label)
    return outcome.code


if __name__ == "__main__":
    sys.exit(main())
