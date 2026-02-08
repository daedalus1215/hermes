import os
from pathlib import Path
from typing import Dict
import yaml


class ApiConfig:
    def __init__(self):
        self.config_dict = {}
        self._load_config()

    def _load_config(self):
        # Default values
        self.config_dict = {
            "host": "0.0.0.0",
            "port": 8000,
            "base_url": "/api/v1",
            "audio_base_dir": "../resources/generated_audio"
        }

        # Load from YAML if exists
        config_path = Path(__file__).parent / "config.yaml"
        if config_path.exists():
            with open(config_path, "r") as f:
                yaml_config = yaml.safe_load(f)
                if yaml_config and "api" in yaml_config:
                    self._update_nested_dict(self.config_dict, yaml_config["api"])

        # Override with environment variables if they exist
        env_mapping = {
            "HERMES_API_HOST": "host",
            "HERMES_API_PORT": "port",
            "HERMES_API_BASE_URL": "base_url",
            "HERMES_API_AUDIO_DIR": "audio_base_dir"
        }

        for env_var, config_key in env_mapping.items():
            if env_value := os.getenv(env_var):
                if config_key == "port":
                    self.config_dict[config_key] = int(env_value)
                else:
                    self.config_dict[config_key] = env_value

    def _update_nested_dict(self, d: Dict, u: Dict) -> Dict:
        """Recursively update nested dictionary."""
        for k, v in u.items():
            if isinstance(v, dict):
                d[k] = self._update_nested_dict(d.get(k, {}), v)
            else:
                d[k] = v
        return d

    @property
    def host(self) -> str:
        return self.config_dict["host"]

    @property
    def port(self) -> int:
        return self.config_dict["port"]

    @property
    def base_url(self) -> str:
        return self.config_dict["base_url"]

    @property
    def audio_base_dir(self) -> str:
        return self.config_dict["audio_base_dir"]
