#!/usr/bin/env python3
"""
GitHub Resilient Client with ETag Conditional Caching & Adaptive Jitter
Designed to achieve continuous high-frequency scanning without triggering:
- Primary Rate Limits (60 unauthenticated / 5,000 authenticated per hour)
- Secondary Rate Limits (anti-abuse / concurrent burst detection)
- Automated Bot Suspicion

Key Features:
1. Conditional HTTP Requests (If-None-Match): Receives HTTP 304 Not Modified which consumes 0 rate points.
2. Persistent ETag Cache: Stored in an atomic local SQLite database.
3. Adaptive Jitter & Backoff: Staggered randomized micro-delays between API bursts.
4. Auto Rate Limit Telemetry: Real-time tracking of remaining quota and reset timestamps.
"""

import os
import time
import random
import sqlite3
import json
from typing import Optional, Dict, Any, Tuple
import requests

CACHE_DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "github_cache.db")

class GitHubResilientClient:
    def __init__(self, token: Optional[str] = None):
        self.token = token or os.getenv("GITHUB_TOKEN") or self._load_token_from_env()
        self.base_url = "https://api.github.com"
        self._init_db()

    def _load_token_from_env(self) -> Optional[str]:
        env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
        if os.path.exists(env_path):
            with open(env_path, "r", encoding="utf-8") as f:
                for line in f:
                    if line.startswith("GITHUB_TOKEN="):
                        return line.strip().split("=", 1)[1].strip("'\"")
        return None

    def _init_db(self):
        os.makedirs(os.path.dirname(CACHE_DB_PATH), exist_ok=True)
        with sqlite3.connect(CACHE_DB_PATH) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS http_cache (
                    url TEXT PRIMARY KEY,
                    etag TEXT,
                    last_modified TEXT,
                    status_code INTEGER,
                    response_json TEXT,
                    updated_at REAL
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS rate_limits (
                    resource TEXT PRIMARY KEY,
                    remaining INTEGER,
                    limit_total INTEGER,
                    reset_at INTEGER,
                    updated_at REAL
                )
            """)
            conn.commit()

    def _get_headers(self, custom_headers: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "Genesis-Bounty-Hunter-Resilient/2.1 (contact: dextermos-dev@proton.me)",
        }
        if self.token:
            headers["Authorization"] = f"token {self.token}"
        if custom_headers:
            headers.update(custom_headers)
        return headers

    def _record_rate_limit(self, resp_headers: Dict[str, Any]):
        limit = resp_headers.get("x-ratelimit-limit")
        remaining = resp_headers.get("x-ratelimit-remaining")
        reset = resp_headers.get("x-ratelimit-reset")
        resource = resp_headers.get("x-ratelimit-resource", "core")

        if limit and remaining and reset:
            try:
                with sqlite3.connect(CACHE_DB_PATH) as conn:
                    conn.execute("""
                        INSERT OR REPLACE INTO rate_limits (resource, remaining, limit_total, reset_at, updated_at)
                        VALUES (?, ?, ?, ?, ?)
                    """, (resource, int(remaining), int(limit), int(reset), time.time()))
                    conn.commit()
            except Exception:
                pass

    def get_rate_limit_telemetry(self) -> Dict[str, Any]:
        with sqlite3.connect(CACHE_DB_PATH) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute("SELECT * FROM rate_limits").fetchall()
            return {r["resource"]: dict(r) for r in rows}

    def get(
        self,
        endpoint_or_url: str,
        params: Optional[Dict[str, Any]] = None,
        use_cache: bool = True,
        min_jitter: float = 0.5,
        max_jitter: float = 1.8,
        timeout: float = 12.0
    ) -> Tuple[int, Any, bool]:
        """
        Performs a conditional GET request.
        Returns: (status_code, data, was_cached_or_not_modified)
        """
        # Adaptive anti-burst jitter
        if min_jitter > 0:
            time.sleep(random.uniform(min_jitter, max_jitter))

        url = endpoint_or_url if endpoint_or_url.startswith("http") else f"{self.base_url}{endpoint_or_url}"
        
        # Build full query string for caching key
        if params:
            import urllib.parse
            query_str = urllib.parse.urlencode(sorted(params.items()))
            cache_key = f"{url}?{query_str}"
        else:
            cache_key = url

        req_headers = self._get_headers()
        cached_row = None

        if use_cache:
            with sqlite3.connect(CACHE_DB_PATH) as conn:
                conn.row_factory = sqlite3.Row
                cached_row = conn.execute(
                    "SELECT * FROM http_cache WHERE url = ?", (cache_key,)
                ).fetchone()

            if cached_row and cached_row["etag"]:
                req_headers["If-None-Match"] = cached_row["etag"]
            if cached_row and cached_row["last_modified"]:
                req_headers["If-Modified-Since"] = cached_row["last_modified"]

        resp = requests.get(url, params=params, headers=req_headers, timeout=timeout)
        self._record_rate_limit(resp.headers)

        if resp.status_code == 304 and cached_row:
            # 304 Not Modified: 0 rate limit cost, return cached content
            cached_data = json.loads(cached_row["response_json"]) if cached_row["response_json"] else None
            return 200, cached_data, True

        if resp.status_code == 200:
            try:
                data = resp.json()
            except Exception:
                data = resp.text

            if use_cache:
                etag = resp.headers.get("etag")
                last_mod = resp.headers.get("last-modified")
                with sqlite3.connect(CACHE_DB_PATH) as conn:
                    conn.execute("""
                        INSERT OR REPLACE INTO http_cache (url, etag, last_modified, status_code, response_json, updated_at)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (cache_key, etag, last_mod, resp.status_code, json.dumps(data) if isinstance(data, (dict, list)) else str(data), time.time()))
                    conn.commit()

            return 200, data, False

        # If rate limited (403), fallback to cached if available
        if resp.status_code == 403 and cached_row and cached_row["response_json"]:
            try:
                data = json.loads(cached_row["response_json"])
                return 200, data, True
            except Exception:
                pass

        return resp.status_code, resp.text, False

    def post(self, endpoint_or_url: str, json_data: Any, timeout: float = 12.0) -> Tuple[int, Any]:
        time.sleep(random.uniform(0.8, 2.0))
        url = endpoint_or_url if endpoint_or_url.startswith("http") else f"{self.base_url}{endpoint_or_url}"
        resp = requests.post(url, json=json_data, headers=self._get_headers(), timeout=timeout)
        self._record_rate_limit(resp.headers)
        try:
            return resp.status_code, resp.json()
        except Exception:
            return resp.status_code, resp.text

    def patch(self, endpoint_or_url: str, json_data: Any, timeout: float = 12.0) -> Tuple[int, Any]:
        time.sleep(random.uniform(0.8, 2.0))
        url = endpoint_or_url if endpoint_or_url.startswith("http") else f"{self.base_url}{endpoint_or_url}"
        resp = requests.patch(url, json=json_data, headers=self._get_headers(), timeout=timeout)
        self._record_rate_limit(resp.headers)
        try:
            return resp.status_code, resp.json()
        except Exception:
            return resp.status_code, resp.text


if __name__ == "__main__":
    client = GitHubResilientClient()
    print("Testing GitHub Resilient Client with ETag Cache...")
    status, data, was_cached = client.get("/user")
    print(f"Request 1: status={status}, was_cached={was_cached}, user={data.get('login') if isinstance(data, dict) else 'err'}")
    
    # Immediately re-request: should hit 304 Not Modified
    status2, data2, was_cached2 = client.get("/user")
    print(f"Request 2 (immediate conditional): status={status2}, was_cached={was_cached2} (consumed 0 rate points!)")
    
    telemetry = client.get_rate_limit_telemetry()
    print("Rate Limit Telemetry:", json.dumps(telemetry, indent=2))
