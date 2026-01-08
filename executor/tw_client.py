import argparse
import os
from dataclasses import dataclass
from typing import Any, Dict, Optional, Tuple

import requests
from dotenv import load_dotenv

def _bool_env(name: str, default: bool) -> bool:
    v = os.getenv(name)
    if v is None:
        return default
    return v.strip().lower() in ("1","true","yes","y","on")

@dataclass
class TWError(Exception):
    status_code: int
    message: str
    url: str
    response_text: str = ""
    def __str__(self) -> str:
        return f"[{self.status_code}] {self.message} ({self.url})"

class ThingWorxClient:
    def __init__(self, base_url: str, app_key: str, verify_tls: bool = True, timeout_s: int = 30):
        self.base_url = base_url.rstrip("/")
        self.verify_tls = verify_tls
        self.timeout_s = timeout_s
        self.session = requests.Session()
        self.session.headers.update({
            "Accept":"application/json",
            "Content-Type":"application/json",
            "appKey": app_key,
        })

    @staticmethod
    def from_env() -> "ThingWorxClient":
        load_dotenv()
        base = os.getenv("THINGWORX_BASE_URL","").strip()
        key  = os.getenv("THINGWORX_APP_KEY","").strip()
        verify = _bool_env("THINGWORX_VERIFY_TLS", True)
        if not base:
            raise RuntimeError("Missing THINGWORX_BASE_URL in .env")
        if not key or "REPLACE" in key:
            raise RuntimeError("Missing THINGWORX_APP_KEY in .env")
        return ThingWorxClient(base, key, verify_tls=verify)

    def _url(self, path: str) -> str:
        if not path.startswith("/"):
            path = "/" + path
        return self.base_url + path

    def _request(self, method: str, path: str, *, json_body: Optional[Dict[str, Any]] = None) -> Tuple[int,str]:
        url = self._url(path)
        try:
            r = self.session.request(method, url, json=json_body, verify=self.verify_tls, timeout=self.timeout_s)
        except requests.RequestException as e:
            raise TWError(0, f"Network error: {e}", url) from e
        return r.status_code, (r.text or "")

    def ping(self) -> bool:
        for path in ("/SystemInformation", "/Resources/EntityServices"):
            code, _ = self._request("GET", path)
            if code in (200,401,403):
                return True
        return False

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ping", action="store_true")
    args = ap.parse_args()
    c = ThingWorxClient.from_env()
    if args.ping:
        print("PING:", "OK" if c.ping() else "FAILED")
    else:
        ap.print_help()

if __name__ == "__main__":
    main()
