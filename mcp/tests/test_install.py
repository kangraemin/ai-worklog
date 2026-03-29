"""TC-01 ~ TC-05: 설치/환경 검증"""
import sys
import importlib


def test_tc01_mcp_importable():
    """TC-01: mcp 패키지 import 가능"""
    import mcp
    assert mcp is not None


def test_tc02_fastmcp_importable():
    """TC-02: mcp.server.fastmcp import 가능"""
    from mcp.server.fastmcp import FastMCP
    assert FastMCP is not None


def test_tc03_python_version():
    """TC-03: Python >= 3.10"""
    assert sys.version_info >= (3, 10), f"Python 3.10+ required, got {sys.version}"


def test_tc04_worklog_mcp_importable():
    """TC-04: worklog_mcp 패키지 import 가능 (uv sync 완료 확인)"""
    import worklog_mcp
    assert worklog_mcp is not None


def test_tc05_entrypoint_exists():
    """TC-05: worklog-mcp CLI 엔트리포인트 존재"""
    import shutil
    # uv run 환경에서는 worklog-mcp 스크립트가 .venv/bin에 설치됨
    from worklog_mcp.server import main
    assert callable(main)
