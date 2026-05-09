import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime
import json

st.set_page_config(
    page_title="Indian Stock Analyzer",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sidebar-header {
        font-size: 1.5rem;
        font-weight: bold;
        color: #2ecc71;
    }
    .buy-signal {
        color: #27ae60;
        font-weight: bold;
        font-size: 1.5rem;
    }
    .sell-signal {
        color: #e74c3c;
        font-weight: bold;
        font-size: 1.5rem;
    }
    .hold-signal {
        color: #f39c12;
        font-weight: bold;
        font-size: 1.5rem;
    }
    .metric-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .stButton>button {
        background-color: #1f77b4;
        color: white;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)


def get_stock_data(symbol):
    """Get comprehensive stock data"""
    ticker = f"{symbol.upper()}.NS"
    stock = yf.Ticker(ticker)
    info = stock.info
    history = stock.history(period="1y")
    
    return stock, info, history


def calculate_technical_indicators(history):
    """Calculate technical indicators"""
    close = history['Close'].copy()
    
    delta = close.diff()
    gain = delta.where(delta > 0, 0).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    
    ema12 = close.ewm(span=12, adjust=False).mean()
    ema26 = close.ewm(span=26, adjust=False).mean()
    macd_line = ema12 - ema26
    signal_line = macd_line.ewm(span=9, adjust=False).mean()
    histogram = macd_line - signal_line
    
    ma20 = close.rolling(window=20).mean()
    ma50 = close.rolling(window=50).mean()
    ma200 = close.rolling(window=200).mean() if len(close) >= 200 else None
    
    sma20 = close.rolling(window=20).mean()
    std20 = close.rolling(window=20).std()
    bb_upper = sma20 + (std20 * 2)
    bb_lower = sma20 - (std20 * 2)
    
    current_price = close.iloc[-1]
    
    return {
        "rsi": rsi.iloc[-1] if not pd.isna(rsi.iloc[-1]) else 50,
        "macd": macd_line.iloc[-1],
        "macd_signal": signal_line.iloc[-1],
        "macd_histogram": histogram.iloc[-1],
        "ma20": ma20.iloc[-1],
        "ma50": ma50.iloc[-1],
        "ma200": ma200.iloc[-1] if ma200 is not None else None,
        "bb_upper": bb_upper.iloc[-1],
        "bb_middle": sma20.iloc[-1],
        "bb_lower": bb_lower.iloc[-1],
        "current_price": current_price,
        "close_data": close
    }


def generate_recommendation(tech_data, info):
    """Generate investment recommendation"""
    signals = []
    weights = []
    
    rsi = tech_data['rsi']
    if rsi < 30:
        signals.append("Oversold - Potential Buy")
        weights.append(1)
    elif rsi > 70:
        signals.append("Overbought - Potential Sell")
        weights.append(-1)
    else:
        signals.append("RSI Neutral")
        weights.append(0)
    
    macd = tech_data['macd']
    macd_signal = tech_data['macd_signal']
    if macd > macd_signal:
        signals.append("MACD Bullish")
        weights.append(1)
    else:
        signals.append("MACD Bearish")
        weights.append(-1)
    
    price = tech_data['current_price']
    ma50 = tech_data['ma50']
    ma200 = tech_data['ma200']
    
    if ma200:
        if price > ma200 and price > ma50:
            signals.append("Strong Uptrend")
            weights.append(2)
        elif price < ma200:
            signals.append("Below 200-MA Bearish")
            weights.append(-2)
        else:
            signals.append("Price Above 50-MA")
            weights.append(1)
    
    bb_upper = tech_data['bb_upper']
    bb_lower = tech_data['bb_lower']
    if price < bb_lower:
        signals.append("Near Lower Bollinger Band")
        weights.append(1)
    elif price > bb_upper:
        signals.append("Near Upper Bollinger Band")
        weights.append(-1)
    
    total_weight = sum(weights)
    
    if total_weight >= 2:
        recommendation = "STRONG BUY"
        action = "Buy"
    elif total_weight >= 0:
        recommendation = "BUY"
        action = "Consider Buying"
    elif total_weight >= -2:
        recommendation = "HOLD"
        action = "Hold"
    else:
        recommendation = "SELL"
        action = "Sell"
    
    target_price = price * 1.15
    stop_loss = price * 0.95
    
    return {
        "recommendation": recommendation,
        "action": action,
        "signals": signals,
        "total_weight": total_weight,
        "target_price": target_price,
        "stop_loss": stop_loss,
        "current_price": price,
        "upside": ((target_price - price) / price) * 100,
        "downside": ((price - stop_loss) / price) * 100
    }


def format_market_cap(value):
    """Format market cap"""
    if value >= 1e12:
        return f"₹{value/1e12:.2f}T"
    elif value >= 1e10:
        return f"₹{value/1e10:.2f}B"
    return f"₹{value:,.0f}"


def main():
    st.markdown('<p class="main-header">📈 Indian Stock Analyzer</p>', unsafe_allow_html=True)
    st.markdown("---")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown('<p class="sidebar-header">🔍 Stock Search</p>', unsafe_allow_html=True)
        
        symbol = st.text_input("Enter Stock Symbol", placeholder="e.g., RELIANCE, TCS, INFY, HDFCBANK")
        
        search_button = st.button("Analyze Stock", type="primary")
        
        st.markdown("### Quick Stats")
        st.info("📊 Enter a NSE stock symbol (without .NS) to analyze Indian stocks listed on NSE/BSE.")
        
        popular_stocks = ["RELIANCE", "TCS", "INFY", "HDFCBANK", "ICICIBANK", "SBIN", "KOTAKBANK", "HUL"]
        selected = st.selectbox("Popular Stocks", popular_stocks)
        if st.button(f"Analyze {selected}"):
            symbol = selected
    
    with col2:
        if search_button and symbol:
            with st.spinner(f"Analyzing {symbol.upper()}..."):
                try:
                    stock, info, history = get_stock_data(symbol)
                    tech_data = calculate_technical_indicators(history)
                    recommendation = generate_recommendation(tech_data, info)
                    
                    current_price = info.get('currentPrice', 0)
                    prev_close = info.get('previousClose', current_price)
                    
                    col_a, col_b, col_c, col_d = st.columns(4)
                    
                    with col_a:
                        st.metric("Current Price", f"₹{current_price}", f"{((current_price-prev_close)/prev_close*100):.2f}%")
                    with col_b:
                        st.metric("Market Cap", format_market_cap(info.get('marketCap', 0)))
                    with col_c:
                        st.metric("P/E Ratio", f"{info.get('trailingPE', 'N/A'):.2f}" if info.get('trailingPE') else "N/A")
                    with col_d:
                        st.metric("52W High", f"₹{info.get('fiftyTwoWeekHigh', 0)}")
                    
                    st.markdown("---")
                    
                    st.markdown(f"### 📋 Investment Recommendation")
                    
                    if recommendation['recommendation'] in ['STRONG BUY', 'BUY']:
                        signal_class = "buy-signal"
                    elif recommendation['recommendation'] == 'SELL':
                        signal_class = "sell-signal"
                    else:
                        signal_class = "hold-signal"
                    
                    st.markdown(f"""
                    <div style='background: linear-gradient(90deg, #1f77b4, #2ecc71); padding: 1.5rem; border-radius: 1rem; text-align: center;'>
                        <h2 style='color: white; margin: 0;'>{recommendation['recommendation']}</h2>
                        <p style='color: white; margin: 0.5rem 0;'>{recommendation['action']}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    col_rec1, col_rec2, col_rec3 = st.columns(3)
                    
                    with col_rec1:
                        st.markdown("#### 🎯 Target Price")
                        st.markdown(f"**Target:** ₹{recommendation['target_price']:.2f}")
                        st.markdown(f"**Upside:** +{recommendation['upside']:.1f}%")
                    
                    with col_rec2:
                        st.markdown("#### 🛡️ Stop Loss")
                        st.markdown(f"**Stop Loss:** ₹{recommendation['stop_loss']:.2f}")
                        st.markdown(f"**Downside Risk:** -{recommendation['downside']:.1f}%")
                    
                    with col_rec3:
                        st.markdown("#### ⏰ Time Horizon")
                        st.markdown("**Recommended:** 3-6 Months")
                        st.markdown("For medium-term gains")
                    
                    st.markdown("---")
                    
                    col_tech1, col_tech2 = st.columns(2)
                    
                    with col_tech1:
                        st.markdown("### 📊 Technical Indicators")
                        
                        rsi = tech_data['rsi']
                        rsi_status = "🟢 Oversold" if rsi < 30 else ("🔴 Overbought" if rsi > 70 else "🟡 Neutral")
                        st.write(f"**RSI (14):** {rsi:.2f} - {rsi_status}")
                        
                        macd = tech_data['macd']
                        macd_signal = tech_data['macd_signal']
                        macd_status = "🟢 Bullish" if macd > macd_signal else "🔴 Bearish"
                        st.write(f"**MACD:** {macd:.2f} - {macd_status}")
                        
                        st.write(f"**MA20:** ₹{tech_data['ma20']:.2f}")
                        st.write(f"**MA50:** ₹{tech_data['ma50']:.2f}")
                        if tech_data['ma200']:
                            st.write(f"**MA200:** ₹{tech_data['ma200']:.2f}")
                        
                        bb_lower = tech_data['bb_lower']
                        bb_upper = tech_data['bb_upper']
                        st.write(f"**Bollinger Bands:** ₹{bb_lower:.2f} - ₹{bb_upper:.2f}")
                    
                    with col_tech2:
                        st.markdown("### 💼 Fundamental Data")
                        
                        st.write(f"**Company:** {info.get('longName', 'N/A')}")
                        st.write(f"**Sector:** {info.get('sector', 'N/A')}")
                        st.write(f"**Industry:** {info.get('industry', 'N/A')}")
                        st.write(f"**EPS:** ₹{info.get('trailingEps', 'N/A'):.2f}")
                        st.write(f"**Div Yield:** {info.get('dividendYield', 0)*100 if info.get('dividendYield') else 0:.2f}%")
                        st.write(f"**Beta:** {info.get('beta', 'N/A'):.2f}")
                        st.write(f"**Volume:** {info.get('volume', 0):,}")
                    
                    st.markdown("---")
                    
                    st.markdown("### 📈 Technical Signals")
                    
                    for signal in recommendation['signals']:
                        st.write(f"- {signal}")
                    
                    st.markdown("---")
                    
                    st.markdown("""
                    ### ⚠️ Disclaimer
                    This analysis is generated by an AI system and should not be considered as professional financial advice. 
                    Investors should conduct their own due diligence and consult with qualified financial advisors 
                    before making investment decisions. Stock market investments involve risks.
                    """)
                    
                except Exception as e:
                    st.error(f"Error analyzing {symbol}: {str(e)}")
        else:
            st.info("👈 Enter a stock symbol on the left and click 'Analyze Stock' to begin analysis")
            
            st.markdown("### How to Use")
            st.markdown("""
            1. **Enter Stock Symbol** - Type a NSE stock code (e.g., RELIANCE, TCS, INFY)
            2. **Click Analyze** - The system will fetch and analyze the stock
            3. **View Results** - See recommendation, target price, and stop-loss
            4. **Make Decision** - Use the analysis to inform your investment
            """)
            
            st.markdown("### Available Stocks")
            st.markdown("""
            - **Banking:** HDFCBANK, ICICIBANK, SBIN, KOTAKBANK
            - **IT:** TCS, INFY, WIPRO, HCLTECH
            - **Energy:** RELIANCE, ONGC, BPCL
            - **FMCG:** HUL, NESTLE, BRITANNIA
            - **Auto:** MARUTI, TATAMOTORS, M&M
            """)


if __name__ == "__main__":
    main()