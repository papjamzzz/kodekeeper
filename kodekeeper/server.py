"""
KodeKeeper — Flask server
Port 5560 | 127.0.0.1 only
Works both as `python server.py` (repo) and `kodekeeper start` (pip install).
"""

import os
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
