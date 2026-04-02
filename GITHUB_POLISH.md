# Kode Keeper — GitHub Polish Checklist

## Repository Health Badges

Add to top of README.md:

```markdown
[![GitHub stars](https://img.shields.io/github/stars/papjamzzz/kodekeeper?style=flat-square&color=7ecb52)](https://github.com/papjamzzz/kodekeeper)
[![License: MIT](https://img.shields.io/badge/license-MIT-orange.svg?style=flat-square)](LICENSE)
[![Status](https://img.shields.io/badge/status-active-7ecb52?style=flat-square)](https://github.com/papjamzzz/kodekeeper)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-7ecb52?style=flat-square)](https://www.python.org/downloads/)
[![macOS](https://img.shields.io/badge/platform-macOS-7ecb52?style=flat-square)](https://www.apple.com/macos/)
```

---

## GitHub Topics

Add these to the repo settings:

```
claude-code
monitoring
dashboard
ai-development
mission-control
real-time-monitoring
python
flask
```

---

## Repository Description

**Current:** (blank or generic)

**New:**
```
Mission control for Claude Code at scale. Real-time monitoring of context window, token burn, costs, project health, and git status. For algo traders, build-to-spec developers, and AI power users.
```

---

## Documentation Structure

```
kodekeeper/
├── README.md (primary landing page + quick start)
├── SALES.md (full sales pitch + positioning)
├── MARKETING.md (social posts, emails, newsletter pitches)
├── INSTALLATION.md (detailed setup for all scenarios)
├── USER_GUIDE.md (how to use each module)
├── API.md (technical docs for extending/integrating)
├── CHANGELOG.md (version history)
├── LICENSE (MIT)
├── CONTRIBUTING.md (for open-source contributors)
└── static/ (screenshots, gifs, logos)
```

---

## Files to Create/Update

### INSTALLATION.md

```markdown
# Installation Guide

## System Requirements
- macOS 10.15+
- Python 3.9+
- 50MB disk space
- Claude Code running (for data collection)

## Option 1: Quick Start (Recommended)
1. Download [latest release](https://github.com/papjamzzz/kodekeeper/releases)
2. Unzip to `~/kodekeeper`
3. Double-click `launch.command`
4. Browser opens automatically

## Option 2: From Source
```bash
git clone https://github.com/papjamzzz/kodekeeper.git
cd kodekeeper
make setup
make run
```

Visit: http://localhost:5560

## Option 3: Docker (Coming Q2)
```bash
docker run -p 5560:5560 papjamzzz/kodekeeper:latest
```

## Troubleshooting
...
```

---

### USER_GUIDE.md

```markdown
# User Guide

## The Five Modules

### Context Oscilloscope
Shows your context window fill percentage as an animated waveform.
- Green (0-50%): Healthy
- Amber (50-80%): Starting to fill
- Red (80-100%): About to reset

Best practice: Start a new session when you hit amber.

### Usage VU Meters
Shows token counts like an audio mixing board.
- Day: Tokens used today
- Week: Last 7 days
- Month: Last 30 days

Values update every 6 seconds.

[Continue for each module...]
```

---

### API.md

```markdown
# API Documentation

## Extending Kode Keeper

Kode Keeper is built on Flask and exposes a `/api/status` endpoint.

### GET /api/status

Returns:
```json
{
  "usage": {...},
  "context": {...},
  "projects": [...],
  "system": {...},
  "warnings": [...]
}
```

### Adding Custom Process Monitors

Edit `tracker.py` and add to the `PROJECTS` list:

```python
{
    "name": "My Bot",
    "slug": "my-bot",
    "port": None,
    "path": "~/my-project",
    "process": "my_bot.py",
    "log": "~/my-project/bot.log"
}
```

Kode Keeper will:
- Check if `my_bot.py` is running
- Parse `bot.log` for stats
- Display online/offline status

[Continue with integration examples...]
```

---

## GitHub Releases Checklist

When ready to ship:

1. ✅ Update version in `setup.py` or `pyproject.toml`
2. ✅ Update `CHANGELOG.md` with changes
3. ✅ Create git tag: `git tag v1.0.0`
4. ✅ Push: `git push origin v1.0.0`
5. ✅ Create GitHub release with:
   - Release notes (copy from CHANGELOG)
   - Attach `.zip` file
   - Mark as "latest" if appropriate

---

## Repository Settings (GitHub Admin Panel)

1. **Description:** Mission control for Claude Code at scale
2. **Website:** https://creativekonsoles.com/kodekeeper (when ready)
3. **Topics:** claude-code, monitoring, dashboard, ai-development, python, flask
4. **License:** MIT
5. **Branch protection (main):**
   - Require pull request reviews before merging
   - Require status checks to pass
6. **Issues:** Enable
7. **Discussions:** Enable
8. **Wikis:** Disable (use docs instead)
9. **Projects:** Disable (use Issues instead)

---

## Directory Structure (After Polish)

```
papjamzzz/kodekeeper
├── 📄 README.md                  # Primary landing page
├── 📄 SALES.md                   # Full pitch
├── 📄 MARKETING.md               # Social templates
├── 📄 INSTALLATION.md            # Setup guide
├── 📄 USER_GUIDE.md              # How to use
├── 📄 API.md                     # Integration docs
├── 📄 CHANGELOG.md               # Version history
├── 📄 CONTRIBUTING.md            # Contributing guide
├── 📄 LICENSE                    # MIT
├── 📁 kodekeeper/                # Source code
├── 📁 static/                    # Logos, banners, screenshots
│   ├── logo.png                  # 256x256 orange/green
│   ├── banner.png                # 1200x400 hero image
│   ├── screenshot-dashboard.png  # Full dashboard view
│   ├── screenshot-oscilloscope.png
│   ├── screenshot-cost-tracker.png
│   └── screenshot-patch-bay.png
├── setup.py / pyproject.toml     # Package metadata
├── requirements.txt              # Python deps
├── Makefile                      # Setup/run targets
└── .github/
    ├── workflows/
    │   ├── tests.yml             # Run tests on push
    │   └── release.yml           # Auto-release on tag
    ├── ISSUE_TEMPLATE/
    │   ├── bug_report.md
    │   └── feature_request.md
    └── PULL_REQUEST_TEMPLATE.md
```

---

## Screenshot List

Take and add these to `static/`:

1. **Dashboard Overview** — Full screenshot of the main dashboard
2. **Context Oscilloscope** — Close-up of the oscilloscope (animated)
3. **Usage VU Meters** — Close-up of the VU meters
4. **Cost Tracker** — Close-up of the cost tracker
5. **Project Patch Bay** — Close-up of project status
6. **Git Status Rack** — Close-up of git status
7. **Mobile/Responsive** — Screenshot at mobile width (or indicate not supported)

---

## .gitignore (Ensure Complete)

```
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
.venv

# IDE
.vscode/
.idea/
*.swp

# OS
.DS_Store
Thumbs.db

# App
.env
*.json (except if tracked)
```

---

## Contributing Guidelines

Create `CONTRIBUTING.md`:

```markdown
# Contributing to Kode Keeper

We welcome contributions! Here's how:

## Development Setup
```bash
git clone https://github.com/papjamzzz/kodekeeper.git
cd kodekeeper
make setup
make run
```

## Reporting Issues
- Check existing issues first
- Describe your environment (macOS version, Python version)
- Include screenshots if visual
- Include browser console errors if applicable

## Pull Requests
1. Fork the repo
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Make your changes
4. Test locally: `make test`
5. Commit with clear messages
6. Push and create PR with description

## Code Style
- PEP 8 for Python
- Vanilla JS (no framework)
- Comments for complex logic
```

---

## Version Numbering

Current: 1.0.0 (at launch)

Format: `MAJOR.MINOR.PATCH`
- MAJOR: Breaking changes
- MINOR: New features (backward compatible)
- PATCH: Bug fixes

---

## Release Cadence

Suggested:
- Bug fixes: As-needed (patch releases)
- Features: Monthly (minor releases)
- Major updates: Quarterly
