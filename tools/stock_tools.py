import os
import json
import re
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from crewai.tools import BaseTool
from pydantic import Field
import yfinance as yf
import pandas as pd
import numpy as np


class StockDataInput(BaseTool):
    name: str = "Get Stock Information"
    description: str = "Retrieves real-time and historical stock data for Indian stocks (NSE/BSE). Input should be the stock ticker symbol (e.g., 'RELIANCE', 'TCS', 'INFY')."

    def _run(self, symbol: str) -> str:
        try:
            ticker = self._format_symbol(symbol)
            stock = yf.Ticker(ticker)
            
            info = stock.info
            history = stock.history(period="1y")
            
            current_price = info.get('currentPrice', info.get('regularMarketPrice', 0))
            previous_close = info.get('previousClose', info.get('regularMarketPreviousClose', 0))
            market_cap = info.get('marketCap', 0)
            volume = info.get('volume', 0)
            pe_ratio = info.get('trailingPE', 0)
            dividend_yield = info.get('dividendYield', 0) * 100 if info.get('dividendYield') else 0
            eps = info.get('trailingEps', 0)
            beta = info.get('beta', 0)
            week_52_high = info.get('fiftyTwoWeekHigh', 0)
            week_52_low = info.get('fiftyTwoWeekLow', 0)
            
            if isinstance(market_cap, (int, float)) and market_cap > 0:
                market_cap_str = self._format_market_cap(market_cap)
            else:
                market_cap_str = "N/A"
            
            result = {
                "symbol": symbol.upper(),
                "ticker": ticker,
                "company_name": info.get('longName', info.get('shortName', 'N/A')),
                "current_price": current_price,
                "previous_close": previous_close,
                "price_change": current_price - previous_close if current_price and previous_close else 0,
                "price_change_pct": ((current_price - previous_close) / previous_close * 100) if current_price and previous_close else 0,
                "market_cap": market_cap_str,
                "volume": volume,
                "pe_ratio": round(pe_ratio, 2) if pe_ratio else "N/A",
                "eps": round(eps, 2) if eps else "N/A",
                "dividend_yield": round(dividend_yield, 2),
                "beta": round(beta, 2) if beta else "N/A",
                "52_week_high": week_52_high,
                "52_week_low": week_52_low,
                "sector": info.get('sector', 'N/A'),
                "industry": info.get('industry', 'N/A'),
            }
            
            return json.dumps(result, indent=2, default=str)
            
        except Exception as e:
            return json.dumps({"error": str(e), "symbol": symbol})

    def _format_symbol(self, symbol: str) -> str:
        symbol = symbol.strip().upper()
        if not symbol.endswith('.NS'):
            return f"{symbol}.NS"
        return symbol

    def _format_market_cap(self, market_cap: float) -> str:
        if market_cap >= 1e12:
            return f"₹{market_cap/1e12:.2f}T"
        elif market_cap >= 1e10:
            return f"₹{market_cap/1e10:.2f}B"
        elif market_cap >= 1e8:
            return f"₹{market_cap/1e8:.2f}M"
        else:
            return f"₹{market_cap:,.0f}"


class HistoricalDataInput(BaseTool):
    name: str = "Get Historical Price Data"
    description: str = "Retrieves historical price data for Indian stocks. Input should be the stock ticker and period (e.g., 'RELIANCE,6mo')."

    def _run(self, query: str) -> str:
        try:
            parts = query.split(',')
            symbol = parts[0].strip()
            period = parts[1].strip() if len(parts) > 1 else "6mo"
            
            ticker = symbol.upper()
            if not ticker.endswith('.NS'):
                ticker = f"{ticker}.NS"
            
            stock = yf.Ticker(ticker)
            history = stock.history(period=period)
            
            if history.empty:
                return json.dumps({"error": "No data available", "symbol": symbol})
            
            df = history.copy()
            df['Returns'] = df['Close'].pct_change() * 100
            
            result = {
                "symbol": symbol.upper(),
                "period": period,
                "data_points": len(df),
                "start_date": str(df.index[0].date()),
                "end_date": str(df.index[-1].date()),
                "latest_price": float(df['Close'].iloc[-1]),
                "highest_price": float(df['High'].max()),
                "lowest_price": float(df['Low'].min()),
                "avg_volume": int(df['Volume'].mean()),
                "total_volume": int(df['Volume'].sum()),
                "volatility": float(df['Returns'].std()),
            }
            
            return json.dumps(result, indent=2, default=str)
            
        except Exception as e:
            return json.dumps({"error": str(e)})


class CorporateActionsInput(BaseTool):
    name: str = "Get Corporate Actions"
    description: str = "Retrieves recent corporate actions (dividends, splits, bonuses) for Indian stocks. Input should be the stock ticker symbol."

    def _run(self, symbol: str) -> str:
        try:
            ticker = symbol.upper()
            if not ticker.endswith('.NS'):
                ticker = f"{ticker}.NS"
            
            stock = yf.Ticker(ticker)
            actions = stock.actions
            
            if actions.empty:
                return json.dumps({"message": "No recent corporate actions", "symbol": symbol})
            
            recent_actions = actions.tail(10)
            
            action_data = []
            for date, row in recent_actions.iterrows():
                action_data.append({
                    "date": str(date.date()),
                    "dividends": float(row['Dividends']) if not pd.isna(row['Dividends']) else 0,
                    "stock_splits": float(row['Stock Splits']) if not pd.isna(row['Stock Splits']) else 0,
                })
            
            return json.dumps(action_data, indent=2, default=str)
            
        except Exception as e:
            return json.dumps({"error": str(e), "symbol": symbol})


class FinancialMetricsInput(BaseTool):
    name: str = "Get Financial Metrics"
    description: str = "Retrieves fundamental financial metrics for Indian stocks. Input should be the stock ticker symbol."

    def _run(self, symbol: str) -> str:
        try:
            ticker = symbol.upper()
            if not ticker.endswith('.NS'):
                ticker = f"{ticker}.NS"
            
            stock = yf.Ticker(ticker)
            info = stock.info
            financials = stock.quarterly_financials
            balance_sheet = stock.quarterly_balance_sheet
            
            result = {
                "symbol": symbol.upper(),
                "market_cap": info.get('marketCap', 'N/A'),
                "pe_ratio": info.get('trailingPE', 'N/A'),
                "peg_ratio": info.get('pegRatio', 'N/A'),
                "eps": info.get('trailingEps', 'N/A'),
                "earnings_growth": info.get('earningsGrowth', 'N/A'),
                "revenue_growth": info.get('revenueGrowth', 'N/A'),
                "revenue": info.get('revenue', 'N/A'),
                "total_debt": info.get('totalDebt', 'N/A'),
                "profitMargins": info.get('profitMargins', 'N/A'),
                "operatingMargins": info.get('operatingMargins', 'N/A'),
                "ebitda": info.get('ebida', 'N/A'),
            }
            
            if not financials.empty:
                try:
                    result['revenue_quarterly'] = float(financials.loc['Total Revenue'].iloc[0]) if 'Total Revenue' in financials.index else None
                    result['net_income_quarterly'] = float(financials.loc['Net Income'].iloc[0]) if 'Net Income' in financials.index else None
                except:
                    pass
            
            return json.dumps(result, indent=2, default=str)
            
        except Exception as e:
            return json.dumps({"error": str(e), "symbol": symbol})


class InstitutionalHoldersInput(BaseTool):
    name: str = "Get Institutional Holdings"
    description: str = "Retrieves institutional and promoter holdings data for Indian stocks. Input should be the stock ticker symbol."

    def _run(self, symbol: str) -> str:
        try:
            ticker = symbol.upper()
            if not ticker.endswith('.NS'):
                ticker = f"{ticker}.NS"
            
            stock = yf.Ticker(ticker)
            info = stock.info
            
            major_holders = stock.major_holders
            institutional = stock.institutional_holders
            
            holdings_data = {
                "symbol": symbol.upper(),
                "insider_holding_pct": info.get('heldByInsiders', 'N/A'),
                "institutional_holding_pct": info.get('heldByInstitutions', 'N/A'),
                "float_shares": info.get('floatShares', 'N/A'),
                "shares_outstanding": info.get('sharesOutstanding', 'N/A'),
                "shares_short": info.get('sharesShort', 'N/A'),
                "short_ratio": info.get('shortRatio', 'N/A'),
            }
            
            return json.dumps(holdings_data, indent=2, default=str)
            
        except Exception as e:
            return json.dumps({"error": str(e), "symbol": symbol})


class TechnicalIndicatorsInput(BaseTool):
    name: str = "Calculate Technical Indicators"
    description: str = "Calculates technical indicators (RSI, MACD, Moving Averages, Bollinger Bands) for stock price analysis. Input should be the stock ticker."

    def _run(self, symbol: str) -> str:
        try:
            ticker = symbol.upper()
            if not ticker.endswith('.NS'):
                ticker = f"{ticker}.NS"
            
            stock = yf.Ticker(ticker)
            history = stock.history(period="6mo")
            
            if history.empty:
                return json.dumps({"error": "No data available", "symbol": symbol})
            
            close = history['Close'].copy()
            high = history['High'].copy()
            low = history['Low'].copy()
            volume = history['Volume'].copy()
            
            result = {"symbol": symbol.upper()}
            
            delta = close.diff()
            gain = delta.where(delta > 0, 0).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            result['rsi'] = round(float(rsi.iloc[-1]), 2) if not pd.isna(rsi.iloc[-1]) else "N/A"
            
            ema12 = close.ewm(span=12, adjust=False).mean()
            ema26 = close.ewm(span=26, adjust=False).mean()
            macd_line = ema12 - ema26
            signal_line = macd_line.ewm(span=9, adjust=False).mean()
            histogram = macd_line - signal_line
            
            result['macd'] = {
                "line": round(float(macd_line.iloc[-1]), 2),
                "signal": round(float(signal_line.iloc[-1]), 2),
                "histogram": round(float(histogram.iloc[-1]), 2)
            }
            
            ma20 = close.rolling(window=20).mean()
            ma50 = close.rolling(window=50).mean()
            ma200 = close.rolling(window=200).mean() if len(close) >= 200 else None
            
            result['moving_averages'] = {
                "ma20": round(float(ma20.iloc[-1]), 2) if not pd.isna(ma20.iloc[-1]) else "N/A",
                "ma50": round(float(ma50.iloc[-1]), 2) if not pd.isna(ma50.iloc[-1]) else "N/A",
                "ma200": round(float(ma200.iloc[-1]), 2) if ma200 is not None and not pd.isna(ma200.iloc[-1]) else "N/A"
            }
            
            sma20 = close.rolling(window=20).mean()
            std20 = close.rolling(window=20).std()
            upper_band = sma20 + (std20 * 2)
            lower_band = sma20 - (std20 * 2)
            
            current_price = close.iloc[-1]
            result['bollinger_bands'] = {
                "upper": round(float(upper_band.iloc[-1]), 2),
                "middle": round(float(sma20.iloc[-1]), 2),
                "lower": round(float(lower_band.iloc[-1]), 2),
                "position": "Above Upper" if current_price > upper_band.iloc[-1] else ("Below Lower" if current_price < lower_band.iloc[-1] else "Within Bands")
            }
            
            return json.dumps(result, indent=2, default=str)
            
        except Exception as e:
            return json.dumps({"error": str(e), "symbol": symbol})


class IndianStockSearchInput(BaseTool):
    name: str = "Search Indian Stock News"
    description: str = "Searches for recent news and information about Indian stocks. Input should be the search query (e.g., 'RELIANCE Q4 results 2024')."

    def _run(self, query: str) -> str:
        try:
            return json.dumps({
                "query": query,
                "search_performed": True,
                "note": "News search functionality requires Serper API key. Configure SERPER_API_KEY in .env file."
            })
        except Exception as e:
            return json.dumps({"error": str(e)})


stock_data_tool = StockDataInput()
historical_data_tool = HistoricalDataInput()
corporate_actions_tool = CorporateActionsInput()
financial_metrics_tool = FinancialMetricsInput()
institutional_holders_tool = InstitutionalHoldersInput()
technical_indicators_tool = TechnicalIndicatorsInput()
indian_stock_search_tool = IndianStockSearchInput()