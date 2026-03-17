"""
KodeKeeper — Data Tracker
Reads Claude Code usage from statusline data files, checks project health,
git status, estimates costs, and serves everything to the dashboard.
"""

import json
import os
import socket
import subprocess
from datetime import datetime, date

USAGE_FILE    = os.path.expanduser("~/.claude/usage/totals.json")
SETTINGS_FILE = os.path.expanduser("~/.claude/usage/kk_settings.json")

# Token costs per million (USD)
MODEL_COSTS = {
    "sonnet 4.6":  {"input": 3.00,  "output": 15.00},
    "opus 4":      {"input": 15.00, "output": 75.00},
    "haiku 4.5":   {"input": 0.80,  "output": 4.00},
    "sonnet 3.5":  {"input": 3.00,  "output": 15.00},
    "default":     {"input": 3.00,  "output": 15.00},
}

PROJECTS = [
    {"name": "Launcher",       "slug": "launcher",        "port": 5554, "path": "~/launcher",              "repo": None},
    {"name": "Kalshi Edge",    "slug": "kalshi-edge",     "port": 5555, "path": "~/kalshi-edge",            "repo": "papjamzzz/kalshi-konnektor"},
    {"name": "StreamFader",    "slug": "streamfader",     "port": 5556, "path": "~/streamfader",            "repo": "papjamzzz/Stream-Fader"},
    {"name": "TrackTracks",    "slug": "tracktracks",     "port": 5557, "path": "~/track_cpu_monitor",      "repo": "papjamzzz/Track-Tracks"},
    {"name": "DAW Doctor",     "slug": "daw-doctor",      "port": 5558, "path": "~/ableton-diagnostics",    "repo": "papjamzzz/Daw-Doctor"},
    {"name": "KK Trader",      "slug": "kk-trader",       "port": 5559, "path": "~/kalshi-trader",          "repo": "papjamzzz/kalshi-trader"},
    {"name": "KodeKeeper",     "slug": "kodekeeper",      "port": 5560, "path": "~/kodekeeper",             "repo": None},
]


def _port_open(port, timeout=0.4):
    try:
        with socket.create_connection(("127.0.0.1", port), timeout=timeout):
            return True
    except Exception:
        return False


def _git_status(path):
    full = os.path.expanduser(path)
    if not os.path.isdir(full):
        return None
    try:
        branch = subprocess.check_output(
            ["git", "-C", full, "symbolic-ref", "--short", "HEAD"],
            stderr=subprocess.DEVNULL
        ).decode().strip()
        dirty_out = subprocess.check_output(
            ["git", "-C", full, "status", "--porcelain"],
            stderr=subprocess.DEVNULL
        ).decode().strip()
        last = subprocess.check_output(
            ["git", "-C", full, "log", "-1", "--format=%ar", "--"],
            stderr=subprocess.DEVNULL
        ).decode().strip()
        return {
            "branch": branch,
            "clean":  len(dirty_out) == 0,
            "last_commit": last or "—",
        }
    except Exception:
        return None


def _load_usage():
    if not os.path.exists(USAGE_FILE):
        return {}
    try:
        with open(USAGE_FILE) as f:
            return json.load(f)
    except Exception:
        return {}


def _cost(tokens, model_key="default", kind="input"):
    rates = MODEL_COSTS.get(model_key.lower(), MODEL_COSTS["default"])
    return (tokens / 1_000_000) * rates[kind]


def _estimate_cost(total_tokens, model="default"):
    # Assume 80% input / 20% output split (typical for coding sessions)
    inp = int(total_tokens * 0.8)
    out = int(total_tokens * 0.2)
    m = model.lower()
    rates = MODEL_COSTS.get(m, MODEL_COSTS["default"])
    return round((inp / 1e6) * rates["input"] + (out / 1e6) * rates["output"], 4)


def load_settings():
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE) as f:
                return json.load(f)
        except Exception:
            pass
    return {"auto_open": True}


def save_settings(data):
    os.makedirs(os.path.dirname(SETTINGS_FILE), exist_ok=True)
    with open(SETTINGS_FILE, "w") as f:
        json.dump(data, f, indent=2)


def get_status():
    usage   = _load_usage()
    settings = load_settings()

    # ── Usage & cost ──────────────────────────────────────────────────────────
    model = usage.get("model", "Sonnet 4.6")

    day_tok  = usage.get("day",   {}).get("tokens", 0)
    wk_tok   = usage.get("week",  {}).get("tokens", 0)
    mo_tok   = usage.get("month", {}).get("tokens", 0)

    day_cost = _estimate_cost(day_tok,  model)
    wk_cost  = _estimate_cost(wk_tok,   model)
    mo_cost  = _estimate_cost(mo_tok,   model)

    # ── Context ───────────────────────────────────────────────────────────────
    ctx_history = usage.get("ctx_history", [])
    ctx_pct     = ctx_history[-1] if ctx_history else 0
    ctx_free_k  = usage.get("ctx_free_k", "—")

    # ── Projects ──────────────────────────────────────────────────────────────
    projects = []
    for p in PROJECTS:
        online = _port_open(p["port"])
        git    = _git_status(p["path"])
        projects.append({
            **p,
            "online": online,
            "git":    git,
        })

    # ── Session start ─────────────────────────────────────────────────────────
    session_start = usage.get("session_start")
    session_mins  = None
    if session_start:
        try:
            started = datetime.fromisoformat(session_start)
            session_mins = int((datetime.now() - started).total_seconds() / 60)
        except Exception:
            pass

    return {
        "usage": {
            "day":  {"tokens": day_tok,  "cost": day_cost},
            "week": {"tokens": wk_tok,   "cost": wk_cost},
            "month":{"tokens": mo_tok,   "cost": mo_cost},
        },
        "context": {
            "pct":     round(ctx_pct, 1),
            "history": ctx_history[-60:],
            "free_k":  ctx_free_k,
            "model":   model,
        },
        "projects":     projects,
        "session_mins": session_mins,
        "settings":     settings,
        "now":          datetime.now().strftime("%H:%M"),
        "today":        str(date.today()),
    }
