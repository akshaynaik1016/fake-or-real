"""Tests never mutate an included database or contact a configured provider."""
import os
import tempfile
from pathlib import Path
import sys
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))
_test_dir = tempfile.TemporaryDirectory(prefix="fake-or-real-tests-")
os.environ["DATABASE_URL"] = "sqlite:///" + str(Path(_test_dir.name) / "tests.db")
os.environ["ENVIRONMENT"] = "development"
os.environ["DEMO_MODE"] = "true"
os.environ["AI_PROVIDER"] = "none"
os.environ["TAVILY_API_KEY"] = ""
os.environ["SAFE_BROWSING_API_KEY"] = ""
os.environ["VIRUSTOTAL_API_KEY"] = ""
os.environ["NETWORK_SCANNERS_ENABLED"] = "false"
os.environ["CASE_URL_FETCH_ENABLED"] = "false"


@pytest.fixture(autouse=True)
def reset_rate_limiter():
    from app.core.rate_limiter import rate_limiter
    rate_limiter.requests.clear()
    yield
