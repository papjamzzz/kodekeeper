<div align="center">
  <img src="static/banner.png" alt="Creative Konsoles — Kode Keeper" width="100%">
</div>

<br>

<div align="center">
  <img src="static/logo.png" alt="Kode Keeper" width="96">
  <h1>Kode Keeper</h1>
  <p><strong>Mission control for every Claude Code session you run.</strong></p>
  <p><sub>Real-time monitoring for AI coding at scale</sub></p>
</div>

<br>

## The Problem

You're running Claude Code. Building. Iterating. But what's actually happening?

- 🤔 How full is your context window?
- 💰 How much have you spent today?
- 🔌 Which of your apps are still live?
- 📦 Is your git clean?

**You're flying blind.**

Kode Keeper answers all of it continuously, without you asking.

---

## The Solution

A hardware synthesizer-inspired dashboard that monitors your AI coding sessions in real time.

### Five Instruments. One Rack.

**Context Oscilloscope** — Animated waveform of your context window fill. Green → amber → red. Tells you when to reset before you lose everything.

**Usage VU Meters** — Day / Week / Month token counts animating like a mixing board. Your actual burn rate, visualized.

**Cost Tracker** — Running USD estimates. Model-aware pricing. Know your costs before the invoice lands.

**Project Patch Bay** — Every app in your stack. Online/offline LED. Git branch. Click to open.

**Git Status Rack** — All your repos. Branch, status, last commit. One glance tells you what's clean and what's dirty.

---

## Why This Matters

### For Algo Traders
Your bots run 24/7. One crash and you're not trading. Kode Keeper tells you instantly if your bot is still breathing.

### For Build-to-Spec Developers
Juggling multiple client projects. Kode Keeper shows which repos are clean, which projects are online, which need attention.

### For Anyone Running Claude Code at Scale
You're spending real money. Stop being surprised by the invoice.

---

## Features

- 🟠 **Orange LED power button** — toggles browser auto-open on/off
- 📡 **Live polling** — refreshes every 6 seconds without a page reload
- 🎛 **Organic color palette** — warm grass greens, no clinical colors
- ⏱ **Session timer** — how long you've been running
- 🔌 **Extensible** — add custom process monitors (Kalshi bots, services, etc.)
- 🎯 **Dead simple setup** — double-click launcher, it works
- 🔒 **Local only** — localhost:5560, your data never leaves your machine

---

## How It Works

```
Claude Code (terminal)
  └── Kode Keeper reads your session state
        • Context window %
        • Token counts (day/week/month)
        • Project status (online/offline)
        • Git repo status
        • Bot health
              ↓
        Real-time dashboard
              ↓
        One glance. Everything.
```

---

## Pricing

| Plan | Cost | Best For |
|------|------|----------|
| **Monthly** | $29/month | Try first, cancel anytime |
| **Annual** | $199/year | Commit & save 3 months |
| **Free Trial** | 7 days, full features | See if it fits your workflow |

**What's included:**
- Unlimited projects to monitor
- Live polling (6-second refresh)
- Cost tracking (model-aware pricing)
- Process monitoring for bots & services
- Git status for all repos
- Email support (24-48h response)

**Coming soon:**
- Cloud sync (Q2)
- Team dashboards (Q3)
- Slack/Discord alerts (Q2)
- Custom integrations ($500 base fee available now)

---

## Quick Start

### Option 1 — Double-click (Mac)
```
1. Download kodekeeper
2. Double-click launch.command
3. Browser opens automatically
```

### Option 2 — Terminal
```bash
git clone https://github.com/papjamzzz/kodekeeper.git
cd kodekeeper
make setup
make run
# Opens http://localhost:5560
```

---

## Requirements

- **macOS** (Windows/Linux coming Q2 2026)
- **Python 3.9+**
- **Claude Code running** (for context data)

---

## Color Language

| Color | Meaning |
|-------|---------|
| 🟢 Grass green `#7ecb52` | Healthy, clean, online |
| 🟠 Orange `#ff8c3a` | Active, power, alert |
| 🟡 Amber `#f5c842` | Watch — filling up, uncommitted |
| 🔴 Warm red `#ff5c38` | Alert — reset now, stop loss |

Organic. Modern. No clinical colors.

---

## FAQ

**Can I modify my Claude Code setup?**
No. Kode Keeper reads existing data files. No changes needed.

**Can I monitor other processes/bots?**
Yes. Process-based monitoring is built in. We monitor Kalshi bots live.

**Is my data synced to the cloud?**
No. Localhost only (127.0.0.1:5560). Your data never leaves your machine.

**What if Claude Code isn't running?**
The dashboard still shows historical data and any running processes. Useful even when idle.

**Do you store my usage data?**
No. Everything stays local. We never see your tokens, costs, or projects.

---

## Stack

- Python + Flask (localhost:5560)
- Vanilla JS — no frameworks
- Canvas API for oscilloscope
- JetBrains Mono + Inter

---

## Part of Creative Konsoles

Kode Keeper is one of six instruments built for Claude Code power users at scale.

| Tool | What It Does | Port |
|------|-------------|------|
| **Launcher** | Hub for all apps | 5554 |
| **Kalshi Edge** | Prediction market edge detection | 5555 |
| **StreamFader** | Content ranker | 5556 |
| **TrackTracks** | Ableton CPU per-track | 5557 |
| **DAW Doctor** | Ableton diagnostics | 5558 |
| **KK Trader** | Autonomous trading bot | 5559 |
| **Kode Keeper** | Claude Code mission control | 5560 |

All built with Claude Code. All designed for one thing: **if you're running AI at scale, you need real instruments.**

---

## Get Started

### [👉 Buy Kode Keeper — $29/month or $199/year](https://checkout.creative-konsoles.com/kodekeeper)

### [📥 Free 7-Day Trial](https://github.com/papjamzzz/kodekeeper/releases)

### [💬 Support](mailto:support@creativekonsoles.com)

---

## Built by

[**Creative Konsoles**](https://creativekonsoles.com) — *tools built using thought*

**GitHub:** [@papjamzzz](https://github.com/papjamzzz)
**Support:** support@creativekonsoles.com
**Website:** [creativekonsoles.com](https://creativekonsoles.com)

---

*Built with Claude Code.*
