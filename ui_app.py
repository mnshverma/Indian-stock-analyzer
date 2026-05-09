import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(
    page_title="Indian Stock Analyzer",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    .block-container { padding: 1rem !important; }
    .main-content { max-width: 1400px; margin: 0 auto; }
    
    /* Header */
    .header-title { font-size: 1.5rem; font-weight: 700; color: #1a237e; }
    .header-subtitle { font-size: 0.9rem; color: #666; }
    
    /* Cards */
    .card { background: white; border-radius: 8px; padding: 1rem; box-shadow: 0 1px 3px rgba(0,0,0,0.1); margin-bottom: 0.75rem; }
    .card-title { font-size: 0.9rem; font-weight: 600; color: #333; margin-bottom: 0.75rem; border-bottom: 1px solid #eee; padding-bottom: 0.5rem; }
    
    /* Metrics */
    .metric-label { font-size: 0.75rem; color: #666; }
    .metric-value { font-size: 1.1rem; font-weight: 600; color: #1a237e; }
    .metric-delta { font-size: 0.8rem; }
    
    /* Signals */
    .signal-buy { background: #c8e6c9; color: #2e7d32; padding: 0.5rem 1rem; border-radius: 6px; font-weight: 600; }
    .signal-sell { background: #ffcdd2; color: #c62828; padding: 0.5rem 1rem; border-radius: 6px; font-weight: 600; }
    .signal-hold { background: #fff9c4; color: #f57f17; padding: 0.5rem 1rem; border-radius: 6px; font-weight: 600; }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] { gap: 0.5rem; }
    .stTabs [data-baseweb="tab"] { padding: 0.5rem 1rem; border-radius: 6px 6px 0 0; }
    
    /* Sidebar */
    section[data-testid="stSidebar"] { width: 200px !important; }
    
    /* Columns */
    div[data-testid="stHorizontalBlock"] { gap: 0.75rem; }
    
    /* Inputs */
    .stTextInput > div > div { border-radius: 6px; }
    
    /* Buttons */
    .stButton > button { border-radius: 6px; padding: 0.5rem 1rem; }
    
    /* Charts */
    .js-plotly-plot { margin-bottom: 0; }
</style>
""", unsafe_allow_html=True)


def get_stock_data(symbol):
    """Get stock data"""
    ticker = f"{symbol.upper()}.NS"
    stock = yf.Ticker(ticker)
    info = stock.info
    history = stock.history(period="2y")
    news = stock.news
    return info, history, news


def calculate_indicators(history):
    """Calculate technical indicators"""
    close = history['Close']
    
    delta = close.diff()
    gain = delta.where(delta > 0, 0).ewm(span=14, adjust=False).mean()
    loss = (-delta.where(delta < 0, 0)).ewm(span=14, adjust=False).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    
    ema12 = close.ewm(span=12, adjust=False).mean()
    ema26 = close.ewm(span=26, adjust=False).mean()
    macd = ema12 - ema26
    macd_signal = macd.ewm(span=9, adjust=False).mean()
    
    sma20 = close.rolling(20).mean()
    sma50 = close.rolling(50).mean()
    sma200 = close.rolling(200).mean() if len(close) >= 200 else None
    
    bb_mid = close.rolling(20).mean()
    bb_std = close.rolling(20).std()
    bb_upper = bb_mid + bb_std * 2
    bb_lower = bb_mid - bb_std * 2
    
    return {
        "rsi": rsi.iloc[-1],
        "macd": macd.iloc[-1],
        "macd_signal": macd_signal.iloc[-1],
        "macd_hist": macd.iloc[-1] - macd_signal.iloc[-1],
        "sma20": sma20.iloc[-1],
        "sma50": sma50.iloc[-1],
        "sma200": sma200.iloc[-1] if sma200 is not None else None,
        "bb_upper": bb_upper.iloc[-1],
        "bb_mid": bb_mid.iloc[-1],
        "bb_lower": bb_lower.iloc[-1],
        "price": close.iloc[-1],
        "close": close,
        "volume": history['Volume']
    }


def get_recommendation(tech, info):
    """Generate recommendation"""
    signals = []
    weight = 0
    price = tech['price']
    
    rsi = tech['rsi']
    if rsi < 30:
        signals.append(("Oversold", "buy"))
        weight += 2
    elif rsi > 70:
        signals.append(("Overbought", "sell"))
        weight -= 2
    
    if tech['macd'] > tech['macd_signal']:
        signals.append(("MACD Bullish", "buy"))
        weight += 1
    else:
        signals.append(("MACD Bearish", "sell"))
        weight -= 1
    
    if tech['sma200']:
        if price > tech['sma200']:
            signals.append(("Above MA200", "buy"))
            weight += 1
        else:
            signals.append(("Below MA200", "sell"))
            weight -= 1
    
    if price < tech['bb_lower']:
        signals.append(("Near Support", "buy"))
        weight += 1
    elif price > tech['bb_upper']:
        signals.append(("Near Resistance", "sell"))
        weight -= 1
    
    if weight >= 2:
        rec = "BUY"
    elif weight >= 0:
        rec = "HOLD"
    else:
        rec = "SELL"
    
    target = price * 1.15 if rec == "BUY" else price * 1.08
    stop = price * 0.95
    
    return {
        "rec": rec,
        "signals": signals,
        "target": target,
        "stop": stop,
        "upside": ((target - price) / price) * 100,
        "downside": ((price - stop) / price) * 100,
        "horizon": "6-12 months" if rec == "BUY" else "3-6 months"
    }


def create_chart(tech):
    """Create price chart"""
    close = tech['close']
    
    fig = make_subplots(specs=[[{"secondary_y": True}]], rows=1, cols=1)
    
    fig.add_trace(go.Scatter(x=close.index, y=close, name="Price", line=dict(color="#1976d2", width=2)), secondary_y=False)
    fig.add_trace(go.Scatter(x=close.rolling(20).mean().index, y=close.rolling(20).mean(), name="MA20", line=dict(color="#ff9800", width=1, dash="dot")), secondary_y=False)
    fig.add_trace(go.Scatter(x=close.rolling(50).mean().index, y=close.rolling(50).mean(), name="MA50", line=dict(color="#4caf50", width=1.5)), secondary_y=False)
    
    bb_upper = close.rolling(20).mean() + close.rolling(20).std() * 2
    bb_lower = close.rolling(20).mean() - close.rolling(20).std() * 2
    
    fig.add_trace(go.Scatter(x=bb_upper.index, y=bb_upper, name="BB Upper", line=dict(color="#ccc", width=1), fill='tonexty', fillcolor='rgba(200,200,200,0.1)', hoverinfo='skip'), secondary_y=False)
    fig.add_trace(go.Scatter(x=bb_lower.index, y=bb_lower, name="BB Lower", line=dict(color="#ccc", width=1), hoverinfo='skip'), secondary_y=False)
    
    colors = ['#26a69a' if close.iloc[i] >= close.iloc[i-1] else '#ef5350' for i in range(1, len(close))]
    fig.add_trace(go.Bar(x=tech['volume'].index[1:], y=tech['volume'].iloc[1:], name="Volume", marker_color='rgba(158,158,158,0.4)', hoverinfo='y'), secondary_y=True)
    
    fig.update_layout(template="plotly_white", height=280, margin=dict(l=20, r=20, t=20, b=20), legend=dict(orientation="h", y=1.1, x=0.5), hovermode="x unified")
    fig.update_yaxes(title_text="", secondary_y=False, showgrid=True, gridcolor="#f5f5f5")
    fig.update_yaxes(title_text="", secondary_y=True, showgrid=False)
    fig.update_xaxes(showgrid=False)
    
    return fig


def format_num(val):
    """Format numbers"""
    if val >= 1e12:
        return f"₹{val/1e12:.2f}T"
    elif val >= 1e10:
        return f"₹{val/1e10:.2f}B"
    elif val >= 1e7:
        return f"₹{val/1e7:.2f}Cr"
    return f"₹{val:,.0f}"


# === MAIN UI ===
st.markdown('<div class="main-content">', unsafe_allow_html=True)

# Header Row
col_h1, col_h2 = st.columns([3, 1])

with col_h1:
    st.markdown('<p class="header-title">📈 Indian Stock Analyzer</p>', unsafe_allow_html=True)
    st.markdown('<p class="header-subtitle">AI-Powered Investment Research for NSE/BSE</p>', unsafe_allow_html=True)

with col_h2:
    symbol = st.text_input("Stock", placeholder="RELIANCE", label_visibility="collapsed")

if symbol:
    with st.spinner(f"Analyzing {symbol}..."):
        try:
            info, history, news = get_stock_data(symbol)
            tech = calculate_indicators(history)
            rec = get_recommendation(tech, info)
            
            price = info.get('currentPrice', 0)
            prev = info.get('previousClose', price)
            change = ((price - prev) / prev * 100) if prev else 0
            
            # === METRICS ROW ===
            m1, m2, m3, m4 = st.columns(4)
            with m1:
                st.metric("Price", f"₹{price:.2f}", f"{change:+.2f}%")
            with m2:
                st.metric("Market Cap", format_num(info.get('marketCap', 0)))
            with m3:
                pe = info.get('trailingPE')
                st.metric("P/E", f"{pe:.1f}" if pe else "N/A")
            with m4:
                st.metric("52W High", f"₹{info.get('fiftyTwoWeekHigh', 0):.0f}")
            
            # === RECOMMENDATION BOX ===
            rec_color = {"BUY": "#c8e6c9", "HOLD": "#fff9c4", "SELL": "#ffcdd2"}.get(rec['rec'], "#fff9c4")
            rec_text = {"BUY": "#2e7d32", "HOLD": "#f57f17", "SELL": "#c62828"}.get(rec['rec'], "#f57f17")
            
            st.markdown(f"""
            <div style="background: {rec_color}; padding: 1rem; border-radius: 8px; text-align: center; margin-bottom: 1rem;">
                <div style="font-size: 1.5rem; font-weight: 700; color: {rec_text};">{rec['rec']}</div>
                <div style="font-size: 0.85rem; color: #666;">Target: ₹{rec['target']:.0f} | Stop: ₹{rec['stop']:.0f} | {rec['horizon']}</div>
            </div>
            """, unsafe_allow_html=True)
            
            # === TABS FOR DETAILS ===
            tab1, tab2, tab3, tab4 = st.tabs(["📊 Chart", "📈 Technical", "💼 Fundamentals", "📰 News"])
            
            with tab1:
                chart = create_chart(tech)
                st.plotly_chart(chart, use_container_width=True)
            
            with tab2:
                c1, c2 = st.columns(2)
                with c1:
                    st.markdown("##### Indicators")
                    rsi = tech['rsi']
                    rsi_stat = "🟢 Oversold" if rsi < 30 else ("🔴 Overbought" if rsi > 70 else "🟡 Neutral")
                    st.markdown(f"**RSI(14):** {rsi:.1f} - {rsi_stat}")
                    macd_stat = "🟢 Bullish" if tech['macd'] > tech['macd_signal'] else "🔴 Bearish"
                    st.markdown(f"**MACD:** {macd_stat}")
                    st.markdown(f"**MA20:** ₹{tech['sma20']:.0f}")
                    st.markdown(f"**MA50:** ₹{tech['sma50']:.0f}")
                    if tech['sma200']:
                        st.markdown(f"**MA200:** ₹{tech['sma200']:.0f}")
                with c2:
                    st.markdown("##### Signals")
                    for sig, tip in rec['signals']:
                        icon = "🟢" if tip == "buy" else ("🔴" if tip == "sell" else "🟡")
                        st.markdown(f"{icon} {sig}")
            
            with tab3:
                c1, c2 = st.columns(2)
                with c1:
                    st.markdown("##### Company")
                    st.markdown(f"**{info.get('longName', 'N/A')}**")
                    st.markdown(f"Sector: {info.get('sector', 'N/A')}")
                    st.markdown(f"Industry: {info.get('industry', 'N/A')}")
                with c2:
                    st.markdown("##### Metrics")
                    st.markdown(f"**52W Low:** ₹{info.get('fiftyTwoWeekLow', 0):.0f}")
                    st.markdown(f"**EPS:** ₹{info.get('trailingEps', 0):.2f}")
                    st.markdown(f"**Div Yield:** {(info.get('dividendYield', 0) or 0)*100:.1f}%")
                    st.markdown(f"**Beta:** {info.get('beta', 0):.2f}")
            
            with tab4:
                if news:
                    for n in news[:5]:
                        st.markdown(f"• {n.get('title', '')[:80]}")
                else:
                    st.info("No recent news")
            
            st.markdown("---")
            st.caption("⚠️ Disclaimer: Not financial advice. Invest at your own risk.")
            
        except Exception as e:
            st.error(f"Error: {str(e)}")
else:
    st.info("👈 Enter a stock symbol above")
    
    st.markdown("---")
    st.markdown("### Popular Stocks")
    pop = ["RELIANCE", "TCS", "INFY", "HDFCBANK", "ICICIBANK", "SBIN", "KOTAKBANK", "HUL"]
    cols = st.columns(4)
    for i, s in enumerate(pop):
        with cols[i % 4]:
            st.caption(f"• {s}")

st.markdown('</div>', unsafe_allow_html=True)