import os
import sys
import json
from pathlib import Path

def get_config_dir(app_name: str) -> Path:
    if sys.platform.startswith("win"):
        base_dir_str = os.environ.get("APPDATA")
        if not base_dir_str:
            base_dir = Path.home() / "AppData" / "Roaming"
        else:
            base_dir = Path(base_dir_str)

    else:
        base_dir_str = os.environ.get("XDG_CONFIG_HOME")
        if not base_dir_str:
            base_dir = Path.home() / ".config"
        else:
            base_dir = Path(base_dir_str)

    return base_dir / app_name

class CPConfig:
    def __init__(self, base_path = None):
        if base_path:
            self.base = Path(base_path).absolute()
            if self.base.exists():
                if not self.base.is_dir():
                    raise ValueError("Given base path is a file not directory")
            else:
                os.makedirs(self.base, exist_ok=True)

        else:
            self.base = get_config_dir('ctfproxy').absolute()
            os.makedirs(self.base, exist_ok=True)

    def _load(self, fpath: Path, default: dict | None = None) -> dict:
        if not fpath.exists():
            if default is not None:
                return default
            else:
                raise FileNotFoundError(filename = fpath)
        with open(fpath, 'r') as f:
            return json.load(f)

    def _save(self, fpath: Path, config: dict):
        with open(fpath, 'w') as f:
            json.dump(config, f)

    def _delete(self, fpath: Path):
        if fpath.exists():
            os.remove(fpath)

    def getClientConfig(self) -> dict:
        return self._load(self.base / "client.cproxy.cfg", dict())

    def saveClientConfig(self, config: dict):
        self._save(self.base / "client.cproxy.cfg", config)

    def getHostConfig(self) -> dict:
        return self._load(self.base / "host.cproxy.cfg", dict())

    def saveHostConfig(self, config: dict):
        self._save(self.base / "host.cproxy.cfg", config)

    def getHostDaemon(self) -> dict:
        return self._load(self.base / "host.cproxy.sock", dict())

    def saveHostDaemon(self, config: dict | None = None):
        if config is None:
            self._delete(self.base / "host.cproxy.sock")
        else:
            self._save(self.base / "host.cproxy.sock", config)

    def getClientDaemon(self) -> dict:
        return self._load(self.base / "client.cproxy.sock", dict())

    def saveClientDaemon(self, config: dict | None = None):
        if config is None:
            self._delete(self.base / "client.cproxy.sock")
        else:
            self._save(self.base / "client.cproxy.sock", config)


