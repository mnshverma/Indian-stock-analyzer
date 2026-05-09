import os
import json
import requests
from typing import Optional, List, Dict
from crewai.tools import BaseTool
from pydantic import Field
import yfinance as yf


class IndianStockNewsSearchTool(BaseTool):
    name: str = "Get Stock News from Yahoo Finance"
    description: str = "Retrieves news and recent information about Indian stocks using Yahoo Finance API. No API key required."

    def _run(self, query: str) -> str:
        try:
            ticker = f"{query.upper()}.NS"
            stock = yf.Ticker(ticker)
            
            news = stock.news
            if not news:
                return json.dumps({
                    "query": query,
                    "news_items": [],
                    "message": "No recent news available"
                })
            
            news_items = []
            for item in news[:10]:
                news_items.append({
                    "title": item.get("title", ""),
                    "publisher": item.get("publisher", ""),
                    "link": item.get("link", ""),
                    "published": item.get("published", "")
                })
            
            return json.dumps({
                "query": query,
                "news_items": news_items,
                "count": len(news_items)
            }, indent=2, default=str)
            
        except Exception as e:
            return json.dumps({"error": str(e)})


class MoneycontrolNewsTool(BaseTool):
    name: str = "Get Stock News"
    description: str = "Fetches latest news for Indian stocks using Yahoo Finance. Input should be the stock ticker symbol."

    def _run(self, symbol: str) -> str:
        try:
            api_key = os.getenv("SERPER_API_KEY")
            
            if not api_key:
                ticker = f"{symbol.upper()}.NS"
                stock = yf.Ticker(ticker)
                news = stock.news
                
                if not news:
                    return json.dumps({
                        "symbol": symbol.upper(),
                        "message": "No recent news available via Yahoo Finance"
                    })
                
                news_items = []
                for item in news[:5]:
                    news_items.append({
                        "title": item.get("title", ""),
                        "publisher": item.get("publisher", "")
                    })
                
                return json.dumps({
                    "symbol": symbol.upper(),
                    "news_items": news_items,
                    "count": len(news_items)
                }, indent=2)
            
        except Exception as e:
            return json.dumps({"error": str(e)})


class SectorPerformanceTool(BaseTool):
    name: str = "Get Sector Performance"
    description: str = "Analyzes sector performance for Indian stocks. Input should be the sector name."

    def _run(self, sector: str) -> str:
        try:
            stock_data = {
                "IT": ["TCS", "INFY", "WIPRO", "HCLTECH"],
                "Banking": ["HDFCBANK", "ICICIBANK", "SBIN", "KOTAKBANK"],
                "Auto": ["MARUTI", "TATAMOTORS", "M&M", "BAJAJ-AUTO"],
                "Pharma": ["SUNPHARMA", "DRREDDY", "CIPLA", "DIVISLAB"],
                "Energy": ["RELIANCE", "ONGC", "BPCL", "COALINDIA"],
                "FMCG": ["HUL", "NESTLE", "BRITANNIA", "DABUR"],
                "Metal": ["TATASTEEL", "JSWSTEEL", "HINDALCO", "VEDANTA"]
            }
            
            sector_stocks = stock_data.get(sector.upper(), [])
            
            if not sector_stocks:
                return json.dumps({
                    "sector": sector,
                    "note": "Sector not recognized",
                    "available_sectors": list(stock_data.keys())
                })
            
            results = []
            for stock_symbol in sector_stocks:
                try:
                    ticker = f"{stock_symbol}.NS"
                    stock = yf.Ticker(ticker)
                    info = stock.info
                    results.append({
                        "symbol": stock_symbol,
                        "price": info.get('currentPrice', 'N/A'),
                        "change": info.get('regularMarketChange', 'N/A'),
                        "change_pct": info.get('regularMarketChangePercent', 'N/A')
                    })
                except:
                    pass
            
            return json.dumps({
                "sector": sector.upper(),
                "stocks": results,
                "analyzed": len(results)
            }, indent=2)
            
        except Exception as e:
            return json.dumps({"error": str(e)})


indian_stock_news_search_tool = IndianStockNewsSearchTool()
moneycontrol_news_tool = MoneycontrolNewsTool()
sector_performance_tool = SectorPerformanceTool()