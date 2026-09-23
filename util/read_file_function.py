from pathlib import Path
import yaml

def read_yaml(path: Path) -> dict:

    with path.open('r', encoding='utf-8') as file:
        data = yaml.safe_load(file)

    return data
