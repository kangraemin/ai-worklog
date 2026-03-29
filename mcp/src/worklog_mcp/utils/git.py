import subprocess
from pathlib import Path

NOISE_EXCLUDES = [
    ":(exclude).worklogs",
    ":(exclude).ai-bouncer-tasks",
    ":(exclude)*.lock",
    ":(exclude).claude",
    ":(exclude)uv.lock",
]


def _is_git_repo(project_path: str) -> bool:
    result = subprocess.run(
        ["git", "rev-parse", "--is-inside-work-tree"],
        cwd=project_path,
        capture_output=True,
        text=True,
    )
    return result.returncode == 0


def get_recent_commits(project_path: str, n: int = 20) -> list[str]:
    """최근 n개 커밋 메시지 반환. git repo 아니면 ValueError."""
    path = Path(project_path).resolve()
    if not path.exists():
        raise FileNotFoundError(f"Path not found: {project_path}")
    if not _is_git_repo(str(path)):
        raise ValueError(f"Not a git repository: {project_path}")

    result = subprocess.run(
        ["git", "log", f"-{n}", "--oneline"],
        cwd=str(path),
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return []

    lines = result.stdout.strip().splitlines()
    return [line for line in lines if line]


def get_recent_changed_files(project_path: str, n: int = 5) -> list[str]:
    """최근 n개 커밋에서 변경된 파일 목록 반환 (노이즈 제외)."""
    path = Path(project_path).resolve()
    if not path.exists():
        raise FileNotFoundError(f"Path not found: {project_path}")
    if not _is_git_repo(str(path)):
        raise ValueError(f"Not a git repository: {project_path}")

    result = subprocess.run(
        ["git", "diff", f"HEAD~{n}..HEAD", "--name-only", "--"] + NOISE_EXCLUDES,
        cwd=str(path),
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        result = subprocess.run(
            ["git", "diff", "--name-only", "--"] + NOISE_EXCLUDES,
            cwd=str(path),
            capture_output=True,
            text=True,
        )

    lines = result.stdout.strip().splitlines()
    return [line for line in lines if line]


def get_diff(project_path: str, n: int = 10) -> dict:
    """최근 n개 커밋의 diff 반환 (노이즈 제외). 500줄 초과 시 파일 목록 + 커밋 메시지만.

    Returns:
        {
            "mode": "full" | "summary",
            "diff": str,
            "changed_files": list[str],
            "commits": list[str],
            "line_count": int,
        }
    """
    path = Path(project_path).resolve()
    if not path.exists():
        raise FileNotFoundError(f"Path not found: {project_path}")
    if not _is_git_repo(str(path)):
        raise ValueError(f"Not a git repository: {project_path}")

    commits = get_recent_commits(str(path), n=n)
    changed_files = get_recent_changed_files(str(path), n=n)

    if not commits:
        return {"mode": "full", "diff": "", "changed_files": [], "commits": [], "line_count": 0}

    result = subprocess.run(
        ["git", "diff", f"HEAD~{min(n, len(commits))}..HEAD", "--"] + NOISE_EXCLUDES,
        cwd=str(path),
        capture_output=True,
        text=True,
    )
    diff_text = result.stdout if result.returncode == 0 else ""
    line_count = len(diff_text.splitlines())

    if line_count <= 500:
        return {
            "mode": "full",
            "diff": diff_text,
            "changed_files": changed_files,
            "commits": commits,
            "line_count": line_count,
        }
    else:
        return {
            "mode": "summary",
            "diff": "",
            "changed_files": changed_files,
            "commits": commits,
            "line_count": line_count,
        }


def get_commits_since_file_update(project_path: str, filepath: str = "PROJECT.md") -> int:
    """파일 마지막 수정 이후 전체 커밋 수 반환.

    파일 수정 기록 없으면 전체 커밋 수 반환.
    """
    path = Path(project_path).resolve()
    if not path.exists():
        raise FileNotFoundError(f"Path not found: {project_path}")
    if not _is_git_repo(str(path)):
        raise ValueError(f"Not a git repository: {project_path}")

    # 파일 마지막 수정 커밋 hash
    result = subprocess.run(
        ["git", "log", "-1", "--format=%H", "--", filepath],
        cwd=str(path),
        capture_output=True,
        text=True,
    )
    last_hash = result.stdout.strip()

    if not last_hash:
        # 파일 수정 기록 없음 → 전체 커밋 수
        all_commits = get_recent_commits(str(path), n=1000)
        return len(all_commits)

    # 그 이후 커밋 수
    result = subprocess.run(
        ["git", "log", "--oneline", f"{last_hash}..HEAD"],
        cwd=str(path),
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return 0

    lines = [l for l in result.stdout.strip().splitlines() if l]
    return len(lines)
