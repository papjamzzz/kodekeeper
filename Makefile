.PHONY: setup run stop

setup:
	python3 -m venv venv
	venv/bin/pip install -q -r requirements.txt
	@echo "✅ KodeKeeper ready — run: make run"

run:
	@pkill -f "kodekeeper/app.py" 2>/dev/null || true
	venv/bin/python app.py

stop:
	@pkill -f "kodekeeper/app.py" 2>/dev/null && echo "⛔ Stopped" || echo "Not running"
