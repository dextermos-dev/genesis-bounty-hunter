#!/usr/bin/env python3
"""
Módulo de Integración Oficial Superteam Earn Agent API (tools/superteam_agent.py)
Protocolo oficial skill.md de Superteam Earn para registro autónomo, descubrimiento y envíos.
"""

import os
import sys
import json
import urllib.request
import urllib.error
from dotenv import load_dotenv

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
CONFIG_FILE = os.path.join(PROJECT_ROOT, "config", "superteam_agent.json")

BASE_URL = "https://superteam.fun"

def load_agent_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}

def save_agent_config(data):
    os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def register_agent(name="dextermos-hunter"):
    """Registra el agente en Superteam Earn y obtiene apiKey y claimCode."""
    config = load_agent_config()
    if config.get("apiKey"):
        print(f"[+] Agente ya registrado: {config.get('username')} (ID: {config.get('agentId')})")
        return config

    url = f"{BASE_URL}/api/agents"
    payload = json.dumps({"name": name}).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=payload,
        headers={"Content-Type": "application/json", "User-Agent": "BountyHunterAI/2.0"}
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as res:
            data = json.loads(res.read().decode("utf-8"))
            save_agent_config(data)
            print(f"🎉 Agente Registrado con Éxito!")
            print(f"👉 API Key: {data.get('apiKey')[:10]}...")
            print(f"👉 Claim Code: {data.get('claimCode')}")
            print(f"👉 Username: {data.get('username')}")
            print(f"👉 Link para reclamar cobros: https://superteam.fun/earn/claim/{data.get('claimCode')}")
            return data
    except Exception as e:
        print(f"[!] Error registrando agente: {e}")
        return None

def fetch_live_listings(api_key=None, limit=20):
    """Obtiene listings activos y elegibles para agentes."""
    if not api_key:
        cfg = load_agent_config()
        api_key = cfg.get("apiKey")
    if not api_key:
        print("[!] No hay API key configurada. Registra el agente primero.")
        return []

    url = f"{BASE_URL}/api/agents/listings/live?take={limit}"
    req = urllib.request.Request(
        url,
        headers={
            "Authorization": f"Bearer {api_key}",
            "User-Agent": "BountyHunterAI/2.0"
        }
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as res:
            return json.loads(res.read().decode("utf-8"))
    except Exception as e:
        print(f"[!] Error obteniendo listings: {e}")
        return []

def get_listing_details(slug, api_key=None):
    """Obtiene detalles completos de un listing."""
    if not api_key:
        cfg = load_agent_config()
        api_key = cfg.get("apiKey")
    url = f"{BASE_URL}/api/agents/listings/details/{slug}"
    req = urllib.request.Request(
        url,
        headers={
            "Authorization": f"Bearer {api_key}",
            "User-Agent": "BountyHunterAI/2.0"
        }
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as res:
            return json.loads(res.read().decode("utf-8"))
    except Exception as e:
        print(f"[!] Error obteniendo detalles de {slug}: {e}")
        return None

def submit_agent_work(listing_id, link, other_info="", tweet="", eligibility_answers=None, telegram=None, api_key=None):
    """Envía la propuesta / solución a un listing de Superteam Earn."""
    if not api_key:
        cfg = load_agent_config()
        api_key = cfg.get("apiKey")
    
    url = f"{BASE_URL}/api/agents/submissions/create"
    payload = {
        "listingId": listing_id,
        "link": link,
        "tweet": tweet or "",
        "otherInfo": other_info or "",
        "eligibilityAnswers": eligibility_answers or [],
        "ask": None,
        "telegram": telegram or "http://t.me/dextermostard"
    }
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "User-Agent": "BountyHunterAI/2.0"
        }
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as res:
            return json.loads(res.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        err_body = e.read().decode("utf-8")
        print(f"[!] HTTP Error {e.code}: {err_body}")
        return {"error": str(e), "code": e.code, "details": err_body}
    except Exception as e:
        print(f"[!] Error enviando submission: {e}")
        return {"error": str(e)}

if __name__ == "__main__":
    reg = register_agent("dextermos-hunter")
    if reg:
        listings = fetch_live_listings()
        print(f"[+] Listings encontrados: {len(listings)}")
