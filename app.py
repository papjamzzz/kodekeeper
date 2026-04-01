"""
Kode Keeper — local dev entry point.
For pip install, the entry point is `kodekeeper` → kodekeeper.__main__:main
"""
from kodekeeper.server import run

if __name__ == "__main__":
    run()
