#!/usr/bin/env python3
"""
Clone or refresh a GitHub repository into the local inbox.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlparse


TOP_LEVEL_FILES = (
    "package.json",
    "pnpm-workspace.yaml",
    "turbo.json",
    "pyproject.toml",
    "requirements.txt",
    "setup.py",
    "setup.cfg",
    "Pipfile",
    "poetry.lock",
    "Cargo.toml",
    "go.mod",
    "pom.xml",
    "build.gradle",
    "build.gradle.kts",
    "settings.gradle",
    "settings.gradle.kts",
    "Dockerfile",
    "docker-compose.yml",
    "docker-compose.yaml",
    "compose.yml",
    "compose.yaml",
    "Makefile",
    "justfile",
    "Taskfile.yml",
    "Taskfile.yaml",
)

LICENSE_FILES = (
    "LICENSE",
    "LICENSE.md",
    "LICENSE.txt",
    "COPYING",
    "COPYING.md",
    "COPYING.txt",
)

TOP_LEVEL_DIRS = (
    "apps",
    "packages",
    "src",
    "lib",
    "cmd",
    "bin",
    "examples",
    "example",
    "demo",
    "docs",
    "tests",
    "test",
    ".github",
)


def run_command(args: list[str], cwd: Path | None = None, check: bool = True) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        args,
        cwd=str(cwd) if cwd else None,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    if check and result.returncode != 0:
        stderr = result.stderr.strip()
        stdout = result.stdout.strip()
        details = stderr or stdout or "unknown error"
        raise RuntimeError(f"Command failed: {' '.join(args)}\n{details}")
    return result


def parse_repo_input(raw: str) -> tuple[str, str]:
    value = raw.strip()
    slug_match = re.fullmatch(r"([A-Za-z0-9_.-]+)/([A-Za-z0-9_.-]+)", value)
    if slug_match:
        return slug_match.group(1), strip_git_suffix(slug_match.group(2))

    ssh_match = re.fullmatch(r"git@github\.com:(.+)", value)
    if ssh_match:
        return split_github_path(ssh_match.group(1))

    parsed = urlparse(value)
    host = parsed.netloc.lower()
    if host in {"github.com", "www.github.com", "git@github.com"}:
        return split_github_path(parsed.path)

    if host.endswith("github.com"):
        return split_github_path(parsed.path)

    raise ValueError(f"Unsupported repository input: {raw}")


def split_github_path(path_value: str) -> tuple[str, str]:
    parts = [part for part in path_value.split("/") if part]
    if len(parts) < 2:
        raise ValueError(f"Could not determine owner/repo from: {path_value}")
    owner = parts[0]
    repo = strip_git_suffix(parts[1])
    return owner, repo


def strip_git_suffix(name: str) -> str:
    return name[:-4] if name.endswith(".git") else name


def default_base_dir() -> Path:
    return Path(r"D:\github_inbox")


def repo_destination(base_dir: Path, owner: str, repo: str) -> Path:
    return base_dir / owner / repo


def ensure_matching_remote(repo_dir: Path, owner: str, repo: str) -> str:
    result = run_command(["git", "-C", str(repo_dir), "remote", "get-url", "origin"], check=False)
    origin = result.stdout.strip()
    if result.returncode != 0 or not origin:
        raise RuntimeError(f"{repo_dir} exists but does not have a readable origin remote")

    existing_owner, existing_repo = parse_repo_input(origin)
    if existing_owner.lower() != owner.lower() or existing_repo.lower() != repo.lower():
        raise RuntimeError(
            f"{repo_dir} already points to {existing_owner}/{existing_repo}, not {owner}/{repo}"
        )
    return origin


def clone_or_update_repo(owner: str, repo: str, base_dir: Path, depth: int) -> tuple[Path, str]:
    clone_url = f"https://github.com/{owner}/{repo}.git"
    destination = repo_destination(base_dir, owner, repo)
    destination.parent.mkdir(parents=True, exist_ok=True)

    if not destination.exists():
        clone_cmd = ["git", "clone", clone_url, str(destination)]
        if depth > 0:
            clone_cmd[2:2] = ["--depth", str(depth)]
        run_command(clone_cmd)
        return destination, "cloned"

    if not (destination / ".git").exists():
        raise RuntimeError(f"{destination} exists but is not a git repository")

    ensure_matching_remote(destination, owner, repo)
    run_command(["git", "-C", str(destination), "fetch", "origin", "--prune"])
    run_command(["git", "-C", str(destination), "remote", "set-head", "origin", "-a"], check=False)
    return destination, "updated"


def get_default_branch(repo_dir: Path) -> str | None:
    result = run_command(
        ["git", "-C", str(repo_dir), "symbolic-ref", "refs/remotes/origin/HEAD"],
        check=False,
    )
    if result.returncode == 0:
        ref = result.stdout.strip()
        prefix = "refs/remotes/origin/"
        if ref.startswith(prefix):
            return ref[len(prefix) :]

    show_result = run_command(["git", "-C", str(repo_dir), "remote", "show", "origin"], check=False)
    if show_result.returncode == 0:
        for line in show_result.stdout.splitlines():
            stripped = line.strip()
            if stripped.startswith("HEAD branch:"):
                return stripped.split(":", 1)[1].strip()
    return None


def get_current_branch(repo_dir: Path) -> str | None:
    result = run_command(["git", "-C", str(repo_dir), "branch", "--show-current"], check=False)
    branch = result.stdout.strip()
    return branch or None


def get_origin_url(repo_dir: Path) -> str:
    return run_command(["git", "-C", str(repo_dir), "remote", "get-url", "origin"]).stdout.strip()


def list_top_level(repo_dir: Path) -> dict[str, list[str]]:
    files = [name for name in TOP_LEVEL_FILES if (repo_dir / name).exists()]
    directories = [name for name in TOP_LEVEL_DIRS if (repo_dir / name).exists()]
    licenses = [name for name in LICENSE_FILES if (repo_dir / name).exists()]
    readmes = sorted(
        child.name
        for child in repo_dir.iterdir()
        if child.is_file() and child.name.lower().startswith("readme")
    )
    workflows = sorted(
        str(path.relative_to(repo_dir)).replace("\\", "/")
        for path in (repo_dir / ".github" / "workflows").glob("*")
    ) if (repo_dir / ".github" / "workflows").exists() else []
    return {
        "readmes": readmes,
        "licenses": licenses,
        "files": files,
        "directories": directories,
        "workflows": workflows,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Clone or refresh a GitHub repository into the local inbox.")
    parser.add_argument("repo", help="GitHub URL, SSH URL, or owner/repo slug")
    parser.add_argument(
        "--base-dir",
        default=None,
        help=r"Optional clone root directory. Defaults to D:\github_inbox.",
    )
    parser.add_argument(
        "--depth",
        type=int,
        default=1,
        help="Shallow clone depth. Use 0 to request a full clone on first download.",
    )
    args = parser.parse_args()

    try:
        owner, repo = parse_repo_input(args.repo)
        base_dir = Path(args.base_dir).expanduser() if args.base_dir else default_base_dir()
        repo_dir, status = clone_or_update_repo(owner, repo, base_dir, args.depth)
        metadata = {
            "status": status,
            "repo_id": f"{owner}/{repo}",
            "owner": owner,
            "repo": repo,
            "clone_url": f"https://github.com/{owner}/{repo}.git",
            "origin_url": get_origin_url(repo_dir),
            "local_path": str(repo_dir),
            "default_branch": get_default_branch(repo_dir),
            "current_branch": get_current_branch(repo_dir),
            "head_commit": run_command(["git", "-C", str(repo_dir), "rev-parse", "HEAD"]).stdout.strip(),
            "head_commit_date": run_command(
                ["git", "-C", str(repo_dir), "show", "-s", "--format=%cI", "HEAD"]
            ).stdout.strip(),
            "top_level": list_top_level(repo_dir),
        }
    except Exception as exc:  # noqa: BLE001
        print(str(exc), file=sys.stderr)
        return 1

    print(json.dumps(metadata, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
