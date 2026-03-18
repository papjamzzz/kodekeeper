"""
Kode Keeper — Terminal Monitor
Runs full-time in a dedicated terminal window.
Refreshes every 5 seconds. CTRL+C to quit.
"""

import json
import os
import socket
import subprocess
import time
from datetime import datetime, date

USAGE_FILE = os.path.expanduser("~/.claude/usage/totals.json")

PROJECTS = [
    {"name": "Launcher",    "port": 5554, "path": "~/launcher"},
    {"name": "Kalshi Edge", "port": 5555, "path": "~/kalshi-edge"},
    {"name": "StreamFader", "port": 5556, "path": "~/streamfader"},
    {"name": "TrackTracks", "port": 5557, "path": "~/track_cpu_monitor"},
    {"name": "DAW Doctor",  "port": 5558, "path": "~/ableton-diagnostics"},
    {"name": "KK Trader",   "port": 5559, "path": "~/kalshi-trader"},
    {"name": "Kode Keeper", "port": 5560, "path": "~/kodekeeper"},
]

# ── ANSI ──────────────────────────────────────────────────────────────────────

RESET  = "\033[0m"
BOLD   = "\033[1m"
DIM    = "\033[2m"

GREEN  = "\033[38;2;88;222;131m"
GREEN2 = "\033[38;2;105;240;155m"
AMBER  = "\033[38;2;218;142;32m"
RED    = "\033[38;2;205;78;20m"
PURPLE = "\033[38;2;157;127;255m"
GREY   = "\033[38;2;74;82;112m"
WHITE  = "\033[38;2;200;207;224m"
BGBK   = "\033[38;2;30;34;48m"   # border color

CLEAR  = "\033[2J\033[H"
HIDE_CURSOR = "\033[?25l"
SHOW_CURSOR = "\033[?25h"


# ── Helpers ───────────────────────────────────────────────────────────────────

def fmt_k(n):
    n = int(n or 0)
    if n >= 1_000_000: return f"{n/1_000_000:.1f}M"
    if n >= 1_000:     return f"{n//1000}k"
    return str(n)

def fmt_cost(v):
    v = float(v or 0)
    if v == 0:    return "$0.00"
    if v < 0.01:  return "<$0.01"
    return f"${v:.2f}"

def fmt_mins(m):
    if not m and m != 0: return "—"
    if m < 60: return f"{m}m"
    h, r = divmod(m, 60)
    return f"{h}h {r}m" if r else f"{h}h"

def port_open(port):
    try:
        with socket.create_connection(("127.0.0.1", port), timeout=0.3):
            return True
    except:
        return False

def git_info(path):
    full = os.path.expanduser(path)
    if not os.path.isdir(full):
        return None
    try:
        branch = subprocess.check_output(
            ["git", "-C", full, "symbolic-ref", "--short", "HEAD"],
            stderr=subprocess.DEVNULL).decode().strip()
        dirty = subprocess.check_output(
            ["git", "-C", full, "status", "--porcelain"],
            stderr=subprocess.DEVNULL).decode().strip()
        return {"branch": branch, "clean": len(dirty) == 0}
    except:
        return None

def ascii_bar(pct, width=10):
    filled = round(pct / 10)
    filled = max(0, min(width, filled))
    return "█" * filled + "░" * (width - filled)

def health(pct):
    if pct >= 85: return RED,    "!! RESET"
    if pct >= 70: return AMBER,  "!! FILL"
    if pct >= 50: return AMBER,  "WATCH"
    return GREEN, "OK"

def load_usage():
    try:
        with open(USAGE_FILE) as f:
            return json.load(f)
    except:
        return {}

def pipe():
    return f"  {GREY}|{RESET}  "


# ── Render ────────────────────────────────────────────────────────────────────

def render():
    usage    = load_usage()
    now      = datetime.now()
    time_str = now.strftime("%H:%M:%S")

    ctx_pct   = float((usage.get("ctx_history") or [0])[-1])
    ctx_free  = usage.get("ctx_free_k", "—")
    model     = usage.get("model", "—")

    day_tok   = usage.get("day",   {}).get("tokens", 0)
    wk_tok    = usage.get("week",  {}).get("tokens", 0)
    mo_tok    = usage.get("month", {}).get("tokens", 0)

    # Estimate cost (Sonnet 4.6: 80% input $3/M, 20% output $15/M)
    def cost(tok):
        return (tok * 0.8 / 1e6 * 3.0) + (tok * 0.2 / 1e6 * 15.0)

    session_start = usage.get("session_start")
    session_mins  = None
    if session_start:
        try:
            started      = datetime.fromisoformat(session_start)
            session_mins = int((now - started).total_seconds() / 60)
        except:
            pass

    hcolor, hlabel = health(ctx_pct)
    bar            = ascii_bar(ctx_pct)

    # Check projects
    proj_status = []
    for p in PROJECTS:
        online = port_open(p["port"])
        git    = git_info(p["path"])
        proj_status.append({**p, "online": online, "git": git})

    online_count = sum(1 for p in proj_status if p["online"])

    # ── Build output ──────────────────────────────────────────────────────────
    lines = []

    W   = 83
    SEP = f"{GREY}{'─' * W}{RESET}"
    TOP = f"{GREY}╭{'─' * W}╮{RESET}"
    BOT = f"{GREY}╰{'─' * W}╯{RESET}"
    MID = f"{GREY}├{'─' * W}┤{RESET}"

    def row(content):
        # Strip ANSI for length calculation
        import re
        clean = re.sub(r'\033\[[0-9;]*m', '', content)
        pad   = W - len(clean) - 2
        return f"{GREY}│{RESET} {content}{' ' * max(0, pad)} {GREY}│{RESET}"

    # ── Header ────────────────────────────────────────────────────────────────
    lines.append("")
    lines.append(f"  {TOP}")
    lines.append("  " + row(
        f"{BOLD}{GREEN}KODE KEEPER{RESET}  "
        f"{GREY}·  Claude Code Mission Control  ·  Creative Konsoles{RESET}"
        f"{'  '}{GREY}{time_str}{RESET}"
    ))
    lines.append(f"  {MID}")

    # ── Context ───────────────────────────────────────────────────────────────
    lines.append("  " + row(
        f"{hcolor}{BOLD}[{hlabel}]{RESET}  "
        f"{hcolor}{bar}{RESET}  "
        f"{hcolor}{BOLD}{ctx_pct:.0f}%{RESET}"
        f"  {GREY}│{RESET}  {GREY}{ctx_free} free{RESET}"
        f"  {GREY}│{RESET}  {WHITE}{model}{RESET}"
        f"  {GREY}│{RESET}  {GREY}session {fmt_mins(session_mins)}{RESET}"
    ))
    lines.append(f"  {MID}")

    # ── Usage ─────────────────────────────────────────────────────────────────
    lines.append("  " + row(
        f"{GREY}tokens{RESET}   "
        f"{GREY}day {RESET}{GREEN}{BOLD}{fmt_k(day_tok)}{RESET}"
        f"  {GREY}│{RESET}  "
        f"{GREY}wk {RESET}{PURPLE}{BOLD}{fmt_k(wk_tok)}{RESET}"
        f"  {GREY}│{RESET}  "
        f"{GREY}mo {RESET}{AMBER}{BOLD}{fmt_k(mo_tok)}{RESET}"
    ))
    lines.append("  " + row(
        f"{GREY}cost{RESET}     "
        f"{GREY}day {RESET}{GREEN}{fmt_cost(cost(day_tok))}{RESET}"
        f"  {GREY}│{RESET}  "
        f"{GREY}wk {RESET}{PURPLE}{fmt_cost(cost(wk_tok))}{RESET}"
        f"  {GREY}│{RESET}  "
        f"{GREY}mo {RESET}{AMBER}{fmt_cost(cost(mo_tok))}{RESET}"
        f"  {GREY}· Sonnet 4.6 · $3/M in · $15/M out{RESET}"
    ))
    lines.append(f"  {MID}")

    # ── Projects ──────────────────────────────────────────────────────────────
    online_str = f"{GREEN}{online_count} online{RESET}" if online_count else f"{GREY}0 online{RESET}"
    lines.append("  " + row(
        f"{GREY}projects  {RESET}{online_str}{GREY} / {len(proj_status)} total{RESET}"
    ))
    lines.append("  " + row(""))

    for p in proj_status:
        led    = f"{GREEN}●{RESET}" if p["online"] else f"{GREY}○{RESET}"
        name   = f"{WHITE}{BOLD}{p['name']:<13}{RESET}"
        port   = f"{GREY}:{p['port']}{RESET}"
        g      = p["git"]
        branch = f"{PURPLE}⎇ {g['branch']}{RESET}" if g else f"{GREY}—{RESET}"
        state  = (f"{GREEN}✓ clean{RESET}" if g["clean"] else f"{AMBER}● dirty{RESET}") if g else f"{GREY}—{RESET}"
        status = f"{GREEN}online{RESET}" if p["online"] else f"{GREY}offline{RESET}"
        lines.append("  " + row(
            f"  {led}  {name}  {port}    {branch}    {state}    {status}"
        ))

    lines.append(f"  {BOT}")
    lines.append(f"  {GREY}  ctrl+c to quit  ·  refreshes every 5s{RESET}")
    lines.append("")

    return "\n".join(lines)


# ── Main loop ─────────────────────────────────────────────────────────────────

def main():
    print(HIDE_CURSOR, end="", flush=True)
    try:
        while True:
            output = render()
            print(CLEAR + output, flush=True)
            time.sleep(5)
    except KeyboardInterrupt:
        print(SHOW_CURSOR)
        print("\n  Kode Keeper monitor stopped.\n")

if __name__ == "__main__":
    main()
