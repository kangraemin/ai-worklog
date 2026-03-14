#!/usr/bin/env python3
"""
WORKLOG_TIMING x WORKLOG_DEST 크로스 조합 e2e 테스트

격리된 git repo에서 post-commit.sh를 실행하여
TIMING(manual/stop) x DEST(git/notion/notion-only) 조합별 동작을 검증한다.

Run: python3 -m pytest tests/test_env_combinations_e2e.py -v
"""

import glob
import json
import os
import shutil
import subprocess
import tempfile
import unittest

PACKAGE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


class _EnvComboBase(unittest.TestCase):
    """격리된 git repo + remote 환경 픽스처 (TIMING x DEST 조합 테스트용)"""

    def setUp(self):
        # jq 검사
        if not shutil.which("jq"):
            self.skipTest("jq not found")

        self.tmp = tempfile.mkdtemp(prefix="ai_wl_envcombo_")

        # 글로벌 git hooks 격리용 env
        git_env = {
            "HOME": self.tmp,
            "PATH": os.environ.get("PATH", "/usr/bin:/bin"),
            "TERM": "dumb",
            "GIT_CONFIG_NOSYSTEM": "1",
        }

        # bare remote repo
        self.remote = os.path.join(self.tmp, "remote.git")
        subprocess.run(["git", "init", "--bare", self.remote], capture_output=True, check=True, env=git_env)

        # local repo (clone)
        self.repo = os.path.join(self.tmp, "repo")
        subprocess.run(["git", "clone", self.remote, self.repo], capture_output=True, check=True, env=git_env)
        subprocess.run(["git", "-C", self.repo, "config", "user.email", "test@test.com"], capture_output=True, env=git_env)
        subprocess.run(["git", "-C", self.repo, "config", "user.name", "Test"], capture_output=True, env=git_env)

        # initial commit
        readme = os.path.join(self.repo, "README.md")
        with open(readme, "w") as f:
            f.write("# test\n")
        subprocess.run(["git", "-C", self.repo, "add", "README.md"], capture_output=True, env=git_env)
        subprocess.run(["git", "-C", self.repo, "commit", "-m", "init"], capture_output=True, env=git_env)
        subprocess.run(["git", "-C", self.repo, "push"], capture_output=True, env=git_env)

        # worklog-for-claude 설치 디렉토리
        self.ai_dir = os.path.join(self.tmp, "worklog-for-claude")
        os.makedirs(os.path.join(self.ai_dir, "scripts"))
        os.makedirs(os.path.join(self.ai_dir, "hooks"))

        # worklog-write.sh 복사
        shutil.copy(
            os.path.join(PACKAGE_DIR, "scripts", "worklog-write.sh"),
            os.path.join(self.ai_dir, "scripts", "worklog-write.sh"),
        )
        os.chmod(os.path.join(self.ai_dir, "scripts", "worklog-write.sh"), 0o755)

        # post-commit.sh 복사
        shutil.copy(
            os.path.join(PACKAGE_DIR, "hooks", "post-commit.sh"),
            os.path.join(self.ai_dir, "hooks", "post-commit.sh"),
        )
        os.chmod(os.path.join(self.ai_dir, "hooks", "post-commit.sh"), 0o755)

        # token-cost.py, duration.py 스텁
        for script in ["token-cost.py", "duration.py"]:
            with open(os.path.join(self.ai_dir, "scripts", script), "w") as f:
                f.write("print('0,0.000')\n")

        # notion-worklog.sh stub
        self.notion_log = os.path.join(self.tmp, "notion-stub.log")
        notion_stub = os.path.join(self.ai_dir, "scripts", "notion-worklog.sh")
        with open(notion_stub, "w") as f:
            f.write(f"""#!/bin/bash
LOG_FILE="${{NOTION_STUB_LOG}}"
echo "TITLE=$1" >> "$LOG_FILE"
echo "DATE=$2" >> "$LOG_FILE"
echo "PROJECT=$3" >> "$LOG_FILE"
echo "---" >> "$LOG_FILE"
exit 0
""")
        os.chmod(notion_stub, 0o755)

        # settings.json (기본값)
        settings = {
            "env": {
                "WORKLOG_TIMING": "stop",
                "WORKLOG_DEST": "git",
                "WORKLOG_GIT_TRACK": "true",
                "WORKLOG_LANG": "ko",
                "AI_WORKLOG_DIR": self.ai_dir,
            }
        }
        with open(os.path.join(self.ai_dir, "settings.json"), "w") as f:
            json.dump(settings, f, indent=2)

        # 스냅샷 디렉토리
        snapshot_dir = os.path.join(self.tmp, ".claude", "worklogs")
        os.makedirs(snapshot_dir, exist_ok=True)

        # claude 스텁 (exit 1 → fallback 모드)
        self._bin = os.path.join(self.tmp, "bin")
        os.makedirs(self._bin, exist_ok=True)
        with open(os.path.join(self._bin, "claude"), "w") as f:
            f.write("#!/bin/bash\nexit 1\n")
        os.chmod(os.path.join(self._bin, "claude"), 0o755)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _env(self, **extra):
        """테스트용 환경변수 (CLAUDECODE 미설정 → 터미널 직접 커밋 모드)"""
        python3_dir = os.path.dirname(shutil.which("python3") or "/usr/bin/python3")
        safe_path = f'{self._bin}:/usr/bin:/bin:/usr/sbin:/sbin:/usr/local/bin:{python3_dir}'
        env = {
            "HOME": self.tmp,
            "AI_WORKLOG_DIR": self.ai_dir,
            "WORKLOG_TIMING": "stop",
            "WORKLOG_DEST": "git",
            "WORKLOG_GIT_TRACK": "true",
            "WORKLOG_LANG": "ko",
            "NOTION_STUB_LOG": self.notion_log,
            "PATH": safe_path,
            "TERM": "dumb",
            "GIT_CONFIG_NOSYSTEM": "1",
        }
        env.update(extra)
        return env

    def _update_settings(self, **env_updates):
        """settings.json의 env를 업데이트"""
        settings_path = os.path.join(self.ai_dir, "settings.json")
        with open(settings_path) as f:
            cfg = json.load(f)
        cfg["env"].update(env_updates)
        with open(settings_path, "w") as f:
            json.dump(cfg, f, indent=2)

    def _make_change_and_commit(self, filename="test.txt", content="hello\n", msg="test commit"):
        """파일 변경 + 커밋"""
        filepath = os.path.join(self.repo, filename)
        with open(filepath, "w") as f:
            f.write(content)
        env = self._env()
        subprocess.run(["git", "-C", self.repo, "add", filename], capture_output=True, env=env)
        subprocess.run(
            ["git", "-C", self.repo, "commit", "-m", msg],
            capture_output=True, env=env, timeout=10,
        )

    def _run_post_commit(self, **env_overrides):
        """post-commit.sh 직접 실행"""
        hook_script = os.path.join(PACKAGE_DIR, "hooks", "post-commit.sh")
        return subprocess.run(
            ["bash", hook_script],
            capture_output=True, text=True,
            cwd=self.repo,
            env=self._env(**env_overrides),
            timeout=30,
        )


class TestTimingDestCombinations(_EnvComboBase):
    """WORKLOG_TIMING x WORKLOG_DEST 크로스 조합 테스트"""

    def test_manual_git_skips(self):
        """TIMING=manual, DEST=git -> 워크로그 미생성"""
        self._update_settings(WORKLOG_TIMING="manual", WORKLOG_DEST="git")
        self._make_change_and_commit()
        self._run_post_commit(WORKLOG_TIMING="manual", WORKLOG_DEST="git")
        self.assertFalse(os.path.exists(os.path.join(self.repo, ".worklogs")))

    def test_manual_notion_skips(self):
        """TIMING=manual, DEST=notion -> stub 미호출"""
        self._update_settings(WORKLOG_TIMING="manual", WORKLOG_DEST="notion", NOTION_DB_ID="fake")
        self._make_change_and_commit()
        self._run_post_commit(WORKLOG_TIMING="manual", WORKLOG_DEST="notion", NOTION_DB_ID="fake")
        self.assertFalse(os.path.exists(self.notion_log))

    def test_manual_notion_only_skips(self):
        """TIMING=manual, DEST=notion-only -> stub 미호출"""
        self._update_settings(WORKLOG_TIMING="manual", WORKLOG_DEST="notion-only", NOTION_DB_ID="fake")
        self._make_change_and_commit()
        self._run_post_commit(WORKLOG_TIMING="manual", WORKLOG_DEST="notion-only", NOTION_DB_ID="fake")
        self.assertFalse(os.path.exists(self.notion_log))

    def test_stop_git_creates_local(self):
        """TIMING=stop, DEST=git -> 로컬 파일 생성"""
        self._update_settings(WORKLOG_TIMING="stop", WORKLOG_DEST="git")
        self._make_change_and_commit(filename="feature.py", content="print('hi')\n", msg="feat: add feature")
        self._run_post_commit(WORKLOG_TIMING="stop", WORKLOG_DEST="git")
        wl_files = glob.glob(os.path.join(self.repo, ".worklogs", "*.md"))
        self.assertTrue(len(wl_files) > 0, "로컬 워크로그 파일 생성되어야 함")

    def test_stop_notion_creates_both(self):
        """TIMING=stop, DEST=notion -> 로컬 + stub 호출"""
        self._update_settings(WORKLOG_TIMING="stop", WORKLOG_DEST="notion", NOTION_DB_ID="fake")
        self._make_change_and_commit(filename="api.py", content="api()\n", msg="feat: api")
        self._run_post_commit(WORKLOG_TIMING="stop", WORKLOG_DEST="notion", NOTION_DB_ID="fake")
        wl_files = glob.glob(os.path.join(self.repo, ".worklogs", "*.md"))
        self.assertTrue(len(wl_files) > 0, "로컬 파일 생성되어야 함")
        self.assertTrue(os.path.exists(self.notion_log), "notion stub 호출되어야 함")

    def test_stop_notion_only_no_local(self):
        """TIMING=stop, DEST=notion-only -> 로컬 없음, stub 호출"""
        self._update_settings(WORKLOG_TIMING="stop", WORKLOG_DEST="notion-only", NOTION_DB_ID="fake")
        self._make_change_and_commit(filename="model.py", content="model()\n", msg="feat: model")
        self._run_post_commit(WORKLOG_TIMING="stop", WORKLOG_DEST="notion-only", NOTION_DB_ID="fake")
        wl_files = glob.glob(os.path.join(self.repo, ".worklogs", "*.md"))
        self.assertEqual(len(wl_files), 0, "로컬 파일 없어야 함")
        self.assertTrue(os.path.exists(self.notion_log), "notion stub 호출되어야 함")


if __name__ == "__main__":
    result = unittest.main(verbosity=2, exit=False)
    import sys
    sys.exit(0 if result.result.wasSuccessful() else 1)
