#!/usr/bin/env python3
"""
Audit GitHub Threads, Notifications & Maintainer Comments (tools/audit_github_threads.py)
Inspects GitHub notifications, recent events, and comments on submitted PRs/issues
for @dextermos and @dextermos-dev.
"""

import os
import json
import urllib.request
import urllib.error
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("GITHUB_TOKEN", "").strip()

def get_headers():
    headers = {
        "User-Agent": "BountyHunterAI-ThreadAuditor/2.0",
        "Accept": "application/vnd.github.v3+json"
    }
    if TOKEN:
        headers["Authorization"] = f"token {TOKEN}"
    return headers

def fetch_json(url):
    req = urllib.request.Request(url, headers=get_headers())
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        print(f"[-] HTTP Error {e.code} on {url}: {e.read().decode()[:200]}")
        return None
    except Exception as e:
        print(f"[-] Error fetching {url}: {e}")
        return None

def check_notifications():
    print("\n--- 1. NOTIFICACIONES DE GITHUB ---")
    if not TOKEN:
        print("[!] GITHUB_TOKEN no encontrado en .env")
        return []
    url = "https://api.github.com/notifications?all=true&per_page=20"
    data = fetch_json(url)
    if data:
        print(f"[+] Total notificaciones encontradas: {len(data)}")
        for notif in data[:10]:
            repo = notif.get("repository", {}).get("full_name")
            subject = notif.get("subject", {})
            title = subject.get("title")
            sub_type = subject.get("type")
            sub_url = subject.get("url")
            unread = notif.get("unread")
            updated = notif.get("updated_at")
            print(f"  * [{updated}] ({repo}) [{sub_type}] {title} (Unread: {unread})")
            print(f"    URL: {sub_url}")
    else:
        print("  (Sin notificaciones recientes o error)")
    return data

def check_specific_threads():
    print("\n--- 2. AUDITORÍA DE HILOS Y PRS ACTIVAS ---")
    targets = [
        ("mallonepay/pay-per-token-llm-gateway", 127),
        ("Cyfrin/security-and-auditing-full-course-s23", 442),
        ("Scottcjn/Rustchain", 8033),
        ("gibwork/gibwork", 177)
    ]
    
    # Also load from data.json active bounties with PR numbers
    try:
        with open("dashboard/data.json", "r") as f:
            d = json.load(f)
            for b in d.get("bounties", []):
                pr_url = b.get("pull_request_url") or ""
                if "github.com/" in pr_url and "/pull/" in pr_url:
                    parts = pr_url.replace("https://github.com/", "").split("/pull/")
                    if len(parts) == 2:
                        repo = parts[0]
                        num = int(parts[1].split("/")[0].split("#")[0])
                        if (repo, num) not in targets:
                            targets.append((repo, num))
    except Exception as e:
        print(f"[!] Error leyendo data.json: {e}")

    for repo, issue_num in targets:
        print(f"\n>> Revisando {repo} #{issue_num}:")
        # Get comments
        url = f"https://api.github.com/repos/{repo}/issues/{issue_num}/comments"
        comments = fetch_json(url)
        if comments:
            print(f"   [+] {len(comments)} comentarios encontrados.")
            for c in comments[-3:]: # Last 3 comments
                user = c.get("user", {}).get("login")
                created = c.get("created_at")
                body = c.get("body", "").replace("\n", " ")[:150]
                print(f"   - [{created}] @{user}: {body}...")
        else:
            print(f"   (Sin comentarios o hilo privado)")

def check_user_events(username):
    print(f"\n--- 3. EVENTOS RECIENTES DE @{username} ---")
    url = f"https://api.github.com/users/{username}/events?per_page=15"
    events = fetch_json(url)
    if events:
        for ev in events[:8]:
            ev_type = ev.get("type")
            repo = ev.get("repo", {}).get("name")
            created = ev.get("created_at")
            payload = ev.get("payload", {})
            action = payload.get("action", "")
            print(f"  * [{created}] {ev_type} ({action}) en {repo}")
    else:
        print(f"  (Sin eventos recientes)")

if __name__ == '__main__':
    check_notifications()
    check_user_events("dextermos-dev")
    check_user_events("dextermos")
    check_specific_threads()
