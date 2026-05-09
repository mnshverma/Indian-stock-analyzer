# Indian Stock Analysis Multi-Agent System - Specification

## 1. Project Overview

**Project Name:** IndiaStockAnalyzer
**Type:** Multi-Agent AI System using CrewAI Framework
**Core Functionality:** Analyze Indian equity stocks (NSE/BSE) through autonomous specialized agents to provide investment recommendations
**Target Users:** Retail investors, portfolio managers, financial analysts focused on Indian markets

## 2. Architecture

### Agent Crew Structure

1. **Market Data Researcher Agent**
   - Role: Data Collection
   - Tools: YFinance, Screener.in API, NSE Tools
   - Data: Real-time price, volume, P/E, market cap, corporate actions

2. **Fundamental Analyst Agent**
   - Role: Deep Financial Analysis
   - Focus: Earnings, ratios, promoter holdings, sector trends

3. **Technical Analyst Agent**
   - Role: Price Pattern Analysis
   - Indicators: RSI, MACD, Moving Averages, Bollinger Bands, Candlesticks

4. **Sentiment & News Analyst Agent**
   - Role: Market Mood Monitoring
   - Sources: Moneycontrol, Economic Times, Social Media

5. **Investment Strategist Agent**
   - Role: Synthesis & Decision
   - Output: Buy/Sell/Hold with rationale, targets, risk parameters

### Process Flow
- **Hierarchical Process** - Manager agent coordinates sub-agents
- Data flows: Research → Analysis → Strategy

## 3. Functionality Specification

### Core Features

1. **Stock Data Retrieval**
   - Fetch NSE/BSE stock data using YFinance
   - Historical price data (1D, 1W, 1M, 3M, 6M, 1Y, 5Y)
   - Key metrics: price, volume, P/E, market cap, dividend yield

2. **Fundamental Analysis**
   - Quarterly earnings review
   - Financial ratios: Debt/Equity, ROE, ROCE, Current Ratio
   - Promoter holding percentage
   - Sector performance comparison

3. **Technical Analysis**
   - RSI (14-period)
   - MACD (12, 26, 9)
   - Moving Averages (20, 50, 200-day)
   - Bollinger Bands (20, 2)
   - Candlestick patterns

4. **Sentiment Analysis**
   - News aggregation from Indian sources
   - Sentiment scoring (Positive/Neutral/Negative)
   - Key news impact assessment

5. **Investment Recommendation**
   - Rating: Strong Buy / Buy / Hold / Sell / Strong Sell
   - Target price (12-month)
   - Stop-loss level
   - Time horizon: Short-term / Medium-term / Long-term
   - Risk assessment

### Data Sources
- YFinance (primary)
- Screener.in (fundamental data)
- NSE India (official data)
- Moneycontrol (news)

## 4. Acceptance Criteria

1. System successfully analyzes NSE-listed stocks
2. All 5 agents produce valid outputs
3. Final recommendation includes buy/sell/hold with targets
4. Risk parameters included in every recommendation
5. Output formatted as professional investment memorandum
6. Process completes without errors