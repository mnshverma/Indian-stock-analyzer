"""
Multi-Agent Stock Analysis System for Indian Equity Markets (NSE/BSE)

This package provides a sophisticated multi-agent system using CrewAI framework
to analyze Indian stocks and provide investment recommendations.

Agents:
- Market Data Researcher: Collects real-time and historical stock data
- Fundamental Analyst: Performs deep-dive financial analysis
- Technical Analyst: Analyzes price patterns and indicators
- Sentiment & News Analyst: Monitors market sentiment and news
- Investment Strategist: Synthesizes all analysis into recommendations

Usage:
    from Indian_stock_analyzer import analyze_stock
    result = analyze_stock("RELIANCE")
"""

__version__ = "1.0.0"

from Indian_stock_analyzer.main import analyze_stock, list_available_tickers

__all__ = [
    "analyze_stock",
    "list_available_tickers",
    "StockAnalysisCrew",
    "create_stock_analysis_crew",
    "Config"
]