import pytest

from pathlib import Path
import logging

from env.session_config import SessionConfig
from util.read_file_function import read_yaml

root_dir = Path(__file__).parent


def pytest_addoption(parser):
    parser.addoption(
        "--env",
        action="store",
        default="local",
        choices=["local", "ut", "sit", "uat"],
        help="透過'--env'決定執行環境"
    )

@pytest.fixture(scope="session", autouse=True)
def session_config(request):
    env = request.config.getoption("--env")
    env_config_file = root_dir / 'env' / 'env_config' / f'{env}_config.yaml'
    env_config = read_yaml(env_config_file)
    SessionConfig.BASE_DIR = root_dir
    SessionConfig.ENV_CONFIG = env_config
    return SessionConfig
