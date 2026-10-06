#!/usr/bin/env python3
import os
import json
import urllib.request
import urllib.error
from dotenv import load_dotenv

load_dotenv()
token = os.getenv("GITHUB_TOKEN", "").strip()

headers = {
    "Authorization": f"token {token}",
    "Accept": "application/vnd.github.v3+json",
    "User-Agent": "BountyHunterAI (dextermos-dev)"
}

comment_text = "Thanks for the clarification and code review, @RevTpark! Understood regarding the OSS nature of the repository. Closing this PR to keep the open PR queue clean. Keep up the great work with Earn!"

# 1. Post Comment
comment_url = "https://api.github.com/repos/SuperteamDAO/earn/issues/1495/comments"
req_c = urllib.request.Request(comment_url, data=json.dumps({"body": comment_text}).encode("utf-8"), headers=headers)

# 2. Close PR
pr_url = "https://api.github.com/repos/SuperteamDAO/earn/pulls/1495"
req_p = urllib.request.Request(pr_url, data=json.dumps({"state": "closed"}).encode("utf-8"), headers=headers, method="PATCH")

try:
    with urllib.request.urlopen(req_c) as res_c:
        print("[+] Comentario publicado con éxito en PR #1495")
    with urllib.request.urlopen(req_p) as res_p:
        print("[+] PR #1495 cerrada oficialmente con éxito")
except Exception as e:
    print("[!] Error:", e)
