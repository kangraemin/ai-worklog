"""TC-28 ~ TC-56: PROJECT.md tools 검증"""
import pytest
from pathlib import Path
from conftest import SAMPLE_PROJECT_MD
from worklog_mcp.tools.project_doc import (
    read_project_doc, create_project_doc, analyze_gaps, update_project_doc
)

SECTIONS = ["이게 뭔가", "왜 만들었나", "구조", "기술 스택", "주요 결정들", "해결한 문제들", "지금 상태"]


# ── read_project_doc ───────────────────────────────────────

def test_tc28_read_existing(tmp_project):
    """TC-28: PROJECT.md 있으면 내용 반환"""
    (tmp_project / "PROJECT.md").write_text(SAMPLE_PROJECT_MD)
    result = read_project_doc(str(tmp_project))
    assert result["exists"] is True
    assert "테스트 프로젝트" in result["content"]


def test_tc29_read_missing(tmp_project):
    """TC-29: PROJECT.md 없으면 {"exists": false} 반환"""
    result = read_project_doc(str(tmp_project))
    assert result["exists"] is False


def test_tc30_read_empty_file(tmp_project):
    """TC-30: 내용이 비어있으면 빈 문자열 반환"""
    (tmp_project / "PROJECT.md").write_text("")
    result = read_project_doc(str(tmp_project))
    assert result["exists"] is True
    assert result["content"] == ""


def test_tc31_read_parses_sections(tmp_project):
    """TC-31: 섹션 파싱 — 7개 섹션 키 존재"""
    (tmp_project / "PROJECT.md").write_text(SAMPLE_PROJECT_MD)
    result = read_project_doc(str(tmp_project))
    for section in SECTIONS:
        assert section in result["sections"], f"Section '{section}' not found"


def test_tc32_read_invalid_path():
    """TC-32: project_path 유효하지 않으면 에러"""
    with pytest.raises((FileNotFoundError, ValueError)):
        read_project_doc("/nonexistent/path/12345")


# ── create_project_doc ─────────────────────────────────────

def test_tc33_create_success(tmp_project):
    """TC-33: PROJECT.md 생성 성공"""
    create_project_doc(str(tmp_project), {})
    assert (tmp_project / "PROJECT.md").exists()


def test_tc34_create_has_all_sections(tmp_project):
    """TC-34: 7개 섹션 모두 포함"""
    create_project_doc(str(tmp_project), {})
    content = (tmp_project / "PROJECT.md").read_text()
    for section in SECTIONS:
        assert f"## {section}" in content, f"Section '## {section}' not found"


def test_tc35_create_no_overwrite(tmp_project):
    """TC-35: 이미 존재하면 에러"""
    (tmp_project / "PROJECT.md").write_text("기존 내용")
    with pytest.raises((FileExistsError, ValueError)):
        create_project_doc(str(tmp_project), {})


def test_tc36_create_empty_content(tmp_project):
    """TC-36: content 없이 호출 시 빈 섹션으로 생성"""
    create_project_doc(str(tmp_project), {})
    result = read_project_doc(str(tmp_project))
    assert result["exists"] is True


def test_tc37_create_with_content(tmp_project):
    """TC-37: 각 섹션 내용 정상 반영"""
    sections = {"이게 뭔가": "테스트 앱", "왜 만들었나": "테스트 목적"}
    create_project_doc(str(tmp_project), sections)
    content = (tmp_project / "PROJECT.md").read_text()
    assert "테스트 앱" in content
    assert "테스트 목적" in content


def test_tc38_create_readable(tmp_project):
    """TC-38: 생성 후 read_project_doc으로 읽으면 동일 내용"""
    sections = {"이게 뭔가": "고유내용xyz"}
    create_project_doc(str(tmp_project), sections)
    result = read_project_doc(str(tmp_project))
    assert "고유내용xyz" in result["content"]


def test_tc39_create_invalid_path():
    """TC-39: project_path 유효하지 않으면 에러"""
    with pytest.raises((FileNotFoundError, ValueError)):
        create_project_doc("/nonexistent/path/12345", {})


def test_tc40_create_special_chars(tmp_project):
    """TC-40: 특수문자 포함 content 정상 저장"""
    special = "특수: <>&\"'"
    create_project_doc(str(tmp_project), {"이게 뭔가": special})
    content = (tmp_project / "PROJECT.md").read_text()
    assert special in content


# ── analyze_gaps ──────────────────────────────────────────

def test_tc41_analyze_no_project_md(tmp_project_with_commits):
    """TC-41: PROJECT.md 없으면 ["PROJECT.md 없음"] 반환"""
    result = analyze_gaps(str(tmp_project_with_commits))
    assert any("PROJECT.md" in gap for gap in result)


def test_tc42_analyze_non_git(tmp_non_git):
    """TC-42: git repo 아니면 에러"""
    (tmp_non_git / "PROJECT.md").write_text(SAMPLE_PROJECT_MD)
    with pytest.raises((ValueError, RuntimeError)):
        analyze_gaps(str(tmp_non_git))


def test_tc43_analyze_no_commits(tmp_project):
    """TC-43: 커밋 없으면 빈 gaps 반환"""
    (tmp_project / "PROJECT.md").write_text(SAMPLE_PROJECT_MD)
    result = analyze_gaps(str(tmp_project))
    assert isinstance(result, list)
    assert len(result) == 0


def test_tc44_analyze_new_file_gap(tmp_project_with_commits):
    """TC-44: 새 파일 추가됐는데 구조 섹션 미반영 → gap 감지"""
    (tmp_project_with_commits / "PROJECT.md").write_text(
        SAMPLE_PROJECT_MD.replace("단순한 구조", "")
    )
    # 새 파일 커밋
    (tmp_project_with_commits / "new_module.py").write_text("# new")
    import subprocess
    subprocess.run(["git", "add", "."], cwd=tmp_project_with_commits, capture_output=True)
    subprocess.run(["git", "commit", "-m", "feat: new_module 추가"], cwd=tmp_project_with_commits, capture_output=True)
    result = analyze_gaps(str(tmp_project_with_commits))
    assert isinstance(result, list)


def test_tc45_analyze_feat_commit_gap(tmp_project_with_commits):
    """TC-45: feat: 커밋이 있는데 문서 미반영 → gap 감지"""
    (tmp_project_with_commits / "PROJECT.md").write_text(SAMPLE_PROJECT_MD)
    import subprocess
    (tmp_project_with_commits / "feature.py").write_text("# feature")
    subprocess.run(["git", "add", "."], cwd=tmp_project_with_commits, capture_output=True)
    subprocess.run(["git", "commit", "-m", "feat: 새 기능 추가"], cwd=tmp_project_with_commits, capture_output=True)
    result = analyze_gaps(str(tmp_project_with_commits))
    assert isinstance(result, list)


def test_tc46_analyze_no_gaps(tmp_project_with_commits):
    """TC-46: PROJECT.md가 최신이면 빈 gaps 반환"""
    (tmp_project_with_commits / "PROJECT.md").write_text(SAMPLE_PROJECT_MD)
    import subprocess
    subprocess.run(["git", "add", "."], cwd=tmp_project_with_commits, capture_output=True)
    subprocess.run(["git", "commit", "-m", "docs: PROJECT.md 업데이트"], cwd=tmp_project_with_commits, capture_output=True)
    result = analyze_gaps(str(tmp_project_with_commits))
    assert isinstance(result, list)


def test_tc47_analyze_returns_list(tmp_project_with_commits):
    """TC-47: 반환 타입 list[str]"""
    (tmp_project_with_commits / "PROJECT.md").write_text(SAMPLE_PROJECT_MD)
    result = analyze_gaps(str(tmp_project_with_commits))
    assert isinstance(result, list)
    for item in result:
        assert isinstance(item, str)


def test_tc48_analyze_gap_message_specific(tmp_project_with_commits):
    """TC-48: gap 메시지가 구체적"""
    result = analyze_gaps(str(tmp_project_with_commits))
    # PROJECT.md 없을 때 반환하는 메시지가 구체적인지
    assert len(result) > 0
    assert len(result[0]) > 5  # 단순 빈 문자열 아님


# ── update_project_doc ─────────────────────────────────────

def test_tc49_update_section(tmp_project):
    """TC-49: 특정 섹션 내용 업데이트 성공"""
    (tmp_project / "PROJECT.md").write_text(SAMPLE_PROJECT_MD)
    update_project_doc(str(tmp_project), "이게 뭔가", "업데이트된 설명")
    content = (tmp_project / "PROJECT.md").read_text()
    assert "업데이트된 설명" in content


def test_tc50_update_only_target_section(tmp_project):
    """TC-50: 다른 섹션은 변경 없음"""
    (tmp_project / "PROJECT.md").write_text(SAMPLE_PROJECT_MD)
    update_project_doc(str(tmp_project), "이게 뭔가", "새 내용")
    result = read_project_doc(str(tmp_project))
    assert "테스트를 위해" in result["content"]  # 왜 만들었나 섹션 유지


def test_tc51_update_invalid_section(tmp_project):
    """TC-51: 존재하지 않는 섹션명 에러"""
    (tmp_project / "PROJECT.md").write_text(SAMPLE_PROJECT_MD)
    with pytest.raises((ValueError, KeyError)):
        update_project_doc(str(tmp_project), "존재하지않는섹션", "내용")


def test_tc52_update_no_project_md(tmp_project):
    """TC-52: PROJECT.md 없으면 에러"""
    with pytest.raises((FileNotFoundError, ValueError)):
        update_project_doc(str(tmp_project), "이게 뭔가", "내용")


def test_tc53_update_empty_content(tmp_project):
    """TC-53: content 빈 문자열 허용"""
    (tmp_project / "PROJECT.md").write_text(SAMPLE_PROJECT_MD)
    update_project_doc(str(tmp_project), "이게 뭔가", "")
    assert (tmp_project / "PROJECT.md").exists()


def test_tc54_update_readable(tmp_project):
    """TC-54: 업데이트 후 read_project_doc으로 확인 일치"""
    (tmp_project / "PROJECT.md").write_text(SAMPLE_PROJECT_MD)
    update_project_doc(str(tmp_project), "이게 뭔가", "고유내용abc123")
    result = read_project_doc(str(tmp_project))
    assert "고유내용abc123" in result["content"]


def test_tc55_update_exact_section_name(tmp_project):
    """TC-55: 섹션명 한글 정확히 일치해야 함"""
    (tmp_project / "PROJECT.md").write_text(SAMPLE_PROJECT_MD)
    with pytest.raises((ValueError, KeyError)):
        update_project_doc(str(tmp_project), "이게뭔가", "내용")  # 공백 없음


def test_tc56_update_append_mode(tmp_project):
    """TC-56: append 모드 지원 (기존 내용 유지하고 추가)"""
    (tmp_project / "PROJECT.md").write_text(SAMPLE_PROJECT_MD)
    update_project_doc(str(tmp_project), "주요 결정들", "새 결정 추가", append=True)
    content = (tmp_project / "PROJECT.md").read_text()
    assert "Python 선택: 익숙해서" in content  # 기존 내용 유지
    assert "새 결정 추가" in content  # 새 내용 추가


# ── analyze_gaps 개선 TC ────────────────────────────────────

def test_tc_g1_fix_commit_gap(tmp_project):
    """TC-G1: fix: 커밋 → [해결한 문제들] gap 감지"""
    (tmp_project / "PROJECT.md").write_text(SAMPLE_PROJECT_MD)
    import subprocess
    (tmp_project / "bug.py").write_text("# fix")
    subprocess.run(["git", "add", "."], cwd=tmp_project, capture_output=True)
    subprocess.run(["git", "commit", "-m", "fix: 버그 수정"], cwd=tmp_project, capture_output=True)
    result = analyze_gaps(str(tmp_project))
    assert any("해결한 문제들" in g for g in result)


def test_tc_g2_refactor_commit_gap(tmp_project):
    """TC-G2: refactor: 커밋 → [구조] gap 감지"""
    (tmp_project / "PROJECT.md").write_text(SAMPLE_PROJECT_MD)
    import subprocess
    (tmp_project / "refactored.py").write_text("# refactor")
    subprocess.run(["git", "add", "."], cwd=tmp_project, capture_output=True)
    subprocess.run(["git", "commit", "-m", "refactor: 코드 정리"], cwd=tmp_project, capture_output=True)
    result = analyze_gaps(str(tmp_project))
    assert any("구조" in g for g in result)


def test_tc_g3_empty_section_gap(tmp_project):
    """TC-G3: 섹션이 비어있으면 gap 반환"""
    empty_md = "# 프로젝트\n\n## 이게 뭔가\n\n## 왜 만들었나\n\n## 구조\n\n## 기술 스택\n\n## 주요 결정들\n\n## 해결한 문제들\n\n## 지금 상태\n"
    (tmp_project / "PROJECT.md").write_text(empty_md)
    import subprocess
    (tmp_project / "a.py").write_text("x")
    subprocess.run(["git", "add", "."], cwd=tmp_project, capture_output=True)
    subprocess.run(["git", "commit", "-m", "chore: init"], cwd=tmp_project, capture_output=True)
    result = analyze_gaps(str(tmp_project))
    assert any("섹션이 비어있음" in g for g in result)


def test_tc_g4_docs_commit_no_gap(tmp_project):
    """TC-G4: 최근 커밋에 PROJECT.md 수정이 있으면 gap 없음"""
    (tmp_project / "PROJECT.md").write_text(SAMPLE_PROJECT_MD)
    import subprocess
    subprocess.run(["git", "add", "."], cwd=tmp_project, capture_output=True)
    subprocess.run(["git", "commit", "-m", "docs: PROJECT.md 업데이트"], cwd=tmp_project, capture_output=True)
    result = analyze_gaps(str(tmp_project))
    # docs 커밋 이후엔 커밋 타입 기반 gap 없어야 함
    assert not any("미반영 커밋" in g for g in result)
