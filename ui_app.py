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
    .main-content { max-width: 1400px; margin: 0 auto; padding: 0.5rem; }
    
    /* Header */
    .app-header { 
        background: linear-gradient(135deg, #1a237e 0%, #3949ab 50%, #5c6bc0 100%);
        padding: 1.5rem; border-radius: 12px; color: white; margin-bottom: 1rem; 
    }
    .app-title { font-size: 2.5rem; font-weight: 700; margin: 0; }
    .app-tagline { font-size: 1rem; opacity: 0.9; margin-top: 0.25rem; }
    
    /* Search */
    .search-box { 
        background: white; padding: 1.25rem; border-radius: 12px; 
        box-shadow: 0 2px 12px rgba(0,0,0,0.08); margin-bottom: 1rem; 
    }
    .stTextInput input { font-size: 1.2rem; padding: 0.75rem 1rem; }
    .stTextInput > div > div { border-radius: 10px; border: 2px solid #e0e0e0; }
    .stTextInput > div > div:focus-within { border-color: #1a237e; }
    
    /* Metrics Grid */
    .metrics-grid { 
        display: grid; grid-template-columns: repeat(6, 1fr); gap: 0.75rem; margin-bottom: 1rem; 
    }
    .metric-card { 
        background: white; padding: 1rem; border-radius: 10px; 
        box-shadow: 0 2px 10px rgba(0,0,0,0.06); text-align: center;
    }
    .metric-label { font-size: 0.7rem; color: #666; text-transform: uppercase; letter-spacing: 0.5px; }
    .metric-value { font-size: 1.3rem; font-weight: 700; color: #1a237e; margin: 0.3rem 0; }
    .metric-change { font-size: 0.85rem; }
    .metric-change.pos { color: #2e7d32; }
    .metric-change.neg { color: #c62828; }
    
    /* Recommendation */
    .rec-box { 
        background: linear-gradient(135deg, #fafafa 0%, #f0f0f0 100%);
        padding: 2rem; border-radius: 16px; text-align: center; margin-bottom: 1.5rem;
        border: 3px solid #e0e0e0;
    }
    .rec-box.buy { background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%); border-color: #43a047; }
    .rec-box.sell { background: linear-gradient(135deg, #ffebee 0%, #ffcdd2 100%); border-color: #e53935; }
    .rec-box.hold { background: linear-gradient(135deg, #fff8e1 0%, #ffecb3 100%); border-color: #ffa000; }
    
    .rec-label-txt { font-size: 0.9rem; color: #666; font-weight: 500; }
    .rec-value-txt { font-size: 3rem; font-weight: 800; letter-spacing: 3px; }
    .rec-box.buy .rec-value-txt { color: #2e7d32; }
    .rec-box.sell .rec-value-txt { color: #c62828; }
    .rec-box.hold .rec-value-txt { color: #f57c00; }
    
    .rec-details { display: flex; justify-content: center; gap: 3rem; margin-top: 1rem; flex-wrap: wrap; }
    .rec-detail { text-align: center; }
    .rec-detail-label { font-size: 0.75rem; color: #666; }
    .rec-detail-value { font-size: 1.1rem; font-weight: 600; color: #1a237e; }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] { gap: 0.5rem; background: #f0f0f0; padding: 0.3rem; border-radius: 10px; }
    .stTabs [data-baseweb="tab"] { padding: 0.6rem 1.2rem; border-radius: 8px 8px 0 0; font-weight: 600; font-size: 0.9rem; }
    .stTabs [aria-selected="true"] { background: white; }
    
    /* Content Panels */
    .panel { 
        background: white; padding: 1.5rem; border-radius: 12px; 
        box-shadow: 0 2px 12px rgba(0,0,0,0.06); margin-bottom: 1rem; 
    }
    .panel-title { 
        font-size: 1rem; font-weight: 700; color: #1a237e; 
        margin-bottom: 1rem; padding-bottom: 0.75rem; border-bottom: 2px solid #1a237e;
    }
    
    /* Data Tables */
    .data-row { display: flex; justify-content: space-between; padding: 0.6rem 0; border-bottom: 1px solid #f0f0f0; }
    .data-row:last-child { border-bottom: none; }
    .data-label { color: #666; font-size: 0.9rem; }
    .data-value { font-weight: 600; color: #1a237e; }
    
    /* Tags */
    .tag { 
        display: inline-block; padding: 0.4rem 0.9rem; border-radius: 20px; 
        font-size: 0.85rem; font-weight: 600; margin: 0.25rem 0.25rem 0.25rem 0;
    }
    .tag.bull { background: #c8e6c9; color: #2e7d32; }
    .tag.bear { background: #ffcdd2; color: #c62828; }
    .tag.neut { background: #fff9c4; color: #f57f17; }
    
    /* News */
    .news-card { 
        padding: 1rem; border-left: 4px solid #1976d2; 
        background: #f8f9fa; margin-bottom: 0.75rem; border-radius: 0 8px 8px 0;
    }
    .news-title-txt { font-size: 0.9rem; font-weight: 600; line-height: 1.4; }
    .news-meta { font-size: 0.8rem; color: #888; margin-top: 0.4rem; }
    
    /* Company Info */
    .company-name { font-size: 1.3rem; font-weight: 700; color: #1a237e; margin-bottom: 0.5rem; }
    .company-meta { font-size: 0.9rem; color: #666; }
    
    /* Chart Height */
    .js-plotly-plot { margin-bottom: 0 !important; }
    
    /* Footer */
    .disclaimer { 
        background: #fff3e0; padding: 1rem; border-radius: 8px; 
        text-align: center; color: #e65100; font-size: 0.85rem; margin-top: 1rem;
    }
</style>
""", unsafe_allow_html=True)


def get_stock_data(symbol):
    """Get stock data"""
    ticker = f"{symbol.upper()}.NS"
    stock = yf.Ticker(ticker)
    info = stock.info
    history = stock.history(period="5y")
    news = stock.news
    return info, history, news


def calculate_indicators(history):
    """Calculate technical indicators"""
    close = history['Close']
    
    if len(close) < 2:
        return None
    
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
    sma100 = close.rolling(100).mean()
    sma200 = close.rolling(200).mean() if len(close) >= 200 else None
    
    # Bollinger Bands
    bb_mid = close.rolling(20).mean()
    bb_std = close.rolling(20).std()
    bb_upper = bb_mid + bb_std * 2
    bb_lower = bb_mid - bb_std * 2
    
    # Stochastic
    stoch_k = close.rolling(14).apply(lambda x: 100 * (x.iloc[-1] - x.min()) / (x.max() - x.min()) if x.max() != x.min() else 50)
    stoch_d = stoch_k.rolling(3).mean()
    
    # ATR
    high_low = history['High'] - history['Low']
    high_close = abs(history['High'] - close.shift())
    low_close = abs(history['Low'] - close.shift())
    tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    atr = tr.rolling(14).mean()
    
    return {
        "rsi": rsi.iloc[-1] if len(rsi) > 0 and not np.isnan(rsi.iloc[-1]) else 50,
        "rsi_prev": rsi.iloc[-5] if len(rsi) > 5 and not np.isnan(rsi.iloc[-5]) else 50,
        "macd": macd.iloc[-1] if len(macd) > 0 else 0,
        "macd_signal": macd_signal.iloc[-1] if len(macd_signal) > 0 else 0,
        "macd_hist": (macd.iloc[-1] - macd_signal.iloc[-1]) if len(macd) > 0 else 0,
        "sma20": sma20.iloc[-1] if len(sma20) > 0 else 0,
        "sma50": sma50.iloc[-1] if len(sma50) > 0 else 0,
        "sma100": sma100.iloc[-1] if len(sma100) > 0 else 0,
        "sma200": sma200.iloc[-1] if sma200 is not None and len(sma200) > 0 else None,
        "bb_upper": bb_upper.iloc[-1] if len(bb_upper) > 0 else 0,
        "bb_mid": bb_mid.iloc[-1] if len(bb_mid) > 0 else 0,
        "bb_lower": bb_lower.iloc[-1] if len(bb_lower) > 0 else 0,
        "stoch_k": stoch_k.iloc[-1] if len(stoch_k) > 0 else 50,
        "stoch_d": stoch_d.iloc[-1] if len(stoch_d) > 0 else 50,
        "atr": atr.iloc[-1] if len(atr) > 0 else 0,
        "price": close.iloc[-1] if len(close) > 0 else 0,
        "close": close,
        "high": history['High'],
        "low": history['Low'],
        "volume": history['Volume'],
        "change_1m": ((close.iloc[-1] - close.iloc[-21]) / close.iloc[-21] * 100) if len(close) > 21 else 0,
        "change_3m": ((close.iloc[-1] - close.iloc[-63]) / close.iloc[-63] * 100) if len(close) > 63 else 0,
        "change_6m": ((close.iloc[-1] - close.iloc[-126]) / close.iloc[-126] * 100) if len(close) > 126 else 0,
        "change_1y": ((close.iloc[-1] - close.iloc[-252]) / close.iloc[-252] * 100) if len(close) > 252 else 0
    }


def get_recommendation(tech, info):
    """Generate investment recommendation"""
    signals = []
    weight = 0
    price = tech['price']
    
    # RSI Analysis
    rsi = tech['rsi']
    if rsi < 30:
        signals.append(("RSI Oversold - Buy Signal", "bull"))
        weight += 2
    elif rsi > 70:
        signals.append(("RSI Overbought - Sell Signal", "bear"))
        weight -= 2
    else:
        signals.append((f"RSI Neutral ({rsi:.0f})", "neut"))
    
    # MACD Analysis
    if tech['macd'] > tech['macd_signal']:
        signals.append(("MACD Bullish Cross", "bull"))
        weight += 1
    else:
        signals.append(("MACD Bearish Cross", "bear"))
        weight -= 1
    
    # Trend Analysis
    if tech['sma200'] and price > tech['sma200']:
        signals.append(("Price Above MA200 - Uptrend", "bull"))
        weight += 1
    elif tech['sma200']:
        signals.append(("Price Below MA200 - Downtrend", "bear"))
        weight -= 1
    
    if tech['sma50'] > tech['sma100']:
        signals.append(("50MA > 100MA - Bullish", "bull"))
        weight += 1
    else:
        signals.append(("50MA < 100MA - Bearish", "bear"))
    
    # Bollinger Analysis
    if price < tech['bb_lower']:
        signals.append(("Near Lower BB - Support", "bull"))
        weight += 1
    elif price > tech['bb_upper']:
        signals.append(("Near Upper BB - Resistance", "bear"))
        weight -= 1
    
    # Stochastic
    stoch = tech['stoch_k']
    if stoch < 20:
        signals.append(("Stochastic Oversold", "bull"))
        weight += 1
    elif stoch > 80:
        signals.append(("Stochastic Overbought", "bear"))
        weight -= 1
    
    # Volume
    vol_avg = tech['volume'].iloc[-20:].mean()
    if tech['volume'].iloc[-1] > vol_avg * 1.5:
        signals.append(("High Volume Spike", "bull"))
        weight += 1
    
    # Final Recommendation
    if weight >= 3:
        rec = "STRONG BUY"
    elif weight >= 1:
        rec = "BUY"
    elif weight >= -1:
        rec = "HOLD"
    else:
        rec = "SELL"
    
    # Targets
    if rec in ["STRONG BUY", "BUY"]:
        target_3m = price * 1.10
        target_6m = price * 1.20
        target_12m = price * 1.35
    elif rec == "HOLD":
        target_3m = price * 1.05
        target_6m = price * 1.10
        target_12m = price * 1.15
    else:
        target_3m = price * 0.97
        target_6m = price * 0.93
        target_12m = price * 0.85
    
    stop_loss = price * (0.93 if rec == "SELL" else 0.95)
    
    return {
        "rec": rec,
        "signals": signals,
        "weight": weight,
        "target_3m": target_3m,
        "target_6m": target_6m,
        "target_12m": target_12m,
        "stop": stop_loss,
        "upside_12m": ((target_12m - price) / price) * 100,
        "downside": ((price - stop_loss) / price) * 100,
        "horizon": "Long-term" if rec == "STRONG BUY" else ("Medium-term" if rec == "BUY" else "Short-term")
    }


def create_chart(tech, period="1y"):
    """Create interactive price chart"""
    close = tech['close']
    
    periods = {"1m": 21, "3m": 63, "6m": 126, "1y": 252, "2y": 504}
    days = periods.get(period, 252)
    close_plot = close.iloc[-days:]
    
    fig = make_subplots(specs=[[{"secondary_y": True}]], rows=1, cols=1)
    
    # Price
    fig.add_trace(go.Scatter(
        x=close_plot.index, y=close_plot, name="Price",
        line=dict(color="#1565c0", width=2.5)
    ), secondary_y=False)
    
    # MA20
    ma20 = close.rolling(20).mean().iloc[-days:]
    fig.add_trace(go.Scatter(
        x=ma20.index, y=ma20, name="MA20",
        line=dict(color="#ff9800", width=1.5, dash="dot")
    ), secondary_y=False)
    
    # MA50
    ma50 = close.rolling(50).mean().iloc[-days:]
    fig.add_trace(go.Scatter(
        x=ma50.index, y=ma50, name="MA50",
        line=dict(color="#4caf50", width=2)
    ), secondary_y=False)
    
    # MA200
    if tech['sma200']:
        ma200 = close.rolling(200).mean().iloc[-days:]
        fig.add_trace(go.Scatter(
            x=ma200.index, y=ma200, name="MA200",
            line=dict(color="#9c27b0", width=2, dash="dash")
        ), secondary_y=False)
    
    # Bollinger Bands
    bb_u = (close.rolling(20).mean() + close.rolling(20).std() * 2).iloc[-days:]
    bb_l = (close.rolling(20).mean() - close.rolling(20).std() * 2).iloc[-days:]
    
    fig.add_trace(go.Scatter(
        x=bb_u.index, y=bb_u, name="BB Upper",
        line=dict(color="#e0e0e0", width=1), fill='tonexty',
        fillcolor='rgba(224,224,224,0.15)', hoverinfo='skip'
    ), secondary_y=False)
    
    fig.add_trace(go.Scatter(
        x=bb_l.index, y=bb_l, name="BB Lower",
        line=dict(color="#e0e0e0", width=1), hoverinfo='skip'
    ), secondary_y=False)
    
    # Volume
    vol = tech['volume'].iloc[-days:]
    colors = ['#26a69a' if close_plot.iloc[i] >= close_plot.iloc[i-1] else '#ef5350' for i in range(1, len(close_plot))]
    fig.add_trace(go.Bar(
        x=vol.index[1:], y=vol.iloc[1:], name="Volume",
        marker_color='rgba(158,158,158,0.35)'
    ), secondary_y=True)
    
    fig.update_layout(
        template="plotly_white",
        height=380,
        margin=dict(l=50, r=30, t=30, b=50),
        legend=dict(orientation="h", yanchor="bottom", y=1.05, xanchor="center", x=0.5),
        hovermode="x unified",
        font=dict(family="Inter", size=11)
    )
    
    fig.update_yaxes(title_text="Price (₹)", secondary_y=False, showgrid=True, gridcolor="#f5f5f5")
    fig.update_yaxes(title_text="Volume", secondary_y=True, showgrid=False)
    fig.update_xaxes(showgrid=False)
    
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
st.markdown('<div class="main-content">', unsafe_allow_html=True)

# Header
st.markdown("""
<div class="app-header">
    <h1 class="app-title">🧠 Manver IQ</h1>
    <p class="app-tagline">Smart Stock Analysis for Smart Investors | NSE/BSE</p>
</div>
""", unsafe_allow_html=True)

# Search
st.markdown('<div class="search-box">', unsafe_allow_html=True)
symbol = st.text_input("Enter Stock Symbol", placeholder="e.g., RELIANCE, TCS, INFY, HDFCBANK, ICICIBANK, SBIN...", key="symbol_input")
st.markdown('</div>', unsafe_allow_html=True)

if symbol:
    with st.spinner(f"Analyzing {symbol.upper()}..."):
        try:
            info, history, news = get_stock_data(symbol)
            
            tech = calculate_indicators(history)
            
            if not tech:
                st.error(f"No data available for {symbol}. Please check the symbol.")
                return
            
            rec = get_recommendation(tech, info)
            
            price = info.get('currentPrice', 0)
            prev = info.get('previousClose', price)
            change = ((price - prev) / prev * 100) if prev else 0
            change_class = "pos" if change >= 0 else "neg"
            
            # 6-Column Metrics
            st.markdown('<div class="metrics-grid">', unsafe_allow_html=True)
            
            st.markdown(f"""<div class="metric-card"><div class="metric-label">Price</div><div class="metric-value">₹{price:.2f}</div><div class="metric-change {change_class}">{'+' if change >= 0 else ''}{change:.2f}%</div></div>""", unsafe_allow_html=True)
            st.markdown(f"""<div class="metric-card"><div class="metric-label">Market Cap</div><div class="metric-value">{format_num(info.get('marketCap', 0))}</div></div>""", unsafe_allow_html=True)
            
            pe = info.get('trailingPE')
            pe_disp = f"{pe:.1f}" if pe else "N/A"
            st.markdown(f"""<div class="metric-card"><div class="metric-label">P/E Ratio</div><div class="metric-value">{pe_disp}</div></div>""", unsafe_allow_html=True)
            
            st.markdown(f"""<div class="metric-card"><div class="metric-label">52W High</div><div class="metric-value">₹{info.get('fiftyTwoWeekHigh', 0):.0f}</div></div>""", unsafe_allow_html=True)
            st.markdown(f"""<div class="metric-card"><div class="metric-label">52W Low</div><div class="metric-value">₹{info.get('fiftyTwoWeekLow', 0):.0f}</div></div>""", unsafe_allow_html=True)
            
            vol = info.get('averageVolume', info.get('volume', 0))
            st.markdown(f"""<div class="metric-card"><div class="metric-label">Avg Volume</div><div class="metric-value">{format_num(vol)}</div></div>""", unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Period Returns
            returns_html = ""
            for period, label in [("1m", "1M"), ("3m", "3M"), ("6m", "6M"), ("1y", "1Y")]:
                change_val = tech.get(f"change_{period}", 0)
                cls = "pos" if change_val >= 0 else "neg"
                returns_html += f"""<div class="metric-card"><div class="metric-label">{label}</div><div class="metric-change {cls}">{'+' if change_val >= 0 else ''}{change_val:.1f}%</div></div>"""
            
            st.markdown(f'<div class="metrics-grid">{returns_html}</div>', unsafe_allow_html=True)
            
            # Recommendation Box
            rec_class = "buy" if rec['rec'] in ["STRONG BUY", "BUY"] else ("sell" if rec['rec'] == "SELL" else "hold")
            
            st.markdown(f"""
            <div class="rec-box {rec_class}">
                <div class="rec-label-txt">INVESTMENT RECOMMENDATION</div>
                <div class="rec-value-txt">{rec['rec']}</div>
                <div class="rec-details">
                    <div class="rec-detail">
                        <div class="rec-detail-label">🎯 3M Target</div>
                        <div class="rec-detail-value">₹{rec['target_3m']:.0f}</div>
                    </div>
                    <div class="rec-detail">
                        <div class="rec-detail-label">🎯 6M Target</div>
                        <div class="rec-detail-value">₹{rec['target_6m']:.0f}</div>
                    </div>
                    <div class="rec-detail">
                        <div class="rec-detail-label">🎯 12M Target</div>
                        <div class="rec-detail-value">₹{rec['target_12m']:.0f}</div>
                    </div>
                    <div class="rec-detail">
                        <div class="rec-detail-label">🛡️ Stop Loss</div>
                        <div class="rec-detail-value">₹{rec['stop']:.0f}</div>
                    </div>
                    <div class="rec-detail">
                        <div class="rec-detail-label">📈 Upside</div>
                        <div class="rec-detail-value">+{rec['upside_12m']:.0f}%</div>
                    </div>
                    <div class="rec-detail">
                        <div class="rec-detail-label">⏱️ Horizon</div>
                        <div class="rec-detail-value">{rec['horizon']}</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Main Tabs
            tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Price Chart", "📈 Technical Analysis", "💼 Company Info", "📰 All News", "📋 Summary"])
            
            with tab1:
                period = st.select_slider("Time Period", options=["1m", "3m", "6m", "1y", "2y"], value="1y")
                chart = create_chart(tech, period)
                st.plotly_chart(chart, use_container_width=True)
                
                st.markdown("### Price Statistics")
                cstat1, cstat2, cstat3 = st.columns(3)
                with cstat1:
                    st.metric("Open", f"₹{tech['close'].iloc[0]:.2f}")
                with cstat2:
                    st.metric("High", f"₹{tech['close'].max():.2f}")
                with cstat3:
                    st.metric("Low", f"₹{tech['close'].min():.2f}")
                st.metric("Avg Price", f"₹{tech['close'].mean():.2f}")
                st.metric("ATR", f"₹{tech['atr']:.2f}")
            
            with tab2:
                # Technical Indicators Panel
                st.markdown('<div class="panel"><div class="panel-title">📊 Technical Indicators</div>', unsafe_allow_html=True)
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**RSI (14)**  \n\n- Below 30 = Oversold (Buy)  \n- Above 70 = Overbought (Sell)  \n- 30-70 = Neutral")
                    
                    rsi = tech['rsi']
                    rsi_tag = "bull" if rsi < 30 else ("bear" if rsi > 70 else "neut")
                    rsi_label = "Oversold" if rsi < 30 else ("Overbought" if rsi > 70 else "Neutral")
                    st.markdown(f"Current: <span class='tag {rsi_tag}'>{rsi:.1f} - {rsi_label}</span>", unsafe_allow_html=True)
                    
                    st.markdown("---")
                    st.markdown("**MACD (12,26,9)**  \n\n- MACD > Signal = Bullish  \n- MACD < Signal = Bearish")
                    
                    macd_tag = "bull" if tech['macd'] > tech['macd_signal'] else "bear"
                    st.markdown(f"MACD: <span class='tag {macd_tag}'>{'Bullish' if tech['macd'] > tech['macd_signal'] else 'Bearish'}</span>", unsafe_allow_html=True)
                    st.markdown(f"MACD: {tech['macd']:.2f} | Signal: {tech['macd_signal']:.2f}")
                    
                    st.markdown("---")
                    st.markdown("**Stochastic (14,3)**")
                    
                    stoch_tag = "bull" if tech['stoch_k'] < 20 else ("bear" if tech['stoch_k'] > 80 else "neut")
                    st.markdown(f"%K: <span class='tag {stoch_tag}'>{tech['stoch_k']:.0f}</span> | %D: {tech['stoch_d']:.0f}")
                
                with col2:
                    st.markdown("**Moving Averages**")
                    st.markdown(f"MA20: ₹{tech['sma20']:.0f}")
                    st.markdown(f"MA50: ₹{tech['sma50']:.0f}")
                    st.markdown(f"MA100: ₹{tech['sma100']:.0f}")
                    if tech['sma200']:
                        st.markdown(f"MA200: ₹{tech['sma200']:.0f}")
                    
                    st.markdown("---")
                    st.markdown("**Bollinger Bands**")
                    st.markdown(f"Upper: ₹{tech['bb_upper']:.0f}")
                    st.markdown(f"Middle: ₹{tech['bb_mid']:.0f}")
                    st.markdown(f"Lower: ₹{tech['bb_lower']:.0f}")
                
                st.markdown("</div>", unsafe_allow_html=True)
                
                # Signals Panel
                st.markdown('<div class="panel"><div class="panel-title">🚦 Technical Signals</div>', unsafe_allow_html=True)
                
                for sig, typ in rec['signals']:
                    icon = "🟢" if typ == "bull" else ("🔴" if typ == "bear" else "🟡")
                    st.markdown(f"{icon} {sig}")
                
                st.markdown("---")
                st.markdown(f"**Signal Score: {rec['weight']}** (Positive = Bullish, Negative = Bearish)")
                st.markdown("</div>", unsafe_allow_html=True)
            
            with tab3:
                c1, c2 = st.columns(2)
                
                with c1:
                    st.markdown('<div class="panel"><div class="panel-title">🏢 Company Information</div>', unsafe_allow_html=True)
                    st.markdown(f"**{info.get('longName', 'N/A')}**")
                    st.markdown(f"**Sector:** {info.get('sector', 'N/A')}")
                    st.markdown(f"**Industry:** {info.get('industry', 'N/A')}")
                    st.markdown(f"**Exchange:** NSE")
                    st.markdown(f"**ISIN:** {info.get('isin', 'N/A')}")
                    st.markdown("</div>", unsafe_allow_html=True)
                
                with c2:
                    st.markdown('<div class="panel"><div class="panel-title">💰 Financial Metrics</div>', unsafe_allow_html=True)
                    
                    eps = info.get('trailingEps')
                    st.markdown(f"<div class='data-row'><span class='data-label'>EPS</span><span class='data-value'>₹{eps:.2f}</span></div>", unsafe_allow_html=True) if eps else None
                    
                    dy = (info.get('dividendYield', 0) or 0) * 100
                    st.markdown(f"<div class='data-row'><span class='data-label'>Dividend Yield</span><span class='data-value'>{dy:.2f}%</span></div>", unsafe_allow_html=True)
                    
                    beta = info.get('beta', 0)
                    st.markdown(f"<div class='data-row'><span class='data-label'>Beta</span><span class='data-value'>{beta:.2f}</span></div>", unsafe_allow_html=True)
                    
                    pb = info.get('priceToBook')
                    if pb:
                        st.markdown(f"<div class='data-row'><span class='data-label'>P/B Ratio</span><span class='data-value'>{pb:.2f}</span></div>", unsafe_allow_html=True)
                    
                    ps = info.get('priceToSales')
                    if ps:
                        st.markdown(f"<div class='data-row'><span class='data-label'>P/S Ratio</span><span class='data-value'>{ps:.2f}</span></div>", unsafe_allow_html=True)
                    
                    roe = info.get('returnOnEquity')
                    if roe:
                        st.markdown(f"<div class='data-row'><span class='data-label'>ROE</span><span class='data-value'>{roe*100:.1f}%</span></div>", unsafe_allow_html=True)
                    
                    roa = info.get('returnOnAssets')
                    if roa:
                        st.markdown(f"<div class='data-row'><span class='data-label'>ROA</span><span class='data-value'>{roa*100:.1f}%</span></div>", unsafe_allow_html=True)
                    
                    st.markdown("</div>", unsafe_allow_html=True)
                
                st.markdown('<div class="panel"><div class="panel-title">📊 Ownership</div>', unsafe_allow_html=True)
                
                insider = info.get('heldByInsiders', 0) * 100 if info.get('heldByInsinders') else 0
                inst = info.get('heldByInstitutions', 0) * 100 if info.get('heldByInstitutions') else 0
                
                st.markdown(f"<div class='data-row'><span class='data-label'>Insider Holdings</span><span class='data-value'>{insider:.1f}%</span></div>", unsafe_allow_html=True)
                st.markdown(f"<div class='data-row'><span class='data-label'>Institutional</span><span class='data-value'>{inst:.1f}%</span></div>", unsafe_allow_html=True)
                
                shares = info.get('sharesOutstanding', 0)
                st.markdown(f"<div class='data-row'><span class='data-label'>Shares Outstanding</span><span class='data-value'>{format_num(shares)}</span></div>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)
            
            with tab4:
                if news:
                    for n in news:
                        title = n.get('title', 'No title')
                        publisher = n.get('publisher', 'Yahoo Finance')
                        st.markdown(f"""
                        <div class="news-card">
                            <div class="news-title-txt">{title}</div>
                            <div class="news-meta">{publisher}</div>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.info("No recent news available")
                
                # Also show historical data if no news
                if not news:
                    st.markdown("### Recent Price History")
                    recent = history.tail(10)[['Close', 'Volume']]
                    st.dataframe(recent, use_container_width=True)
            
            with tab5:
                st.markdown('<div class="panel"><div class="panel-title">📋 Investment Summary</div>', unsafe_allow_html=True)
                
                st.markdown(f"**Stock:** {symbol.upper()}")
                st.markdown(f"**Company:** {info.get('longName', 'N/A')}")
                st.markdown(f"**Current Price:** ₹{price:.2f}")
                st.markdown(f"**Recommendation:** {rec['rec']}")
                
                st.markdown("---")
                st.markdown("### Targets")
                st.markdown(f"- **3 Months:** ₹{rec['target_3m']:.0f}")
                st.markdown(f"- **6 Months:** ₹{rec['target_6m']:.0f}")
                st.markdown(f"- **12 Months:** ₹{rec['target_12m']:.0f}")
                st.markdown(f"- **Stop Loss:** ₹{rec['stop']:.0f} ({rec['downside']:.1f}% risk)")
                
                st.markdown("---")
                st.markdown("### Risk Assessment")
                st.markdown("- Market Risk: Medium")
                st.markdown("- Company Risk: Low-Medium")
                st.markdown("- Liquidity Risk: Low")
                
                st.markdown("</div>", unsafe_allow_html=True)
            
            # Disclaimer
            st.markdown("""
            <div class="disclaimer">
                ⚠️ <strong>Disclaimer:</strong> This AI-generated analysis is for educational purposes only and is NOT financial advice. 
                Stock investments involve risk. Consult a SEBI-registered financial advisor before investing.
            </div>
            """, unsafe_allow_html=True)
            
        except Exception as e:
            st.error(f"Error analyzing {symbol}: {str(e)}")
else:
    st.info("👈 Enter a stock symbol above to begin analysis")
    
    st.markdown("---")
    st.markdown("### 📈 Popular Stocks to Try")
    
    stocks = ["RELIANCE", "TCS", "INFY", "HDFCBANK", "ICICIBANK", "SBIN", "KOTAKBANK", "HUL", 
             "MARUTI", "TATAMOTORS", "M&M", "SUNPHARMA", "NESTLE", "BRITANNIA", "WIPRO", "HCLTECH"]
    
    for i in range(0, len(stocks), 4):
        cols = st.columns(4)
        for j, s in enumerate(stocks[i:i+4]):
            with cols[j]:
                st.caption(f"• {s}")

st.markdown('</div>', unsafe_allow_html=True)