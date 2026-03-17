"""
KodeKeeper — Claude Code Mission Control
Port 5560 | 127.0.0.1 only
"""

import os
import threading
import webbrowser
from flask import Flask, jsonify, render_template, request
from tracker import get_status, load_settings, save_settings

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/status")
def status():
    return jsonify(get_status())


@app.route("/api/settings", methods=["GET"])
def settings_get():
    return jsonify(load_settings())


@app.route("/api/settings", methods=["POST"])
def settings_post():
    data = request.get_json(force=True)
    s = load_settings()
    s.update(data)
    save_settings(s)
    return jsonify({"ok": True})


def _open_browser():
    import time
    time.sleep(1.2)
    webbrowser.open("http://localhost:5560")


if __name__ == "__main__":
    print("  🎛  KodeKeeper — Claude Code Mission Control")
    print("  🌐  http://localhost:5560")

    settings = load_settings()
    if settings.get("auto_open", True):
        t = threading.Thread(target=_open_browser, daemon=True)
        t.start()

    app.run(host="127.0.0.1", port=5560, debug=False)
