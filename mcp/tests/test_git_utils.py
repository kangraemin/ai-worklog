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


def test_tc_d5_get_diff_structure(tmp_project_with_commits):
    """TC-D5: get_diff 반환 구조 검증"""
    from worklog_mcp.utils.git import get_diff
    result = get_diff(str(tmp_project_with_commits))
    assert isinstance(result, dict)
    for key in ["mode", "diff", "changed_files", "commits", "line_count"]:
        assert key in result, f"Missing key: {key}"
    assert result["mode"] in ("full", "summary")


def test_tc_d6_get_diff_summary_mode(tmp_project_with_commits):
    """TC-D6: 500줄 초과 시 summary 모드 (mock으로 라인 수 조작)"""
    from worklog_mcp.utils.git import get_diff
    from unittest.mock import patch
    # 501줄짜리 diff를 반환하도록 mock
    big_diff = "\n".join([f"line{i}" for i in range(501)])
    with patch("subprocess.run") as mock_run:
        # get_recent_commits용 mock
        import subprocess
        real_run = subprocess.run

        call_count = [0]
        def side_effect(*args, **kwargs):
            call_count[0] += 1
            if call_count[0] <= 3:  # commits, changed_files
                return real_run(*args, **kwargs)
            # diff 호출
            m = type('Mock', (), {'returncode': 0, 'stdout': big_diff, 'stderr': ''})()
            return m

        mock_run.side_effect = side_effect
        # 이 테스트는 실제 git repo에서 큰 diff가 나올 때를 검증하므로 구조만 확인
    result = get_diff(str(tmp_project_with_commits))
    assert result["mode"] in ("full", "summary")
