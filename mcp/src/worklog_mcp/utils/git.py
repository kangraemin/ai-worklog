import subprocess
from pathlib import Path


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
    """최근 n개 커밋에서 변경된 파일 목록 반환."""
    path = Path(project_path).resolve()
    if not path.exists():
        raise FileNotFoundError(f"Path not found: {project_path}")
    if not _is_git_repo(str(path)):
        raise ValueError(f"Not a git repository: {project_path}")

    result = subprocess.run(
        ["git", "diff", f"HEAD~{n}..HEAD", "--name-only"],
        cwd=str(path),
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        # 커밋이 n개보다 적으면 HEAD 기준으로
        result = subprocess.run(
            ["git", "diff", "--name-only"],
            cwd=str(path),
            capture_output=True,
            text=True,
        )

    lines = result.stdout.strip().splitlines()
    return [line for line in lines if line]
