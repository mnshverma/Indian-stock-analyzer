import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL_NAME = os.getenv("OPENAI_MODEL_NAME", "minimax/minimax-m2.5:free")
    
    SERPER_API_KEY = os.getenv("SERPER_API_KEY", "")
    
    DEFAULT_TICKERS = ["RELIANCE", "TCS", "INFY", "HDFCBANK", "ICICIBANK"]
    
    OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "reports")
    
    RSI_PERIOD = 14
    MACD_FAST = 12
    MACD_SLOW = 26
    MACD_SIGNAL = 9
    MA_SHORT = 20
    MA_MEDIUM = 50
    MA_LONG = 200
    BOLLINGER_PERIOD = 20
    BOLLINGER_STD = 2
    
    ANALYSIS_PERIODS = {
        "1mo": "1 Month",
        "3mo": "3 Months",
        "6mo": "6 Months",
        "1y": "1 Year",
        "5y": "5 Years"
    }