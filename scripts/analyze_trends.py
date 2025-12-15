#!/usr/bin/env python3
"""
Trend Analysis Script for Buffett/Berkshire Radar
Analyzes week-over-week changes and identifies significant trends
"""

import json
import os
from pathlib import Path
from datetime import datetime, timedelta


PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data" / "weekly"


def load_weekly_data(week_id):
    """Load weekly data from JSON file"""
    filename = DATA_DIR / f"{week_id}.json"
    if not filename.exists():
        return None
    
    with open(filename, 'r') as f:
        return json.load(f)


def get_previous_week_id(week_id):
    """Calculate previous week ID"""
    year, week = week_id.split('-W')
    year = int(year)
    week = int(week)
    
    if week == 1:
        # Previous week is last week of previous year
        return f"{year-1}-W52"
    else:
        return f"{year}-W{week-1:02d}"


def compare_stock_performance(current, previous):
    """Compare BRK.B stock performance week-over-week"""
    changes = []
    
    if not current or not previous:
        return changes
    
    curr_brk = current.get("berkshire_stock", {}).get("brk_b", {})
    prev_brk = previous.get("berkshire_stock", {}).get("brk_b", {})
    
    if not curr_brk or not prev_brk:
        return changes
    
    # Price change
    price_change = curr_brk.get("price_close", 0) - prev_brk.get("price_close", 0)
    price_change_pct = (price_change / prev_brk.get("price_close", 1)) * 100
    
    changes.append({
        "metric": "BRK.B Price",
        "current": f"${curr_brk.get('price_close', 0):.2f}",
        "previous": f"${prev_brk.get('price_close', 0):.2f}",
        "change": f"${price_change:+.2f} ({price_change_pct:+.2f}%)",
        "significance": "high" if abs(price_change_pct) > 3 else "medium" if abs(price_change_pct) > 1 else "low"
    })
    
    # YTD performance change
    ytd_change = curr_brk.get("ytd_return_pct", 0) - prev_brk.get("ytd_return_pct", 0)
    changes.append({
        "metric": "YTD Return",
        "current": f"{curr_brk.get('ytd_return_pct', 0):.2f}%",
        "previous": f"{prev_brk.get('ytd_return_pct', 0):.2f}%",
        "change": f"{ytd_change:+.2f} pp",
        "significance": "medium"
    })
    
    # Relative performance vs S&P 500
    rel_perf_change = curr_brk.get("vs_sp500_ytd", 0) - prev_brk.get("vs_sp500_ytd", 0)
    changes.append({
        "metric": "vs S&P 500 (YTD)",
        "current": f"{curr_brk.get('vs_sp500_ytd', 0):+.2f} pp",
        "previous": f"{prev_brk.get('vs_sp500_ytd', 0):+.2f} pp",
        "change": f"{rel_perf_change:+.2f} pp",
        "significance": "high" if abs(rel_perf_change) > 1 else "medium"
    })
    
    return changes


def compare_cash_position(current, previous):
    """Compare cash position week-over-week"""
    changes = []
    
    curr_cash = current.get("cash_position", {})
    prev_cash = previous.get("cash_position", {})
    
    if curr_cash.get("as_of_date") != prev_cash.get("as_of_date"):
        # New quarterly data available
        cash_change = curr_cash.get("total_cash_billions", 0) - prev_cash.get("total_cash_billions", 0)
        changes.append({
            "metric": "Cash Position",
            "current": f"${curr_cash.get('total_cash_billions', 0)}B",
            "previous": f"${prev_cash.get('total_cash_billions', 0)}B",
            "change": f"${cash_change:+.0f}B",
            "significance": "high",
            "note": "NEW QUARTERLY DATA"
        })
    
    return changes


def compare_buyback_activity(current, previous):
    """Compare buyback activity week-over-week"""
    changes = []
    
    curr_buyback = current.get("buyback_activity", {})
    prev_buyback = previous.get("buyback_activity", {})
    
    if curr_buyback.get("last_buyback_date") != prev_buyback.get("last_buyback_date"):
        changes.append({
            "metric": "Buyback Activity",
            "current": curr_buyback.get("last_buyback_date", "N/A"),
            "previous": prev_buyback.get("last_buyback_date", "N/A"),
            "change": "NEW BUYBACK DETECTED",
            "significance": "critical"
        })
    else:
        # Check if months since buyback increased
        months_change = curr_buyback.get("months_since_buyback", 0) - prev_buyback.get("months_since_buyback", 0)
        if months_change > 0:
            changes.append({
                "metric": "Months Since Buyback",
                "current": str(curr_buyback.get("months_since_buyback", 0)),
                "previous": str(prev_buyback.get("months_since_buyback", 0)),
                "change": f"+{months_change} month(s)",
                "significance": "medium" if curr_buyback.get("months_since_buyback", 0) > 12 else "low"
            })
    
    return changes


def compare_holdings_performance(current, previous):
    """Compare top holdings performance week-over-week"""
    changes = []
    
    curr_holdings = {h["ticker"]: h for h in current.get("top_holdings_performance", [])}
    prev_holdings = {h["ticker"]: h for h in previous.get("top_holdings_performance", [])}
    
    # Find biggest movers
    movers = []
    for ticker, curr_data in curr_holdings.items():
        if ticker in prev_holdings:
            curr_change = curr_data.get("weekly_change_pct", 0)
            movers.append({
                "ticker": ticker,
                "company": curr_data.get("company", ""),
                "change_pct": curr_change
            })
    
    # Sort by absolute change
    movers.sort(key=lambda x: abs(x["change_pct"]), reverse=True)
    
    # Report top 3 movers
    for i, mover in enumerate(movers[:3]):
        changes.append({
            "metric": f"Top Mover #{i+1}",
            "current": f"{mover['ticker']} ({mover['company']})",
            "previous": "-",
            "change": f"{mover['change_pct']:+.2f}%",
            "significance": "high" if abs(mover["change_pct"]) > 5 else "medium"
        })
    
    return changes


def detect_new_sec_filings(current, previous):
    """Detect new SEC filings"""
    changes = []
    
    curr_filings = current.get("sec_filings", {}).get("new_filings", [])
    prev_filings = previous.get("sec_filings", {}).get("new_filings", [])
    
    # Simple check: if current has filings and previous doesn't, or counts differ
    if len(curr_filings) > len(prev_filings):
        new_count = len(curr_filings) - len(prev_filings)
        changes.append({
            "metric": "New SEC Filings",
            "current": str(len(curr_filings)),
            "previous": str(len(prev_filings)),
            "change": f"+{new_count} new filing(s)",
            "significance": "high"
        })
        
        # List the new filings
        for filing in curr_filings[:new_count]:
            changes.append({
                "metric": f"  - {filing.get('type', 'Unknown')}",
                "current": filing.get("date", ""),
                "previous": "-",
                "change": filing.get("description", ""),
                "significance": filing.get("significance", "medium")
            })
    
    return changes


def generate_changes_report(current_week_id):
    """Generate comprehensive changes report"""
    current = load_weekly_data(current_week_id)
    if not current:
        print(f"Error: Could not load data for {current_week_id}")
        return None
    
    previous_week_id = get_previous_week_id(current_week_id)
    previous = load_weekly_data(previous_week_id)
    
    if not previous:
        print(f"Warning: No previous week data found ({previous_week_id})")
        print("This may be the first week of data collection.")
        return None
    
    all_changes = []
    
    # Analyze different aspects
    all_changes.extend(compare_stock_performance(current, previous))
    all_changes.extend(compare_cash_position(current, previous))
    all_changes.extend(compare_buyback_activity(current, previous))
    all_changes.extend(detect_new_sec_filings(current, previous))
    all_changes.extend(compare_holdings_performance(current, previous))
    
    return {
        "current_week": current_week_id,
        "previous_week": previous_week_id,
        "comparison_date": datetime.now().isoformat(),
        "changes": all_changes,
        "summary": {
            "total_changes": len(all_changes),
            "critical_changes": len([c for c in all_changes if c.get("significance") == "critical"]),
            "high_significance": len([c for c in all_changes if c.get("significance") == "high"]),
            "medium_significance": len([c for c in all_changes if c.get("significance") == "medium"])
        }
    }


def print_changes_report(changes_data):
    """Print changes report to console"""
    if not changes_data:
        return
    
    print("\n" + "=" * 80)
    print(f"WEEK-OVER-WEEK CHANGES: {changes_data['current_week']} vs {changes_data['previous_week']}")
    print("=" * 80)
    
    print(f"\nSummary:")
    print(f"  Total Changes: {changes_data['summary']['total_changes']}")
    print(f"  Critical: {changes_data['summary']['critical_changes']}")
    print(f"  High Significance: {changes_data['summary']['high_significance']}")
    print(f"  Medium Significance: {changes_data['summary']['medium_significance']}")
    
    print(f"\nDetailed Changes:")
    print("-" * 80)
    
    for change in changes_data['changes']:
        sig_icon = "🔴" if change.get("significance") == "critical" else "🟠" if change.get("significance") == "high" else "🟡"
        print(f"\n{sig_icon} {change['metric']}")
        print(f"   Current:  {change['current']}")
        print(f"   Previous: {change['previous']}")
        print(f"   Change:   {change['change']}")
        if change.get("note"):
            print(f"   Note:     {change['note']}")


def main():
    """Main execution function"""
    # Get current week
    now = datetime.now()
    week_num = now.isocalendar()[1]
    year = now.year
    current_week_id = f"{year}-W{week_num:02d}"
    
    print("=" * 80)
    print("Buffett/Berkshire Radar - Trend Analysis")
    print("=" * 80)
    print(f"\nAnalyzing week: {current_week_id}")
    
    # Generate changes report
    changes_data = generate_changes_report(current_week_id)
    
    if changes_data:
        # Print to console
        print_changes_report(changes_data)
        
        # Save to file
        output_file = PROJECT_ROOT / "reports" / current_week_id / "changes.json"
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w') as f:
            json.dump(changes_data, f, indent=2)
        
        print(f"\n✓ Changes report saved to: {output_file}")
    else:
        print("\n⚠ Could not generate changes report (missing previous week data)")


if __name__ == "__main__":
    main()
