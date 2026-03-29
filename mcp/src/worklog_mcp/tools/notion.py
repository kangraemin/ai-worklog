import os
from datetime import datetime

import httpx


def _md_to_notion_blocks(content: str) -> list[dict]:
    """마크다운 텍스트를 Notion block 리스트로 변환."""
    blocks = []
    for line in content.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        text = stripped[:2000]
        if stripped.startswith("### "):
            blocks.append({"object": "block", "type": "heading_3",
                           "heading_3": {"rich_text": [{"text": {"content": text[4:]}}]}})
        elif stripped.startswith("## "):
            blocks.append({"object": "block", "type": "heading_2",
                           "heading_2": {"rich_text": [{"text": {"content": text[3:]}}]}})
        elif stripped.startswith("# "):
            blocks.append({"object": "block", "type": "heading_1",
                           "heading_1": {"rich_text": [{"text": {"content": text[2:]}}]}})
        elif stripped.startswith("- "):
            blocks.append({"object": "block", "type": "bulleted_list_item",
                           "bulleted_list_item": {"rich_text": [{"text": {"content": text[2:]}}]}})
        else:
            blocks.append({"object": "block", "type": "paragraph",
                           "paragraph": {"rich_text": [{"text": {"content": text}}]}})
    return blocks


def write_worklog_to_notion(
    title: str,
    content: str,
    project: str,
    notion_token: str = "",
    notion_db_id: str = "",
    cost: float = 0.0,
    duration: int = 0,
    model: str = "claude-sonnet-4-6",
    tokens: int = 0,
) -> str:
    """워크로그를 Notion DB에 기록한다.

    Args:
        title: 작업 제목 (Notion 페이지 제목)
        content: 워크로그 내용 (마크다운)
        project: 프로젝트 이름
        notion_token: Notion API 토큰. 미지정 시 NOTION_TOKEN 환경변수 사용
        notion_db_id: Notion DB ID. 미지정 시 NOTION_DB_ID 환경변수 사용
        cost: 이번 작업 비용 (USD)
        duration: 소요 시간 (분)
        model: 사용한 모델
        tokens: 사용한 토큰 수
    """
    token = notion_token or os.environ.get("NOTION_TOKEN", "")
    db_id = notion_db_id or os.environ.get("NOTION_DB_ID", "")

    if not token:
        raise ValueError("NOTION_TOKEN이 필요합니다. 파라미터 또는 환경변수로 설정하세요.")
    if not db_id:
        raise ValueError("NOTION_DB_ID가 필요합니다. 파라미터 또는 환경변수로 설정하세요.")

    now = datetime.now().isoformat()
    blocks = _md_to_notion_blocks(content)

    payload: dict = {
        "parent": {"database_id": db_id},
        "icon": {"type": "emoji", "emoji": "📖"},
        "properties": {
            "Title": {"title": [{"text": {"content": title}}]},
            "Project": {"select": {"name": project}},
            "Model": {"select": {"name": model}},
            "DateTime": {"date": {"start": now}},
        },
        "children": blocks,
    }

    if cost:
        payload["properties"]["Cost"] = {"number": round(cost, 3)}
    if duration:
        payload["properties"]["Duration"] = {"number": duration}
    if tokens:
        payload["properties"]["Tokens"] = {"number": tokens}

    try:
        response = httpx.post(
            "https://api.notion.com/v1/pages",
            headers={
                "Authorization": f"Bearer {token}",
                "Notion-Version": "2022-06-28",
                "Content-Type": "application/json",
            },
            json=payload,
            timeout=30.0,
        )
    except httpx.TimeoutException:
        raise RuntimeError("Notion API 타임아웃 (30초)")

    if response.status_code == 200:
        return "OK"

    raise RuntimeError(f"Notion API 실패: HTTP {response.status_code} — {response.text[:200]}")
