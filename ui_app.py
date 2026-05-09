import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(
    page_title="Indian Stock Analyzer",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    * { font-family: 'Inter', sans-serif; }
    
    .block-container { padding: 2rem; }
    
    .main-header {
        font-size: 2rem;
        font-weight: 700;
        color: #0d47a1;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    
    .sub-header {
        font-size: 1rem;
        color: #666;
        text-align: center;
        margin-bottom: 1.5rem;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.25rem;
        border-radius: 12px;
        color: white;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    .metric-card.green { background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); }
    .metric-card.red { background: linear-gradient(135deg, #eb3349 0%, #f45c43 100%); }
    .metric-card.orange { background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); }
    .metric-card.blue { background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); }
    
    .metric-value { font-size: 1.75rem; font-weight: 700; }
    .metric-label { font-size: 0.85rem; opacity: 0.9; }
    .metric-delta { font-size: 0.9rem; font-weight: 500; }
    
    .signal-box {
        padding: 1.5rem;
        border-radius: 16px;
        text-align: center;
        margin: 1rem 0;
    }
    
    .signal-buy {
        background: linear-gradient(135deg, #d4fc79 0%, #96e6a1 100%);
        border: 3px solid #00c853;
    }
    
    .signal-strong-buy {
        background: linear-gradient(135deg, #00c853 0%, #009624 100%);
        color: white;
        border: 3px solid #004d40;
    }
    
    .signal-sell {
        background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 99%, #fecfef 100%);
        border: 3px solid #d50000;
    }
    
    .signal-hold {
        background: linear-gradient(135deg, #fff6b7 0%, #f6416c 2%, #fff6b7 100%);
        border: 3px solid #ffab00;
    }
    
    .card {
        background: white;
        border-radius: 12px;
        padding: 1.25rem;
        box-shadow: 0 2px 12px rgba(0,0,0,0.08);
        margin-bottom: 1rem;
    }
    
    .card-title {
        font-size: 1rem;
        font-weight: 600;
        color: #1a237e;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .indicator-box {
        display: inline-block;
        padding: 0.4rem 0.8rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 500;
        margin: 0.25rem;
    }
    
    .indicator-bullish { background: #c8e6c9; color: #2e7d32; }
    .indicator-bearish { background: #ffcdd2; color: #c62828; }
    .indicator-neutral { background: #fff9c4; color: #f57f17; }
    
    .news-item {
        padding: 0.75rem;
        border-left: 3px solid #1976d2;
        background: #f5f5f5;
        margin-bottom: 0.5rem;
        border-radius: 0 8px 8px 0;
    }
    
    .news-title { font-weight: 500; font-size: 0.9rem; }
    .news-source { font-size: 0.75rem; color: #666; }
    
    .stTextInput > div > div { border-radius: 8px; }
    .stButton > button {
        border-radius: 8px;
        font-weight: 600;
        padding: 0.5rem 1.5rem;
    }
    
    div[data-testid="stMetric"] {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    
    .recommendation-badge {
        font-size: 2rem;
        font-weight: 800;
        padding: 1rem 2rem;
        border-radius: 12px;
        display: inline-block;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_data(ttl=3600)
def get_stock_data(symbol):
    """Get comprehensive stock data"""
    ticker = f"{symbol.upper()}.NS"
    stock = yf.Ticker(ticker)
    info = stock.info
    history = stock.history(period="2y")
    news = stock.news
    
    return stock, info, history, news


@st.cache_data(ttl=3600)
def calculate_technical_indicators(history):
    """Calculate technical indicators"""
    close = history['Close'].copy()
    high = history['High'].copy()
    low = history['Low'].copy()
    volume = history['Volume'].copy()
    
    delta = close.diff()
    gain = delta.where(delta > 0, 0).ewm(span=14, adjust=False).mean()
    loss = (-delta.where(delta < 0, 0)).ewm(span=14, adjust=False).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    
    ema12 = close.ewm(span=12, adjust=False).mean()
    ema26 = close.ewm(span=26, adjust=False).mean()
    macd_line = ema12 - ema26
    signal_line = macd_line.ewm(span=9, adjust=False).mean()
    histogram = macd_line - signal_line
    
    sma20 = close.rolling(window=20).mean()
    sma50 = close.rolling(window=50).mean()
    sma200 = close.rolling(window=200).mean() if len(close) >= 200 else None
    
    bb_middle = close.rolling(window=20).mean()
    bb_std = close.rolling(window=20).std()
    bb_upper = bb_middle + (bb_std * 2)
    bb_lower = bb_middle - (bb_std * 2)
    
    rsi_prev = rsi.iloc[-5] if len(rsi) > 5 else rsi.iloc[0]
    rsi_change = rsi.iloc[-1] - rsi_prev
    
    return {
        "rsi": rsi.iloc[-1] if not pd.isna(rsi.iloc[-1]) else 50,
        "rsi_change": rsi_change,
        "macd": macd_line.iloc[-1],
        "macd_signal": signal_line.iloc[-1],
        "macd_histogram": histogram.iloc[-1],
        "macd_crossover": "BULLISH" if macd_line.iloc[-1] > signal_line.iloc[-1] else "BEARISH",
        "sma20": sma20.iloc[-1],
        "sma50": sma50.iloc[-1],
        "sma200": sma200.iloc[-1] if sma200 is not None else None,
        "bb_upper": bb_upper.iloc[-1],
        "bb_middle": bb_middle.iloc[-1],
        "bb_lower": bb_lower.iloc[-1],
        "current_price": close.iloc[-1],
        "close_data": close,
        "volume": volume,
        "high": high,
        "low": low
    }


def generate_recommendation(tech_data, info):
    """Generate investment recommendation"""
    signals = []
    weight = 0
    
    rsi = tech_data['rsi']
    if rsi < 30:
        signals.append(("RSI Oversold", "bullish"))
        weight += 2
    elif rsi > 70:
        signals.append(("RSI Overbought", "bearish"))
        weight -= 2
    else:
        signals.append(("RSI Neutral", "neutral"))
    
    if tech_data['macd'] > tech_data['macd_signal']:
        signals.append(("MACD Bullish Cross", "bullish"))
        weight += 1
    else:
        signals.append(("MACD Bearish Cross", "bearish"))
        weight -= 1
    
    price = tech_data['current_price']
    ma50 = tech_data['sma50']
    ma200 = tech_data['sma200']
    
    if ma200:
        if price > ma200 > ma50:
            signals.append(("Strong Uptrend", "bullish"))
            weight += 2
        elif price > ma50:
            signals.append(("Above 50-MA", "bullish"))
            weight += 1
        else:
            signals.append(("Below 50-MA", "bearish"))
            weight -= 1
    
    if price < tech_data['bb_lower']:
        signals.append(("Near Lower BB", "bullish"))
        weight += 1
    elif price > tech_data['bb_upper']:
        signals.append(("Near Upper BB", "bearish"))
        weight -= 1
    
    volume_current = tech_data['volume'].iloc[-20:].mean()
    volume_prev = tech_data['volume'].iloc[-60:-20].mean()
    if volume_current > volume_prev * 1.5:
        signals.append(("High Volume", "bullish"))
        weight += 1
    
    if weight >= 3:
        recommendation = "STRONG BUY"
    elif weight >= 1:
        recommendation = "BUY"
    elif weight >= -1:
        recommendation = "HOLD"
    else:
        recommendation = "SELL"
    
    target_price = price * (1.20 if recommendation in ["STRONG BUY", "BUY"] else 1.10)
    stop_loss = price * (0.92 if recommendation in ["SELL"] else 0.95)
    
    return {
        "recommendation": recommendation,
        "signals": signals,
        "weight": weight,
        "target_price": target_price,
        "stop_loss": stop_loss,
        "current_price": price,
        "upside": ((target_price - price) / price) * 100,
        "downside": ((price - stop_loss) / price) * 100,
        "time_horizon": "3-6 months" if recommendation == "HOLD" else "6-12 months"
    }


def create_price_chart(tech_data, info):
    """Create interactive price chart"""
    close = tech_data['close_data']
    sma20 = close.rolling(20).mean()
    sma50 = close.rolling(50).mean()
    sma200 = close.rolling(200).mean() if len(close) >= 200 else None
    
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    fig.add_trace(
        go.Scatter(x=close.index, y=close, name="Price", line=dict(color="#1976d2", width=2)),
        secondary_y=False
    )
    
    fig.add_trace(
        go.Scatter(x=sma20.index, y=sma20, name="MA20", line=dict(color="#ff9800", width=1.5, dash="dot")),
        secondary_y=False
    )
    
    fig.add_trace(
        go.Scatter(x=sma50.index, y=sma50, name="MA50", line=dict(color="#4caf50", width=1.5)),
        secondary_y=False
    )
    
    if sma200 is not None:
        fig.add_trace(
            go.Scatter(x=sma200.index, y=sma200, name="MA200", line=dict(color="#9c27b0", width=1.5, dash="dash")),
            secondary_y=False
        )
    
    bb_upper = close.rolling(20).mean() + close.rolling(20).std() * 2
    bb_lower = close.rolling(20).mean() - close.rolling(20).std() * 2
    
    fig.add_trace(
        go.Scatter(x=bb_upper.index, y=bb_upper, name="BB Upper", 
                   line=dict(color="#e0e0e0", width=1), fill='tonexty', fillcolor='rgba(224,224,224,0.3)',
                   hoverinfo='skip'),
        secondary_y=False
    )
    
    fig.add_trace(
        go.Scatter(x=bb_lower.index, y=bb_lower, name="BB Lower",
                   line=dict(color="#e0e0e0", width=1), hoverinfo='skip'),
        secondary_y=False
    )
    
    volume = tech_data['volume']
    colors = ['#26a69a' if close.iloc[i] >= close.iloc[i-1] else '#ef5350' for i in range(len(close))]
    
    fig.add_trace(
        go.Bar(x=volume.index, y=volume, name="Volume", marker_color='rgba(158,158,158,0.5)', hoverinfo='y'),
        secondary_y=True
    )
    
    fig.update_layout(
        template="plotly_white",
        height=400,
        margin=dict(l=20, r=20, t=20, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
        hovermode="x unified"
    )
    
    fig.update_yaxes(title_text="Price (���)", secondary_y=False, showgrid=True, gridcolor="#f0f0f0")
    fig.update_yaxes(title_text="Volume", secondary_y=True, showgrid=False)
    fig.update_xaxes(showgrid=True, gridcolor="#f0f0f0")
    
    return fig


def format_number(value):
    """Format large numbers"""
    if value >= 1e12:
        return f"₹{value/1e12:.2f}T"
    elif value >= 1e10:
        return f"₹{value/1e10:.2f}B"
    elif value >= 1e8:
        return f"₹{value/1e8:.2f}Cr"
    return f"₹{value:,.0f}"


def main():
    with st.sidebar:
        st.markdown("### 📈 Stock Search")
        
        symbol = st.text_input("Stock Symbol", placeholder="RELIANCE, TCS, INFY...", key="symbol_input")
        
        search_btn = st.button("🔍 Analyze Stock", type="primary", use_container_width=True)
        
        st.markdown("---")
        
        st.markdown("### 📊 Popular Stocks")
        
        quick_stocks = {
            "Blue Chip": ["RELIANCE", "TCS", "INFY", "HDFCBANK"],
            "Banking": ["ICICIBANK", "SBIN", "KOTAKBANK"],
            "Auto": ["MARUTI", "TATAMOTORS", "M&M"],
            "FMCG": ["HUL", "NESTLE", "BRITANNIA"],
            "Pharma": ["SUNPHARMA", "DRREDDY", "CIPLA"]
        }
        
        for category, stocks in quick_stocks.items():
            with st.expander(f"### {category}"):
                for s in stocks:
                    if st.button(s, key=f"btn_{s}", use_container_width=True):
                        symbol = s
    
    col_main1, col_main2 = st.columns([2, 1])
    
    with col_main1:
        st.markdown('<p class="main-header">Indian Stock Analyzer</p>', unsafe_allow_html=True)
        st.markdown('<p class="sub-header">AI-Powered Investment Research for NSE/BSE Stocks</p>', unsafe_allow_html=True)
    
    if search_btn and symbol:
        with st.spinner(f"Analyzing {symbol.upper()}..."):
            try:
                stock, info, history, news = get_stock_data(symbol)
                tech_data = calculate_technical_indicators(history)
                recommendation = generate_recommendation(tech_data, info)
                
                current_price = info.get('currentPrice', 0)
                prev_close = info.get('previousClose', current_price)
                price_change = current_price - prev_close
                price_change_pct = (price_change / prev_close * 100) if prev_close else 0
                
                with col_main1:
                    with st.container():
                        c1, c2, c3, c4 = st.columns(4)
                        
                        with c1:
                            st.metric("Current Price", f"₹{current_price:.2f}", 
                                     f"{price_change:+.2f} ({price_change_pct:+.2f}%)")
                        with c2:
                            st.metric("Market Cap", format_number(info.get('marketCap', 0)))
                        with c3:
                            pe = info.get('trailingPE')
                            st.metric("P/E Ratio", f"{pe:.2f}" if pe else "N/A")
                        with c4:
                            vol = info.get('averageVolume', info.get('volume', 0))
                            st.metric("Avg Volume", f"{vol/1e6:.1f}M" if vol else "N/A")
                
                with col_main2:
                    rec = recommendation['recommendation']
                    
                    if rec == "STRONG BUY":
                        color = "#00c853"
                        bg = "#e8f5e9"
                    elif rec == "BUY":
                        color = "#4caf50"
                        bg = "#f1f8e9"
                    elif rec == "SELL":
                        color = "#d32f2f"
                        bg = "#ffebee"
                    else:
                        color = "#f57c00"
                        bg = "#fff3e0"
                    
                    st.markdown(f"""
                    <div style='background: {bg}; padding: 1.5rem; border-radius: 16px; text-align: center; border: 3px solid {color};'>
                        <div style='font-size: 1rem; color: #666;'>Recommendation</div>
                        <div style='font-size: 2rem; font-weight: 800; color: {color};'>{rec}</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                st.markdown("---")
                
                col_p1, col_p2 = st.columns([2, 1])
                
                with col_p1:
                    chart = create_price_chart(tech_data, info)
                    st.plotly_chart(chart, use_container_width=True)
                
                with col_p2:
                    st.markdown("#### 💰 Price Targets")
                    
                    rec_data = recommendation
                    st.markdown(f"""
                    <div class="card">
                        <div style="display: flex; justify-content: space-between; padding: 0.5rem 0;">
                            <span>Current Price</span>
                            <strong>₹{rec_data['current_price']:.2f}</strong>
                        </div>
                        <hr style="margin: 0.5rem 0;">
                        <div style="display: flex; justify-content: space-between; padding: 0.5rem 0; color: #2e7d32;">
                            <span>🎯 Target Price</span>
                            <strong>₹{rec_data['target_price']:.2f}</strong>
                        </div>
                        <div style="padding: 0.5rem 0; color: #2e7d32; font-size: 0.9rem;">+{rec_data['upside']:.1f}% upside</div>
                        <hr style="margin: 0.5rem 0;">
                        <div style="display: flex; justify-content: space-between; padding: 0.5rem 0; color: #c62828;">
                            <span>🛡️ Stop Loss</span>
                            <strong>₹{rec_data['stop_loss']:.2f}</strong>
                        </div>
                        <div style="padding: 0.5rem 0; color: #c62828; font-size: 0.9rem;">-{rec_data['downside']:.1f}% risk</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.markdown(f"**⏱️ Time Horizon:** {rec_data['time_horizon']}")
                
                st.markdown("---")
                
                col_t1, col_t2, col_t3 = st.columns(3)
                
                with col_t1:
                    with st.container():
                        st.markdown("#### 📊 Technical Indicators")
                        
                        rsi = tech_data['rsi']
                        rsi_class = "indicator-bullish" if rsi < 30 else ("indicator-bearish" if rsi > 70 else "indicator-neutral")
                        st.markdown(f"""
                        <div class="card">
                            <div style="display: flex; justify-content: space-between;">
                                <span>RSI (14)</span>
                                <span class="indicator-box {rsi_class}">{rsi:.1f}</span>
                            </div>
                            <div style="display: flex; justify-content: space-between; margin-top: 0.5rem;">
                                <span>MACD</span>
                                <span class="indicator-box {'indicator-bullish' if tech_data['macd'] > tech_data['macd_signal'] else 'indicator-bearish'}">{tech_data['macd_crossover']}</span>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        st.markdown(f"**MA20:** ₹{tech_data['sma20']:.2f}")
                        st.markdown(f"**MA50:** ₹{tech_data['sma50']:.2f}")
                        if tech_data['sma200']:
                            st.markdown(f"**MA200:** ₹{tech_data['sma200']:.2f}")
                        st.markdown(f"**BB Range:** ₹{tech_data['bb_lower']:.2f} - ₹{tech_data['bb_upper']:.2f}")
                
                with col_t2:
                    with st.container():
                        st.markdown("#### 🏢 Company Info")
                        st.markdown(f"**{info.get('longName', 'N/A')}**")
                        st.markdown(f"**Sector:** {info.get('sector', 'N/A')}")
                        st.markdown(f"**Industry:** {info.get('industry', 'N/A')}")
                        
                        st.markdown("---")
                        
                        st.markdown("#### 📈 Key Metrics")
                        st.markdown(f"**52W High:** ₹{info.get('fiftyTwoWeekHigh', 0)}")
                        st.markdown(f"**52W Low:** ₹{info.get('fiftyTwoWeekLow', 0)}")
                        st.markdown(f"**EPS:** ₹{info.get('trailingEps', 0):.2f}")
                        st.markdown(f"**Div Yield:** {(info.get('dividendYield', 0) or 0)*100:.2f}%")
                        st.markdown(f"**Beta:** {info.get('beta', 0):.2f}")
                
                with col_t3:
                    with st.container():
                        st.markdown("#### 📰 Latest News")
                        
                        if news and len(news) > 0:
                            for item in news[:4]:
                                title = item.get('title', '')[:60] + '...' if len(item.get('title', '')) > 60 else item.get('title', '')
                                publisher = item.get('publisher', 'Yahoo Finance')
                                st.markdown(f"""
                                <div class="news-item">
                                    <div class="news-title">{title}</div>
                                    <div class="news-source">{publisher}</div>
                                </div>
                                """, unsafe_allow_html=True)
                        else:
                            st.info("No recent news available")
                
                st.markdown("---")
                
                col_s1, col_s2 = st.columns(2)
                
                with col_s1:
                    st.markdown("#### 📋 Technical Signals")
                    
                    signals = recommendation['signals']
                    for sig_name, sig_type in signals:
                        if sig_type == "bullish":
                            icon = "🟢"
                            color = "#2e7d32"
                        elif sig_type == "bearish":
                            icon = "🔴"
                            color = "#c62828"
                        else:
                            icon = "🟡"
                            color = "#f57f17"
                        
                        st.markdown(f"{icon} **{sig_name}**")
                
                with col_s2:
                    st.markdown("#### ⚠️ Risk Assessment")
                    
                    weight = recommendation['weight']
                    if weight >= 2:
                        risk = "Low"
                        risk_color = "#2e7d32"
                    elif weight >= 0:
                        risk = "Medium"
                        risk_color = "#f57c00"
                    else:
                        risk = "High"
                        risk_color = "#c62828"
                    
                    st.markdown(f"**Risk Level:** {risk}")
                    
                    st.markdown("""
                    **Key Risks:**
                    - Market volatility
                    - Sector-specific risks
                    - Regulatory changes
                    - Currency fluctuations
                    """)
                
                st.markdown("---")
                
                st.markdown("""
                ### ⚠️ Disclaimer
                This analysis is generated by an AI system and should NOT be considered as professional financial advice. 
                Investors should conduct their own due diligence and consult qualified financial advisors before making investment decisions.
                Stock market investments involve significant risk including potential loss of capital.
                """)
                
            except Exception as e:
                st.error(f"Error analyzing {symbol}: {str(e)}")
                import traceback
                st.code(traceback.format_exc())
    
    else:
        st.markdown("""
        <div style="text-align: center; padding: 3rem;">
            <h2>👈 Enter a stock symbol to begin analysis</h2>
            <p style="color: #666; margin-top: 1rem;">
                Try popular stocks: RELIANCE, TCS, INFY, HDFCBANK, ICICIBANK
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        st.markdown("### 📊 Features")
        
        col_f1, col_f2, col_f3 = st.columns(3)
        
        with col_f1:
            st.markdown("""
            #### 📈 Technical Analysis
            - RSI, MACD indicators
            - Moving Averages (20/50/200)
            - Bollinger Bands
            - Volume analysis
            """)
        
        with col_f2:
            st.markdown("""
            #### 💼 Fundamental Data
            - P/E ratio
            - Market cap
            - EPS, Dividend yield
            - 52-week range
            """)
        
        with col_f3:
            st.markdown("""
            #### 🎯 Smart Recommendations
            - Buy/Sell/Hold signals
            - Target price
            - Stop-loss levels
            - Time horizon
            """)


if __name__ == "__main__":
    main()