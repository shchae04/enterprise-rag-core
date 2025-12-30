import os
import sys
from pathlib import Path


def pytest_configure() -> None:
    # pytest 실행 환경에 따라 repo root가 sys.path에 없을 수 있어 app 패키지 import가 실패할 수 있음.
    repo_root = Path(__file__).resolve().parents[1]
    repo_root_str = str(repo_root)
    if repo_root_str not in sys.path:
        sys.path.insert(0, repo_root_str)

    # app.core.config.Settings 가 import 시점에 필수 env를 요구하므로,
    # CI/로컬 모두에서 최소한의 더미 값을 제공해 테스트 수집이 실패하지 않게 함.
    os.environ.setdefault("GOOGLE_API_KEY", "dummy")
