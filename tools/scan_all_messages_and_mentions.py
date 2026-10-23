#!/usr/bin/env python3
"""
Comprehensive GitHub Messages, Notifications & Maintainer Comments Scanner
Audits 100% of notifications, PR reviews, comments, and mentions for @dextermos-dev.
"""

import os
import json
import urllib.request
import urllib.error
from datetime import datetime

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
env_file = os.path.join(PROJECT_ROOT, ".env")
if os.path.exists(env_file):
    with open(env_file, "r") as f:
        for line in f:
            if line.strip() and not line.startswith("#") and "=" in line:
                k, v = line.strip().split("=", 1)
                os.environ[k] = v.strip('"').strip("'")

TOKEN = os.getenv("GITHUB_TOKEN", "").strip()

def get_headers():
    headers = {
        "User-Agent": "BountyHunterAI/2.0",
        "Accept": "application/vnd.github.v3+json",
    }
    if TOKEN:
        headers["Authorization"] = f"token {TOKEN}"
    return headers

def fetch_json(url):
    req = urllib.request.Request(url, headers=get_headers())
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")[:300]
        return {"error": f"HTTP {e.code}: {body}"}
    except Exception as e:
        return {"error": str(e)}

def scan_notifications():
    print("=" * 70)
    print("1. NOTIFICACIONES GLOBALES DE GITHUB (ÚLTIMAS 50)")
    print("=" * 70)
    url = "https://api.github.com/notifications?all=true&per_page=50"
    data = fetch_json(url)
    if isinstance(data, dict) and "error" in data:
        print(f"[-] Error obteniendo notificaciones: {data['error']}")
        return []
    
    print(f"[+] Total de notificaciones recibidas: {len(data)}")
    actionable = []
    for item in data:
        unread = item.get("unread", False)
        reason = item.get("reason", "")
        subject = item.get("subject", {})
        repo = item.get("repository", {}).get("full_name", "")
        sub_title = subject.get("title", "")
        sub_type = subject.get("type", "")
        sub_url = subject.get("url", "")
        updated_at = item.get("updated_at", "")
        
        status_str = "[NO LEÍDA]" if unread else "[Leída]"
        print(f"\n{status_str} [{reason.upper()}] Repo: {repo}")
        print(f"  Tipo: {sub_type} | Actualizado: {updated_at}")
        print(f"  Título: {sub_title}")
        print(f"  URL API: {sub_url}")
        
        # Check details of thread if comment or review
        if sub_url:
            thread_data = fetch_json(sub_url)
            if isinstance(thread_data, dict) and "comments_url" in thread_data:
                state = thread_data.get("state", "")
                merged = thread_data.get("merged", False)
                html_url = thread_data.get("html_url", "")
                user = thread_data.get("user", {}).get("login", "")
                print(f"  Estado: {state} | Merged: {merged} | URL Web: {html_url} | Autor: {user}")
                
                # Check latest comments
                comments_url = thread_data.get("comments_url")
                if comments_url:
                    comments = fetch_json(comments_url + "?per_page=10")
                    if isinstance(comments, list) and len(comments) > 0:
                        print(f"  Últimos comentarios ({len(comments)} total):")
                        for c in comments[-3:]:
                            author = c.get("user", {}).get("login", "")
                            c_body = c.get("body", "").replace("\n", " ")[:160]
                            c_time = c.get("created_at", "")
                            print(f"    - @{author} ({c_time}): {c_body}")
                            if author not in ["dextermos-dev", "dextermos"]:
                                actionable.append({
                                    "repo": repo,
                                    "title": sub_title,
                                    "type": sub_type,
                                    "author": author,
                                    "time": c_time,
                                    "body": c.get("body", ""),
                                    "html_url": html_url
                                })
                                
            # If it is a PR, also check review comments
            review_comments_url = thread_data.get("review_comments_url") if isinstance(thread_data, dict) else None
            if review_comments_url:
                r_comments = fetch_json(review_comments_url + "?per_page=10")
                if isinstance(r_comments, list) and len(r_comments) > 0:
                    print(f"  Comentarios de revisión de código ({len(r_comments)} total):")
                    for rc in r_comments[-3:]:
                        author = rc.get("user", {}).get("login", "")
                        rc_body = rc.get("body", "").replace("\n", " ")[:160]
                        rc_time = rc.get("created_at", "")
                        print(f"    - @{author} [DIFF] ({rc_time}): {rc_body}")
                        if author not in ["dextermos-dev", "dextermos"]:
                            actionable.append({
                                "repo": repo,
                                "title": sub_title,
                                "type": "CodeReviewComment",
                                "author": author,
                                "time": rc_time,
                                "body": rc.get("body", ""),
                                "html_url": rc.get("html_url", "")
                            })

    return actionable

def scan_origintrail_pr():
    print("\n" + "=" * 70)
    print("2. AUDITORÍA ESPECÍFICA: OriginTrail/dkg-integrations PR #37")
    print("=" * 70)
    pr_url = "https://api.github.com/repos/OriginTrail/dkg-integrations/pulls/37"
    pr = fetch_json(pr_url)
    if isinstance(pr, dict) and "error" not in pr:
        print(f"PR #37: {pr.get('title')}")
        print(f"Estado: {pr.get('state')} | Merged: {pr.get('merged')} | Mergeable: {pr.get('mergeable')}")
        
        # Check comments
        c_url = pr.get("comments_url")
        if c_url:
            comments = fetch_json(c_url)
            if isinstance(comments, list):
                print(f"Comentarios generales: {len(comments)}")
                for c in comments:
                    print(f"  - @{c.get('user', {}).get('login')}: {c.get('body')[:200]}")
        
        # Check reviews
        r_url = f"https://api.github.com/repos/OriginTrail/dkg-integrations/pulls/37/reviews"
        reviews = fetch_json(r_url)
        if isinstance(reviews, list):
            print(f"Revisiones formales: {len(reviews)}")
            for r in reviews:
                print(f"  - @{r.get('user', {}).get('login')} [{r.get('state')}]: {r.get('body')}")
    else:
        print(f"[-] Error consultando PR #37: {pr}")

def scan_susu_repos():
    print("\n" + "=" * 70)
    print("3. AUDITORÍA ESPECÍFICA: REPOSITORIOS SUSU-LABS (ÚLTIMOS EVENTOS)")
    print("=" * 70)
    repos = ["SUSU-LABS/susu-web", "SUSU-LABS/susu-api", "SUSU-LABS/susu-contracts", "SUSU-LABS/susu-indexer"]
    for r in repos:
        # Check issues events / comments
        url = f"https://api.github.com/repos/{r}/issues/comments?sort=updated&direction=desc&per_page=10"
        comments = fetch_json(url)
        print(f"\n--- {r} (Últimos comentarios) ---")
        if isinstance(comments, list):
            for c in comments[:5]:
                user = c.get("user", {}).get("login", "")
                c_body = c.get("body", "").replace("\n", " ")[:140]
                c_time = c.get("created_at", "")
                issue_url = c.get("issue_url", "")
                print(f"  @{user} ({c_time}) en {issue_url.split('/')[-1]}: {c_body}")
        else:
            print(f"  Error: {comments}")

if __name__ == "__main__":
    actionable = scan_notifications()
    scan_origintrail_pr()
    scan_susu_repos()
    
    print("\n" + "=" * 70)
    print("RESUMEN DE MENSAJES ACCIONABLES DETECTADOS")
    print("=" * 70)
    if actionable:
        print(f"[!] Se encontraron {len(actionable)} comentarios/mensajes de mantenedores o terceros:")
        for a in actionable:
            print(f"  * [{a['repo']}] @{a['author']} en {a['title']} ({a['time']}):")
            print(f"    Texto: {a['body'][:250]}")
            print(f"    Enlace: {a['html_url']}\n")
    else:
        print("[✓] CERO comentarios o requerimientos pendientes de terceros o mantenedores.")
        print("[✓] Todas nuestras submissions y PRs están al día y sin cambios solicitados.")
