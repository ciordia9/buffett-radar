#!/usr/bin/env python3
"""
Backfill Historical Data for Buffett Radar
Generates weekly snapshots for the past N weeks using historical stock data
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
import yfinance as yf

PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data" / "weekly"
DATA_DIR.mkdir(parents=True, exist_ok=True)


def get_week_id_for_date(date):
    """Get week ID for a specific date"""
    week_num = date.isocalendar()[1]
    year = date.year
    return f"{year}-W{week_num:02d}"


def get_monday_of_week(date):
    """Get Monday of the week for a given date"""
    return date - timedelta(days=date.weekday())


def fetch_historical_brk_data(start_date, end_date):
    """Fetch historical BRK.B data for a date range"""
    try:
        brk = yf.Ticker("BRK-B")
        sp500 = yf.Ticker("SPY")
        
        # Get data for the specific week
        brk_hist = brk.history(start=start_date, end=end_date)
        sp500_hist = sp500.history(start=start_date, end=end_date)
        
        if len(brk_hist) < 1:
            return None
        
        # Get first and last prices of the week
        brk_close = float(brk_hist['Close'].iloc[-1])
        brk_open_week = float(brk_hist['Close'].iloc[0])
        weekly_change_pct = ((brk_close - brk_open_week) / brk_open_week) * 100
        
        # Get YTD data (from start of year to end_date)
        year_start = datetime(end_date.year, 1, 1)
        brk_ytd = brk.history(start=year_start, end=end_date)
        sp500_ytd = sp500.history(start=year_start, end=end_date)
        
        if len(brk_ytd) < 2 or len(sp500_ytd) < 2:
            return None
        
        brk_ytd_return = ((brk_ytd['Close'].iloc[-1] - brk_ytd['Close'].iloc[0]) / brk_ytd['Close'].iloc[0]) * 100
        sp500_ytd_return = ((sp500_ytd['Close'].iloc[-1] - sp500_ytd['Close'].iloc[0]) / sp500_ytd['Close'].iloc[0]) * 100
        
        # Get 52-week range (approximate)
        year_ago = end_date - timedelta(days=365)
        brk_52w = brk.history(start=year_ago, end=end_date)
        week_52_high = float(brk_52w['High'].max())
        week_52_low = float(brk_52w['Low'].min())
        
        return {
            "price_close": round(brk_close, 2),
            "weekly_change_pct": round(weekly_change_pct, 2),
            "ytd_return_pct": round(brk_ytd_return, 2),
            "vs_sp500_ytd": round(brk_ytd_return - sp500_ytd_return, 2),
            "52week_high": round(week_52_high, 2),
            "52week_low": round(week_52_low, 2)
        }
    except Exception as e:
        print(f"Error fetching historical data: {e}")
        return None


def fetch_historical_holdings(tickers, end_date):
    """Fetch historical performance for top holdings"""
    holdings = []
    
    # Get week's data
    week_start = end_date - timedelta(days=7)
    
    for ticker_info in tickers:
        try:
            ticker = yf.Ticker(ticker_info["ticker"])
            hist = ticker.history(start=week_start, end=end_date)
            
            if len(hist) < 1:
                continue
            
            close_price = float(hist['Close'].iloc[-1])
            
            if len(hist) > 1:
                open_week = float(hist['Close'].iloc[0])
                weekly_change = ((close_price - open_week) / open_week) * 100
            else:
                weekly_change = 0.0
            
            holdings.append({
                "rank": ticker_info["rank"],
                "ticker": ticker_info["ticker"],
                "company": ticker_info["company"],
                "portfolio_pct": ticker_info.get("portfolio_pct", 0),
                "price": round(close_price, 2),
                "weekly_change_pct": round(weekly_change, 2),
                "value_billions": ticker_info.get("value_billions", 0)
            })
        except Exception as e:
            print(f"  Warning: Could not fetch {ticker_info['ticker']}: {e}")
            continue
    
    return holdings


def create_historical_snapshot(weeks_ago):
    """Create a historical snapshot for N weeks ago"""
    
    # Calculate the date
    today = datetime.now()
    target_date = today - timedelta(weeks=weeks_ago)
    monday = get_monday_of_week(target_date)
    sunday = monday + timedelta(days=6)
    
    week_id = get_week_id_for_date(target_date)
    
    print(f"\nGenerating data for {week_id} ({monday.strftime('%Y-%m-%d')} to {sunday.strftime('%Y-%m-%d')})")
    
    # Top holdings configuration (same as current)
    top_holdings_config = [
        {"rank": 1, "ticker": "AAPL", "company": "Apple Inc.", "portfolio_pct": 22.6, "value_billions": 60.7},
        {"rank": 2, "ticker": "BAC", "company": "Bank of America", "portfolio_pct": 11.0, "value_billions": 35.0},
        {"rank": 3, "ticker": "AXP", "company": "American Express", "portfolio_pct": 18.8, "value_billions": 49.5},
        {"rank": 4, "ticker": "KO", "company": "Coca-Cola", "portfolio_pct": 9.9, "value_billions": 18.8},
        {"rank": 5, "ticker": "CVX", "company": "Chevron", "portfolio_pct": 7.1, "value_billions": 9.6},
        {"rank": 6, "ticker": "OXY", "company": "Occidental Petroleum", "portfolio_pct": 4.7, "value_billions": 12.0},
        {"rank": 7, "ticker": "MCO", "company": "Moody's", "portfolio_pct": 4.4, "value_billions": 11.5},
        {"rank": 8, "ticker": "CB", "company": "Chubb Ltd", "portfolio_pct": 3.3, "value_billions": 8.8},
        {"rank": 9, "ticker": "KHC", "company": "Kraft Heinz", "portfolio_pct": 3.2, "value_billions": 8.5},
        {"rank": 10, "ticker": "GOOGL", "company": "Alphabet", "portfolio_pct": 1.6, "value_billions": 4.3},
    ]
    
    # Fetch historical BRK data
    brk_data = fetch_historical_brk_data(monday, sunday)
    if not brk_data:
        print(f"  ⚠ Could not fetch BRK data for this week")
        return None
    
    # Fetch historical holdings data
    holdings_data = fetch_historical_holdings(top_holdings_config, sunday)
    
    # Create snapshot
    snapshot = {
        "week_id": week_id,
        "date_range": {
            "start": monday.strftime("%Y-%m-%d"),
            "end": sunday.strftime("%Y-%m-%d")
        },
        "timestamp": target_date.isoformat(),
        "backfilled": True,  # Mark as backfilled data
        
        "sec_filings": {
            "new_filings": [],
            "latest_13f": {
                "date": "2025-11-14",
                "quarter": "Q3-2025",
                "total_value": 267300000000,
                "holdings_count": 45
            }
        },
        
        "berkshire_stock": {
            "brk_b": brk_data
        },
        
        "cash_position": {
            "total_cash_billions": 382,
            "as_of_date": "2025-09-30",
            "quarter": "Q3-2025",
            "qoq_change_billions": 28,
            "cash_to_equity_ratio": 1.43
        },
        
        "buyback_activity": {
            "last_buyback_date": "2024-05-31",
            "months_since_buyback": 18 - (weeks_ago // 4),  # Approximate
            "ytd_buybacks_billions": 0
        },
        
        "portfolio_changes": {
            "new_positions": [],
            "major_reductions": [],
            "exits": []
        },
        
        "top_holdings_performance": holdings_data,
        
        "news_events": [],
        
        "market_signals": {
            "cash_hoard_signal": "maximum_caution",
            "buyback_signal": "bearish",
            "portfolio_activity": "net_seller",
            "overall_sentiment": "defensive"
        },
        
        "analyst_notes": {
            "key_takeaways": ["Historical data - backfilled"],
            "week_over_week_changes": []
        }
    }
    
    print(f"  ✓ BRK.B: ${brk_data['price_close']} ({brk_data['weekly_change_pct']:+.2f}%)")
    print(f"  ✓ Fetched {len(holdings_data)} holdings")
    
    return snapshot


def main():
    """Main backfill function"""
    print("=" * 80)
    print("BUFFETT RADAR: HISTORICAL DATA BACKFILL")
    print("=" * 80)
    
    # Number of weeks to backfill
    num_weeks = 8
    
    print(f"\nBackfilling {num_weeks} weeks of historical data...")
    print("This will fetch historical stock prices and create weekly snapshots.")
    
    successful = 0
    failed = 0
    
    for weeks_ago in range(num_weeks, 0, -1):
        snapshot = create_historical_snapshot(weeks_ago)
        
        if snapshot:
            # Save to file
            filename = DATA_DIR / f"{snapshot['week_id']}.json"
            
            # Don't overwrite existing files
            if filename.exists():
                print(f"  ⚠ File already exists, skipping: {filename.name}")
                continue
            
            with open(filename, 'w') as f:
                json.dump(snapshot, f, indent=2)
            
            print(f"  ✓ Saved: {filename.name}")
            successful += 1
        else:
            print(f"  ✗ Failed to generate snapshot")
            failed += 1
    
    print("\n" + "=" * 80)
    print(f"BACKFILL COMPLETE")
    print("=" * 80)
    print(f"  Successful: {successful}")
    print(f"  Failed: {failed}")
    print(f"\nHistorical data saved to: {DATA_DIR}")
    print("\nNext steps:")
    print("  1. Review the generated files in data/weekly/")
    print("  2. Run analyze_trends.py to see week-over-week changes")
    print("  3. Commit and push to GitHub")


if __name__ == "__main__":
    main()
