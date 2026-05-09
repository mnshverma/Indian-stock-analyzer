import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import feedparser
import os
from dotenv import load_dotenv

st.set_page_config(page_title="Manver IQ", page_icon="📈", layout="wide")

st.markdown("""
<style>
    .block-container { padding: 0.5rem !important; }
    .search-box input { font-size: 1rem; }
</style>
""", unsafe_allow_html=True)

st.markdown("<div style='margin-top: 0.5rem;'></div>", unsafe_allow_html=True)

col1, col2 = st.columns([1, 4])
with col1:
    st.image("manver_logo.png", width=70)
with col2:
    st.markdown("**Manver IQ**")
    st.caption("Smart Stock Analysis")

col_s1, col_s2 = st.columns([5, 1])
with col_s1:
    sym = st.text_input("", placeholder="Search stock (RELIANCE, TCS...)", label_visibility="collapsed", key="s")
with col_s2:
    submitted = st.button("🔍")

st.markdown("""
<style>
    * { font-family: Arial, sans-serif; font-size: 11px; }
    .block-container { padding: 0.4rem !important; }
    div[data-testid="stMetric"] { background: white; padding: 0.25rem; border-radius: 3px; }
    div[data-testid="stMetric"] label { font-size: 9px; color: #666; }
    div[data-testid="stMetric"] .stMarkdown { font-size: 10px; font-weight: 600; }
    .search-box input { font-size: 0.8rem; }
    h1, h2, h3 { font-size: 0.9rem; }
    p, small { font-size: 10px; }
    .rec { padding: 0.4rem; border-radius: 5px; text-align: center; margin-bottom: 0.4rem; }
    .rec.buy { background: linear-gradient(135deg, #e8f5e9, #c8e6c9); border: 2px solid #4caf50; }
    .rec.sell { background: linear-gradient(135deg, #ffebee, #ffcdd2); border: 2px solid #f44336; }
    .rec.hold { background: linear-gradient(135deg, #fff8e1, #ffecb3); border: 2px solid #ffc107; }
    .rec-val { font-size: 0.9rem; font-weight: 700; }
    .rec.buy .rec-val { color: #2e7d32; }
    .rec.sell .rec-val { color: #c62828; }
    .rec.hold .rec-val { color: #f57c00; }
    .news { padding: 0.25rem; border-left: 3px solid #1976d2; background: #f5f5f5; margin-bottom: 0.15rem; }
    .news-t { font-size: 0.6rem; }
    .news-s { font-size: 0.5rem; color: #888; }
    .tag { padding: 0.1rem 0.25rem; border-radius: 8px; font-size: 0.55rem; }
    .tag.bull { background: #c8e6c9; color: #2e7d32; }
    .tag.bear { background: #ffcdd2; color: #c62828; }
    .ai-box { background: #e3f2fd; padding: 0.4rem; border-radius: 5px; margin-bottom: 0.4rem; border: 1px solid #1976d2; }
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown strong { font-size: 0.85rem; }
    .stTabs [data-baseweb="tab-list"] { gap: 0.3rem; }
    .stTabs [data-baseweb="tab"] { font-size: 0.7rem; padding: 0.2rem 0.5rem; }
    div[data-testid="stVerticalBlock"] { gap: 0.3rem; }
    .stMarkdown { margin-bottom: 0.2rem; }
    .stDivider { margin: 0.3rem 0; }
    @media (max-width: 600px) {
        * { font-size: 10px; }
    }
</style>
""", unsafe_allow_html=True)


def get_stock(sym):
    t = f"{sym.upper()}.NS"
    s = yf.Ticker(t)
    return s.info, s.history(period="5y")


def get_news(sym):
    news, seen = [], set()
    sym_c = sym.upper().replace(".NS", "")
    try:
        feed = feedparser.parse(f"https://news.moneycontrol.com/rss/companyfeed/{sym_c}", timeout=8)
        for e in feed.entries[:5]:
            t = e.get("title", "")
            if t and len(t) > 15 and t.lower() not in seen:
                seen.add(t.lower())
                news.append({"title": t[:120], "source": "Moneycontrol"})
    except:
        pass
    if not news:
        news = [{"title": "No news available", "source": "Info"}]
    return news[:8]


def get_tech(hist):
    c = hist["Close"]
    if len(c) < 2:
        return None
    d = c.diff()
    g = d.where(d > 0, 0).ewm(span=14).mean()
    l = (-d.where(d < 0, 0)).ewm(span=14).mean()
    rsi = 100 - (100 / (1 + g / l))
    e12, e26 = c.ewm(span=12).mean(), c.ewm(span=26).mean()
    macd = e12 - e26
    macd_s = macd.ewm(span=9).mean()
    m20 = c.rolling(20).mean().iloc[-1]
    m50 = c.rolling(50).mean().iloc[-1]
    m200 = c.rolling(200).mean().iloc[-1] if len(c) >= 200 else None
    return {"rsi": rsi.iloc[-1], "macd": macd.iloc[-1], "macd_s": macd_s.iloc[-1], "m20": m20, "m50": m50, "m200": m200, "price": c.iloc[-1], "close": c, "volume": hist["Volume"]}


def get_rec(tech):
    w, sigs = 0, []
    if tech["rsi"] < 30:
        sigs.append(("Oversold", "bull"))
        w += 2
    elif tech["rsi"] > 70:
        sigs.append(("Overbought", "bear"))
        w -= 2
    if tech["macd"] > tech["macd_s"]:
        sigs.append(("MACD Bull", "bull"))
        w += 1
    else:
        sigs.append(("MACD Bear", "bear"))
        w -= 1
    if tech["m200"] and tech["price"] > tech["m200"]:
        sigs.append((">MA200", "bull"))
        w += 1
    rec = "STRONG BUY" if w >= 2 else ("BUY" if w >= 0 else ("SELL" if w < -1 else "HOLD"))
    tgt = tech["price"] * (1.25 if rec == "STRONG BUY" else (1.15 if rec == "BUY" else (1.05 if rec == "HOLD" else 0.95)))
    stop = tech["price"] * (0.93 if rec == "SELL" else 0.95)
    return {"rec": rec, "tgt": tgt, "stop": stop, "up": ((tgt-tech["price"])/tech["price"])*100, "dn": ((tech["price"]-stop)/tech["price"])*100}


def run_ai_analysis(sym):
    try:
        api_key = None
        try:
            import streamlit as st
            api_key = st.secrets.get("OPENAI_API_KEY") if hasattr(st, 'secrets') else None
        except:
            pass
        if not api_key:
            load_dotenv()
            api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            return None
        from crew_agents import run_stock_analysis
        return run_stock_analysis(sym)
    except Exception as e:
        return {"error": str(e)}


def make_chart(tech, period="1y"):
    c = tech["close"]
    days = {"1m": 21, "3m": 63, "6m": 126, "1y": 252}.get(period, 252)
    cp = c.iloc[-days:]
    f = make_subplots(specs=[[{"secondary_y": True}]])
    f.add_trace(go.Scatter(x=cp.index, y=cp, name="Price", line=dict(color="#1565c0", width=2)), secondary_y=False)
    f.add_trace(go.Scatter(x=c.rolling(20).mean().iloc[-days:].index, y=c.rolling(20).mean().iloc[-days:], name="MA20", line=dict(color="#ff9800", width=1, dash="dot")), secondary_y=False)
    f.add_trace(go.Scatter(x=c.rolling(50).mean().iloc[-days:].index, y=c.rolling(50).mean().iloc[-days:], name="MA50", line=dict(color="#4caf50", width=1.5)), secondary_y=False)
    if tech["m200"]:
        f.add_trace(go.Scatter(x=c.rolling(200).mean().iloc[-days:].index, y=c.rolling(200).mean().iloc[-days:], name="MA200", line=dict(color="#9c27b0", width=1.5, dash="dash")), secondary_y=False)
    f.add_trace(go.Bar(x=tech["volume"].iloc[-days:].index, y=tech["volume"].iloc[-days:], name="Vol", marker_color="rgba(150,150,150,0.4)"), secondary_y=True)
    f.update_layout(template="plotly_white", height=280, margin=dict(l=30, r=20, t=20, b=30), legend=dict(orientation="h", y=1.05, x=0.5))
    return f


def fmt(v):
    if not v:
        return "N/A"
    if v >= 1e12:
        return f"₹{v/1e12:.1f}T"
    if v >= 1e10:
        return f"₹{v/1e10:.1f}B"
    if v >= 1e7:
        return f"₹{v/1e7:.1f}Cr"
    return f"₹{v:,.0f}"


if sym and submitted:
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    ai_result = run_ai_analysis(sym) if api_key else None

    with st.spinner("Loading..."):
        try:
            info, hist = get_stock(sym)
            tech = get_tech(hist)
            if not tech:
                st.error("No data")
                st.stop()

            rec = get_rec(tech)
            news = get_news(sym)
            p = info.get("currentPrice", 0)
            pc = info.get("previousClose", p)
            chg = ((p - pc) / pc * 100) if pc else 0

            if ai_result and ai_result.get("status") == "success":
                st.markdown('<div class="ai-box"><b>🤖 AI Analysis:</b><br>' + ai_result.get("result", "")[:1500] + '</div>', unsafe_allow_html=True)

            c1, c2, c3, c4, c5 = st.columns(5)
            c1.metric("Price", f"₹{p:.1f}", f"{chg:+.1f}%")
            c2.metric("Mkt Cap", fmt(info.get("marketCap", 0)))
            pe = info.get("trailingPE")
            c3.metric("P/E", f"{pe:.1f}" if pe else "N/A")
            c4.metric("52W High", f"₹{info.get('fiftyTwoWeekHigh', 0):.0f}")
            c5.metric("52W Low", f"₹{info.get('fiftyTwoWeekLow', 0):.0f}")

            rc = "buy" if rec["rec"] in ["STRONG BUY", "BUY"] else ("sell" if rec["rec"] == "SELL" else "hold")
            st.markdown(f'<div class="rec {rc}"><div class="rec-val">{rec["rec"]}</div><div>Target: ₹{rec["tgt"]:.0f} (+{rec["up"]:.0f}%) | Stop: ₹{rec["stop"]:.0f} (-{rec["dn"]:.0f}%)</div></div>', unsafe_allow_html=True)

            t1, t2, t3, t4 = st.tabs(["📊 Overview", "📈 Technical", "🏢 Company", "📰 News"])
            with t1:
                st.markdown("**Today's Price Action**")
                c_p1, c_p2, c_p3, c_p4 = st.columns(4)
                with c_p1:
                    st.metric("Today's High", f"₹{info.get('fiftyTwoWeekHigh', 0):.0f}")
                with c_p2:
                    st.metric("Today's Low", f"₹{info.get('fiftyTwoWeekLow', 0):.0f}")
                with c_p3:
                    st.metric("Open", f"₹{info.get('open', p):.1f}")
                with c_p4:
                    st.metric("Prev Close", f"₹{pc:.1f}")
                
                c_v1, c_v2 = st.columns(2)
                with c_v1:
                    vol = info.get("volume", 0)
                    st.metric("Volume", f"{vol:,.0f}" if vol else "N/A")
                with c_v2:
                    st.metric("Circuit", f"₹{info.get('dayLow', 0):.0f} / ₹{info.get('dayHigh', 0):.0f}")
                
                st.markdown("---")
                st.markdown("**📊 Fundamentals**")
                mc = info.get("marketCap", 0)
                roe = info.get("returnOnEquity")
                pe = info.get("trailingPE")
                eps = info.get("trailingEps")
                pb = info.get("priceToBook")
                dy = info.get("dividendYield")
                bv = info.get("bookValue")
                de = info.get("debtToEquity")
                fv = info.get("faceValue")
                
                c_f1, c_f2, c_f3, c_f4 = st.columns(4)
                with c_f1:
                    st.markdown("<small>Mkt Cap<br><b>" + fmt(mc) + "</b></small>", unsafe_allow_html=True)
                with c_f2:
                    st.markdown("<small>ROE<br><b>" + f"{(roe or 0)*100:.1f}%</b></small>" if roe else "<small>ROE<br><b>N/A</b></small>", unsafe_allow_html=True)
                with c_f3:
                    st.markdown("<small>P/E<br><b>" + f"{pe:.1f}" + "</b></small>" if pe else "<small>P/E<br><b>N/A</b></small>", unsafe_allow_html=True)
                with c_f4:
                    st.markdown("<small>EPS<br><b>₹" + f"{eps:.2f}" + "</b></small>" if eps else "<small>EPS<br><b>N/A</b></small>", unsafe_allow_html=True)
                
                c_f5, c_f6, c_f7, c_f8 = st.columns(4)
                with c_f5:
                    st.markdown("<small>P/B<br><b>" + f"{pb:.1f}" + "</b></small>" if pb else "<small>P/B<br><b>N/A</b></small>", unsafe_allow_html=True)
                with c_f6:
                    st.markdown("<small>Div Yield<br><b>" + f"{(dy or 0)*100:.1f}%" + "</b></small>" if dy else "<small>Div Yield<br><b>N/A</b></small>", unsafe_allow_html=True)
                with c_f7:
                    st.markdown("<small>Book Value<br><b>₹" + f"{bv:.2f}" + "</b></small>" if bv else "<small>Book Value<br><b>N/A</b></small>", unsafe_allow_html=True)
                with c_f8:
                    st.markdown("<small>Debt/Eq<br><b>" + f"{de:.1f}" + "</b></small>" if de else "<small>Debt/Eq<br><b>N/A</b></small>", unsafe_allow_html=True)
                
                st.markdown("---")
                st.markdown("**📈 52 Week Performance**")
                c_52_1, c_52_2 = st.columns(2)
                with c_52_1:
                    st.metric("52W High", f"₹{info.get('fiftyTwoWeekHigh', 0):.0f}")
                with c_52_2:
                    st.metric("52W Low", f"₹{info.get('fiftyTwoWeekLow', 0):.0f}")
            
            with t2:
                per = st.select_slider("", ["1m", "3m", "6m", "1y", "2y"], label_visibility="collapsed")
                st.plotly_chart(make_chart(tech, per), use_container_width=True)
            with t2:
                rsi = tech["rsi"]
                rt = "bull" if rsi < 30 else ("bear" if rsi > 70 else "neut")
                mt = "bull" if tech["macd"] > tech["macd_s"] else "bear"
                
                st.markdown("**📊 Indicators**")
                c_ind1, c_ind2 = st.columns(2)
                with c_ind1:
                    st.markdown("RSI (0-100): <small>below 30=oversold, above 70=overbought</small>", unsafe_allow_html=True)
                    st.metric("RSI", f"{rsi:.0f}")
                with c_ind2:
                    st.markdown("MACD: <small>above Signal=bullish cross</small>", unsafe_allow_html=True)
                    st.metric("MACD vs Signal", f"{tech['macd']:.2f} vs {tech['macd_s']:.2f}")
                
                st.markdown("**📈 Moving Averages**")
                c_ma1, c_ma2, c_ma3 = st.columns(3)
                with c_ma1:
                    st.metric("MA20", f"₹{tech['m20']:.0f}")
                with c_ma2:
                    st.metric("MA50", f"₹{tech['m50']:.0f}")
                with c_ma3:
                    st.metric("MA200", f"₹{tech['m200']:.0f}" if tech["m200"] else "N/A")
                
                st.markdown("**💰 Price Basis**")
                pe = info.get("trailingPE")
                pb = info.get("priceToBook")
                c_f1, c_f2, c_f3 = st.columns(3)
                with c_f1:
                    st.markdown("P/E: <small>lower=cheap (15-25 avg)</small>", unsafe_allow_html=True)
                    st.metric("P/E", f"{pe:.1f}" if pe else "N/A")
                with c_f2:
                    st.markdown("P/B: <small>lower=undervalued (<3 good)</small>", unsafe_allow_html=True)
                    st.metric("P/B", f"{pb:.1f}" if pb else "N/A")
                with c_f3:
                    ps = info.get("priceToSalesTrailing12Months")
                    st.markdown("P/S: <small>lower=better (<2 ideal)</small>", unsafe_allow_html=True)
                    st.metric("P/S", f"{ps:.1f}" if ps else "N/A")
                
                st.markdown("**⚡ Efficiency**")
                roe = info.get("returnOnEquity")
                roa = info.get("returnOnAssets")
                c_o1, c_o2 = st.columns(2)
                with c_o1:
                    st.markdown("ROE: <small>higher=better (>15% good)</small>", unsafe_allow_html=True)
                    st.metric("ROE", f"{(roe or 0)*100:.1f}%" if roe else "N/A")
                with c_o2:
                    st.markdown("ROA: <small>higher=efficient (>5% good)</small>", unsafe_allow_html=True)
                    st.metric("ROA", f"{(roa or 0)*100:.1f}%" if roa else "N/A")
                
                de = info.get("debtToEquity")
                st.markdown("D/E: <small>lower=less debt (<50 safe)</small>", unsafe_allow_html=True)
                st.metric("Debt/Equity", f"{de:.1f}" if de else "N/A")
                
                st.markdown("**🎯 Valuation**")
                eps = info.get("trailingEps")
                bv = info.get("bookValue")
                dy = info.get("dividendYield")
                c_v1, c_v2, c_v3 = st.columns(3)
                with c_v1:
                    st.markdown("EPS: <small>earnings/share (higher=better)</small>", unsafe_allow_html=True)
                    st.metric("EPS", f"₹{eps:.2f}" if eps else "N/A")
                with c_v2:
                    st.markdown("Book Value: <small>assets per share</small>", unsafe_allow_html=True)
                    st.metric("Book", f"₹{bv:.2f}" if bv else "N/A")
                with c_v3:
                    st.markdown("Div Yield: <small>annual dividend %</small>", unsafe_allow_html=True)
                    st.metric("Yield", f"{(dy or 0)*100:.1f}%" if dy else "N/A")
            with t3:
                st.markdown(f"**{info.get('longName', sym.upper())}**")
                st.markdown(f"Sector: {info.get('sector', 'N/A')}")
                eps = info.get("trailingEps")
                st.markdown(f"EPS: ₹{eps:.2f}" if eps else "EPS: N/A")
                st.markdown(f"Div Yield: {(info.get('dividendYield', 0) or 0)*100:.1f}%")
            with t4:
                for n in news:
                    st.markdown(f"<div class='news'><div class='news-t'>{n['title']}</div><div class='news-s'>{n['source']}</div></div>", unsafe_allow_html=True)

            st.caption("⚠️ Not financial advice.")
        except Exception as e:
            st.error(f"Error: {e}")
else:
    st.info("Enter a stock symbol to analyze")
    st.markdown("**Popular:** RELIANCE, TCS, INFY, HDFCBANK, ICICIBANK, SBIN")