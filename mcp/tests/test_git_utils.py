"""TC-57 ~ TC-61: git utils 검증"""
import pytest
from worklog_mcp.utils.git import get_recent_commits, get_recent_changed_files


def test_tc57_get_recent_commits(tmp_project_with_commits):
    """TC-57: get_recent_commits — git log 반환"""
    result = get_recent_commits(str(tmp_project_with_commits))
    assert isinstance(result, list)
    assert len(result) > 0
    assert any("초기 커밋" in c for c in result)


def test_tc58_get_recent_commits_n(tmp_project_with_commits):
    """TC-58: get_recent_commits — n 파라미터 동작"""
    result = get_recent_commits(str(tmp_project_with_commits), n=1)
    assert len(result) <= 1


def test_tc59_get_recent_changed_files(tmp_project_with_commits):
    """TC-59: get_recent_changed_files — 변경 파일 목록 반환"""
    result = get_recent_changed_files(str(tmp_project_with_commits))
    assert isinstance(result, list)


def test_tc60_non_git_repo(tmp_non_git):
    """TC-60: git repo 아닌 경로 에러 처리"""
    with pytest.raises((ValueError, RuntimeError)):
        get_recent_commits(str(tmp_non_git))


def test_tc61_empty_commit_history(tmp_project):
    """TC-61: 빈 커밋 히스토리 처리"""
    result = get_recent_commits(str(tmp_project))
    assert isinstance(result, list)
    assert len(result) == 0
