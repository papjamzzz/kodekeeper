# Kode Keeper — CLAUDE.md
*Re-entry: Kode Keeper*

## What This Is
Claude Code Mission Control — hardware synthesizer-style dashboard for monitoring
every Claude Code session. Port 5560.

## Status
🟢 Built and running

## Architecture
- `app.py`     — Flask server (port 5560), auto-opens browser on start
- `tracker.py` — Reads ~/.claude/usage/totals.json, checks project ports, git status, estimates cost
- `templates/index.html` — Full dashboard (oscilloscope, VU meters, cost tracker, patch bay, git rack)

## Data Flow
statusline-command.sh → ~/.claude/usage/totals.json → tracker.py → /api/status → dashboard

## Modules
1. **Context Oscilloscope** — animated waveform of context window fill history
2. **Usage VU Meters** — day/week/month token counts as audio-level meters
3. **Cost Tracker** — estimated USD cost per day/week/month
4. **Project Patch Bay** — all 7 apps, live online/offline status, git branch
5. **Git Status Rack** — all repos, branch, clean/dirty, last commit

## Features
- Orange LED power button — toggles auto_open on/off, persists in ~/.claude/usage/kk_settings.json
- Auto-opens browser on start by default
- Polls /api/status every 6 seconds
- Organic warm color palette (warm green, orange-red, no clinical colors)

## Color Palette
- Green: #7ecb52 (sunlit grass)
- Red: #ff5c38 (warm, slight orange hue)
- Orange: #ff8c3a (power LED / Ableton accent)
- Background: #09090d (warm dark)

## Next Steps
- [ ] Update statusline to write ctx_history + model to totals.json
- [ ] GitHub push
- [ ] Add to launcher hub
