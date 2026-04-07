"""
KodeKeeper — Flask server
Port 5560 | 127.0.0.1 only
Works both as `python server.py` (repo) and `kodekeeper start` (pip install).
"""

import json as _json
import os
import signal
import socket
import subprocess
import threading
import urllib.request
import webbrowser
from datetime import datetime, date
from flask import Flask, Response, jsonify, render_template, request, stream_with_context
from dotenv import load_dotenv

load_dotenv()

ANTHROPIC_KEY = os.getenv("ANTHROPIC_API_KEY", "")

# Absolute paths so Flask finds templates/static when pip-installed
_PKG = os.path.dirname(os.path.abspath(__file__))

app = Flask(
    __name__,
    template_folder=os.path.join(_PKG, "templates"),
    static_folder=os.path.join(_PKG, "static"),
)

# ── Visit counter ─────────────────────────────────────────────────────────────
_VISITS_FILE = os.path.expanduser("~/.claude/usage/kk_visits.json")
_visits_lock = threading.Lock()

def _load_visits():
    if os.path.exists(_VISITS_FILE):
        try:
            with open(_VISITS_FILE) as f:
                return _json.load(f)
        except Exception:
            pass
    return {"total": 0, "today": 0, "today_date": "", "by_day": {}}

def _record_visit():
    with _visits_lock:
        v = _load_visits()
        today = str(date.today())
        if v.get("today_date") != today:
            v["today"] = 0
            v["today_date"] = today
        v["total"] = v.get("total", 0) + 1
        v["today"] = v.get("today", 0) + 1
        v["by_day"][today] = v["by_day"].get(today, 0) + 1
        os.makedirs(os.path.dirname(_VISITS_FILE), exist_ok=True)
        with open(_VISITS_FILE, "w") as f:
            _json.dump(v, f)
    return v


@app.route("/")
def index():
    _record_visit()
    return render_template("index.html")


@app.route("/api/visits")
def api_visits():
    return jsonify(_load_visits())


@app.route("/api/status")
def api_status():
    from kodekeeper.tracker import get_status
    data = get_status()
    data["visits"] = _load_visits()
    return jsonify(data)


@app.route("/api/settings", methods=["GET"])
def settings_get():
    from kodekeeper.tracker import load_settings
    return jsonify(load_settings())


@app.route("/api/settings", methods=["POST"])
def settings_post():
    from kodekeeper.tracker import load_settings, save_settings
    data = request.get_json(force=True)
    s = load_settings()
    s.update(data)
    save_settings(s)
    return jsonify({"ok": True})


def _project_by_slug(slug):
    from kodekeeper.tracker import PROJECTS
    return next((p for p in PROJECTS if p["slug"] == slug), None)


def _pids_on_port(port):
    """Return list of PIDs listening on the given port."""
    try:
        out = subprocess.check_output(
            ["lsof", "-ti", f":{port}"], stderr=subprocess.DEVNULL, text=True
        )
        return [int(p) for p in out.strip().split() if p.strip()]
    except Exception:
        return []


# ── Project action routes ─────────────────────────────────────────────────────

@app.route("/api/project/<slug>/logs")
def project_logs(slug):
    p = _project_by_slug(slug)
    if not p:
        return jsonify({"error": "not found"}), 404
    path = os.path.expanduser(p["path"])
    # Check common log file locations
    candidates = [
        os.path.join(path, "app.log"),
        os.path.join(path, "server.log"),
        os.path.join(path, "logs", "app.log"),
        os.path.expanduser(f"~/.claude/logs/{slug}.log"),
    ]
    log_file = next((f for f in candidates if os.path.exists(f)), None)
    if not log_file:
        return jsonify({"lines": [], "source": None, "note": "No log file found. Run the server with output redirected to app.log."})
    try:
        out = subprocess.check_output(
            ["tail", "-n", "80", log_file], text=True, stderr=subprocess.DEVNULL
        )
        lines = out.splitlines()
        return jsonify({"lines": lines, "source": log_file})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/project/<slug>/open-folder", methods=["POST"])
def project_open_folder(slug):
    p = _project_by_slug(slug)
    if not p:
        return jsonify({"error": "not found"}), 404
    path = os.path.expanduser(p["path"])
    try:
        subprocess.Popen(["open", path])
        return jsonify({"ok": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/project/<slug>/open-terminal", methods=["POST"])
def project_open_terminal(slug):
    p = _project_by_slug(slug)
    if not p:
        return jsonify({"error": "not found"}), 404
    path = os.path.expanduser(p["path"])
    script = f'tell application "Terminal" to do script "cd {path}"'
    try:
        subprocess.Popen(["osascript", "-e", script])
        return jsonify({"ok": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/project/<slug>/assets")
def project_assets(slug):
    """List image/brand files in the project's assets folder."""
    p = _project_by_slug(slug)
    if not p:
        return jsonify({"error": "not found"}), 404
    assets_path = os.path.expanduser(p.get("assets", ""))
    if not assets_path or not os.path.isdir(assets_path):
        return jsonify({"files": [], "path": None, "note": "No assets folder found."})
    IMAGE_EXT = {".png", ".jpg", ".jpeg", ".svg", ".gif", ".webp", ".ico"}
    files = []
    for f in sorted(os.listdir(assets_path)):
        ext = os.path.splitext(f)[1].lower()
        if ext in IMAGE_EXT:
            files.append({"name": f, "path": os.path.join(assets_path, f)})
    return jsonify({"files": files, "path": assets_path})


@app.route("/api/project/<slug>/assets/open-folder", methods=["POST"])
def project_assets_open_folder(slug):
    p = _project_by_slug(slug)
    if not p:
        return jsonify({"error": "not found"}), 404
    assets_path = os.path.expanduser(p.get("assets", ""))
    # Fall back to project root if no assets folder
    if not assets_path or not os.path.isdir(assets_path):
        assets_path = os.path.expanduser(p["path"])
    try:
        subprocess.Popen(["open", assets_path])
        return jsonify({"ok": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/project/<slug>/assets/reveal", methods=["POST"])
def project_assets_reveal(slug):
    """Reveal a specific file in Finder."""
    p = _project_by_slug(slug)
    if not p:
        return jsonify({"error": "not found"}), 404
    data = request.get_json(force=True)
    file_path = data.get("path", "")
    if not file_path or not os.path.exists(file_path):
        return jsonify({"error": "file not found"}), 404
    try:
        subprocess.Popen(["open", "-R", file_path])
        return jsonify({"ok": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/project/<slug>/inject-env", methods=["POST"])
def project_inject_env(slug):
    """Open Terminal with bwdotenv command pre-typed — user runs it themselves."""
    p = _project_by_slug(slug)
    if not p:
        return jsonify({"error": "not found"}), 404
    bw_item = p.get("bw_item")
    if not bw_item:
        return jsonify({"error": "no Bitwarden item mapped for this project"}), 400
    env_path = os.path.join(os.path.expanduser(p["path"]), ".env")
    cmd = f'bwunlock && bwdotenv "{bw_item}" {env_path}'
    script = f'tell application "Terminal" to do script "{cmd}"'
    try:
        subprocess.Popen(["osascript", "-e", script])
        return jsonify({"ok": True, "cmd": cmd})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/project/<slug>/restart", methods=["POST"])
def project_restart(slug):
    p = _project_by_slug(slug)
    if not p:
        return jsonify({"error": "not found"}), 404
    path = os.path.expanduser(p["path"])
    port = p["port"]

    # Kill existing process on port
    killed = []
    for pid in _pids_on_port(port):
        try:
            os.kill(pid, signal.SIGTERM)
            killed.append(pid)
        except Exception:
            pass

    # Start in background via make run, fall back to python3 app.py
    makefile = os.path.join(path, "Makefile")
    if os.path.exists(makefile):
        cmd = ["make", "-C", path, "run"]
    else:
        cmd = ["python3", os.path.join(path, "app.py")]

    log_path = os.path.join(path, "app.log")
    try:
        with open(log_path, "a") as log_f:
            subprocess.Popen(
                cmd, stdout=log_f, stderr=log_f,
                cwd=path, start_new_session=True
            )
        return jsonify({"ok": True, "killed": killed, "log": log_path})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ── Call on Claude routes ─────────────────────────────────────────────────────

def _claude_system(status):
    """Build a system prompt from live dashboard state."""
    projects = status.get("projects", [])
    ctx_pct  = status.get("context", {}).get("pct", 0)

    proj_lines = "\n".join(
        f"  - {p['name']}: path={p.get('path','?')} port={p.get('port','—')} "
        f"{'online' if p.get('online') else 'OFFLINE'} "
        f"{'dirty' if not p.get('git', {}).get('clean', True) else 'clean'}"
        for p in projects
    )

    return f"""You are Call on Claude — an AI assistant embedded directly in Kode Keeper, \
a developer mission control dashboard. You have real-time visibility into the developer's \
projects and can take action.

LIVE STATE:
- Context window: {ctx_pct}% used
- Projects:
{proj_lines}

When you need to run a shell command (git commit, server restart, run tests, etc.), \
embed it in your response using this exact format — the dashboard will extract it and \
offer to execute it:

<execute>
{{"command": "shell command here", "description": "one line describing what this does"}}
</execute>

Rules for <execute> blocks:
- Use absolute-style paths starting with ~ (e.g. cd ~/kalshi-edge && ...)
- Chain steps with && so they fail fast
- For git commits, generate a short meaningful commit message based on context
- Never put secrets or passwords in commands
- You may include multiple <execute> blocks if needed

Be direct and concise. The developer is in flow — don't pad responses."""


@app.route("/api/search", methods=["POST"])
def code_search():
    """Grep across project source files for a query string."""
    data  = request.get_json(force=True) or {}
    query = data.get("query", "").strip()
    slug  = data.get("slug", "").strip()
    if len(query) < 2:
        return jsonify({"error": "query too short"}), 400

    from kodekeeper.tracker import PROJECTS
    targets = [p for p in PROJECTS if not slug or p["slug"] == slug]

    results = []
    for p in targets:
        path = os.path.expanduser(p["path"])
        if not os.path.isdir(path):
            continue
        try:
            out = subprocess.check_output(
                ["grep", "-rn", "--include=*.py", "--include=*.html",
                 "--include=*.js", "--include=*.css", "--include=*.md",
                 "-m", "8", query, path],
                text=True, stderr=subprocess.DEVNULL
            )
            for line in out.splitlines()[:20]:
                parts = line.split(":", 2)
                if len(parts) >= 3:
                    file_rel = os.path.relpath(parts[0], path)
                    results.append({
                        "project": p["name"],
                        "file": file_rel,
                        "line": parts[1],
                        "text": parts[2].strip()
                    })
        except Exception:
            pass

    return jsonify({"results": results[:60], "query": query})


@app.route("/api/claude/suggestions", methods=["POST"])
def claude_suggestions():
    """Return 3 context-aware action suggestions from Claude Haiku (fast)."""
    if not ANTHROPIC_KEY:
        return jsonify({"suggestions": [
            {"label": "Commit all dirty repos to GitHub", "prompt": "commit all dirty repositories to GitHub with an auto-generated commit message", "type": "execute"},
            {"label": "Why are projects offline?",        "prompt": "which projects are offline and what's likely causing it?",                        "type": "ask"},
            {"label": "Context window check",             "prompt": "how is my context window usage looking and should I start a fresh session?",      "type": "ask"},
        ]})

    from kodekeeper.tracker import get_status
    status   = get_status()
    projects = status.get("projects", [])
    dirty    = [p["name"] for p in projects if not p.get("git", {}).get("clean", True)]
    offline  = [p["name"] for p in projects if not p.get("online")]
    ctx_pct  = status.get("context", {}).get("pct", 0)

    state_summary = (
        f"Context: {ctx_pct}% used. "
        f"Offline: {', '.join(offline) or 'none'}. "
        f"Dirty repos: {', '.join(dirty) or 'none'}. "
        f"Projects: {', '.join(p['name'] for p in projects[:6])}."
    )

    prompt = (
        f"Developer dashboard state: {state_summary}\n\n"
        "Generate exactly 3 short, specific, actionable suggestions for right now. "
        "Return ONLY a JSON array — no markdown, no prose.\n"
        'Each item: {"label":"short label","prompt":"full instruction","type":"execute|ask"}\n'
        "Use type execute for git/server/shell actions, ask for analysis/questions.\n"
        "JSON only:"
    )

    try:
        payload = _json.dumps({
            "model": "claude-haiku-4-5-20251001",
            "max_tokens": 350,
            "messages": [{"role": "user", "content": prompt}]
        }).encode()
        req = urllib.request.Request(
            "https://api.anthropic.com/v1/messages",
            data=payload,
            headers={"x-api-key": ANTHROPIC_KEY, "anthropic-version": "2023-06-01",
                     "content-type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=12) as resp:
            data = _json.loads(resp.read())
            raw  = data["content"][0]["text"].strip()
            # Strip markdown fences if present
            if "```" in raw:
                raw = raw.split("```")[1]
                if raw.startswith("json"):
                    raw = raw[4:]
            suggestions = _json.loads(raw.strip())
            return jsonify({"suggestions": suggestions[:3]})
    except Exception as exc:
        print(f"[COC suggestions] {exc}")
        return jsonify({"suggestions": [
            {"label": f"Commit {dirty[0]} to GitHub" if dirty else "Check git status", "prompt": f"commit {dirty[0]} to github" if dirty else "show git status for all projects", "type": "execute"},
            {"label": "Why is something offline?" if offline else "Open project terminal", "prompt": f"why is {offline[0]} offline?" if offline else "open a terminal for kalshi-edge", "type": "ask"},
            {"label": "Analyze context usage", "prompt": "how is my context window usage and should I start fresh?", "type": "ask"},
        ]})


@app.route("/api/claude/ask", methods=["POST"])
def claude_ask():
    """Stream a Claude Sonnet response for any developer prompt."""
    if not ANTHROPIC_KEY:
        def _no_key():
            yield f"data: {_json.dumps({'text': 'ANTHROPIC_API_KEY not set in .env'})}\n\n"
            yield "data: [DONE]\n\n"
        return Response(stream_with_context(_no_key()), content_type="text/event-stream",
                        headers={"X-Accel-Buffering": "no", "Cache-Control": "no-cache"})

    data   = request.get_json(force=True) or {}
    prompt = data.get("prompt", "").strip()
    if not prompt:
        return jsonify({"error": "empty prompt"}), 400

    from kodekeeper.tracker import get_status
    status = get_status()
    system = _claude_system(status)

    def _stream():
        payload = _json.dumps({
            "model": "claude-sonnet-4-5-20251101",
            "max_tokens": 700,
            "stream": True,
            "system": system,
            "messages": [{"role": "user", "content": prompt}]
        }).encode()
        req = urllib.request.Request(
            "https://api.anthropic.com/v1/messages",
            data=payload,
            headers={"x-api-key": ANTHROPIC_KEY, "anthropic-version": "2023-06-01",
                     "content-type": "application/json"},
        )
        try:
            with urllib.request.urlopen(req, timeout=45) as resp:
                for raw_line in resp:
                    line = raw_line.decode().strip()
                    if not line.startswith("data: "):
                        continue
                    chunk = line[6:]
                    if chunk == "[DONE]":
                        break
                    try:
                        ev = _json.loads(chunk)
                        if ev.get("type") == "content_block_delta":
                            text = ev.get("delta", {}).get("text", "")
                            if text:
                                yield f"data: {_json.dumps({'text': text})}\n\n"
                    except Exception:
                        pass
        except Exception as exc:
            yield f"data: {_json.dumps({'error': str(exc)})}\n\n"
        yield "data: [DONE]\n\n"

    return Response(stream_with_context(_stream()), content_type="text/event-stream",
                    headers={"X-Accel-Buffering": "no", "Cache-Control": "no-cache"})


@app.route("/api/claude/execute", methods=["POST"])
def claude_execute():
    """Execute a shell command and stream its output line by line."""
    data    = request.get_json(force=True) or {}
    command = data.get("command", "").strip()
    if not command:
        return jsonify({"error": "no command"}), 400

    # Block genuinely destructive patterns
    _blocked = ["rm -rf /", "rm -rf ~", "sudo rm", "mkfs", "dd if=/dev/zero",
                "> /dev/sd", "chmod -R 777 /", ":(){ :|:& };:"]
    for b in _blocked:
        if b in command:
            return jsonify({"error": f"Blocked for safety: '{b}'"}), 403

    def _stream():
        try:
            proc = subprocess.Popen(
                command, shell=True,
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                text=True, bufsize=1,
                cwd=os.path.expanduser("~"),
            )
            for line in iter(proc.stdout.readline, ""):
                yield f"data: {_json.dumps({'line': line.rstrip()})}\n\n"
            proc.wait()
            yield f"data: {_json.dumps({'done': True, 'exit_code': proc.returncode})}\n\n"
        except Exception as exc:
            yield f"data: {_json.dumps({'error': str(exc)})}\n\n"

    return Response(stream_with_context(_stream()), content_type="text/event-stream",
                    headers={"X-Accel-Buffering": "no", "Cache-Control": "no-cache"})


def _open_browser():
    import time
    time.sleep(1.2)
    webbrowser.open("http://localhost:5560")


def run():
    print("  🎛  Kode Keeper — Claude Code Mission Control")
    print("  🌐  http://localhost:5560")

    from kodekeeper.tracker import load_settings
    settings = load_settings()
    if settings.get("auto_open", True):
        t = threading.Thread(target=_open_browser, daemon=True)
        t.start()

    app.run(host="127.0.0.1", port=5560, debug=False)


if __name__ == "__main__":
    run()
