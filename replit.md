# CreatorAudit — Instagram Lead Intelligence

## Overview
A Flask web app that scrapes public Instagram profiles, analyzes content quality (hooks, engagement rates, posting consistency), and generates sales reports to help sell script writing and idea generation services to low-performing creators.

## Architecture
- **Backend**: Python Flask (`app.py`)
- **Scraping**: `instaloader` library for public Instagram profiles
- **Analysis**: `analyzer.py` — scores hook quality, engagement rate, posting consistency, opportunity score
- **Report Generation**: `report_generator.py` — exports downloadable HTML audit reports
- **Frontend**: Jinja2 template (`templates/index.html`) — single-page dark UI

## Key Files
- `app.py` — Flask routes: `/`, `/api/scrape`, `/api/report`
- `analyzer.py` — Profile analysis engine (hook scoring, engagement analysis, opportunity scoring)
- `report_generator.py` — HTML report builder for export
- `templates/index.html` — Frontend UI

## Running the App
The app runs on port 5000 via the "Start app" workflow.

## User Preferences
- Dark, professional UI aesthetic
- Business-focused tool for outreach/sales
