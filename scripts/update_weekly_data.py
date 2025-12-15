#!/usr/bin/env python3
"""
Weekly Buffett/Berkshire Radar Data Update Script
Fetches and stores weekly intelligence data in structured JSON format
"""

import json
import os
from datetime import datetime, timedelta
import yfinance as yf
from pathlib import Path

# Configuration
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data" / "weekly"
DATA_DIR.mkdir(parents=True, exist_ok=True)


def get_week_id():
    """Get current week ID in format YYYY-WXX"""
    now = datetime.now()
    week_num = now.isocalendar()[1]
    year = now.year
    return f"{year}-W{week_num:02d}"


def get_date_range():
    """Get start and end dates for current week (Monday-Sunday)"""
    now = datetime.now()
    # Get Monday of current week
    monday = now - timedelta(days=now.weekday())
    sunday = monday + timedelta(days=6)
    return {
        "start": monday.strftime("%Y-%m-%d"),
        "end": sunday.strftime("%Y-%m-%d")
    }


def fetch_brk_stock_data():
    """Fetch Berkshire Hathaway Class B stock data"""
    try:
        brk = yf.Ticker("BRK-B")
        sp500 = yf.Ticker("SPY")
        
        # Get current price and weekly change
        brk_hist = brk.history(period="5d")
        sp500_hist = sp500.history(period="5d")
        
        if len(brk_hist) < 2:
            print("Warning: Insufficient BRK-B data")
            return {}
        
        brk_close = float(brk_hist['Close'].iloc[-1])
        brk_open_week = float(brk_hist['Close'].iloc[0])
        weekly_change_pct = ((brk_close - brk_open_week) / brk_open_week) * 100
        
        # Get YTD data
        brk_ytd = brk.history(period="ytd")
        sp500_ytd = sp500.history(period="ytd")
        
        brk_ytd_return = ((brk_ytd['Close'].iloc[-1] - brk_ytd['Close'].iloc[0]) / brk_ytd['Close'].iloc[0]) * 100
        sp500_ytd_return = ((sp500_ytd['Close'].iloc[-1] - sp500_ytd['Close'].iloc[0]) / sp500_ytd['Close'].iloc[0]) * 100
        
        # Get 52-week range
        brk_52w = brk.history(period="1y")
        week_52_high = float(brk_52w['High'].max())
        week_52_low = float(brk_52w['Low'].min())
        
        return {
            "brk_b": {
                "price_close": round(brk_close, 2),
                "weekly_change_pct": round(weekly_change_pct, 2),
                "ytd_return_pct": round(brk_ytd_return, 2),
                "vs_sp500_ytd": round(brk_ytd_return - sp500_ytd_return, 2),
                "52week_high": round(week_52_high, 2),
                "52week_low": round(week_52_low, 2)
            }
        }
    except Exception as e:
        print(f"Error fetching BRK stock data: {e}")
        return {}


def fetch_top_holdings_performance(tickers):
    """Fetch performance data for top holdings"""
    holdings = []
    
    for ticker_info in tickers:
        try:
            ticker = yf.Ticker(ticker_info["ticker"])
            hist = ticker.history(period="5d")
            
            if len(hist) < 2:
                continue
            
            close_price = float(hist['Close'].iloc[-1])
            open_week = float(hist['Close'].iloc[0])
            weekly_change = ((close_price - open_week) / open_week) * 100
            
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
            print(f"Error fetching {ticker_info['ticker']}: {e}")
            continue
    
    return holdings


def create_weekly_snapshot():
    """Create comprehensive weekly data snapshot"""
    
    week_id = get_week_id()
    date_range = get_date_range()
    
    # Top holdings to track (from latest 13F)
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
    
    snapshot = {
        "week_id": week_id,
        "date_range": date_range,
        "timestamp": datetime.now().isoformat(),
        
        "sec_filings": {
            "new_filings": [],  # To be manually populated or fetched from SEC API
            "latest_13f": {
                "date": "2025-11-14",
                "quarter": "Q3-2025",
                "total_value": 267300000000,
                "holdings_count": 45
            }
        },
        
        "berkshire_stock": fetch_brk_stock_data(),
        
        "cash_position": {
            "total_cash_billions": 382,
            "as_of_date": "2025-09-30",
            "quarter": "Q3-2025",
            "qoq_change_billions": 28,
            "cash_to_equity_ratio": 1.43
        },
        
        "buyback_activity": {
            "last_buyback_date": "2024-05-31",
            "months_since_buyback": 18,
            "ytd_buybacks_billions": 0
        },
        
        "portfolio_changes": {
            "new_positions": [],
            "major_reductions": [],
            "exits": []
        },
        
        "top_holdings_performance": fetch_top_holdings_performance(top_holdings_config),
        
        "news_events": [],  # To be manually populated
        
        "market_signals": {
            "cash_hoard_signal": "maximum_caution",
            "buyback_signal": "bearish",
            "portfolio_activity": "net_seller",
            "overall_sentiment": "defensive"
        },
        
        "analyst_notes": {
            "key_takeaways": [],
            "week_over_week_changes": []
        }
    }
    
    return snapshot


def save_weekly_snapshot(snapshot):
    """Save weekly snapshot to JSON file"""
    week_id = snapshot["week_id"]
    filename = DATA_DIR / f"{week_id}.json"
    
    with open(filename, 'w') as f:
        json.dump(snapshot, f, indent=2)
    
    print(f"✓ Saved weekly snapshot: {filename}")
    return filename


def main():
    """Main execution function"""
    print("=" * 60)
    print("Weekly Buffett/Berkshire Radar Data Update")
    print("=" * 60)
    
    # Create weekly snapshot
    print("\nFetching data...")
    snapshot = create_weekly_snapshot()
    
    # Save to file
    filename = save_weekly_snapshot(snapshot)
    
    print(f"\n✓ Weekly data update complete!")
    print(f"  Week ID: {snapshot['week_id']}")
    print(f"  Date Range: {snapshot['date_range']['start']} to {snapshot['date_range']['end']}")
    print(f"  BRK.B Close: ${snapshot['berkshire_stock']['brk_b']['price_close']}")
    print(f"  Weekly Change: {snapshot['berkshire_stock']['brk_b']['weekly_change_pct']}%")
    print(f"\nNext steps:")
    print(f"  1. Review and edit {filename}")
    print(f"  2. Add SEC filings, news events, analyst notes manually")
    print(f"  3. Run analyze_trends.py to detect changes")
    print(f"  4. Run generate_report.py to create weekly report")


if __name__ == "__main__":
    main()
