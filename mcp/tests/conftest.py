import pytest
import tempfile
import os
import subprocess
from pathlib import Path


@pytest.fixture
def tmp_project(tmp_path):
    """임시 git 프로젝트 디렉토리."""
    subprocess.run(["git", "init"], cwd=tmp_path, capture_output=True)
    subprocess.run(["git", "config", "user.email", "test@test.com"], cwd=tmp_path, capture_output=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=tmp_path, capture_output=True)
    return tmp_path


@pytest.fixture
def tmp_project_with_commits(tmp_project):
    """커밋이 있는 임시 git 프로젝트."""
    f = tmp_project / "main.py"
    f.write_text("print('hello')")
    subprocess.run(["git", "add", "."], cwd=tmp_project, capture_output=True)
    subprocess.run(["git", "commit", "-m", "feat: 초기 커밋"], cwd=tmp_project, capture_output=True)
    return tmp_project


@pytest.fixture
def tmp_non_git(tmp_path):
    """git repo가 아닌 디렉토리."""
    return tmp_path


SAMPLE_PROJECT_MD = """# 테스트 프로젝트

## 이게 뭔가
테스트용 프로젝트

## 왜 만들었나
테스트를 위해

## 구조
단순한 구조

## 기술 스택
Python

## 주요 결정들
- Python 선택: 익숙해서

## 해결한 문제들
- 없음

## 지금 상태
초기 상태
"""
