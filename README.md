# Buffett/Berkshire Radar: Persistent Memory System

A GitHub-based intelligence tracking system for weekly Berkshire Hathaway analysis with historical context, trend detection, and automated reporting.

## Overview

This repository provides a **persistent memory system** for tracking Warren Buffett and Berkshire Hathaway's activities, enabling week-over-week comparison, trend analysis, and historical context that would otherwise be lost between weekly reports.

### Key Features

- **Structured Data Storage:** Weekly snapshots in JSON format
- **Trend Detection:** Automated week-over-week change analysis
- **Historical Context:** Easy access to past weeks, months, quarters
- **Time-Series Metrics:** CSV files for long-term trend visualization
- **Automated Updates:** Scripts to fetch and update data
- **Git Version Control:** Complete audit trail of all changes

## Repository Structure

```
buffett-radar/
├── data/                    # Structured data storage
│   ├── weekly/              # Weekly JSON snapshots
│   ├── metrics/             # Time-series CSV files
│   └── filings/             # SEC filing metadata
├── reports/                 # Generated weekly reports
├── scripts/                 # Automation scripts
├── templates/               # Report templates
├── config/                  # Configuration files
└── docs/                    # Documentation
```

## Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/buffett-radar.git
cd buffett-radar
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Run Weekly Update

```bash
python scripts/update_weekly_data.py
```

This will:
- Fetch current BRK.B stock data
- Fetch top holdings performance
- Create a weekly snapshot JSON file
- Save to `data/weekly/YYYY-WXX.json`

### 4. Analyze Trends

```bash
python scripts/analyze_trends.py
```

This will:
- Compare current week vs previous week
- Identify significant changes
- Generate changes report
- Save to `reports/YYYY-WXX/changes.json`

### 5. Manual Enrichment

Edit the generated `data/weekly/YYYY-WXX.json` file to add:
- New SEC filings
- News events
- Analyst notes
- Portfolio changes

### 6. Commit and Push

```bash
git add data/ reports/
git commit -m "Weekly update: $(date +%Y-W%V)"
git push origin main
```

## Data Schema

### Weekly Snapshot (JSON)

Each week's data is stored in `data/weekly/YYYY-WXX.json`:

```json
{
  "week_id": "2025-W50",
  "date_range": {
    "start": "2025-12-08",
    "end": "2025-12-15"
  },
  "berkshire_stock": {
    "brk_b": {
      "price_close": 499.52,
      "weekly_change_pct": -0.96,
      "ytd_return_pct": 10.73,
      "vs_sp500_ytd": -5.88
    }
  },
  "cash_position": {
    "total_cash_billions": 382,
    "quarter": "Q3-2025"
  },
  "buyback_activity": {
    "last_buyback_date": "2024-05-31",
    "months_since_buyback": 18
  },
  "top_holdings_performance": [...],
  "sec_filings": {...},
  "news_events": [...],
  "market_signals": {...}
}
```

## Usage for AI Agents

### Loading Historical Data

```python
import json
from pathlib import Path

def load_weekly_data(week_id):
    """Load a specific week's data"""
    with open(f"data/weekly/{week_id}.json") as f:
        return json.load(f)

# Load last 8 weeks
weeks = ["2025-W50", "2025-W49", "2025-W48", ...]
historical_data = [load_weekly_data(w) for w in weeks]
```

### Analyzing Trends

```python
# Compare two weeks
current = load_weekly_data("2025-W50")
previous = load_weekly_data("2025-W49")

# Calculate changes
cash_change = current["cash_position"]["total_cash_billions"] - \
              previous["cash_position"]["total_cash_billions"]

price_change_pct = current["berkshire_stock"]["brk_b"]["weekly_change_pct"]
```

### Generating Reports with Context

```python
# Load historical context
historical_data = load_last_n_weeks(8)

# Calculate trends
cash_trend = [w["cash_position"]["total_cash_billions"] for w in historical_data]
avg_cash_growth = (cash_trend[-1] - cash_trend[0]) / len(cash_trend)

# Include in report
report = f"""
## Historical Context

Over the past 8 weeks:
- Cash position: ${cash_trend[0]}B → ${cash_trend[-1]}B
- Average weekly growth: ${avg_cash_growth:.1f}B
- Trend: {"Accelerating" if cash_trend[-1] > cash_trend[-2] else "Stable"}
"""
```

## Key Metrics Tracked

### Stock Performance
- BRK.B price and weekly changes
- YTD returns vs S&P 500
- 52-week highs/lows

### Capital Allocation
- Cash position (quarterly)
- Share buyback activity
- Portfolio changes (quarterly from 13F)

### Portfolio Holdings
- Top 10 holdings performance
- Week-over-week price changes
- Portfolio concentration

### SEC Filings
- 13F quarterly holdings reports
- 8-K material events
- 10-Q/10-K financial statements

### Market Signals
- Cash hoard signal (defensive/neutral/aggressive)
- Buyback signal (bullish/neutral/bearish)
- Portfolio activity (net buyer/seller)

## Automation

### Weekly Workflow

1. **Monday Morning:** Run `update_weekly_data.py`
2. **Manual Review:** Edit JSON file with SEC filings, news, notes
3. **Trend Analysis:** Run `analyze_trends.py`
4. **Report Generation:** Run `generate_report.py` (future)
5. **Commit:** Git commit and push

### GitHub Actions (Optional)

Set up automated weekly runs:

```yaml
name: Weekly Update
on:
  schedule:
    - cron: '0 9 * * 1'  # Every Monday at 9 AM
jobs:
  update:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
      - run: pip install -r requirements.txt
      - run: python scripts/update_weekly_data.py
      - run: git add data/
      - run: git commit -m "Automated weekly update"
      - run: git push
```

## Benefits

1. **No More Starting from Scratch:** Every week builds on previous data
2. **Trend Visibility:** Easily spot patterns and inflection points
3. **Automated Insights:** Scripts highlight what's changed
4. **Reproducibility:** Git history provides complete audit trail
5. **Collaboration:** Multiple analysts can contribute
6. **API-Ready:** Structured data enables programmatic access

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

MIT License - see LICENSE file for details

## Contact

For questions or suggestions, please open an issue on GitHub.

---

**Last Updated:** December 15, 2025
