"""TC-11 ~ TC-27: worklog tools 검증"""
import pytest
from datetime import date, datetime
from pathlib import Path
from worklog_mcp.tools.worklog import write_worklog, read_worklog


# ── write_worklog ──────────────────────────────────────────

def test_tc11_write_creates_file(tmp_project):
    """TC-11: 정상 기록 → .worklogs/YYYY-MM-DD.md 생성"""
    write_worklog(str(tmp_project), "작업 내용")
    today = date.today().strftime("%Y-%m-%d")
    assert (tmp_project / ".worklogs" / f"{today}.md").exists()


def test_tc12_write_appends(tmp_project):
    """TC-12: 같은 날 두 번 호출 → append"""
    write_worklog(str(tmp_project), "첫 번째")
    write_worklog(str(tmp_project), "두 번째")
    today = date.today().strftime("%Y-%m-%d")
    content = (tmp_project / ".worklogs" / f"{today}.md").read_text()
    assert "첫 번째" in content
    assert "두 번째" in content


def test_tc13_write_creates_dir(tmp_project):
    """TC-13: .worklogs/ 디렉토리 없으면 자동 생성"""
    assert not (tmp_project / ".worklogs").exists()
    write_worklog(str(tmp_project), "내용")
    assert (tmp_project / ".worklogs").is_dir()


def test_tc14_write_invalid_path():
    """TC-14: project_path 존재하지 않으면 에러"""
    with pytest.raises((FileNotFoundError, ValueError)):
        write_worklog("/nonexistent/path/12345", "내용")


def test_tc15_write_empty_content(tmp_project):
    """TC-15: content 빈 문자열이면 에러"""
    with pytest.raises(ValueError):
        write_worklog(str(tmp_project), "")


def test_tc16_write_has_timestamp(tmp_project):
    """TC-16: 파일에 타임스탬프 헤더 포함 (## HH:MM)"""
    write_worklog(str(tmp_project), "내용")
    today = date.today().strftime("%Y-%m-%d")
    content = (tmp_project / ".worklogs" / f"{today}.md").read_text()
    import re
    assert re.search(r"## \d{2}:\d{2}", content), f"No timestamp found in: {content}"


def test_tc17_write_multiline(tmp_project):
    """TC-17: 멀티라인 content 정상 저장"""
    multiline = "첫 줄\n둘째 줄\n셋째 줄"
    write_worklog(str(tmp_project), multiline)
    today = date.today().strftime("%Y-%m-%d")
    content = (tmp_project / ".worklogs" / f"{today}.md").read_text()
    assert "첫 줄" in content
    assert "셋째 줄" in content


def test_tc18_write_special_chars(tmp_project):
    """TC-18: 특수문자 포함 content 정상 저장"""
    special = "특수문자: <>&\"'`!@#$%^*()"
    write_worklog(str(tmp_project), special)
    today = date.today().strftime("%Y-%m-%d")
    content = (tmp_project / ".worklogs" / f"{today}.md").read_text()
    assert special in content


def test_tc19_write_relative_path(tmp_project, monkeypatch):
    """TC-19: project_path가 상대경로여도 동작"""
    monkeypatch.chdir(tmp_project.parent)
    write_worklog(tmp_project.name, "내용")
    today = date.today().strftime("%Y-%m-%d")
    assert (tmp_project / ".worklogs" / f"{today}.md").exists()


def test_tc20_write_absolute_path(tmp_project):
    """TC-20: project_path가 절대경로여도 동작"""
    write_worklog(str(tmp_project.resolve()), "내용")
    today = date.today().strftime("%Y-%m-%d")
    assert (tmp_project / ".worklogs" / f"{today}.md").exists()


# ── read_worklog ───────────────────────────────────────────

def test_tc21_read_today(tmp_project):
    """TC-21: 오늘 날짜 파일 읽기 성공"""
    write_worklog(str(tmp_project), "오늘 작업")
    result = read_worklog(str(tmp_project))
    assert "오늘 작업" in result


def test_tc22_read_specific_date(tmp_project):
    """TC-22: 특정 날짜 지정해서 읽기 성공"""
    today = date.today().strftime("%Y-%m-%d")
    write_worklog(str(tmp_project), "특정 날짜 내용")
    result = read_worklog(str(tmp_project), date=today)
    assert "특정 날짜 내용" in result


def test_tc23_read_missing_file(tmp_project):
    """TC-23: 파일 없으면 'No worklog found' 반환"""
    result = read_worklog(str(tmp_project), date="2000-01-01")
    assert "No worklog found" in result


def test_tc24_read_default_today(tmp_project):
    """TC-24: date 미지정 시 오늘 날짜 기본값"""
    write_worklog(str(tmp_project), "오늘")
    result = read_worklog(str(tmp_project))
    assert "오늘" in result


def test_tc25_read_date_format_valid(tmp_project):
    """TC-25: date 포맷 YYYY-MM-DD 검증"""
    today = date.today().strftime("%Y-%m-%d")
    write_worklog(str(tmp_project), "내용")
    result = read_worklog(str(tmp_project), date=today)
    assert isinstance(result, str)


def test_tc26_read_invalid_date_format(tmp_project):
    """TC-26: 잘못된 date 포맷 에러"""
    with pytest.raises(ValueError):
        read_worklog(str(tmp_project), date="2026/03/28")


def test_tc27_read_matches_write(tmp_project):
    """TC-27: 읽은 내용이 write한 내용과 일치"""
    content = "고유한 내용 xyz123"
    write_worklog(str(tmp_project), content)
    result = read_worklog(str(tmp_project))
    assert content in result
