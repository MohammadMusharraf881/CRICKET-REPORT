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

