import os
from pathlib import Path
from typing import Dict
import yaml


class HermesConfig:
    def __init__(self):
        self.config_dict = {}
        self._load_config()

    def _load_config(self):
        # Default values
        self.config_dict = {
            "process": {
                "folder": os.path.join("../resources/", "hermes-process"),
            },
            "output": {"folder": os.path.join("../resources/", "hermes-audio-out")},
        }

        # Load from YAML if exists
        config_path = Path(__file__).parent / "config.yaml"
        if config_path.exists():
            with open(config_path, "r") as f:
                yaml_config = yaml.safe_load(f)
                if yaml_config:
                    self._update_nested_dict(self.config_dict, yaml_config)

        # Override with environment variables if they exist
        env_mapping = {
            "HERMES_INPUT_FOLDER": ("input", "folder"),
            "HERMES_INPUT_FILE": ("input", "file"),
            "HERMES_OUTPUT_FOLDER": ("output", "folder"),
        }

        for env_var, config_path in env_mapping.items():
            if env_value := os.getenv(env_var):
                current = self.config_dict
                for key in config_path[:-1]:
                    current = current[key]
                current[config_path[-1]] = env_value

    def _update_nested_dict(self, d: Dict, u: Dict) -> Dict:
        """Recursively update nested dictionary."""
        for k, v in u.items():
            if isinstance(v, dict):
                d[k] = self._update_nested_dict(d.get(k, {}), v)
            else:
                d[k] = v
        return d

    @property
    def input_folder(self) -> str:
        return self.config_dict["input"]["folder"]

    @property
    def process_folder(self) -> str:
        return self.config_dict["process"]["folder"]

    @property
    def output_folder(self) -> str:
        return self.config_dict["output"]["folder"]
