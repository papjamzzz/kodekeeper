# Kode Keeper — Sales Page

## Headline
**Stop flying blind in Claude Code. Mission control for your AI sessions.**

You're running Claude Code. Building. Iterating. But what's actually happening?
- How full is your context window?
- How much have you spent today?
- Which of your 7 apps are still live?
- Did someone commit without testing?

Kode Keeper answers all of it, continuously, without you asking.

---

## The Problem (For Your Customer)

### You're a Claude Code Power User
You run multiple AI sessions simultaneously. Kalshi trading bots. Build-to-spec projects. Research agents. Each one burns tokens, fills context, costs money.

**But you're blind to it.**

You don't know:
- When your context window is about to fill (and reset everything)
- Your actual token burn rate until the bill arrives
- Whether your trading bots are still running or crashed silently
- If your repos have uncommitted changes before you push
- Which projects are online and which have gone dark

You open a terminal, tail a log, check a git status, open 3 different browser tabs. Every session.

**Kode Keeper eliminates that friction.**

---

## The Solution

A hardware synthesizer-inspired dashboard. Real-time. Always on. One glance tells you everything.

### The Five Modules

**Context Oscilloscope**
Animated waveform of your context window fill over time. Color shifts from grass green → amber → warm red as the window fills. Tells you when to start a new session before you hit the wall.

**Usage VU Meters**
Three vertical bars — Day / Week / Month. Token counts animate like a mixing board. You'll see your burn rate in real-time, not in your invoice.

**Cost Tracker**
Running USD estimates for today, this week, this month. Model-aware pricing (Opus vs Sonnet costs are different). You know your burn before you commit to a session.

**Project Patch Bay**
Every app in your stack laid out like a modular patch bay. Online/offline LED per port. Git branch and clean/dirty state per project. Click to open any of them.

**Git Status Rack**
All your repos. Branch, status, last commit. One row per repo. Green dot = clean. Amber = uncommitted changes.

---

## Why This Matters

### For Algo Traders (Kalshi, etc.)
Your trading bots run 24/7. One crash and you're not trading. One context reset and your session state is lost. Kode Keeper tells you instantly if your bot is still breathing.

### For Build-to-Spec Developers
You're juggling multiple client projects. You need to know: which repos are clean, which have uncommitted work, which projects are online. Kode Keeper shows all of it in one glance.

### For Anyone Running Claude Code at Scale
You're spending real money. Kode Keeper shows you your burn rate before you're shocked by the invoice.

---

## Features

- 🟠 **Orange LED power button** — toggles browser auto-open on/off
- 📡 **Live polling** — refreshes every 6 seconds without a page reload
- 🎛 **Organic color palette** — warm grass greens, no clinical colors
- ⏱ **Session timer** — know how long you've been running
- 🔌 **Extensible** — add custom process monitors (we just added live Kalshi bot stats)
- 🎯 **Dead simple setup** — double-click launcher, it works

---

## Who It's For

- Claude Code power users running 3+ simultaneous projects
- Algo traders with autonomous bots
- Build-to-spec developers managing multiple codebases
- Anyone who cares about token burn rate and context health
- Teams running distributed Claude Code sessions

**Not for:** casual Claude users. This is a power user instrument.

---

## Pricing

**$29/month** or **$199/year** (save 3 months)

Why this price?
- Professional-grade monitoring tools cost $50-200/month
- You save hours per week avoiding log tailing and manual checks
- For traders, one prevented bot crash pays for a year of Kode Keeper
- For developers, avoiding one context reset saves the cost immediately

### What's Included
- Unlimited projects to monitor
- Live polling (6-second refresh)
- Cost tracking (model-aware pricing)
- Process monitoring (bots, services, etc.)
- Git status for all repos
- Email support (24-48h response)

### What's Not Included (Yet)
- Cloud sync (coming Q3)
- Team dashboards (coming Q4)
- Slack/Discord alerts (coming Q2)
- Custom integrations (available for $500 base fee)

---

## How It Works

```
Claude Code (running in terminal)
  └── Kode Keeper reads your session state
        • Context window fill %
        • Token counts (day/week/month)
        • Open projects (online/offline)
        • Git repo status
        • Bot process health
              ↓
        Real-time dashboard (localhost:5560)
              ↓
        One glance. Everything. No context switching.
```

---

## Quick Setup

1. **Download & Install**
   ```bash
   git clone https://github.com/papjamzzz/kodekeeper.git
   cd kodekeeper
   make setup
   ```

2. **Launch**
   Double-click `launch.command` in Finder. Opens your browser automatically.

3. **Watch**
   Keep the dashboard open while you work. Glance every few minutes.

That's it.

---

## Testimonials (Placeholder — will add real ones)

> "I was burning through context resets constantly. Kode Keeper shows me exactly when I'm about to hit the wall. Saved my project timeline." — *Algo Trader, Kalshi*

> "Managing 5 active projects. Before Kode Keeper I had tabs open everywhere. Now it's one dashboard. Indispensable." — *Build-to-Spec Dev*

> "Seeing my token burn rate in USD, in real-time, changed how I think about session management. Worth every penny." — *Claude Code Power User*

---

## FAQ

**Q: Do I need to modify my Claude Code setup?**
A: No. Kode Keeper reads existing data files. No setup required beyond install.

**Q: Can I monitor bots/services other than Claude Code?**
A: Yes. Process-based monitoring is built in. We monitor Kalshi bots live.

**Q: Is this cloud-based?**
A: No. Localhost only (127.0.0.1:5560). Your data never leaves your machine.

**Q: Can I use this on Windows/Linux?**
A: Currently macOS only. Windows/Linux support in Q2 2026.

**Q: What if Claude Code isn't running?**
A: The dashboard still shows your historical data and any running processes. It's useful even when Claude Code is idle.

**Q: Do you store my usage data?**
A: No. Everything is local. We never see your tokens, costs, or project names.

---

## Get Started

**[Buy Kode Keeper — $29/month or $199/year](https://checkout.creative-konsoles.com/kodekeeper)**

Or:

**[Download Free Trial (7 days, full features)](https://github.com/papjamzzz/kodekeeper/releases)**

---

## Support

**Email:** support@creativekonsoles.com
**Response time:** 24-48 hours
**GitHub:** [papjamzzz/kodekeeper](https://github.com/papjamzzz/kodekeeper)

---

## About

Built by [Creative Konsoles](https://creativekonsoles.com) — tools for Claude Code power users.

Part of the suite: **Kalshi Edge** • **StreamFader** • **TrackTracks** • **DAW Doctor** • **KK Trader** • **Kode Keeper**

All of them share one philosophy: **if you're running AI code at scale, you need real instruments.**
