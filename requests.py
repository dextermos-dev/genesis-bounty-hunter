"""
Lightweight zero-dependency requests shim using urllib
"""
import json
import urllib.request
import urllib.error
import urllib.parse
from typing import Optional, Dict, Any

class Response:
    def __init__(self, status_code: int, content: bytes, headers: Optional[dict] = None):
        self.status_code = status_code
        self.content = content
        self.headers = headers or {}
        self.text = content.decode("utf-8", errors="ignore") if isinstance(content, bytes) else str(content)
        self.ok = 200 <= status_code < 400

    def json(self):
        return json.loads(self.text) if self.text else {}

    def raise_for_status(self):
        if not self.ok:
            raise RuntimeError(f"HTTP Error {self.status_code}: {self.text[:200]}")

def _request(method: str, url: str, params: Optional[dict] = None, data: Any = None, json_data: Any = None, headers: Optional[dict] = None, timeout: float = 10.0) -> Response:
    headers = dict(headers or {})
    if params:
        query_str = urllib.parse.urlencode(params)
        url = f"{url}?{query_str}" if "?" not in url else f"{url}&{query_str}"

    body = None
    if json_data is not None:
        body = json.dumps(json_data).encode("utf-8")
        headers["Content-Type"] = "application/json"
    elif data is not None:
        body = data.encode("utf-8") if isinstance(data, str) else data

    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            resp_content = resp.read()
            resp_headers = dict(resp.headers)
            return Response(resp.status, resp_content, resp_headers)
    except urllib.error.HTTPError as e:
        err_content = e.read()
        err_headers = dict(e.headers)
        return Response(e.code, err_content, err_headers)
    except Exception as e:
        return Response(500, str(e).encode("utf-8"))

def get(url: str, params: Optional[dict] = None, headers: Optional[dict] = None, timeout: float = 10.0, **kwargs) -> Response:
    return _request("GET", url, params=params, headers=headers, timeout=timeout)

def post(url: str, data: Any = None, json: Any = None, params: Optional[dict] = None, headers: Optional[dict] = None, timeout: float = 10.0, **kwargs) -> Response:
    return _request("POST", url, params=params, data=data, json_data=json, headers=headers, timeout=timeout)

def put(url: str, data: Any = None, json: Any = None, params: Optional[dict] = None, headers: Optional[dict] = None, timeout: float = 10.0, **kwargs) -> Response:
    return _request("PUT", url, params=params, data=data, json_data=json, headers=headers, timeout=timeout)

def patch(url: str, data: Any = None, json: Any = None, params: Optional[dict] = None, headers: Optional[dict] = None, timeout: float = 10.0, **kwargs) -> Response:
    return _request("PATCH", url, params=params, data=data, json_data=json, headers=headers, timeout=timeout)

def delete(url: str, params: Optional[dict] = None, headers: Optional[dict] = None, timeout: float = 10.0, **kwargs) -> Response:
    return _request("DELETE", url, params=params, headers=headers, timeout=timeout)

def request(method: str, url: str, **kwargs) -> Response:
    data = kwargs.get("data")
    json_data = kwargs.get("json")
    params = kwargs.get("params")
    headers = kwargs.get("headers")
    timeout = kwargs.get("timeout", 10.0)
    return _request(method.upper(), url, params=params, data=data, json_data=json_data, headers=headers, timeout=timeout)

class Session:
    def __init__(self):
        self.headers = {}
    def get(self, url, **kwargs):
        headers = {**self.headers, **kwargs.pop("headers", {})}
        return get(url, headers=headers, **kwargs)
    def post(self, url, **kwargs):
        headers = {**self.headers, **kwargs.pop("headers", {})}
        return post(url, headers=headers, **kwargs)
    def put(self, url, **kwargs):
        headers = {**self.headers, **kwargs.pop("headers", {})}
        return put(url, headers=headers, **kwargs)
    def delete(self, url, **kwargs):
        headers = {**self.headers, **kwargs.pop("headers", {})}
        return delete(url, headers=headers, **kwargs)

class utils:
    quote = staticmethod(urllib.parse.quote)
    unquote = staticmethod(urllib.parse.unquote)

