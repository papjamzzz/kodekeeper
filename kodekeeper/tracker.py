"""
KodeKeeper — Data Tracker
Reads Claude Code usage from statusline data files, checks project health,
git status, estimates costs, fires budget alerts, and serves everything to
the dashboard.
"""

import json
import os
import re
import socket
import subprocess
from datetime import datetime, date, timedelta

try:
    import psutil
    _HAS_PSUTIL = True
except ImportError:
    _HAS_PSUTIL = False

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
    {"name": "Launcher",    "slug": "launcher",    "port": 5554, "path": "~/launcher",           "repo": None,                       "needs_env": False},
    {"name": "Kalshi Edge", "slug": "kalshi-edge", "port": 5555, "path": "~/kalshi-edge",         "repo": "papjamzzz/kalshi-konnektor","needs_env": True},
    {"name": "StreamFader", "slug": "streamfader", "port": 5556, "path": "~/streamfader",         "repo": "papjamzzz/Stream-Fader",   "needs_env": False},
    {"name": "TrackTracks", "slug": "tracktracks", "port": 5557, "path": "~/track_cpu_monitor",   "repo": "papjamzzz/Track-Tracks",   "needs_env": False},
    {"name": "DAW Doctor",  "slug": "daw-doctor",  "port": 5558, "path": "~/ableton-diagnostics", "repo": "papjamzzz/Daw-Doctor",     "needs_env": False},
    {"name": "KK Trader",   "slug": "kk-trader",   "port": 5559, "path": "~/kalshi-trader",       "repo": "papjamzzz/kalshi-trader",  "needs_env": True},
    {"name": "KodeKeeper",  "slug": "kodekeeper",  "port": 5560, "path": "~/kodekeeper",          "repo": None,                       "needs_env": False},
    {"name": "Pipeline",    "slug": "pipeline",    "port": 5561, "path": "~/pipeline",            "repo": None,                       "needs_env": False},
    {"name": "5i",          "slug": "5i",          "port": 5562, "path": "~/5i",                  "repo": "papjamzzz/5i",             "needs_env": True},
]


# ── Helpers ───────────────────────────────────────────────────────────────────

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
        ahead, behind = 0, 0
        try:
            ab = subprocess.check_output(
                ["git", "-C", full, "rev-list", "--left-right", "--count",
                 f"origin/{branch}...HEAD"],
                stderr=subprocess.DEVNULL
            ).decode().strip()
            parts = ab.split()
            if len(parts) == 2:
                behind, ahead = int(parts[0]), int(parts[1])
        except Exception:
            pass
        return {
            "branch":      branch,
            "clean":       len(dirty_out) == 0,
            "last_commit": last or "—",
            "ahead":       ahead,
            "behind":      behind,
        }
    except Exception:
        return None


def _estimate_cost(total_tokens, model="default"):
    inp = int(total_tokens * 0.8)
    out = int(total_tokens * 0.2)
    m   = model.lower()
    rates = MODEL_COSTS.get(m, MODEL_COSTS["default"])
    return round((inp / 1e6) * rates["input"] + (out / 1e6) * rates["output"], 4)


def _load_usage():
    if not os.path.exists(USAGE_FILE):
        return {}
    try:
        with open(USAGE_FILE) as f:
            return json.load(f)
    except Exception:
        return {}


# ── Settings ──────────────────────────────────────────────────────────────────

_DEFAULT_SETTINGS = {
    "auto_open":       True,
    "theme":           "light",
    "daily_budget":    None,   # USD float or null
    "monthly_budget":  None,   # USD float or null
    "last_budget_alert": None, # ISO timestamp of last Mac notification
}


def load_settings():
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE) as f:
                saved = json.load(f)
            return {**_DEFAULT_SETTINGS, **saved}
        except Exception:
            pass
    return dict(_DEFAULT_SETTINGS)


def save_settings(data):
    os.makedirs(os.path.dirname(SETTINGS_FILE), exist_ok=True)
    with open(SETTINGS_FILE, "w") as f:
        json.dump(data, f, indent=2)


# ── Budget alerts ─────────────────────────────────────────────────────────────

def _fire_mac_alert(title, message):
    """Send a Mac notification. Silent if osascript is unavailable."""
    try:
        script = (
            f'display notification "{message}" '
            f'with title "Kode Keeper" subtitle "{title}" sound name "Basso"'
        )
        subprocess.run(["osascript", "-e", script],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                       timeout=3)
    except Exception:
        pass


def _should_alert(settings):
    """Return True if we haven't fired a budget alert in the last hour."""
    last = settings.get("last_budget_alert")
    if not last:
        return True
    try:
        last_dt = datetime.fromisoformat(last)
        return (datetime.now() - last_dt) > timedelta(hours=1)
    except Exception:
        return True


def _check_budgets(day_cost, mo_cost, settings):
    """
    Return a list of budget warning strings and fire Mac alerts if needed.
    Updates last_budget_alert in settings (caller must save).
    """
    warnings = []
    alerted  = False

    daily_budget   = settings.get("daily_budget")
    monthly_budget = settings.get("monthly_budget")

    if daily_budget and day_cost >= daily_budget:
        overage = day_cost - daily_budget
        warnings.append(
            f"💸 Daily budget hit — ${day_cost:.2f} spent (limit ${daily_budget:.2f}, over by ${overage:.2f})"
        )
        if _should_alert(settings):
            _fire_mac_alert(
                "Daily Budget Exceeded",
                f"${day_cost:.2f} spent today (limit ${daily_budget:.2f})"
            )
            alerted = True

    if monthly_budget and mo_cost >= monthly_budget:
        overage = mo_cost - monthly_budget
        warnings.append(
            f"💸 Monthly budget hit — ${mo_cost:.2f} spent (limit ${monthly_budget:.2f}, over by ${overage:.2f})"
        )
        if not alerted and _should_alert(settings):
            _fire_mac_alert(
                "Monthly Budget Exceeded",
                f"${mo_cost:.2f} spent this month (limit ${monthly_budget:.2f})"
            )
            alerted = True

    if alerted:
        settings["last_budget_alert"] = datetime.now().isoformat()
        save_settings(settings)

    return warnings


# ── Warnings ──────────────────────────────────────────────────────────────────

def _build_warnings(projects, system, budget_warnings):
    warnings = list(budget_warnings)

    if system.get("disk_free") is not None and system["disk_free"] < 15:
        warnings.append(f"⚠ Low disk — only {system['disk_free']:.0f} GB free")

    if system.get("ram_pct") is not None and system["ram_pct"] > 85:
        warnings.append(f"⚠ RAM at {system['ram_pct']:.0f}% — crashes possible")

    for p in projects:
        proj_path = os.path.expanduser(p["path"])
        if p.get("needs_env") and os.path.isdir(proj_path) and not os.path.exists(os.path.join(proj_path, ".env")):
            warnings.append(f"⚠ {p['name']} — missing .env")

        g = p.get("git")
        if g and not g["clean"]:
            warnings.append(f"↑ {p['name']} — uncommitted changes")

        if g and g.get("behind", 0) > 0:
            warnings.append(f"↓ {p['name']} — {g['behind']} commit(s) behind origin")

    return warnings


# ── System stats ──────────────────────────────────────────────────────────────

def _get_system_stats():
    stats = {
        "ram_used": None, "ram_total": None, "ram_pct": None,
        "swap_used": None, "swap_total": None, "swap_pct": None,
        "cpu_pct": None, "cpu_temp": None,
        "disk_free": None, "disk_total": None, "disk_pct": None,
        "battery_pct": None, "battery_charging": False, "battery_mins": 0,
    }

    if _HAS_PSUTIL:
        try:
            mem = psutil.virtual_memory()
            stats["ram_used"]  = round(mem.used  / 1e9, 1)
            stats["ram_total"] = round(mem.total / 1e9, 1)
            stats["ram_pct"]   = round(mem.percent, 1)
        except Exception:
            pass

        try:
            sw = psutil.swap_memory()
            stats["swap_used"]  = round(sw.used  / 1e9, 1)
            stats["swap_total"] = round(sw.total / 1e9, 1)
            stats["swap_pct"]   = round(sw.percent, 1)
        except Exception:
            pass

        try:
            stats["cpu_pct"] = round(psutil.cpu_percent(interval=0.2), 1)
        except Exception:
            pass

        try:
            disk = psutil.disk_usage("/")
            stats["disk_free"]  = round(disk.free  / 1e9, 1)
            stats["disk_total"] = round(disk.total / 1e9, 1)
            stats["disk_pct"]   = round(disk.percent, 1)
        except Exception:
            pass

    try:
        tmp = subprocess.check_output(
            ["osx-cpu-temp"], text=True, stderr=subprocess.DEVNULL
        ).strip()
        m = re.search(r'([\d.]+)', tmp)
        if m:
            stats["cpu_temp"] = float(m.group(1))
    except Exception:
        pass

    try:
        out = subprocess.check_output(["pmset", "-g", "batt"], text=True, stderr=subprocess.DEVNULL)
        m = re.search(r'(\d+)%;\s*(\w+);?\s*(?:(\d+):(\d+)\s*remaining)?', out)
        if m:
            stats["battery_pct"]      = int(m.group(1))
            status                    = m.group(2).lower()
            stats["battery_charging"] = status in ("charging", "charged", "finishing")
            if m.group(3) and m.group(4):
                stats["battery_mins"] = int(m.group(3)) * 60 + int(m.group(4))
    except Exception:
        pass

    return stats


# ── Main ──────────────────────────────────────────────────────────────────────

def get_status():
    usage    = _load_usage()
    settings = load_settings()

    model = usage.get("model", "Sonnet 4.6")

    day_tok = usage.get("day",   {}).get("tokens", 0)
    wk_tok  = usage.get("week",  {}).get("tokens", 0)
    mo_tok  = usage.get("month", {}).get("tokens", 0)

    day_cost = _estimate_cost(day_tok,  model)
    wk_cost  = _estimate_cost(wk_tok,   model)
    mo_cost  = _estimate_cost(mo_tok,   model)

    ctx_history = usage.get("ctx_history", [])
    non_zero    = [v for v in ctx_history if v]
    ctx_pct     = non_zero[-1] if non_zero else 0
    ctx_free_k  = usage.get("ctx_free_k", "—")

    projects = []
    for p in PROJECTS:
        online = _port_open(p["port"])
        git    = _git_status(p["path"])
        projects.append({**p, "online": online, "git": git})

    session_start = usage.get("session_start")
    session_mins  = None
    if session_start:
        try:
            started = datetime.fromisoformat(session_start)
            session_mins = int((datetime.now() - started).total_seconds() / 60)
        except Exception:
            pass

    session_tokens = usage.get("last_session_total", 0)
    tok_per_min = None
    if session_mins and session_mins > 0 and session_tokens > 0:
        tok_per_min = round(session_tokens / session_mins)

    system = _get_system_stats()

    budget_warnings = _check_budgets(day_cost, mo_cost, settings)

    return {
        "usage": {
            "day":   {"tokens": day_tok, "cost": day_cost},
            "week":  {"tokens": wk_tok,  "cost": wk_cost},
            "month": {"tokens": mo_tok,  "cost": mo_cost},
        },
        "context": {
            "pct":     round(ctx_pct, 1),
            "history": ctx_history[-60:],
            "free_k":  ctx_free_k,
            "model":   model,
        },
        "budgets": {
            "daily":   settings.get("daily_budget"),
            "monthly": settings.get("monthly_budget"),
        },
        "projects":     projects,
        "session_mins": session_mins,
        "tok_per_min":  tok_per_min,
        "settings":     settings,
        "system":       system,
        "warnings":     _build_warnings(projects, system, budget_warnings),
        "now":          datetime.now().strftime("%H:%M"),
        "today":        str(date.today()),
    }
