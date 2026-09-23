from dataclasses import dataclass

from pathlib import Path

@dataclass
class SessionConfig:

    BASE_DIR: Path
    ENV_CONFIG: dict
