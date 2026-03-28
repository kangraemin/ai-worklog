import re
from pathlib import Path
from worklog_mcp.utils.git import get_recent_commits, get_recent_changed_files

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


def analyze_gaps(project_path: str) -> list[str]:
    """최근 git 커밋과 PROJECT.md를 비교해 반영 안 된 내용(gap)을 반환한다.

    Args:
        project_path: 프로젝트 루트 디렉토리 경로
    """
    path = Path(project_path).resolve()

    # git repo 확인 (에러 전파)
    commits = get_recent_commits(str(path), n=20)

    doc_path = path / "PROJECT.md"
    if not doc_path.exists():
        return ["PROJECT.md 없음 — create_project_doc으로 먼저 생성하세요"]

    if not commits:
        return []

    content = doc_path.read_text(encoding="utf-8")
    gaps: list[str] = []

    # feat: 커밋이 있는데 최근 PROJECT.md 수정이 없으면 gap
    feat_commits = [c for c in commits if "feat:" in c.lower()]
    doc_commits = [c for c in commits if "docs:" in c.lower() or "PROJECT.md" in c]

    if feat_commits and not doc_commits:
        gap_msgs = [c.split(" ", 1)[1] if " " in c else c for c in feat_commits[:3]]
        gaps.append(f"[주요 결정들 / 지금 상태] feat 커밋 미반영: {', '.join(gap_msgs)}")

    # 최근 변경 파일 중 구조에 없는 것
    changed = get_recent_changed_files(str(path), n=5)
    new_files = [f for f in changed if f.endswith(".py") or f.endswith(".ts")]
    if new_files:
        sections = _parse_sections(content)
        structure = sections.get("구조", "")
        unmentioned = [f for f in new_files if Path(f).name not in structure]
        if unmentioned:
            gaps.append(f"[구조] 신규 파일 미반영: {', '.join(unmentioned[:5])}")

    return gaps


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
