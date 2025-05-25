import os
from pathlib import Path
import yaml
from typing import Dict, Optional, Union, TypedDict, NotRequired

DEFAULT_CONFIG_PATH = os.path.expanduser("~/.config/ttc_alerts/config.yaml")
ENV_CONFIG_PATH = "TTC_ALERTS_CONFIG"

class ConfigDict(TypedDict):
    log_level: str
    log_file: Optional[str]
    output_format: str
    monitor_interval: int

default_config: ConfigDict = {
    "log_level": "INFO",
    "log_file": None,
    "output_format": "text",
    "monitor_interval": 5,
}

def load_config_file(path: Optional[str] = None) -> Dict[str, Union[str, int, None]]:
    config_path = path or os.environ.get(ENV_CONFIG_PATH, DEFAULT_CONFIG_PATH)
    if config_path and os.path.exists(config_path):
        with open(config_path, "r") as f:
            return yaml.safe_load(f) or {}
    return {}

def load_env_config() -> Dict[str, Union[str, int]]:
    env_map = {
        "log_level": os.environ.get("TTC_ALERTS_LOG_LEVEL"),
        "log_file": os.environ.get("TTC_ALERTS_LOG_FILE"),
        "output_format": os.environ.get("TTC_ALERTS_OUTPUT_FORMAT"),
        "monitor_interval": os.environ.get("TTC_ALERTS_MONITOR_INTERVAL"),
    }
    # Remove None values and convert monitor_interval to int if set
    result: Dict[str, Union[str, int]] = {k: v for k, v in env_map.items() if v is not None}
    if "monitor_interval" in result:
        try:
            result["monitor_interval"] = int(str(result["monitor_interval"]))
        except ValueError:
            result["monitor_interval"] = default_config["monitor_interval"]
    return result

def get_effective_config(cli_args: Optional[Dict[str, Union[str, int, None]]] = None, config_path: Optional[str] = None) -> ConfigDict:
    config = default_config.copy()
    config.update(load_config_file(config_path))
    config.update(load_env_config())
    if cli_args:
        # Only update with non-None CLI args
        config.update({k: v for k, v in cli_args.items() if v is not None})
    return config 