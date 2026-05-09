"""
Multi-Agent Stock Analysis Crew using CrewAI
Sequential flow: Data Research → Fundamentals → Technical → Sentiment → Final Recommendation
"""

from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI
import os
from dotenv import load_dotenv

load_dotenv()


# Create LLM
def get_llm():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return None
    return ChatOpenAI(
        model="gpt-4",
        openai_api_key=api_key,
        temperature=0.3
    )


# ============================================================
# AGENT 1: Market Data Researcher
# ============================================================
market_researcher = Agent(
    role="Market Data Researcher",
    goal="Fetch real-time market data for Indian stocks (NSE/BSE) including price, volume, P/E, market cap",
    backstory="""You are an expert in retrieving stock market data from Yahoo Finance.
    You specialize in getting current price, trading volume, P/E ratio, market capitalization,
    52-week high/low for Indian stocks listed on NSE/BSE.""",
    verbose=True,
    allow_delegation=False
)


# ============================================================
# AGENT 2: Fundamental Analyst  
# ============================================================
fundamental_analyst = Agent(
    role="Fundamental Analyst",
    goal="Analyze financial health - EPS, revenue, debt, ROE, dividend yield, promoter holdings",
    backstory="""You are a seasoned fundamental analyst with 15+ years experience.
    You analyze earnings per share (EPS), revenue growth, debt-to-equity ratio, 
    return on equity (ROE), dividend yield, and promoter holdings.""",
    verbose=True,
    allow_delegation=False
)


# ============================================================
# AGENT 3: Technical Analyst
# ============================================================
technical_analyst = Agent(
    role="Technical Analyst",
    goal="Analyze price trends using RSI, MACD, Moving Averages, and predict future price movements",
    backstory="""You are a technical analysis expert specializing in Indian stock markets.
    You analyze RSI (14-period), MACD (12,26,9), Moving Averages (20,50,200-day),
    Bollinger Bands, and identify trends. You predict future price movements.""",
    verbose=True,
    allow_delegation=False
)


# ============================================================
# AGENT 4: Sentiment Analyst
# ============================================================
sentiment_analyst = Agent(
    role="Sentiment & News Analyst",
    goal="Monitor market sentiment and news impact on stock price",
    backstory="""You monitor financial news from Moneycontrol, Economic Times.
    You gauge market mood, news impact, and macroeconomic factors like RBI policy.""",
    verbose=True,
    allow_delegation=False
)


# ============================================================
# AGENT 5: Investment Strategist (Final Decision)
# ============================================================
investment_strategist = Agent(
    role="Investment Strategist",
    goal="Synthesize all analysis to provide Buy/Sell/Hold with target price and stop loss",
    backstory="""You are a senior investment strategist. You integrate all data from:
    - Market Data Researcher (price, P/E, volume)
    - Fundamental Analyst (EPS, ROE, debt)
    - Technical Analyst (RSI, MACD, trends)
    - Sentiment Analyst (news, mood)
    
    Provide: Recommendation, Target Price, Stop Loss, Time Horizon""",
    verbose=True,
    allow_delegation=True
)


# ============================================================
# TASKS
# ============================================================

task1_description = """
Fetch comprehensive market data for {symbol}:

1. Current price and previous close
2. Trading volume
3. P/E ratio
4. Market capitalization
5. 52-week high and low
6. Dividend yield

Return data in structured format.
"""

task2_description = """
Perform fundamental analysis for {symbol}:

1. Earnings per share (EPS)
2. Annual revenue
3. Debt-to-equity ratio
4. Return on Equity (ROE)
5. Dividend yield percentage
6. Promoter holdings %
7. Institutional holdings %

Return financial ratios.
"""

task3_description = """
Analyze technical indicators for {symbol}:

1. Calculate RSI (14-period)
2. Calculate MACD (12,26,9)
3. Moving Averages (20, 50, 200-day)
4. Current trend direction (bullish/bearish)
5. Support and resistance levels

Predict 3-month and 6-month price targets.
"""

task4_description = """
Analyze market sentiment for {symbol}:

1. Recent news from financial sources
2. Overall market mood (positive/negative/neutral)
3. Key news impact
4. Macroeconomic factors (RBI policy if relevant)

Return sentiment score.
"""

task5_description = """
Create final investment recommendation for {symbol}:

Synthesize all data from previous 4 agents:
- Market data
- Fundamentals  
- Technical analysis
- Sentiment analysis

Provide:
1. Recommendation: STRONG BUY / BUY / HOLD / SELL / STRONG SELL
2. Target Price (12 months)
3. Stop Loss Level
4. Time Horizon (short/medium/long term)
5. Rationale

Format as professional investment memorandum.
"""


# ============================================================
# CREATE CREW
# ============================================================

def create_stock_crew(symbol):
    """Create sequential crew for stock analysis"""
    
    llm = get_llm()
    if not llm:
        return None, "No OpenAI API key. Set OPENAI_API_KEY in .env"
    
    # Create tasks
    task1 = Task(
        description=task1_description.format(symbol=symbol),
        agent=market_researcher,
        expected_output="Market data for {symbol}"
    )
    
    task2 = Task(
        description=task2_description.format(symbol=symbol),
        agent=fundamental_analyst,
        expected_output="Fundamental analysis"
    )
    
    task3 = Task(
        description=task3_description.format(symbol=symbol),
        agent=technical_analyst,
        expected_output="Technical analysis with price predictions"
    )
    
    task4 = Task(
        description=task4_description.format(symbol=symbol),
        agent=sentiment_analyst,
        expected_output="Sentiment analysis"
    )
    
    task5 = Task(
        description=task5_description.format(symbol=symbol),
        agent=investment_strategist,
        expected_output="Investment recommendation memorandum"
    )
    
    # Create crew with sequential process
    crew = Crew(
        agents=[market_researcher, fundamental_analyst, technical_analyst, 
                sentiment_analyst, investment_strategist],
        tasks=[task1, task2, task3, task4, task5],
        process=Process.sequential,
        verbose=True,
        manager_agent=investment_strategist
    )
    
    return crew


# ============================================================
# RUN ANALYSIS
# ============================================================

def run_stock_analysis(symbol):
    """Run complete stock analysis using 5 agents"""
    
    crew = create_stock_crew(symbol)
    if isinstance(crew, str):
        return {"error": crew}
    
    try:
        result = crew.kickoff()
        return {
            "symbol": symbol.upper(),
            "result": str(result),
            "status": "success"
        }
    except Exception as e:
        return {
            "symbol": symbol.upper(),
            "error": str(e),
            "status": "failed"
        }


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":
    # Test with a stock
    result = run_stock_analysis("RELIANCE")
    print(result)