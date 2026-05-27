# 🏏 Cricket Daily Report Generator

A Python script that fetches live cricket scores every morning, generates a beautiful HTML report, and automatically publishes it to GitHub Pages — fully automated with Docker + GitHub Actions.

**Live report:** `https://YOUR_USERNAME.github.io/cricket-report`

---

## How it works

```
Every day at 7 AM UTC
        │
        ▼
GitHub Actions wakes up
        │
        ▼
Docker builds the Python container
        │
        ▼
Python fetches cricket scores (cricapi.com)
        │
        ▼
Generates report.html
        │
        ▼
Commits report back to repo
        │
        ▼
Deploys to GitHub Pages (live URL)
```

---

## Project structure

```
cricket-report/
├── .github/
│   └── workflows/
│       └── generate.yml     ← runs every morning at 7 AM UTC
├── src/
│   └── generate_report.py   ← fetches data + builds HTML report
├── Dockerfile               ← multi-stage Python container
├── requirements.txt
└── README.md
```

---

## Setup (4 steps)

### 1. Get a free Cricket API key
- Sign up at [cricapi.com](https://cricapi.com) — free tier gives 100 calls/day
- Copy your API key

### 2. Add the API key as a GitHub Secret
- Go to your repo → **Settings → Secrets and variables → Actions**
- Click **New repository secret**
- Name: `CRICKET_API_KEY`
- Value: your key from step 1

### 3. Push to GitHub
```bash
git init
git add .
git commit -m "feat: cricket report generator"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/cricket-report.git
git push -u origin main
```

### 4. Enable GitHub Pages
- Repo → **Settings → Pages**
- Source: **Deploy from a branch**
- Branch: **gh-pages** → Save

---

## Your report is live at:
```
https://YOUR_USERNAME.github.io/cricket-report
```

It refreshes automatically every morning at 7 AM UTC (12:30 PM IST).

---

## Run locally

```bash
# Without API key (uses demo data)
docker build -t cricket-report .
docker run --rm -v $(pwd)/reports:/output cricket-report

# With API key
docker run --rm \
  -e CRICKET_API_KEY=your_key_here \
  -v $(pwd)/reports:/output \
  cricket-report

# Open reports/report.html in your browser
```

---

## Run manually on GitHub
- Go to repo → **Actions** tab
- Click **Generate Cricket Report**
- Click **Run workflow** → report generates in ~30 seconds

---

## CV description

> "Built a fully automated daily report pipeline using Python, Docker, and GitHub Actions with scheduled cron jobs. The system fetches live cricket data from a public API, generates a styled HTML report, commits it back to the repository, and publishes it to GitHub Pages — all without any manual intervention."

---

## Extending the project
- Add email delivery with `smtplib` (send report to yourself)
- Add player stats or series standings
- Add a chart with match win/loss history
- Add Telegram/WhatsApp notification on match completion
