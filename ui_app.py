import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(
    page_title="Manver IQ - Stock Analyzer",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    html, body, .block-container { font-family: 'Inter', sans-serif; }
    
    /* Main Container */
    .main-content { max-width: 1200px; margin: 0 auto; padding: 0.5rem; }
    
    /* Header */
    .app-header { 
        background: linear-gradient(135deg, #1a237e 0%, #3949ab 50%, #5c6bc0 100%);
        padding: 1.5rem; border-radius: 12px; color: white; margin-bottom: 1rem; 
        box-shadow: 0 4px 20px rgba(26, 35, 126, 0.3);
    }
    .app-title { font-size: 2rem; font-weight: 700; margin: 0; letter-spacing: -0.5px; }
    .app-tagline { font-size: 0.95rem; opacity: 0.9; margin-top: 0.25rem; }
    
    /* Search Box */
    .search-container { 
        background: white; padding: 1rem; border-radius: 10px; 
        box-shadow: 0 2px 10px rgba(0,0,0,0.08); margin-bottom: 1rem; 
    }
    .stTextInput > div > div { border-radius: 8px; }
    .stTextInput input { font-size: 1.1rem; padding: 0.75rem; }
    
    /* Metrics Grid */
    .metrics-row { display: grid; grid-template-columns: repeat(4, 1fr); gap: 0.75rem; margin-bottom: 1rem; }
    .metric-box { 
        background: white; padding: 1rem; border-radius: 10px; 
        box-shadow: 0 2px 8px rgba(0,0,0,0.06); text-align: center;
    }
    .metric-label { font-size: 0.75rem; color: #666; text-transform: uppercase; letter-spacing: 0.5px; }
    .metric-value { font-size: 1.25rem; font-weight: 700; color: #1a237e; margin: 0.25rem 0; }
    .metric-change { font-size: 0.85rem; }
    .metric-change.up { color: #2e7d32; }
    .metric-change.down { color: #c62828; }
    
    /* Recommendation Card */
    .rec-card { 
        background: linear-gradient(135deg, #f5f5f5 0%, #eeeeee 100%);
        padding: 1.5rem; border-radius: 12px; text-align: center; margin-bottom: 1rem;
        border: 2px solid #e0e0e0;
    }
    .rec-card.buy { background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%); border-color: #4caf50; }
    .rec-card.sell { background: linear-gradient(135deg, #ffebee 0%, #ffcdd2 100%); border-color: #f44336; }
    .rec-card.hold { background: linear-gradient(135deg, #fff8e1 0%, #ffecb3 100%); border-color: #ffc107; }
    
    .rec-label { font-size: 0.85rem; color: #666; margin-bottom: 0.5rem; }
    .rec-value { font-size: 2.5rem; font-weight: 800; letter-spacing: 2px; }
    .rec-card.buy .rec-value { color: #2e7d32; }
    .rec-card.sell .rec-value { color: #c62828; }
    .rec-card.hold .rec-value { color: #f57c00; }
    
    .rec-targets { display: flex; justify-content: center; gap: 2rem; margin-top: 0.75rem; font-size: 0.9rem; }
    .rec-targets span { color: #666; }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] { gap: 0.5rem; background: #f5f5f5; padding: 0.25rem; border-radius: 8px; }
    .stTabs [data-baseweb="tab"] { 
        padding: 0.5rem 1rem; border-radius: 6px 6px 0 0; font-weight: 500;
    }
    .stTabs [aria-selected="true"] { background: white; }
    
    /* Content Cards */
    .content-card { 
        background: white; padding: 1.25rem; border-radius: 10px; 
        box-shadow: 0 2px 8px rgba(0,0,0,0.06); margin-bottom: 0.75rem; 
    }
    .content-title { 
        font-size: 0.9rem; font-weight: 600; color: #1a237e; 
        margin-bottom: 1rem; padding-bottom: 0.5rem; border-bottom: 1px solid #eee;
    }
    
    /* Indicator Tags */
    .tag { 
        display: inline-block; padding: 0.35rem 0.75rem; border-radius: 20px; 
        font-size: 0.8rem; font-weight: 500; margin: 0.25rem;
    }
    .tag.bullish { background: #e8f5e9; color: #2e7d32; }
    .tag.bearish { background: #ffebee; color: #c62828; }
    .tag.neutral { background: #fff8e1; color: #f57c00; }
    
    /* News Items */
    .news-item { 
        padding: 0.75rem; border-left: 3px solid #1976d2; 
        background: #f8f9fa; margin-bottom: 0.5rem; border-radius: 0 6px 6px 0;
    }
    .news-title { font-size: 0.85rem; font-weight: 500; }
    .news-source { font-size: 0.75rem; color: #888; }
    
    /* Chart */
    .js-plotly-plot { margin-bottom: 0 !important; }
    
    /* Footer */
    .footer { 
        text-align: center; padding: 1rem; color: #999; font-size: 0.8rem; 
        margin-top: 1rem;
    }
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
    
    # RSI
    delta = close.diff()
    gain = delta.where(delta > 0, 0).ewm(span=14, adjust=False).mean()
    loss = (-delta.where(delta < 0, 0)).ewm(span=14, adjust=False).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    
    # MACD
    ema12 = close.ewm(span=12, adjust=False).mean()
    ema26 = close.ewm(span=26, adjust=False).mean()
    macd = ema12 - ema26
    macd_signal = macd.ewm(span=9, adjust=False).mean()
    
    # Moving Averages
    sma20 = close.rolling(20).mean()
    sma50 = close.rolling(50).mean()
    sma200 = close.rolling(200).mean() if len(close) >= 200 else None
    
    # Bollinger Bands
    bb_mid = close.rolling(20).mean()
    bb_std = close.rolling(20).std()
    bb_upper = bb_mid + bb_std * 2
    bb_lower = bb_mid - bb_std * 2
    
    return {
        "rsi": rsi.iloc[-1] if not np.isnan(rsi.iloc[-1]) else 50,
        "macd": macd.iloc[-1],
        "macd_signal": macd_signal.iloc[-1],
        "sma20": sma20.iloc[-1],
        "sma50": sma50.iloc[-1],
        "sma200": sma200.iloc[-1] if sma200 is not None else None,
        "bb_upper": bb_upper.iloc[-1],
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
        signals.append(("RSI Oversold", "bullish"))
        weight += 2
    elif rsi > 70:
        signals.append(("RSI Overbought", "bearish"))
        weight -= 2
    
    if tech['macd'] > tech['macd_signal']:
        signals.append(("MACD Bullish", "bullish"))
        weight += 1
    else:
        signals.append(("MACD Bearish", "bearish"))
        weight -= 1
    
    if tech['sma200']:
        if price > tech['sma200']:
            signals.append(("Above MA200", "bullish"))
            weight += 1
        else:
            signals.append(("Below MA200", "bearish"))
            weight -= 1
    
    if price < tech['bb_lower']:
        signals.append(("Near Support", "bullish"))
        weight += 1
    elif price > tech['bb_upper']:
        signals.append(("Near Resistance", "bearish"))
        weight -= 1
    
    if weight >= 2:
        rec = "BUY"
    elif weight >= 0:
        rec = "HOLD"
    else:
        rec = "SELL"
    
    target = price * 1.20 if rec == "BUY" else (price * 1.10 if rec == "HOLD" else price * 1.08)
    stop = price * 0.95
    
    return {
        "rec": rec,
        "signals": signals,
        "target": target,
        "stop": stop,
        "upside": ((target - price) / price) * 100,
        "downside": ((price - stop) / price) * 100,
        "horizon": "6-12 months" if rec == "BUY" else ("3-6 months" if rec == "HOLD" else "1-3 months")
    }


def create_chart(tech):
    """Create interactive price chart"""
    close = tech['close']
    
    fig = make_subplots(specs=[[{"secondary_y": True}]], rows=1, cols=1)
    
    # Price line
    fig.add_trace(go.Scatter(
        x=close.index, y=close, name="Price",
        line=dict(color="#1a237e", width=2)
    ), secondary_y=False)
    
    # MA20
    ma20 = close.rolling(20).mean()
    fig.add_trace(go.Scatter(
        x=ma20.index, y=ma20, name="MA20",
        line=dict(color="#ff9800", width=1, dash="dot")
    ), secondary_y=False)
    
    # MA50
    ma50 = close.rolling(50).mean()
    fig.add_trace(go.Scatter(
        x=ma50.index, y=ma50, name="MA50",
        line=dict(color="#4caf50", width=1.5)
    ), secondary_y=False)
    
    # MA200 if available
    if tech['sma200']:
        ma200 = close.rolling(200).mean()
        fig.add_trace(go.Scatter(
            x=ma200.index, y=ma200, name="MA200",
            line=dict(color="#9c27b0", width=1.5, dash="dash")
        ), secondary_y=False)
    
    # Bollinger Bands
    bb_u = close.rolling(20).mean() + close.rolling(20).std() * 2
    bb_l = close.rolling(20).mean() - close.rolling(20).std() * 2
    
    fig.add_trace(go.Scatter(
        x=bb_u.index, y=bb_u, name="BB Upper",
        line=dict(color="#e0e0e0", width=1), fill='tonexty',
        fillcolor='rgba(224,224,224,0.2)', hoverinfo='skip'
    ), secondary_y=False)
    
    fig.add_trace(go.Scatter(
        x=bb_l.index, y=bb_l, name="BB Lower",
        line=dict(color="#e0e0e0", width=1), hoverinfo='skip'
    ), secondary_y=False)
    
    # Volume bars
    colors = ['#26a69a' if close.iloc[i] >= close.iloc[i-1] else '#ef5350' for i in range(1, len(close))]
    fig.add_trace(go.Bar(
        x=tech['volume'].index[1:], y=tech['volume'].iloc[1:],
        name="Volume", marker_color='rgba(158,158,158,0.4)'
    ), secondary_y=True)
    
    fig.update_layout(
        template="plotly_white",
        height=320,
        margin=dict(l=40, r=20, t=20, b=40),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
        hovermode="x unified",
        font=dict(family="Inter")
    )
    
    fig.update_yaxes(title_text="Price (₹)", secondary_y=False, showgrid=True, gridcolor="#f5f5f5")
    fig.update_yaxes(title_text="Volume", secondary_y=True, showgrid=False)
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


# === MAIN APP ===
st.markdown('<div class="main-content">', unsafe_allow_html=True)

# Header
st.markdown("""
<div class="app-header">
    <h1 class="app-title">🧠 Manver IQ</h1>
    <p class="app-tagline">Smart Stock Analysis for Smart Investors</p>
</div>
""", unsafe_allow_html=True)

# Search
st.markdown('<div class="search-container">', unsafe_allow_html=True)
symbol = st.text_input("Enter Stock Symbol", placeholder="e.g., RELIANCE, TCS, INFY, HDFCBANK...", key="symbol_input")
st.markdown('</div>', unsafe_allow_html=True)

if symbol:
    with st.spinner(f"Analyzing {symbol.upper()}..."):
        try:
            info, history, news = get_stock_data(symbol)
            tech = calculate_indicators(history)
            rec = get_recommendation(tech, info)
            
            price = info.get('currentPrice', 0)
            prev = info.get('previousClose', price)
            change = ((price - prev) / prev * 100) if prev else 0
            change_class = "up" if change >= 0 else "down"
            change_icon = "▲" if change >= 0 else "▼"
            
            # Metrics Row
            st.markdown('<div class="metrics-row">', unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class="metric-box">
                <div class="metric-label">Current Price</div>
                <div class="metric-value">₹{price:.2f}</div>
                <div class="metric-change {change_class}">{change_icon} {abs(change):.2f}%</div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class="metric-box">
                <div class="metric-label">Market Cap</div>
                <div class="metric-value">{format_num(info.get('marketCap', 0))}</div>
            </div>
            """, unsafe_allow_html=True)
            
            pe_val = info.get('trailingPE')
            pe_str = f"{pe_val:.1f}" if pe_val else "N/A"
            st.markdown(f"""
            <div class="metric-box">
                <div class="metric-label">P/E Ratio</div>
                <div class="metric-value">{pe_str}</div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class="metric-box">
                <div class="metric-label">52W High</div>
                <div class="metric-value">₹{info.get('fiftyTwoWeekHigh', 0):.0f}</div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Recommendation Card
            rec_class = rec['rec'].lower()
            rec_bg = {"buy": "buy", "sell": "sell", "hold": "hold"}.get(rec_class, "hold")
            
            st.markdown(f"""
            <div class="rec-card {rec_bg}">
                <div class="rec-label">INVESTMENT RECOMMENDATION</div>
                <div class="rec-value">{rec['rec']}</div>
                <div class="rec-targets">
                    <span>🎯 Target: ₹{rec['target']:.0f} (+{rec['upside']:.1f}%)</span>
                    <span>🛡️ Stop: ₹{rec['stop']:.0f} (-{rec['downside']:.1f}%)</span>
                    <span>⏱️ {rec['horizon']}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Tabs
            tab1, tab2, tab3, tab4 = st.tabs(["📊 Chart", "📈 Technical", "💼 Fundamentals", "📰 News"])
            
            with tab1:
                chart = create_chart(tech)
                st.plotly_chart(chart, use_container_width=True)
            
            with tab2:
                c1, c2 = st.columns(2)
                
                with c1:
                    st.markdown('<div class="content-card"><div class="content-title">Technical Indicators</div>', unsafe_allow_html=True)
                    
                    rsi = tech['rsi']
                    rsi_tag = "bullish" if rsi < 30 else ("bearish" if rsi > 70 else "neutral")
                    st.markdown(f"RSI (14): <span class='tag {rsi_tag}'>{rsi:.1f}</span>", unsafe_allow_html=True)
                    
                    macd_tag = "bullish" if tech['macd'] > tech['macd_signal'] else "bearish"
                    macd_stat = "Bullish" if tech['macd'] > tech['macd_signal'] else "Bearish"
                    st.markdown(f"MACD: <span class='tag {macd_tag}'>{macd_stat}</span>", unsafe_allow_html=True)
                    
                    st.markdown(f"MA20: ₹{tech['sma20']:.0f}")
                    st.markdown(f"MA50: ₹{tech['sma50']:.0f}")
                    if tech['sma200']:
                        st.markdown(f"MA200: ₹{tech['sma200']:.0f}")
                    
                    st.markdown("</div>", unsafe_allow_html=True)
                
                with c2:
                    st.markdown('<div class="content-card"><div class="content-title">Technical Signals</div>', unsafe_allow_html=True)
                    
                    for sig_name, sig_type in rec['signals']:
                        icon = "🟢" if sig_type == "bullish" else ("🔴" if sig_type == "bearish" else "🟡")
                        st.markdown(f"{icon} {sig_name}")
                    
                    st.markdown("</div>", unsafe_allow_html=True)
            
            with tab3:
                c1, c2 = st.columns(2)
                
                with c1:
                    st.markdown('<div class="content-card"><div class="content-title">Company Info</div>', unsafe_allow_html=True)
                    st.markdown(f"**{info.get('longName', 'N/A')}**")
                    st.markdown(f"Sector: {info.get('sector', 'N/A')}")
                    st.markdown(f"Industry: {info.get('industry', 'N/A')}")
                    st.markdown("</div>", unsafe_allow_html=True)
                
                with c2:
                    st.markdown('<div class="content-card"><div class="content-title">Key Metrics</div>', unsafe_allow_html=True)
                    st.markdown(f"52W Low: ₹{info.get('fiftyTwoWeekLow', 0):.0f}")
                    st.markdown(f"EPS: ₹{info.get('trailingEps', 0):.2f}")
                    st.markdown(f"Div Yield: {(info.get('dividendYield', 0) or 0)*100:.2f}%")
                    st.markdown(f"Beta: {info.get('beta', 0):.2f}")
                    st.markdown("</div>", unsafe_allow_html=True)
            
            with tab4:
                if news:
                    for n in news[:5]:
                        st.markdown(f"""
                        <div class="news-item">
                            <div class="news-title">{n.get('title', '')[:80]}</div>
                            <div class="news-source">{n.get('publisher', 'Yahoo Finance')}</div>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.info("No recent news available")
            
            # Disclaimer
            st.markdown("""
            <div class="footer">
                ⚠️ <strong>Disclaimer:</strong> This is AI-generated analysis and NOT financial advice. 
                Invest at your own risk. Consult a qualified advisor.
            </div>
            """, unsafe_allow_html=True)
            
        except Exception as e:
            st.error(f"Error analyzing {symbol}: {str(e)}")
else:
    st.info("👈 Enter a stock symbol above to begin analysis")
    
    st.markdown("---")
    st.markdown("### 📈 Popular Stocks to Try")
    
    pop_cols = st.columns(4)
    pop_stocks = ["RELIANCE", "TCS", "INFY", "HDFCBANK", "ICICIBANK", "SBIN", "KOTAKBANK", "HUL"]
    
    for i, s in enumerate(pop_stocks):
        with pop_cols[i % 4]:
            st.caption(f"• {s}")

st.markdown('</div>', unsafe_allow_html=True)