"""Test script for Indian Stock Analysis System"""

import sys
import os

print("="*60)
print("INDIAN STOCK ANALYSIS SYSTEM - TEST")
print("="*60)

print("\n[1] Testing imports...")

try:
    from Indian_stock_analyzer import analyze_stock, list_available_tickers
    print("    PASS: Main imports successful")
except Exception as e:
    print(f"    FAIL: {e}")
    sys.exit(1)

try:
    from Indian_stock_analyzer.config import Config
    print("    PASS: Config import successful")
except Exception as e:
    print(f"    FAIL: {e}")
    sys.exit(1)

print("\n[2] Testing YFinance data...")

try:
    import yfinance as yf
    stock = yf.Ticker("RELIANCE.NS")
    info = stock.info
    price = info.get('currentPrice', 0)
    pe = info.get('trailingPE', 0)
    print(f"    PASS: RELIANCE - ₹{price}, P/E: {pe}")
except Exception as e:
    print(f"    FAIL: {e}")
    sys.exit(1)

print("\n[3] Testing technical indicators...")

try:
    from Indian_stock_analyzer.tools.stock_tools import technical_indicators_tool
    result = technical_indicators_tool._run("RELIANCE")
    print("    PASS: Technical indicators working")
except Exception as e:
    print(f"    FAIL: {e}")
    sys.exit(1)

print("\n[4] Available stock tickers:")
for ticker in list_available_tickers():
    print(f"    - {ticker}")

print("\n" + "="*60)
print("ALL TESTS PASSED")
print("="*60)

print("""
To analyze a stock:
    from Indian_stock_analyzer import analyze_stock
    result = analyze_stock("RELIANCE")

Or from command line:
    python -m stock_analysis.main RELIANCE
""")

import json

def quick_analyze(symbol: str) -> dict:
    """Quick analysis without full crew (for testing)"""
    
    import yfinance as yf
    
    ticker = f"{symbol}.NS"
    stock = yf.Ticker(ticker)
    info = stock.info
    history = stock.history(period="6mo")
    
    close = history['Close']
    
    delta = close.diff()
    gain = delta.where(delta > 0, 0).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    
    ema12 = close.ewm(span=12, adjust=False).mean()
    ema26 = close.ewm(span=26, adjust=False).mean()
    macd = ema12 - ema26
    
    ma50 = close.rolling(window=50).mean()
    ma200 = close.rolling(window=200).mean() if len(close) >= 200 else None
    
    sma20 = close.rolling(window=20).mean()
    std20 = close.rolling(window=20).std()
    bb_upper = sma20 + (std20 * 2)
    bb_lower = sma20 - (std20 * 2)
    
    return {
        "symbol": symbol.upper(),
        "company": info.get('longName', 'N/A'),
        "current_price": info.get('currentPrice'),
        "pe_ratio": info.get('trailingPE'),
        "market_cap": info.get('marketCap'),
        "volume": info.get('volume'),
        "52_week_high": info.get('fiftyTwoWeekHigh'),
        "52_week_low": info.get('fiftyTwoWeekLow'),
        "dividend_yield": info.get('dividendYield', 0) * 100 if info.get('dividendYield') else 0,
        "technical": {
            "rsi_14": round(float(rsi.iloc[-1]), 2) if not pd.isna(rsi.iloc[-1]) else None,
            "macd": round(float(macd.iloc[-1]), 2),
            "ma50": round(float(ma50.iloc[-1]), 2),
            "ma200": round(float(ma200.iloc[-1]), 2) if ma200 is not None else None,
            "bb_upper": round(float(bb_upper.iloc[-1]), 2),
            "bb_lower": round(float(bb_lower.iloc[-1]), 2)
        }
    }

import pandas as pd

print("\n[5] Quick technical analysis...")
result = quick_analyze("RELIANCE")
print(f"    Price: ₹{result['current_price']}")
print(f"    P/E: {result['pe_ratio']}")
print(f"    RSI(14): {result['technical']['rsi_14']}")
print(f"    MACD: {result['technical']['macd']}")
print(f"    MA50: ₹{result['technical']['ma50']}")
print(f"    MA200: ₹{result['technical']['ma200']}")
print(f"    Bollinger: ₹{result['technical']['bb_lower']} - ₹{result['technical']['bb_upper']}")