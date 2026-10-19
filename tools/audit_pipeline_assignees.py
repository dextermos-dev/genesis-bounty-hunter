#!/usr/bin/env python3
"""
Pipeline Assignee Auditor & Competitor Purge Tool (tools/audit_pipeline_assignees.py)

Audits all active GitHub issues in dashboard/data.json.
If any issue has been assigned by a maintainer or bot (e.g. drips-wave[bot])
to a competitor (assignee != 'dextermos' and assignee != 'dextermos-dev'):
1. Immediately purges the issue from dashboard/data.json.
2. Recalculates all pipeline metrics.
3. Emits a PIPELINE_CLEANUP warning in dashboard/live_events.json.
4. Triggers Telegram alert if configured.
"""

import os
import sys
import re
import json
import urllib.request
import urllib.error
from datetime import datetime
from dotenv import load_dotenv

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

load_dotenv()
TOKEN = os.getenv("GITHUB_TOKEN", "").strip()
DATA_PATH = os.path.join(PROJECT_ROOT, "dashboard", "data.json")
EVENTS_PATH = os.path.join(PROJECT_ROOT, "dashboard", "live_events.json")

OUR_HANDLES = {"dextermos", "dextermos-dev"}


def get_headers():
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "dextermos-dev"
    }
    if TOKEN:
        headers["Authorization"] = f"token {TOKEN}"
    return headers


def parse_github_issue_url(url):
    """Extrae (owner, repo, issue_number) de una URL de GitHub issue."""
    if not url:
        return None
    m = re.search(r"github\.com/([^/]+)/([^/]+)/issues/(\d+)", url)
    if m:
        return m.group(1), m.group(2), int(m.group(3))
    return None


def fetch_issue_data(owner, repo, number):
    url = f"https://api.github.com/repos/{owner}/{repo}/issues/{number}"
    req = urllib.request.Request(url, headers=get_headers())
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return json.loads(r.read().decode("utf-8"))
    except Exception as e:
        print(f"  [!] Error fetching {owner}/{repo}#{number}: {e}")
        return None


def log_event(event_type, title, details, severity="warning"):
    events = []
    if os.path.exists(EVENTS_PATH):
        try:
            with open(EVENTS_PATH, "r", encoding="utf-8") as f:
                events = json.load(f)
        except Exception:
            events = []

    new_event = {
        "timestamp": datetime.now().strftime("%H:%M:%S"),
        "date": datetime.now().strftime("%Y-%m-%d"),
        "type": event_type,
        "title": title,
        "details": details,
        "severity": severity
    }
    events.insert(0, new_event)
    events = events[:30]
    with open(EVENTS_PATH, "w", encoding="utf-8") as f:
        json.dump(events, f, indent=2, ensure_ascii=False)


def run_assignee_audit():
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Iniciando auditoría de asignaciones de competidores...")
    if not os.path.exists(DATA_PATH):
        print(f"[!] No se encontró {DATA_PATH}")
        return

    with open(DATA_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    bounties = data.get("bounties", [])
    initial_count = len(bounties)
    surviving_bounties = []
    purged = []

    for b in bounties:
        b_id = b.get("id") or b.get("bounty_id", "")
        status = b.get("status", "")
        # Si ya está MERGED o ganado por nosotros, no se audita asignación
        if status in ["MERGED (Won)", "COMPLETED", "PAID"]:
            surviving_bounties.append(b)
            continue

        # Extraer URL del issue original
        issue_url = b.get("source_url") or b.get("url") or ""
        parsed = parse_github_issue_url(issue_url)

        if not parsed:
            # Si no es un issue de GitHub directo (ej. Grant, RFC-x402, etc.), se conserva
            surviving_bounties.append(b)
            continue

        owner, repo, number = parsed
        issue_info = fetch_issue_data(owner, repo, number)

        if not issue_info:
            surviving_bounties.append(b)
            continue

        assignee = issue_info.get("assignee")
        assignees = [a.get("login") for a in issue_info.get("assignees", [])]

        competitor_assignee = None
        if assignee and assignee.get("login") not in OUR_HANDLES:
            competitor_assignee = assignee.get("login")
        elif any(a not in OUR_HANDLES for a in assignees):
            competitor_assignee = [a for a in assignees if a not in OUR_HANDLES][0]

        if competitor_assignee:
            print(f"  [⚠️ PURGA] Issue {owner}/{repo}#{number} ('{b_id}') asignado al competidor @{competitor_assignee}. Eliminando del dashboard.")
            purged.append({
                "id": b_id,
                "repo": f"{owner}/{repo}",
                "number": number,
                "competitor": competitor_assignee,
                "reward": b.get("reward_usd", 0)
            })
            log_event(
                event_type="PIPELINE_PURGE",
                title=f"Bounty Asignado a Competidor Removido: {b_id}",
                details=f"Issue {owner}/{repo}#{number} asignado por mantenedores a @{competitor_assignee}. Removido del dashboard para integridad contable.",
                severity="warning"
            )
        else:
            surviving_bounties.append(b)

    if purged:
        print(f"\n[!] Se purgaron {len(purged)} bounties asignados a competidores.")
        data["bounties"] = surviving_bounties
        data["total_bounties_count"] = len(surviving_bounties)
        
        # Recalcular métricas
        sprint_prs = [b for b in surviving_bounties if b.get("sprint") or "prism" in (b.get("id") or "") or "slippay" in (b.get("id") or "")]
        data["sprint_in_review_prs"] = sum(1 for b in sprint_prs if b.get("status") == "In Review")
        
        with open(DATA_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"[✅] Dashboard data.json actualizado exitosamente. Bounties activos: {len(surviving_bounties)}")
    else:
        print(f"[✅] Todos los bounties activos ({len(surviving_bounties)}) están limpios y sin asignación a competidores.")


if __name__ == "__main__":
    run_assignee_audit()
