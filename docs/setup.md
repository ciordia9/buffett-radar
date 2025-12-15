# Setup Instructions

## Prerequisites

- Python 3.8 or higher
- Git
- GitHub account (for hosting the repository)

## Initial Setup

### 1. Create GitHub Repository

1. Go to https://github.com/new
2. Repository name: `buffett-radar` (or your preferred name)
3. Description: "Weekly Berkshire Hathaway intelligence tracking with persistent memory"
4. **Set to Private** (recommended for proprietary analysis)
5. Do NOT initialize with README (we already have one)
6. Click "Create repository"

### 2. Clone This Repository Locally

If you received this as a zip file:

```bash
# Extract the zip file
unzip buffett-radar.zip
cd buffett-radar

# Initialize git (if not already done)
git init
git branch -m main
```

### 3. Install Python Dependencies

```bash
pip install -r requirements.txt
```

Or install individually:

```bash
pip install yfinance pandas numpy matplotlib pyyaml requests
```

### 4. Connect to Your GitHub Repository

```bash
# Add your GitHub repository as remote
git remote add origin https://github.com/YOUR_USERNAME/buffett-radar.git

# Verify
git remote -v
```

### 5. Initial Commit

```bash
# Add all files
git add .

# Commit
git commit -m "Initial commit: Buffett Radar memory system"

# Push to GitHub
git push -u origin main
```

## Configuration (Optional)

### API Keys

If you plan to use additional data sources (GuruFocus, Alpha Vantage, etc.):

1. Copy the example config:
```bash
cp config/config.yaml.example config/config.yaml
```

2. Edit `config/config.yaml` and add your API keys

3. **Important:** The `.gitignore` file already excludes `config/secrets.yaml` and `config/api_keys.yaml` to prevent accidental commits of sensitive data.

## First Run

### Generate Initial Data

```bash
python scripts/update_weekly_data.py
```

This will:
- Fetch current BRK.B stock data
- Fetch top holdings performance
- Create `data/weekly/YYYY-WXX.json`

### Review and Enrich

1. Open the generated JSON file in `data/weekly/`
2. Add any SEC filings from the past week
3. Add news events
4. Add analyst notes

### Commit Your First Week

```bash
git add data/
git commit -m "Week 1: Initial data snapshot"
git push
```

## Weekly Workflow

Every Monday (or your preferred day):

### 1. Update Data

```bash
python scripts/update_weekly_data.py
```

### 2. Manual Enrichment

Edit `data/weekly/YYYY-WXX.json` to add:
- SEC filings (check https://www.sec.gov/cgi-bin/browse-edgar?company=berkshire&CIK=0001067983)
- News events
- Portfolio changes (if new 13F filed)
- Analyst notes and key takeaways

### 3. Analyze Trends

```bash
python scripts/analyze_trends.py
```

This compares current week vs previous week and highlights changes.

### 4. Commit and Push

```bash
git add data/ reports/
git commit -m "Weekly update: $(date +%Y-W%V)"
git push
```

## Accessing Historical Data

### Via Python

```python
import json

# Load a specific week
with open('data/weekly/2025-W50.json') as f:
    week_data = json.load(f)

# Access metrics
cash_position = week_data['cash_position']['total_cash_billions']
brk_price = week_data['berkshire_stock']['brk_b']['price_close']
```

### Via Command Line

```bash
# View a specific week
cat data/weekly/2025-W50.json | jq '.'

# Extract specific metric
cat data/weekly/2025-W50.json | jq '.cash_position.total_cash_billions'

# Compare two weeks
diff <(cat data/weekly/2025-W49.json) <(cat data/weekly/2025-W50.json)
```

## Troubleshooting

### "ModuleNotFoundError: No module named 'yfinance'"

Install dependencies:
```bash
pip install -r requirements.txt
```

### "Permission denied" when pushing to GitHub

Set up SSH keys or use personal access token:
```bash
# Generate SSH key
ssh-keygen -t ed25519 -C "your_email@example.com"

# Add to GitHub: Settings > SSH and GPG keys > New SSH key
```

Or use HTTPS with personal access token (GitHub Settings > Developer settings > Personal access tokens)

### Data fetch errors

- Check internet connection
- Verify ticker symbols are correct
- Some data sources may have rate limits

## Advanced Setup

### GitHub Actions (Automated Weekly Runs)

Create `.github/workflows/weekly-update.yml`:

```yaml
name: Weekly Update
on:
  schedule:
    - cron: '0 9 * * 1'  # Every Monday at 9 AM UTC
  workflow_dispatch:  # Allow manual trigger

jobs:
  update:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: pip install -r requirements.txt
      
      - name: Update weekly data
        run: python scripts/update_weekly_data.py
      
      - name: Commit changes
        run: |
          git config user.name "GitHub Actions"
          git config user.email "actions@github.com"
          git add data/
          git commit -m "Automated weekly update: $(date +%Y-W%V)" || echo "No changes"
          git push
```

## Support

For questions or issues:
1. Check existing documentation in `docs/`
2. Review the README.md
3. Open an issue on GitHub

---

**Next:** See [usage.md](usage.md) for detailed usage instructions
