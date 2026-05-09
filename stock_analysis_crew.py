from crewai import Agent, Task, Process
from typing import List, Dict, Any
import json
from datetime import datetime

from .tools.stock_tools import (
    stock_data_tool,
    historical_data_tool,
    corporate_actions_tool,
    financial_metrics_tool,
    institutional_holders_tool,
    technical_indicators_tool,
    indian_stock_search_tool
)
from .tools.news_tools import (
    indian_stock_news_search_tool,
    moneycontrol_news_tool,
    sector_performance_tool
)


def create_market_researcher_agent() -> Agent:
    return Agent(
        role="Market Data Researcher",
        goal="Retrieve accurate real-time and historical market data for Indian stocks including price, volume, P/E ratios, market cap, and corporate actions",
        backstory=(
            "You are an expert financial data researcher with deep knowledge of Indian stock markets (NSE/BSE). "
            "You specialize in retrieving and verifying stock market data from reliable financial data sources. "
            "Your expertise includes analyzing price movements, volume patterns, and corporate announcements."
        ),
        tools=[
            stock_data_tool,
            historical_data_tool,
            corporate_actions_tool
        ],
        verbose=True,
        allow_delegation=False
    )


def create_fundamental_analyst_agent() -> Agent:
    return Agent(
        role="Fundamental Analyst",
        goal="Perform comprehensive fundamental analysis including financial ratios, earnings, and promoter holdings",
        backstory=(
            "You are a seasoned fundamental analyst with 15+ years of experience analyzing Indian companies. "
            "You excel at evaluating financial health through ratios like Debt-to-Equity, ROE, ROCE, and understanding "
            "promoter holding patterns. Your analysis focuses on long-term value creation and financial stability."
        ),
        tools=[
            financial_metrics_tool,
            institutional_holders_tool,
            stock_data_tool
        ],
        verbose=True,
        allow_delegation=False
    )


def create_technical_analyst_agent() -> Agent:
    return Agent(
        role="Technical Analyst",
        goal="Analyze price action using technical indicators to identify optimal entry and exit points for Indian stocks",
        backstory=(
            "You are a technical analysis expert specializing in Indian stock markets. "
            "You use RSI, MACD, Moving Averages, Bollinger Bands, and candlestick patterns to identify "
            "optimal entry and exit points. Your analysis focuses on price momentum and trend reversals."
        ),
        tools=[
            technical_indicators_tool,
            historical_data_tool
        ],
        verbose=True,
        allow_delegation=False
    )


def create_sentiment_analyst_agent() -> Agent:
    return Agent(
        role="Sentiment & News Analyst",
        goal="Monitor financial news and social sentiment to gauge market mood regarding specific Indian stocks",
        backstory=(
            "You are a financial news analyst specializing in Indian markets. You monitor sources like "
            "Moneycontrol, Economic Times, and Bloomberg Quint to gauge market sentiment. "
            "You analyze how news and macroeconomic factors (RBI policy, budget announcements) affect stock performance."
        ),
        tools=[
            indian_stock_news_search_tool,
            moneycontrol_news_tool,
            sector_performance_tool
        ],
        verbose=True,
        allow_delegation=False
    )


def create_investment_strategist_agent() -> Agent:
    return Agent(
        role="Investment Strategist",
        goal="Synthesize all analysis outputs into a cohesive investment report with Buy/Sell/Hold recommendations",
        backstory=(
            "You are a senior investment strategist with expertise in Indian equity markets. "
            "You integrate data from all analysis streams to provide actionable investment recommendations. "
            "Your recommendations include rating, target price, stop-loss, time horizon, and comprehensive risk assessment."
        ),
        tools=[
            stock_data_tool,
            sector_performance_tool
        ],
        verbose=True,
        allow_delegation=True
    )


class StockAnalysisCrew:
    """Multi-Agent Stock Analysis System for Indian Equity Markets"""
    
    def __init__(self, stock_symbol: str, company_name: str = None):
        self.stock_symbol = stock_symbol.upper()
        self.company_name = company_name or stock_symbol
        self.agents = {}
        self.tasks = {}
        self.crew = None
        self._initialize_agents()
    
    def _initialize_agents(self):
        """Initialize all agents for the crew"""
        self.agents['researcher'] = create_market_researcher_agent()
        self.agents['fundamental'] = create_fundamental_analyst_agent()
        self.agents['technical'] = create_technical_analyst_agent()
        self.agents['sentiment'] = create_sentiment_analyst_agent()
        self.agents['strategist'] = create_investment_strategist_agent()
    
    def _create_tasks(self) -> List[Task]:
        """Create analysis tasks for the crew"""
        
        task_market_data = Task(
            description=f"""
            Research and retrieve comprehensive market data for {self.stock_symbol}.
            
            1. Get current stock information including:
               - Current price and previous close
               - 52-week high and low
               - Trading volume
               - P/E ratio and market cap
               - Dividend yield
               
            2. Get historical price data for analysis periods:
               - 1 month, 3 months, 6 months, 1 year
               
            3. Get recent corporate actions:
               - Dividends, stock splits, bonuses
               
            Output all data in structured JSON format.
            """,
            agent=self.agents['researcher'],
            expected_output="Comprehensive market data report in JSON format"
        )
        
        task_fundamental = Task(
            description=f"""
            Perform fundamental analysis for {self.stock_symbol}.
            
            1. Analyze financial metrics:
               - Revenue and earnings growth
               - Profit margins (operating, net)
               - P/E and PEG ratios
               - Debt-to-equity ratio
               - Return on Equity (ROE)
               - Return on Capital Employed (ROCE)
               
            2. Analyze ownership:
               - Promoter holding percentage
               - Institutional holding
               - Foreign institutional investor (FII) positions
               
            3. Sector analysis:
               - Compare with sector peers
               - Industry positioning
               
            Output detailed fundamental analysis in JSON format.
            """,
            agent=self.agents['fundamental'],
            expected_output="Detailed fundamental analysis report in JSON format"
        )
        
        task_technical = Task(
            description=f"""
            Perform technical analysis for {self.stock_symbol}.
            
            1. Calculate and analyze:
               - RSI (14-period)
               - MACD (12, 26, 9)
               - Moving Averages (20, 50, 200-day)
               - Bollinger Bands (20, 2)
               
            2. Identify:
               - Current trend direction
               - Support and resistance levels
               - Price momentum
               - Overbought/oversold conditions
               
            3. Provide entry/exit recommendations based on:
               - Technical indicators alignment
               - Price patterns
               
            Output technical analysis with trading signals.
            """,
            agent=self.agents['technical'],
            expected_output="Technical analysis report with trading signals"
        )
        
        task_sentiment = Task(
            description=f"""
            Analyze market sentiment and news for {self.stock_symbol}.
            
            1. Search recent news:
               - Moneycontrol, Economic Times coverage
               - Company announcements
               - Analyst upgrades/downgrades
               
            2. Analyze sentiment:
               - Overall market mood (positive/negative/neutral)
               - Key news impact assessment
               
            3. Macroeconomic factors:
               - RBI policy impact
               - Budget announcements
               - Regulatory changes
               
            Output sentiment analysis report.
            """,
            agent=self.agents['sentiment'],
            expected_output="Sentiment and news analysis report"
        )
        
        task_strategy = Task(
            description=f"""
            Create comprehensive investment recommendation for {self.stock_symbol}.
            
            Synthesize outputs from:
            1. Market Data Researcher
            2. Fundamental Analyst
            3. Technical Analyst
            4. Sentiment & News Analyst
            
            Final output must include:
            - Investment Rating: Strong Buy / Buy / Hold / Sell / Strong Sell
            - Target Price (12-month)
            - Stop-Loss Level
            - Time Horizon: Short-term / Medium-term / Long-term
            - Rationale (comprehensive explanation)
            - Risk Assessment with specific parameters
            - Key catalysts and concerns
            
            Format as professional investment memorandum.
            """,
            agent=self.agents['strategist'],
            expected_output="Professional investment recommendation memorandum"
        )
        
        self.tasks = {
            'market_data': task_market_data,
            'fundamental': task_fundamental,
            'technical': task_technical,
            'sentiment': task_sentiment,
            'strategy': task_strategy
        }
        
        return [
            task_market_data,
            task_fundamental,
            task_technical,
            task_sentiment,
            task_strategy
        ]
    
    def create_crew(self, process: Process = Process.hierarchical) -> 'Crew':
        """Create the crew with hieride_rchical process flow"""
        
        tasks = self._create_tasks()
        
        from crewai import Crew
        
        self.crew = Crew(
            agents=[
                self.agents['researcher'],
                self.agents['fundamental'],
                self.agents['technical'],
                self.agents['sentiment'],
                self.agents['strategist']
            ],
            tasks=tasks,
            process=process,
            manager_agent=self.agents['strategist'],
            verbose=True,
            memory=True
        )
        
        return self.crew
    
    def run_analysis(self) -> Dict[str, Any]:
        """Execute the analysis crew"""
        
        if not self.crew:
            self.create_crew()
        
        result = self.crew.kickoff()
        
        return {
            "symbol": self.stock_symbol,
            "analysis_date": datetime.now().isoformat(),
            "result": str(result)
        }
    
    def get_crew(self) -> 'Crew':
        """Get the created crew"""
        if not self.crew:
            self.create_crew()
        return self.crew


def create_stock_analysis_crew(stock_symbol: str) -> StockAnalysisCrew:
    """Factory function to create stock analysis crew"""
    return StockAnalysisCrew(stock_symbol)