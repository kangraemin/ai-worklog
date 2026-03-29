"""TC-N1 ~ TC-N6: Notion 연동 검증"""
import pytest
import httpx
from pytest_httpx import HTTPXMock
from worklog_mcp.tools.notion import write_worklog_to_notion, _md_to_notion_blocks


def test_tc_n1_success(httpx_mock: HTTPXMock):
    """TC-N1: 정상 호출 → 'OK' 반환"""
    httpx_mock.add_response(status_code=200, json={"id": "page-123"})
    result = write_worklog_to_notion(
        title="테스트 작업",
        content="작업 내용",
        project="my-project",
        notion_token="secret_token",
        notion_db_id="db-id-123",
    )
    assert result == "OK"


def test_tc_n2_missing_token():
    """TC-N2: NOTION_TOKEN 없으면 에러"""
    import os
    os.environ.pop("NOTION_TOKEN", None)
    with pytest.raises(ValueError, match="NOTION_TOKEN"):
        write_worklog_to_notion(
            title="제목",
            content="내용",
            project="proj",
            notion_token="",
            notion_db_id="db-id",
        )


def test_tc_n3_missing_db_id():
    """TC-N3: NOTION_DB_ID 없으면 에러"""
    import os
    os.environ.pop("NOTION_DB_ID", None)
    with pytest.raises(ValueError, match="NOTION_DB_ID"):
        write_worklog_to_notion(
            title="제목",
            content="내용",
            project="proj",
            notion_token="secret",
            notion_db_id="",
        )


def test_tc_n4_markdown_conversion():
    """TC-N4: 마크다운 → Notion blocks 변환"""
    md = "# 제목\n## 소제목\n### 소소제목\n- 항목1\n일반 텍스트"
    blocks = _md_to_notion_blocks(md)
    types = [b["type"] for b in blocks]
    assert "heading_1" in types
    assert "heading_2" in types
    assert "heading_3" in types
    assert "bulleted_list_item" in types
    assert "paragraph" in types


def test_tc_n5_api_failure(httpx_mock: HTTPXMock):
    """TC-N5: API 실패(4xx) → 에러 반환"""
    httpx_mock.add_response(status_code=401, text="Unauthorized")
    with pytest.raises(RuntimeError, match="401"):
        write_worklog_to_notion(
            title="제목",
            content="내용",
            project="proj",
            notion_token="bad_token",
            notion_db_id="db-id",
        )


def test_tc_n6_timeout(httpx_mock: HTTPXMock):
    """TC-N6: 네트워크 타임아웃 → 에러 반환"""
    httpx_mock.add_exception(httpx.TimeoutException("timeout"))
    with pytest.raises(RuntimeError, match="타임아웃"):
        write_worklog_to_notion(
            title="제목",
            content="내용",
            project="proj",
            notion_token="secret",
            notion_db_id="db-id",
        )
