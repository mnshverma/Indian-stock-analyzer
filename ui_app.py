import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests
from datetime import datetime, timedelta
import feedparser

st.set_page_config(
    page_title="Manver IQ - Stock Analyzer",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    html, body, .block-container { font-family: 'Inter', sans-serif; max-width: 100% !important; }
    
    .main-wrap { max-width: 1300px; margin: 0 auto; padding: 0.5rem; }
    
    /* Header */
    .header { background: linear-gradient(135deg, #1a237e 0%, #3949ab 100%); padding: 1rem 1.5rem; border-radius: 10px; color: white; margin-bottom: 1rem; }
    .header h1 { font-size: 1.8rem; font-weight: 700; margin: 0; }
    .header p { font-size: 0.9rem; opacity: 0.9; margin: 0.25rem 0 0 0; }
    
    /* Search */
    .search-box { background: white; padding: 1rem; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.08); margin-bottom: 1rem; }
    .stTextInput input { font-size: 1rem; }
    .stTextInput > div > div { border-radius: 6px; }
    
    /* Metrics Row - Horizontal */
    .metrics-row { display: flex; gap: 0.5rem; margin-bottom: 0.75rem; flex-wrap: wrap; }
    .metric-card { flex: 1; min-width: 100px; background: white; padding: 0.75rem; border-radius: 6px; box-shadow: 0 1px 4px rgba(0,0,0,0.06); text-align: center; }
    .metric-label { font-size: 0.65rem; color: #666; text-transform: uppercase; }
    .metric-value { font-size: 1rem; font-weight: 700; color: #1a237e; margin: 0.2rem 0; }
    .metric-change { font-size: 0.75rem; }
    .metric-change.pos { color: #2e7d32; }
    .metric-change.neg { color: #c62828; }
    
    /* Rec Box */
    .rec-box { background: linear-gradient(135deg, #fafafa 0%, #f0f0f0 100%); padding: 1rem; border-radius: 8px; text-align: center; margin-bottom: 1rem; border: 2px solid #ddd; }
    .rec-box.buy { background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%); border-color: #43a047; }
    .rec-box.sell { background: linear-gradient(135deg, #ffebee 0%, #ffcdd2 100%); border-color: #e53935; }
    .rec-box.hold { background: linear-gradient(135deg, #fff8e1 0%, #ffecb3 100%); border-color: #ffa000; }
    .rec-label { font-size: 0.75rem; color: #666; }
    .rec-value { font-size: 2rem; font-weight: 800; letter-spacing: 2px; }
    .rec-box.buy .rec-value { color: #2e7d32; }
    .rec-box.sell .rec-value { color: #c62828; }
    .rec-box.hold .rec-value { color: #f57c00; }
    .rec-targets { display: flex; justify-content: center; gap: 1.5rem; margin-top: 0.5rem; font-size: 0.8rem; flex-wrap: wrap; }
    
    /* Compact Tabs */
    .stTabs [data-baseweb="tab-list"] { gap: 0.3rem; background: #f5f5f5; padding: 0.25rem; border-radius: 6px; }
    .stTabs [data-baseweb="tab"] { padding: 0.4rem 0.8rem; border-radius: 5px 5px 0 0; font-weight: 500; font-size: 0.85rem; }
    .stTabs [aria-selected="true"] { background: white; }
    
    /* Panels */
    .panel { background: white; padding: 1rem; border-radius: 8px; box-shadow: 0 1px 4px rgba(0,0,0,0.05); margin-bottom: 0.75rem; }
    .panel-title { font-size: 0.9rem; font-weight: 600; color: #1a237e; margin-bottom: 0.75rem; padding-bottom: 0.5rem; border-bottom: 2px solid #1a237e; }
    
    /* Data Grid */
    .data-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(150px, 1fr)); gap: 0.5rem; }
    .data-item { display: flex; justify-content: space-between; padding: 0.4rem; border-bottom: 1px solid #f5f5f5; }
    .data-label { color: #666; font-size: 0.85rem; }
    .data-value { font-weight: 600; color: #1a237e; font-size: 0.85rem; }
    
    /* Tags */
    .tag { display: inline-block; padding: 0.3rem 0.6rem; border-radius: 15px; font-size: 0.75rem; font-weight: 600; margin: 0.2rem; }
    .tag.bull { background: #c8e6c9; color: #2e7d32; }
    .tag.bear { background: #ffcdd2; color: #c62828; }
    .tag.neut { background: #fff9c4; color: #f57f17; }
    
    /* News */
    .news-item { padding: 0.6rem; border-left: 3px solid #1976d2; background: #f8f9fa; margin-bottom: 0.4rem; border-radius: 0 5px 5px 0; }
    .news-title { font-size: 0.8rem; font-weight: 500; line-height: 1.3; }
    .news-source { font-size: 0.7rem; color: #888; margin-top: 0.2rem; }
    
    /* Chart */
    .js-plotly-plot { margin-bottom: 0 !important; }
</style>
""", unsafe_allow_html=True)


def get_stock_data(symbol):
    """Get stock data"""
    ticker = f"{symbol.upper()}.NS"
    stock = yf.Ticker(ticker)
    info = stock.info
    history = stock.history(period="5y")
    return info, history


def get_moneycontrol_news(symbol):
    """Get news from Moneycontrol RSS"""
    news = []
    symbol_clean = symbol.upper().replace('.NS', '')
    
    try:
        url = f"https://news.moneycontrol.com/rss/companyfeed/{symbol_clean}"
        feed = feedparser.parse(url, timeout=10)
        
        if feed.entries:
            for entry in feed.entries[:10]:
                news.append({
                    'title': entry.get('title', ''),
                    'source': 'Moneycontrol',
                    'link': entry.get('link', ''),
                    'published': entry.get('published', '')
                })
    except:
        pass
    
    if len(news) < 3:
        try:
            search_url = f"https://news.moneycontrol.com/rss/searchfeed/SECTIONS_{symbol_clean.replace('NS', '')}"
            feed2 = feedparser.parse(search_url, timeout=10)
            for entry in feed2.entries[:5]:
                if len(news) >= 10:
                    break
                exists = any(item['link'] == entry.get('link', '') for item in news)
                if not exists:
                    news.append({
                        'title': entry.get('title', ''),
                        'source': 'Moneycontrol',
                        'link': entry.get('link', ''),
                        'published': entry.get('published', '')
                    })
        except:
            pass
    
    return news


def get_business_std_news(symbol):
    """Get news from Business Standard"""
    news = []
    try:
        search_term = symbol.upper().replace('.NS', '')
        url = f"https://api.business-standard.com/rssfeed/1030/search/{search_term}.xml"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            feed = feedparser.parse(response.text)
            for entry in feed.entries[:8]:
                news.append({
                    'title': entry.get('title', ''),
                    'source': 'Business Standard',
                    'link': entry.get('link', ''),
                    'published': entry.get('published', '')
                })
    except:
        pass
    return news


def get_all_news(symbol):
    """Get news from multiple sources"""
    all_news = []
    seen = set()
    
    for news_source in [get_moneycontrol_news, get_business_std_news]:
        try:
            news_list = news_source(symbol)
            for item in news_list:
                title = item.get('title', '').strip()
                if title and len(title) > 20:
                    if title.lower() not in seen:
                        seen.add(title.lower())
                        all_news.append(item)
        except:
            pass
    
    return all_news[:12]


def calculate_indicators(history):
    """Calculate technical indicators"""
    close = history['Close']
    
    if len(close) < 2:
        return None
    
    delta = close.diff()
    gain = delta.where(delta > 0, 0).ewm(span=14, adjust=False).mean()
    loss = (-delta.where(delta < 0, 0)).ewm(span=14, adjust=False).mean()
    rsi = 100 - (100 / (1 + (gain / loss)))
    
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
        "rsi": rsi.iloc[-1] if len(rsi) > 0 and not np.isnan(rsi.iloc[-1]) else 50,
        "macd": macd.iloc[-1] if len(macd) > 0 else 0,
        "macd_signal": macd_signal.iloc[-1] if len(macd_signal) > 0 else 0,
        "sma20": sma20.iloc[-1] if len(sma20) > 0 else 0,
        "sma50": sma50.iloc[-1] if len(sma50) > 0 else 0,
        "sma200": sma200.iloc[-1] if sma200 is not None and len(sma200) > 0 else None,
        "bb_upper": bb_upper.iloc[-1] if len(bb_upper) > 0 else 0,
        "bb_lower": bb_lower.iloc[-1] if len(bb_lower) > 0 else 0,
        "price": close.iloc[-1],
        "close": close,
        "volume": history['Volume']
    }


def get_recommendation(tech, info):
    """Generate investment recommendation"""
    signals = []
    weight = 0
    price = tech['price']
    
    rsi = tech['rsi']
    if rsi < 30:
        signals.append(("RSI Oversold", "bull"))
        weight += 2
    elif rsi > 70:
        signals.append(("RSI Overbought", "bear"))
        weight -= 2
    
    if tech['macd'] > tech['macd_signal']:
        signals.append(("MACD Bullish", "bull"))
        weight += 1
    else:
        signals.append(("MACD Bearish", "bear"))
        weight -= 1
    
    if tech['sma200'] and price > tech['sma200']:
        signals.append(("Above MA200", "bull"))
        weight += 1
    elif tech['sma200']:
        signals.append(("Below MA200", "bear"))
        weight -= 1
    
    if weight >= 2:
        rec = "STRONG BUY"
    elif weight >= 0:
        rec = "BUY"
    else:
        rec = "SELL" if weight < -1 else "HOLD"
    
    target = price * (1.25 if rec in ["STRONG BUY"] else (1.15 if rec == "BUY" else (1.05 if rec == "HOLD" else 0.95)))
    stop = price * (0.93 if rec == "SELL" else 0.95)
    
    return {
        "rec": rec,
        "signals": signals,
        "target": target,
        "stop": stop,
        "upside": ((target - price) / price) * 100,
        "downside": ((price - stop) / price) * 100,
        "horizon": "6-12M" if rec in ["STRONG BUY", "BUY"] else "3-6M"
    }


def create_chart(tech, period="1y"):
    """Create interactive price chart"""
    close = tech['close']
    periods = {"1m": 21, "3m": 63, "6m": 126, "1y": 252, "2y": 504}
    days = periods.get(period, 252)
    close_plot = close.iloc[-days:]
    
    fig = make_subplots(specs=[[{"secondary_y": True}]], rows=1, cols=1)
    
    fig.add_trace(go.Scatter(x=close_plot.index, y=close_plot, name="Price", line=dict(color="#1565c0", width=2)), secondary_y=False)
    fig.add_trace(go.Scatter(x=close.rolling(20).mean().iloc[-days:].index, y=close.rolling(20).mean().iloc[-days:], name="MA20", line=dict(color="#ff9800", width=1, dash="dot")), secondary_y=False)
    fig.add_trace(go.Scatter(x=close.rolling(50).mean().iloc[-days:].index, y=close.rolling(50).mean().iloc[-days:], name="MA50", line=dict(color="#4caf50", width=1.5)), secondary_y=False)
    
    if tech['sma200']:
        fig.add_trace(go.Scatter(x=close.rolling(200).mean().iloc[-days:].index, y=close.rolling(200).mean().iloc[-days:], name="MA200", line=dict(color="#9c27b0", width=1.5, dash="dash")), secondary_y=False)
    
    vol = tech['volume'].iloc[-days:]
    fig.add_trace(go.Bar(x=vol.index[1:], y=vol.iloc[1:], name="Volume", marker_color='rgba(158,158,158,0.35)'), secondary_y=True)
    
    fig.update_layout(template="plotly_white", height=320, margin=dict(l=40, r=20, t=20, b=40), legend=dict(orientation="h", y=1.05, xanchor="center", x=0.5), hovermode="x unified")
    fig.update_yaxes(title_text="", secondary_y=False, showgrid=True, gridcolor="#f0f0f0")
    fig.update_yaxes(title_text="", secondary_y=True, showgrid=False)
    
    return fig


def format_num(val):
    """Format numbers"""
    if not val:
        return "N/A"
    if val >= 1e12:
        return f"₹{val/1e12:.2f}T"
    elif val >= 1e10:
        return f"₹{val/1e10:.2f}B"
    elif val >= 1e7:
        return f"₹{val/1e7:.2f}Cr"
    return f"₹{val:,.0f}"


# === MAIN APP ===
st.markdown('<div class="main-wrap">', unsafe_allow_html=True)

# Header
st.markdown("""
<div class="header">
    <h1>🧠 Manver IQ</h1>
    <p>Smart Stock Analysis | NSE/BSE Stocks</p>
</div>
""", unsafe_allow_html=True)

# Search
st.markdown('<div class="search-box">', unsafe_allow_html=True)
symbol = st.text_input("Enter Stock Symbol", placeholder="RELIANCE, TCS, HDFCBANK, INFY...", key="symbol_input")
st.markdown('</div>', unsafe_allow_html=True)

if symbol:
    with st.spinner(f"Analyzing {symbol.upper()}..."):
        try:
            info, history = get_stock_data(symbol)
            tech = calculate_indicators(history)
            
            if not tech:
                st.error(f"No data for {symbol}")
            else:
                rec = get_recommendation(tech, info)
                news = get_all_news(symbol)
                
                price = info.get('currentPrice', 0)
                prev = info.get('previousClose', price)
                change = ((price - prev) / prev * 100) if prev else 0
                
                # Compact Metrics Row
                st.markdown('<div class="metrics-row">', unsafe_allow_html=True)
                
                st.markdown(f"""<div class="metric-card"><div class="metric-label">Price</div><div class="metric-value">₹{price:.1f}</div><div class="metric-change {'pos' if change >= 0 else 'neg'}">{'+' if change >= 0 else ''}{change:.1f}%</div></div>""", unsafe_allow_html=True)
                st.markdown(f"""<div class="metric-card"><div class="metric-label">Mkt Cap</div><div class="metric-value">{format_num(info.get('marketCap', 0))}</div></div>""", unsafe_allow_html=True)
                pe = info.get('trailingPE')
                st.markdown(f"""<div class="metric-card"><div class="metric-label">P/E</div><div class="metric-value">{f"{pe:.1f}" if pe else "N/A"}</div></div>""", unsafe_allow_html=True)
                st.markdown(f"""<div class="metric-card"><div class="metric-label">52W High</div><div class="metric-value">₹{info.get('fiftyTwoWeekHigh', 0):.0f}</div></div>""", unsafe_allow_html=True)
                st.markdown(f"""<div class="metric-card"><div class="metric-label">52W Low</div><div class="metric-value">₹{info.get('fiftyTwoWeekLow', 0):.0f}</div></div>""", unsafe_allow_html=True)
                st.markdown(f"""<div class="metric-card"><div class="metric-label">Volume</div><div class="metric-value">{info.get('averageVolume', info.get('volume', 0))/1e6:.1f}M</div></div>""", unsafe_allow_html=True)
                
                st.markdown('</div>', unsafe_allow_html=True)
                
                # Compact Rec Box
                rec_class = "buy" if rec['rec'] in ["STRONG BUY", "BUY"] else ("sell" if rec['rec'] == "SELL" else "hold")
                
                st.markdown(f"""
                <div class="rec-box {rec_class}">
                    <div class="rec-label">RECOMMENDATION</div>
                    <div class="rec-value">{rec['rec']}</div>
                    <div class="rec-targets">
                        <span>🎯 ₹{rec['target']:.0f} (+{rec['upside']:.0f}%)</span>
                        <span>🛡️ ₹{rec['stop']:.0f} (-{rec['downside']:.0f}%)</span>
                        <span>⏱️ {rec['horizon']}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Tabs
                tab1, tab2, tab3, tab4 = st.tabs(["📊 Chart", "📈 Technical", "💼 Company", "📰 News"])
                
                with tab1:
                    period_sel = st.select_slider("Period", options=["1m", "3m", "6m", "1y", "2y"], value="1y")
                    chart = create_chart(tech, period_sel)
                    st.plotly_chart(chart, use_container_width=True)
                
                with tab2:
                    c1, c2 = st.columns(2)
                    
                    with c1:
                        st.markdown("##### Indicators")
                        
                        rsi = tech['rsi']
                        rsi_t = "bull" if rsi < 30 else ("bear" if rsi > 70 else "neut")
                        st.markdown(f"RSI: <span class='tag {rsi_t}'>{rsi:.0f}</span>", unsafe_allow_html=True)
                        
                        macd_t = "bull" if tech['macd'] > tech['macd_signal'] else "bear"
                        st.markdown(f"MACD: <span class='tag {macd_t}'>{'Bullish' if tech['macd'] > tech['macd_signal'] else 'Bearish'}</span>", unsafe_allow_html=True)
                        
                        st.markdown(f"MA20: ₹{tech['sma20']:.0f}")
                        st.markdown(f"MA50: ₹{tech['sma50']:.0f}")
                        if tech['sma200']:
                            st.markdown(f"MA200: ₹{tech['sma200']:.0f}")
                    
                    with c2:
                        st.markdown("##### Signals")
                        for sig, typ in rec['signals']:
                            ic = "🟢" if typ == "bull" else ("🔴" if typ == "bear" else "🟡")
                            st.markdown(f"{ic} {sig}")
                
                with tab3:
                    c1, c2 = st.columns(2)
                    
                    with c1:
                        st.markdown("##### Company")
                        st.markdown(f"**{info.get('longName', symbol.upper())}**")
                        st.markdown(f"Sector: {info.get('sector', 'N/A')}")
                        st.markdown(f"Industry: {info.get('industry', 'N/A')}")
                    
                    with c2:
                        st.markdown("##### Metrics")
                        eps = info.get('trailingEps')
                        if eps:
                            st.markdown(f"EPS: ₹{eps:.2f}")
                        dy = (info.get('dividendYield', 0) or 0) * 100
                        st.markdown(f"Div Yield: {dy:.1f}%")
                        st.markdown(f"Beta: {info.get('beta', 0):.2f}")
                        pb = info.get('priceToBook')
                        if pb:
                            st.markdown(f"P/B: {pb:.2f}")
                        roe = info.get('returnOnEquity')
                        if roe:
                            st.markdown(f"ROE: {roe*100:.1f}%")
                
                with tab4:
                    if news:
                        for n in news[:10]:
                            st.markdown(f"""
                            <div class="news-item">
                                <div class="news-title">{n.get('title', '')}</div>
                                <div class="news-source">{n.get('source', 'News')}</div>
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.info("No news available. Try checking Moneycontrol manually.")
                        st.markdown(f"**Search manually:** [Moneycontrol {symbol}](https://www.moneycontrol.com/stocks/cp_search/?search={symbol.upper()})")
                
                st.caption("⚠��� Not financial advice. Invest at own risk.")
                
        except Exception as e:
            st.error(f"Error: {str(e)}")
else:
    st.info("👈 Enter a stock symbol above")
    
    st.markdown("---")
    st.markdown("### Popular Stocks")
    stocks = ["RELIANCE", "TCS", "INFY", "HDFCBANK", "ICICIBANK", "SBIN", "KOTAKBANK", "HUL"]
    for s in stocks:
        st.caption(f"• {s}")

st.markdown('</div>', unsafe_allow_html=True)