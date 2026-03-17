#!/bin/bash
cd "$(dirname "$0")"

if [ ! -d "venv" ]; then
  echo "⚙️  First run — setting up KodeKeeper..."
  python3 -m venv venv
  venv/bin/pip install -q -r requirements.txt
  echo "✅ Ready"
fi

pkill -f "kodekeeper/app.py" 2>/dev/null

echo "🎛  Starting KodeKeeper at http://localhost:5560"
venv/bin/python app.py
