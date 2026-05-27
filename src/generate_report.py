"""
🏏 Cricket Daily Report
Generated automatically by GitHub Actions on 27 May, 4:30 PM
Fetches live + recent cricket scores from cricapi.com (free tier)
and generates a beautiful HTML report.
"""

import json
import os
import re
import urllib.request
import urllib.error
from datetime import datetime, timezone

# ── Config ─────────────────────────────────────────────────────────────────
API_KEY  = os.getenv("CRICKET_API_KEY", "demo")   # set as GitHub secret
BASE_URL = "https://api.cricapi.com/v1"
OUTPUT   = os.getenv("REPORT_OUTPUT", "report.html")


# ── Fetch helpers ───────────────────────────────────────────────────────────
def fetch(endpoint: str, params: dict = {}) -> dict:
    params["apikey"] = API_KEY
    query = "&".join(f"{k}={v}" for k, v in params.items())
    url   = f"{BASE_URL}/{endpoint}?{query}"
    try:
        with urllib.request.urlopen(url, timeout=10) as r:
            return json.loads(r.read().decode())
    except Exception as e:
        print(f"[WARN] fetch {endpoint} failed: {e}")
        return {}


def get_matches() -> list:
    """Return a list of recent + live match dicts."""
    data = fetch("currentMatches", {"offset": 0})
    return data.get("data", []) or []


# ── Demo data (used when API key is 'demo' or quota exceeded) ───────────────
DEMO_MATCHES = [
    {
        "name": "India vs Australia, 3rd ODI",
        "status": "India won by 47 runs",
        "matchType": "odi",
        "teams": ["India", "Australia"],
        "score": [
            {"r": 312, "w": 6, "o": 50, "inning": "India Inning 1"},
            {"r": 265, "w": 10, "o": 45.3, "inning": "Australia Inning 1"},
        ],
        "date": "2025-05-27T09:00:00",
        "venue": "Narendra Modi Stadium, Ahmedabad",
    },
    {
        "name": "England vs Pakistan, 1st Test – Day 3",
        "status": "In Progress",
        "matchType": "test",
        "teams": ["England", "Pakistan"],
        "score": [
            {"r": 445, "w": 8, "o": 120, "inning": "England Inning 1"},
            {"r": 178, "w": 4, "o": 56, "inning": "Pakistan Inning 1"},
        ],
        "date": "2025-05-25T10:00:00",
        "venue": "Lord's Cricket Ground, London",
    },
    {
        "name": "Mumbai Indians vs Chennai Super Kings, IPL Final",
        "status": "Chennai Super Kings won by 5 wickets",
        "matchType": "t20",
        "teams": ["Mumbai Indians", "Chennai Super Kings"],
        "score": [
            {"r": 189, "w": 6, "o": 20, "inning": "Mumbai Indians Inning 1"},
            {"r": 192, "w": 5, "o": 19.2, "inning": "Chennai Super Kings Inning 1"},
        ],
        "date": "2025-05-26T19:30:00",
        "venue": "Wankhede Stadium, Mumbai",
    },
    {
        "name": "South Africa vs New Zealand, 2nd T20I",
        "status": "South Africa won by 23 runs",
        "matchType": "t20",
        "teams": ["South Africa", "New Zealand"],
        "score": [
            {"r": 201, "w": 4, "o": 20, "inning": "South Africa Inning 1"},
            {"r": 178, "w": 9, "o": 20, "inning": "New Zealand Inning 1"},
        ],
        "date": "2025-05-26T14:00:00",
        "venue": "Newlands, Cape Town",
    },
    {
        "name": "Bangladesh vs Sri Lanka, ODI Series",
        "status": "Match starts in 2 hours",
        "matchType": "odi",
        "teams": ["Bangladesh", "Sri Lanka"],
        "score": [],
        "date": "2025-05-27T14:00:00",
        "venue": "Shere Bangla National Stadium, Dhaka",
    },
]


# ── Team flag emoji map ─────────────────────────────────────────────────────
FLAGS = {
    "india": "🇮🇳", "australia": "🇦🇺", "england": "🏴󠁧󠁢󠁥󠁮󠁧󠁿",
    "pakistan": "🇵🇰", "south africa": "🇿🇦", "new zealand": "🇳🇿",
    "sri lanka": "🇱🇰", "bangladesh": "🇧🇩", "west indies": "🏝️",
    "afghanistan": "🇦🇫", "zimbabwe": "🇿🇼", "ireland": "🇮🇪",
    "mumbai indians": "🔵", "chennai super kings": "🟡",
    "royal challengers": "🔴", "kolkata knight riders": "🟣",
    "delhi capitals": "🔵", "sunrisers hyderabad": "🟠",
    "rajasthan royals": "🩷", "punjab kings": "🔴",
    "lucknow super giants": "🩵", "gujarat titans": "🔵",
}

def flag(team: str) -> str:
    return FLAGS.get(team.lower(), "🏏")


def match_type_badge(mtype: str) -> str:
    styles = {
        "test": ("TEST", "#1a3a5c", "#b8d4f0"),
        "odi":  ("ODI",  "#1a4a2a", "#a8e0b8"),
        "t20":  ("T20",  "#4a1a1a", "#f0b8b8"),
    }
    key   = mtype.lower()
    label, bg, fg = styles.get(key, (mtype.upper(), "#333", "#eee"))
    return f'<span class="badge" style="background:{bg};color:{fg}">{label}</span>'


def status_class(status: str) -> str:
    s = status.lower()
    if "won" in s or "win" in s:
        return "status-done"
    if "progress" in s or "live" in s or "innings" in s:
        return "status-live"
    return "status-upcoming"


def score_line(score_list: list) -> str:
    if not score_list:
        return "<em style='color:#888'>Yet to bat</em>"
    parts = []
    for s in score_list:
        inning = s.get("inning", "")
        r, w, o = s.get("r", 0), s.get("w", 0), s.get("o", 0)
        team = inning.replace(" Inning 1", "").replace(" Inning 2", "")
        parts.append(f"<strong>{team}</strong>: {r}/{w} ({o} ov)")
    return "<br>".join(parts)


# ── HTML template ───────────────────────────────────────────────────────────
HTML_HEAD = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>Cricket Daily Report – {date}</title>
<link rel="preconnect" href="https://fonts.googleapis.com"/>
<link href="https://fonts.googleapis.com/css2?family=Syne:wght@400;700;800&family=DM+Mono:wght@400&display=swap" rel="stylesheet"/>
<style>
*,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}
:root{{
  --bg:#0d0d0d;--surface:#161616;--border:#262626;
  --text:#e8e4dc;--muted:#6b6660;--accent:#c8f060;--accent2:#60c8f0;
}}
body{{background:var(--bg);color:var(--text);font-family:'Syne',sans-serif;padding:0 1rem 4rem}}
header{{max-width:900px;margin:0 auto;padding:3rem 0 2rem;border-bottom:1px solid var(--border)}}
.logo{{font-family:'DM Mono',monospace;font-size:.8rem;color:var(--accent);letter-spacing:.1em;text-transform:uppercase;margin-bottom:1.2rem}}
h1{{font-size:clamp(2rem,5vw,3.5rem);font-weight:800;letter-spacing:-.03em;line-height:1.1}}
h1 span{{color:var(--accent)}}
.meta{{margin-top:.75rem;font-family:'DM Mono',monospace;font-size:.75rem;color:var(--muted);letter-spacing:.07em}}
.summary{{max-width:900px;margin:2rem auto;display:grid;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));gap:1px;border:1px solid var(--border)}}
.stat{{background:var(--surface);padding:1.25rem 1.5rem}}
.stat-val{{font-size:2rem;font-weight:800;letter-spacing:-.03em}}
.stat-label{{font-family:'DM Mono',monospace;font-size:.7rem;color:var(--muted);letter-spacing:.1em;text-transform:uppercase;margin-top:.25rem}}
.matches{{max-width:900px;margin:2rem auto;display:flex;flex-direction:column;gap:1px}}
.section-label{{font-family:'DM Mono',monospace;font-size:.7rem;color:var(--muted);letter-spacing:.14em;text-transform:uppercase;margin:2rem 0 .75rem}}
.card{{background:var(--surface);border:1px solid var(--border);padding:1.5rem 1.75rem}}
.card-top{{display:flex;justify-content:space-between;align-items:flex-start;gap:1rem;margin-bottom:1rem}}
.match-name{{font-size:1.05rem;font-weight:700;letter-spacing:-.01em}}
.teams{{margin:.35rem 0;font-size:.95rem;color:var(--muted)}}
.scores{{font-size:.9rem;line-height:1.9;margin:.75rem 0}}
.venue{{font-family:'DM Mono',monospace;font-size:.72rem;color:var(--muted);margin-top:.5rem}}
.status{{font-size:.82rem;margin-top:.65rem;padding:.3rem .7rem;display:inline-block;border-radius:2px}}
.status-done{{background:#1a3a1a;color:#80e880}}
.status-live{{background:#3a1a1a;color:#f08080;animation:pulse 2s infinite}}
.status-upcoming{{background:#1a1a3a;color:#8080f0}}
@keyframes pulse{{0%,100%{{opacity:1}}50%{{opacity:.6}}}}
.badge{{font-family:'DM Mono',monospace;font-size:.68rem;padding:.25rem .6rem;border-radius:2px;letter-spacing:.05em;font-weight:700}}
footer{{max-width:900px;margin:3rem auto 0;border-top:1px solid var(--border);padding-top:1.5rem;font-family:'DM Mono',monospace;font-size:.72rem;color:var(--muted);display:flex;justify-content:space-between;flex-wrap:wrap;gap:.5rem}}
</style>
</head>
<body>
"""

HTML_FOOT = """
<footer>
  <span>🏏 Cricket Daily Report</span>
  <span>Generated by Python · Deployed via GitHub Actions · Docker</span>
</footer>
</body></html>
"""


# ── Build report ────────────────────────────────────────────────────────────
def build_report(matches: list) -> str:
    now     = datetime.now(timezone.utc)
    date_str = now.strftime("%B %d, %Y")
    time_str = now.strftime("%H:%M UTC")

    total   = len(matches)
    live    = sum(1 for m in matches if "progress" in m.get("status","").lower() or "live" in m.get("status","").lower())
    done    = sum(1 for m in matches if "won" in m.get("status","").lower())
    upcoming= total - live - done

    html = HTML_HEAD.format(date=date_str)

    # Header
    html += f"""
<header>
  <div class="logo">🏏 Daily Report</div>
  <h1>Cricket <span>Scores</span><br>&amp; Results</h1>
  <p class="meta">Generated on {date_str} at {time_str} &nbsp;·&nbsp; {total} matches tracked</p>
</header>
"""

    # Summary stats
    html += f"""
<div class="summary">
  <div class="stat"><div class="stat-val">{total}</div><div class="stat-label">Total Matches</div></div>
  <div class="stat"><div class="stat-val" style="color:#f08080">{live}</div><div class="stat-label">Live Now</div></div>
  <div class="stat"><div class="stat-val" style="color:#80e880">{done}</div><div class="stat-label">Completed</div></div>
  <div class="stat"><div class="stat-val" style="color:#8080f0">{upcoming}</div><div class="stat-label">Upcoming</div></div>
</div>
"""

    html += '<div class="matches">'

    # Live first
    live_matches     = [m for m in matches if "progress" in m.get("status","").lower() or "live" in m.get("status","").lower()]
    done_matches     = [m for m in matches if "won" in m.get("status","").lower()]
    upcoming_matches = [m for m in matches if m not in live_matches and m not in done_matches]

    def render_section(title, items):
        if not items:
            return ""
        out = f'<div class="section-label">{title}</div>'
        for m in items:
            name   = m.get("name", "Unknown Match")
            status = m.get("status", "")
            mtype  = m.get("matchType", "")
            teams  = m.get("teams", [])
            scores = m.get("score", [])
            venue  = m.get("venue", "")
            date   = m.get("date", "")[:10]

            team_line = " &nbsp;vs&nbsp; ".join(
                f'{flag(t)} {t}' for t in teams
            ) if teams else name

            out += f"""
<div class="card">
  <div class="card-top">
    <div>
      <div class="match-name">{name}</div>
      <div class="teams">{team_line}</div>
    </div>
    {match_type_badge(mtype)}
  </div>
  <div class="scores">{score_line(scores)}</div>
  <div class="venue">📍 {venue} &nbsp;·&nbsp; 📅 {date}</div>
  <div><span class="status {status_class(status)}">{status}</span></div>
</div>"""
        return out

    html += render_section("🔴 Live Matches", live_matches)
    html += render_section("✅ Completed", done_matches)
    html += render_section("🕐 Upcoming", upcoming_matches)

    html += "</div>"
    html += HTML_FOOT
    return html


# ── Main ────────────────────────────────────────────────────────────────────
def main():
    print("Fetching cricket data...")

    if API_KEY == "demo":
        print("[INFO] No API key set — using demo data.")
        matches = DEMO_MATCHES
    else:
        matches = get_matches()
        if not matches:
            print("[WARN] API returned no data — falling back to demo data.")
            matches = DEMO_MATCHES

    print(f"Found {len(matches)} matches. Generating report...")

    report = build_report(matches)

    with open(OUTPUT, "w", encoding="utf-8") as f:
        f.write(report)

    print(f"✅ Report saved to {OUTPUT}")


if __name__ == "__main__":
    main()
