"""
KodeKeeper — Flask server
Port 5560 | 127.0.0.1 only
Works both as `python server.py` (repo) and `kodekeeper start` (pip install).
"""

import os
import signal
import socket
import subprocess
import threading
import webbrowser
from flask import Flask, jsonify, render_template, request

# Absolute paths so Flask finds templates/static when pip-installed
_PKG = os.path.dirname(os.path.abspath(__file__))

app = Flask(
    __name__,
    template_folder=os.path.join(_PKG, "templates"),
    static_folder=os.path.join(_PKG, "static"),
)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/status")
def api_status():
    from kodekeeper.tracker import get_status
    return jsonify(get_status())


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
