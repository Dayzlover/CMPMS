import json
from pathlib import Path


class ConfigManager:
    def __init__(self):
        root = Path(__file__).resolve().parents[2]
        config_path = root / "config" / "server.json"

        with open(config_path, "r", encoding="utf-8") as file:
            self.config = json.load(file)

    def get(self, key, default=None):
        return self.config.get(key, default)