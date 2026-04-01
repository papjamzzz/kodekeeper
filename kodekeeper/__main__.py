"""
KodeKeeper CLI
  kodekeeper          → start the dashboard (default)
  kodekeeper start    → start the dashboard
  kodekeeper setup    → install Claude Code statusline hook
  kodekeeper status   → print current status to terminal
"""

import argparse
import json
import os
import shutil


def cmd_start():
    from kodekeeper.server import run
    run()


def cmd_setup():
    home       = os.path.expanduser("~")
    claude_dir = os.path.join(home, ".claude")
    os.makedirs(claude_dir, exist_ok=True)

    # Copy statusline script
    pkg_dir = os.path.dirname(os.path.abspath(__file__))
    src_sh  = os.path.join(pkg_dir, "data", "statusline-command.sh")
    dst_sh  = os.path.join(claude_dir, "statusline-command.sh")
    shutil.copy2(src_sh, dst_sh)
    os.chmod(dst_sh, 0o755)
    print(f"  ✓ Statusline script → {dst_sh}")

    # Patch ~/.claude/settings.json
    settings_file = os.path.join(claude_dir, "settings.json")
    settings = {}
    if os.path.exists(settings_file):
        try:
            with open(settings_file) as f:
                settings = json.load(f)
        except Exception:
            pass

    settings["statusLine"] = {
        "type":    "command",
        "command": f"bash {dst_sh}",
    }
    with open(settings_file, "w") as f:
        json.dump(settings, f, indent=4)
    print(f"  ✓ Claude settings.json updated")
    print(f"\n  Setup complete. Run `kodekeeper start` to launch the dashboard.")


def cmd_status():
    from kodekeeper.tracker import get_status
    s   = get_status()
    ctx = s["context"]
    u   = s["usage"]
    print(f"\n  Kode Keeper — current status")
    print(f"  Model:  {ctx['model']}")
    print(f"  Window: {100 - ctx['pct']:.0f}% remaining  ({ctx['free_k']} free)")
    print(f"  Day:    {u['day']['tokens']:,} tok   ${u['day']['cost']:.4f}")
    print(f"  Week:   {u['week']['tokens']:,} tok   ${u['week']['cost']:.4f}")
    print(f"  Month:  {u['month']['tokens']:,} tok   ${u['month']['cost']:.4f}")
    if s.get("warnings"):
        print()
        for w in s["warnings"]:
            print(f"  {w}")
    print()


def main():
    parser = argparse.ArgumentParser(
        prog="kodekeeper",
        description="Kode Keeper — Claude Code Mission Control",
    )
    sub = parser.add_subparsers(dest="cmd")
    sub.add_parser("start",  help="Start the dashboard server (default)")
    sub.add_parser("setup",  help="Install the Claude Code statusline hook")
    sub.add_parser("status", help="Print current status to terminal")

    args = parser.parse_args()

    if args.cmd == "setup":
        cmd_setup()
    elif args.cmd == "status":
        cmd_status()
    else:
        cmd_start()


if __name__ == "__main__":
    main()
