import re
from pathlib import Path
from worklog_mcp.utils.git import get_recent_commits, get_recent_changed_files, get_diff, get_commits_since_file_update

SECTIONS = ["이게 뭔가", "왜 만들었나", "구조", "기술 스택", "주요 결정들", "해결한 문제들", "지금 상태"]


def _parse_sections(content: str) -> dict[str, str]:
    """PROJECT.md 내용을 섹션별로 파싱."""
    sections: dict[str, str] = {s: "" for s in SECTIONS}
    current = None
    lines: list[str] = []

    for line in content.splitlines():
        m = re.match(r"^## (.+)$", line)
        if m:
            if current is not None:
                sections[current] = "\n".join(lines).strip()
            candidate = m.group(1).strip()
            current = candidate if candidate in SECTIONS else None
            lines = []
        elif current is not None:
            lines.append(line)

    if current is not None:
        sections[current] = "\n".join(lines).strip()

    return sections


def read_project_doc(project_path: str) -> dict:
    """PROJECT.md를 읽어 반환한다.

    Args:
        project_path: 프로젝트 루트 디렉토리 경로
    """
    path = Path(project_path).resolve()
    if not path.exists():
        raise FileNotFoundError(f"Path not found: {project_path}")

    doc_path = path / "PROJECT.md"
    if not doc_path.exists():
        return {"exists": False, "content": "", "sections": {}}

    content = doc_path.read_text(encoding="utf-8")
    return {
        "exists": True,
        "content": content,
        "sections": _parse_sections(content),
    }


def create_project_doc(project_path: str, sections: dict[str, str]) -> str:
    """PROJECT.md를 생성한다. 이미 존재하면 에러.

    Args:
        project_path: 프로젝트 루트 디렉토리 경로
        sections: 섹션별 초기 내용 (없으면 빈 섹션)
    """
    path = Path(project_path).resolve()
    if not path.exists():
        raise FileNotFoundError(f"Path not found: {project_path}")

    doc_path = path / "PROJECT.md"
    if doc_path.exists():
        raise FileExistsError(f"PROJECT.md already exists at {doc_path}")

    project_name = path.name
    lines = [f"# {project_name}\n"]
    for section in SECTIONS:
        lines.append(f"\n## {section}\n")
        content = sections.get(section, "")
        if content:
            lines.append(f"{content}\n")

    doc_path.write_text("".join(lines), encoding="utf-8")
    return f"Created {doc_path}"


def analyze_gaps(project_path: str, n: int = 10) -> dict:
    """PROJECT.md와 최근 변경사항을 반환한다. Claude가 gap을 판단한다.

    Args:
        project_path: 프로젝트 루트 디렉토리 경로
        n: 분석할 최근 커밋 수 (기본 10)

    Returns:
        {
            "project_doc": str | None,       # 현재 PROJECT.md 내용 (없으면 None)
            "sections": dict[str, str],      # 섹션별 파싱 결과 (없으면 {})
            "diff_mode": "full" | "summary",
            "diff": str,
            "changed_files": list[str],
            "commits": list[str],
            "line_count": int,
            "commits_since_doc_update": int, # PROJECT.md 마지막 수정 이후 커밋 수
        }
    """
    path = Path(project_path).resolve()

    diff_info = get_diff(str(path), n=n)

    doc_path = path / "PROJECT.md"
    if doc_path.exists():
        project_doc = doc_path.read_text(encoding="utf-8")
        sections = _parse_sections(project_doc)
    else:
        project_doc = None
        sections = {}

    commits_since = get_commits_since_file_update(str(path), "PROJECT.md")

    return {
        "project_doc": project_doc,
        "sections": sections,
        "diff_mode": diff_info["mode"],
        "diff": diff_info["diff"],
        "changed_files": diff_info["changed_files"],
        "commits": diff_info["commits"],
        "line_count": diff_info["line_count"],
        "commits_since_doc_update": commits_since,
    }


def update_project_doc(
    project_path: str, section: str, content: str, append: bool = False
) -> str:
    """PROJECT.md의 특정 섹션을 업데이트한다.

    Args:
        project_path: 프로젝트 루트 디렉토리 경로
        section: 업데이트할 섹션명 (예: "이게 뭔가")
        content: 새 내용
        append: True면 기존 내용에 추가, False면 교체
    """
    path = Path(project_path).resolve()
    doc_path = path / "PROJECT.md"

    if not doc_path.exists():
        raise FileNotFoundError(f"PROJECT.md not found at {doc_path}")

    if section not in SECTIONS:
        raise ValueError(f"Invalid section: '{section}'. Must be one of: {SECTIONS}")

    full_content = doc_path.read_text(encoding="utf-8")
    parsed = _parse_sections(full_content)

    if append and parsed.get(section):
        parsed[section] = parsed[section] + "\n" + content
    else:
        parsed[section] = content

    # 재조립: 헤더(# 프로젝트명) 유지
    header_match = re.match(r"^(#[^\n]*\n)", full_content)
    header = header_match.group(1) if header_match else ""

    lines = [header] if header else []
    for s in SECTIONS:
        lines.append(f"\n## {s}\n")
        if parsed.get(s):
            lines.append(f"{parsed[s]}\n")

    doc_path.write_text("".join(lines), encoding="utf-8")
    return f"Updated section '{section}' in {doc_path}"
