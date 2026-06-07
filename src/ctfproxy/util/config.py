import os
import sys
import json
import base64
import hashlib
from pathlib import Path
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

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
    BEGIN_MARKER = "----------------- CPROXY -- BEGIN -----------------"
    END_MARKER   = "------------------ CPROXY -- END ------------------"
    KEY = hashlib.sha256(b"justsimplewaytohardenuseredits").digest()


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
        try:
            with open(fpath, 'r') as f:
                return json.load(f)
        except Exception as e:
            if default is not None:
                return default
            else:
                raise e

    def _loads(self, fpath: Path, default: str | None = None) -> str:
        if not fpath.exists():
            if default is not None:
                return default
            else:
                raise FileNotFoundError(filename = fpath)
        try:
            with open(fpath, 'r') as f:
                return f.read().strip()
        except Exception as e:
            if default is not None:
                return default
            else:
                raise e

    def _loade(self, fpath: Path, default: dict | None = None) -> dict:
        if not fpath.exists():
            if default is not None:
                return default
            else:
                raise FileNotFoundError(filename = fpath)
        try:
            with open(fpath, 'r') as f:
                data = f.read().strip().splitlines()
                if len(data) < 3 or data[0] != self.BEGIN_MARKER or data[-1] != self.END_MARKER:
                    if default is not None:
                        return default
                    else:
                        raise ValueError("Invalid file format.")

                b64data = "".join(data[1:-1])
                rawdata = base64.b64decode(b64data)

                iv = rawdata[:16]
                ct = rawdata[16:]

                cipher = AES.new(self.KEY, AES.MODE_CBC, iv)
                jsondata = unpad(cipher.decrypt(ct), 16).decode()

                return json.loads(jsondata)
        except Exception as e:
            if default is not None:
                return default
            else:
                raise e



    def _save(self, fpath: Path, config: dict):
        with open(fpath, 'w') as f:
            json.dump(config, f)

    def _saves(self, fpath: Path, data: str):
        with open(fpath, 'w') as f:
            f.write(data)

    def _savee(self, fpath: Path, config: dict):
        jsondata = json.dumps(config).encode()

        cipher = AES.new(self.KEY, AES.MODE_CBC)
        ct = cipher.encrypt(pad(jsondata, 16))

        payload = cipher.iv + ct
        b64data = base64.b64encode(payload).decode()

        wraped = "\n".join([b64data[i:i+50] for i in range(0, len(b64data), 50)])
        data = f"{self.BEGIN_MARKER}\n{wraped}\n{self.END_MARKER}\n"
        with open(fpath, 'w') as f:
            f.write(data)

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


    def getDefaultServer(self) -> str:
        return self._loads(self.base / "default.server", "")

    def setDefaultServer(self, servername: str):
        return self._saves(self.base / "default.server", servername)

    def getServerConfig(self, servername: str) -> dict:
        return self._loade(self.base / f"servers/{servername}.cfg", {})

    def getDefaultServerConfig(self):
        ds = self.getDefaultServer()
        if ds:
            return self.getServerConfig(ds)
        else:
            return {}


