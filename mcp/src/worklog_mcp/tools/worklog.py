from datetime import date, datetime
from pathlib import Path


def write_worklog(project_path: str, content: str) -> str:
    """워크로그 항목을 .worklogs/YYYY-MM-DD.md 파일에 기록한다.

    Args:
        project_path: 프로젝트 루트 디렉토리 경로
        content: 기록할 내용
    """
    if not content:
        raise ValueError("content cannot be empty")

    path = Path(project_path).resolve()
    if not path.exists():
        raise FileNotFoundError(f"Path not found: {project_path}")

    worklogs_dir = path / ".worklogs"
    worklogs_dir.mkdir(exist_ok=True)

    today = date.today().strftime("%Y-%m-%d")
    log_file = worklogs_dir / f"{today}.md"

    timestamp = datetime.now().strftime("%H:%M")
    entry = f"\n## {timestamp}\n\n{content}\n"

    with open(log_file, "a", encoding="utf-8") as f:
        f.write(entry)

    return f"Written to {log_file}"


def read_worklog(project_path: str, date: str | None = None) -> str:
    """워크로그 파일을 읽어 반환한다.

    Args:
        project_path: 프로젝트 루트 디렉토리 경로
        date: 읽을 날짜 (YYYY-MM-DD). 미지정 시 오늘
    """
    from datetime import date as date_type

    if date is not None:
        try:
            datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            raise ValueError(f"Invalid date format: '{date}'. Use YYYY-MM-DD")
        target_date = date
    else:
        target_date = date_type.today().strftime("%Y-%m-%d")

    path = Path(project_path).resolve()
    log_file = path / ".worklogs" / f"{target_date}.md"

    if not log_file.exists():
        return f"No worklog found for {target_date}"

    return log_file.read_text(encoding="utf-8")
