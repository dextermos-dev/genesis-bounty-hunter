#!/usr/bin/env python3
import urllib.request
import re
import json

paths = [
    "/bounties",
    "/org/comet-ml/bounties",
    "/org/daytonaio/bounties",
    "/org/outerbase/bounties",
    "/org/twenty/bounties",
    "/org/firecrawl/bounties"
]

for p in paths:
    url = f"https://console.algora.io{p}"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            html = resp.read().decode("utf-8", errors="ignore")
            print(f"SUCCESS {p}: length {len(html)}")
            gh = set(re.findall(r'https://github\.com/[^"\'\s<>]+/issues/\d+', html))
            print(f"  GitHub issues found: {len(gh)}")
            for g in gh:
                print("   ->", g)
    except urllib.error.HTTPError as e:
        print(f"HTTP {e.code} for {p}")
    except Exception as e:
        print(f"ERR for {p}: {e}")
