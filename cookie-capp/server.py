#!/usr/bin/env python3
"""Serve the Cookie PnL cApp and proxy Cookie Chain RPC.

rpc.cookiescan.io currently serves an expired TLS cert, so browsers cannot
call it directly. This local proxy keeps the live demo usable for judges.
"""
from __future__ import annotations

import json
import ssl
import sys
import urllib.error
import urllib.request
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlencode, urlparse

ROOT = Path(__file__).resolve().parent
RPC = "https://rpc.cookiescan.io"
COOKIEBOX_QUOTE = "https://agg.cookiebox.app/quote"
MARKETS = "https://cookiescan.io/api/tokens"
CTX = ssl._create_unverified_context()
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8787
QUOTE_KEYS = ("inputMint", "outputMint", "amount", "slippageBps", "owner")


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def log_message(self, fmt: str, *args) -> None:
        sys.stderr.write("%s - %s\n" % (self.address_string(), fmt % args))

    def _cors(self) -> None:
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def do_OPTIONS(self) -> None:  # noqa: N802
        self.send_response(204)
        self._cors()
        self.end_headers()

    def do_GET(self) -> None:  # noqa: N802
        path = self.path.split("?", 1)[0]
        if path.rstrip("/") == "/api/quote":
            from urllib.parse import parse_qs, urlencode, urlparse

            qs = parse_qs(urlparse(self.path).query)
            params = {k: qs[k][0] for k in QUOTE_KEYS if k in qs and qs[k]}
            if "inputMint" not in params or "outputMint" not in params or "amount" not in params:
                self.send_response(400)
                self.send_header("Content-Type", "application/json")
                self._cors()
                self.end_headers()
                self.wfile.write(b'{"error":"inputMint, outputMint, amount required"}')
                return
            self._proxy_get(COOKIEBOX_QUOTE + "?" + urlencode(params))
            return
        if path.rstrip("/") == "/api/markets":
            self._proxy_get(MARKETS)
            return
        super().do_GET()

    def _proxy_get(self, url: str) -> None:
        req = urllib.request.Request(
            url,
            headers={"Accept": "application/json", "User-Agent": "CookiePnL/1.0"},
        )
        try:
            with urllib.request.urlopen(req, timeout=30, context=CTX) as resp:
                data = resp.read()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self._cors()
            self.end_headers()
            self.wfile.write(data)
        except urllib.error.HTTPError as exc:
            payload = exc.read()
            self.send_response(exc.code)
            self.send_header("Content-Type", "application/json")
            self._cors()
            self.end_headers()
            self.wfile.write(payload or json.dumps({"error": str(exc)}).encode())
        except Exception as exc:  # noqa: BLE001
            self.send_response(502)
            self.send_header("Content-Type", "application/json")
            self._cors()
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(exc)}).encode())

    def do_POST(self) -> None:  # noqa: N802
        if self.path.rstrip("/") != "/rpc":
            self.send_error(404)
            return
        length = int(self.headers.get("Content-Length") or 0)
        body = self.rfile.read(length)
        req = urllib.request.Request(
            RPC,
            data=body,
            headers={"Content-Type": "application/json", "Accept": "application/json"},
        )
        try:
            with urllib.request.urlopen(req, timeout=30, context=CTX) as resp:
                data = resp.read()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self._cors()
            self.end_headers()
            self.wfile.write(data)
        except urllib.error.HTTPError as exc:
            payload = exc.read()
            self.send_response(exc.code)
            self.send_header("Content-Type", "application/json")
            self._cors()
            self.end_headers()
            self.wfile.write(payload or json.dumps({"error": str(exc)}).encode())
        except Exception as exc:  # noqa: BLE001
            self.send_response(502)
            self.send_header("Content-Type", "application/json")
            self._cors()
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(exc)}).encode())


def main() -> int:
    httpd = ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    print(f"Cookie PnL -> http://127.0.0.1:{PORT}/")
    print("RPC proxy  -> POST /rpc  -> https://rpc.cookiescan.io")
    httpd.serve_forever()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
