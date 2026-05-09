import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests
import feedparser
import json

st.set_page_config(page_title="Manver IQ", page_icon="🧠", layout="wide")

st.markdown("""
<style>
    * { font-family: Arial, sans-serif; }
    .block-container { padding: 1rem !important; max-width: 100% !important; }
    
    .header { background: linear-gradient(135deg, #1a237e, #3949ab); padding: 1rem; border-radius: 8px; color: white; margin-bottom: 0.75rem; text-align: center; }
    .header h1 { font-size: 1.5rem; font-weight: 700; margin: 0; }
    .header p { font-size: 0.85rem; opacity: 0.9; margin: 0.25rem 0 0 0; }
    
    .search { padding: 0.75rem; background: white; border-radius: 8px; box-shadow: 0 1px 4px rgba(0,0,0,0.1); margin-bottom: 0.75rem; }
    .stTextInput input { font-size: 1rem; }
    
    .metrics { display: flex; gap: 0.4rem; margin-bottom: 0.5rem; flex-wrap: wrap; }
    .m { flex: 1; min-width: 90px; background: white; padding: 0.5rem; border-radius: 6px; box-shadow: 0 1px 3px rgba(0,0,0,0.08); text-align: center; }
    .m-label { font-size: 0.6rem; color: #666; text-transform: uppercase; }
    .m-val { font-size: 0.9rem; font-weight: 700; color: #1a237e; }
    .m-delta { font-size: 0.7rem; }
    .m-delta.pos { color: #2e7d32; }
    .m-delta.neg { color: #c62828; }
    
    .rec { padding: 0.75rem; border-radius: 8px; text-align: center; margin-bottom: 0.75rem; }
    .rec.buy { background: #e8f5e9; border: 2px solid #4caf50; }
    .rec.sell { background: #ffebee; border: 2px solid #f44336; }
    .rec.hold { background: #fff8e1; border: 2px solid #ffc107; }
    .rec-lbl { font-size: 0.7rem; color: #666; }
    .rec-val { font-size: 1.8rem; font-weight: 800; }
    .rec.buy .rec-val { color: #2e7d32; }
    .rec.sell .rec-val { color: #c62828; }
    .rec.hold .rec-val { color: #f57c00; }
    .rec-tags { display: flex; justify-content: center; gap: 0.75rem; font-size: 0.75rem; margin-top: 0.4rem; flex-wrap: wrap; }
    
    .tabs { margin-bottom: 0.5rem; }
    .stTabs [data-baseweb="tab-list"] { gap: 0.25rem; background: #f5f5f5; padding: 0.2rem; border-radius: 5px; }
    .stTabs [data-baseweb="tab"] { padding: 0.35rem 0.7rem; border-radius: 4px 4px 0 0; font-size: 0.8rem; }
    .stTabs [aria-selected="true"] { background: white; }
    
    .panel { background: white; padding: 0.75rem; border-radius: 6px; box-shadow: 0 1px 3px rgba(0,0,0,0.06); margin-bottom: 0.5rem; }
    .panel h3 { font-size: 0.85rem; font-weight: 600; color: #1a237e; margin: 0 0 0.5rem 0; padding-bottom: 0.3rem; border-bottom: 2px solid #1a237e; }
    
    .row { display: flex; justify-content: space-between; padding: 0.3rem 0; border-bottom: 1px solid #f0f0f0; }
    .row:last-child { border-bottom: none; }
    .row-l { color: #666; font-size: 0.8rem; }
    .row-r { font-weight: 600; color: #1a237e; font-size: 0.8rem; }
    
    .tag { display: inline-block; padding: 0.2rem 0.5rem; border-radius: 12px; font-size: 0.7rem; font-weight: 600; margin: 0.15rem; }
    .tag.bull { background: #c8e6c9; color: #2e7d32; }
    .tag.bear { background: #ffcdd2; color: #c62828; }
    .tag.neut { background: #fff9c4; color: #f57f17; }
    
    .news { padding: 0.5rem; border-left: 3px solid #1976d2; background: #f5f5f5; margin-bottom: 0.35rem; border-radius: 0 4px 4px 0; }
    .news-t { font-size: 0.75rem; font-weight: 500; }
    .news-s { font-size: 0.65rem; color: #888; }
    
    .cols { display: flex; gap: 0.5rem; }
    .col { flex: 1; }
    .col h4 { font-size: 0.8rem; font-weight: 600; color: #333; margin: 0 0 0.4rem 0; }
</style>
""", unsafe_allow_html=True)


def get_stock(sym):
    t = f"{sym.upper()}.NS"
    s = yf.Ticker(t)
    info = s.info
    hist = s.history(period="5y")
    return info, hist


def get_news(sym):
    news, seen = [], set()
    sym_c = sym.upper().replace(".NS", "")
    
    try:
        feed = feedparser.parse(f"https://news.moneycontrol.com/rss/companyfeed/{sym_c}", timeout=8)
        for e in feed.entries[:8]:
            t = e.get("title", "")
            if t and len(t) > 15 and t.lower() not in seen:
                seen.add(t.lower())
                news.append({"title": t, "source": "Moneycontrol"})
    except:
        pass
    
    if not news:
        try:
            feed = feedparser.parse(f"https://news.moneycontrol.com/rss/searchfeed/SECTIONS_{sym_c}", timeout=8)
            for e in feed.entries[:6]:
                t = e.get("title", "")
                if t and len(t) > 15 and t.lower() not in seen:
                    seen.add(t.lower())
                    news.append({"title": t, "source": "Moneycontrol"})
        except:
            pass
    
    return news[:10]


def get_tech(hist):
    c = hist["Close"]
    if len(c) < 2:
        return None
    
    d = c.diff()
    g = d.where(d > 0, 0).ewm(span=14, adjust=False).mean()
    l = (-d.where(d < 0, 0)).ewm(span=14, adjust=False).mean()
    rsi = 100 - (100 / (1 + (g / l)))
    
    e12 = c.ewm(span=12).mean()
    e26 = c.ewm(span=26).mean()
    macd = e12 - e26
    macd_s = macd.ewm(span=9).mean()
    
    m20 = c.rolling(20).mean().iloc[-1]
    m50 = c.rolling(50).mean().iloc[-1]
    m200 = c.rolling(200).mean().iloc[-1] if len(c) >= 200 else None
    
    return {
        "rsi": rsi.iloc[-1] if len(rsi) > 0 and not np.isnan(rsi.iloc[-1]) else 50,
        "macd": macd.iloc[-1] if len(macd) > 0 else 0,
        "macd_s": macd_s.iloc[-1] if len(macd_s) > 0 else 0,
        "m20": m20, "m50": m50, "m200": m200,
        "price": c.iloc[-1]
    }


def get_rec(tech):
    w, sigs = 0, []
    
    if tech["rsi"] < 30:
        sigs.append(("Oversold", "bull")); w += 2
    elif tech["rsi"] > 70:
        sigs.append(("Overbought", "bear")); w -= 2
    
    if tech["macd"] > tech["macd_s"]:
        sigs.append(("MACD Bull", "bull")); w += 1
    else:
        sigs.append(("MACD Bear", "bear")); w -= 1
    
    if tech["m200"] and tech["price"] > tech["m200"]:
        sigs.append((">MA200", "bull")); w += 1
    
    rec = "STRONG BUY" if w >= 2 else ("BUY" if w >= 0 else ("SELL" if w < -1 else "HOLD"))
    tgt = tech["price"] * (1.25 if rec == "STRONG BUY" else (1.15 if rec == "BUY" else (1.05 if rec == "HOLD" else 0.95)))
    stop = tech["price"] * (0.93 if rec == "SELL" else 0.95)
    
    return {"rec": rec, "sigs": sigs, "tgt": tgt, "stop": stop, "up": ((tgt-tech["price"])/tech["price"])*100, "dn": ((tech["price"]-stop)/tech["price"])*100}


def make_chart(tech, period="1y"):
    c = tech["close"]
    days = {"1m":21,"3m":63,"6m":126,"1y":252}.get(period,252)
    cp = c.iloc[-days:]
    
    f = make_subplots(specs=[[{"secondary_y": True}]])
    f.add_trace(go.Scatter(x=cp.index, y=cp, name="Price", line=dict(color="#1565c0", width=2)), secondary_y=False)
    f.add_trace(go.Scatter(x=c.rolling(20).mean().iloc[-days:].index, y=c.rolling(20).mean().iloc[-days:], name="MA20", line=dict(color="#ff9800", width=1, dash="dot")), secondary_y=False)
    f.add_trace(go.Scatter(x=c.rolling(50).mean().iloc[-days:].index, y=c.rolling(50).mean().iloc[-days:], name="MA50", line=dict(color="#4caf50", width=1.5)), secondary_y=False)
    
    if tech["m200"]:
        f.add_trace(go.Scatter(x=c.rolling(200).mean().iloc[-days:].index, y=c.rolling(200).mean().iloc[-days:], name="MA200", line=dict(color="#9c27b0", width=1.5, dash="dash")), secondary_y=False)
    
    f.add_trace(go.Bar(x=tech["volume"].iloc[-days:].index, y=tech["volume"].iloc[-days:], name="Vol", marker_color="rgba(150,150,150,0.4)"), secondary_y=True)
    f.update_layout(template="plotly_white", height=300, margin=dict(l=30,r=20,t=20,b=30), legend=dict(orientation="h",y=1.05,x=0.5), hovermode="x unified")
    f.update_yaxes(showgrid=True, gridcolor="#f5f5f5", secondary_y=False)
    f.update_yaxes(secondary_y=True, showgrid=False)
    return f


def fmt(v):
    if not v: return "N/A"
    if v >= 1e12: return f"₹{v/1e12:.1f}T"
    if v >= 1e10: return f"₹{v/1e10:.1f}B"
    if v >= 1e7: return f"₹{v/1e7:.1f}Cr"
    return f"₹{v:,.0f}"


# === MAIN ===
st.markdown('<div style="max-width:1100px;margin:0 auto;">', unsafe_allow_html=True)

st.markdown('<div class="header"><h1>🧠 Manver IQ</h1><p>Smart Stock Analysis | NSE/BSE</p></div>', unsafe_allow_html=True)

st.markdown('<div class="search">', unsafe_allow_html=True)
sym = st.text_input("Stock Symbol", placeholder="RELIANCE, TCS, HDFCBANK...", key="s")
st.markdown('</div>', unsafe_allow_html=True)

if sym:
    st.caption(f"Analyzing {sym.upper()}...")
    try:
        info, hist = get_stock(sym)
        tech = get_tech(hist)
        
        if not tech:
            st.error("No data. Check symbol.")
        else:
            rec = get_rec(tech)
            news = get_news(sym)
            
            p = info.get("currentPrice", 0)
            pc = info.get("previousClose", p)
            chg = ((p-pc)/pc*100) if pc else 0
            
            # Metrics
            st.markdown('<div class="metrics">', unsafe_allow_html=True)
            st.markdown(f'<div class="m"><div class="m-label">Price</div><div class="m-val">₹{p:.1f}</div><div class="m-delta {"pos" if chg>=0 else "neg"}">{chg:+.1f}%</div></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="m"><div class="m-label">MktCap</div><div class="m-val">{fmt(info.get("marketCap"))}</div></div>', unsafe_allow_html=True)
            pe = info.get("trailingPE")
            pe_val = f"{pe:.1f}" if pe else "N/A"
            st.markdown(f'<div class="m"><div class="m-label">P/E</div><div class="m-val">{pe_val}</div></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="m"><div class="m-label">52W High</div><div class="m-val">₹{info.get("fiftyTwoWeekHigh",0):.0f}</div></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="m"><div class="m-label">52W Low</div><div class="m-val">₹{info.get("fiftyTwoWeekLow",0):.0f}</div></div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Rec
            rc = "buy" if rec["rec"] in ["STRONG BUY","BUY"] else ("sell" if rec["rec"]=="SELL" else "hold")
            st.markdown(f'''
            <div class="rec {rc}">
                <div class="rec-lbl">RECOMMENDATION</div>
                <div class="rec-val">{rec["rec"]}</div>
                <div class="rec-tags">
                    <span>Target ₹{rec["tgt"]:.0f} (+{rec["up"]:.0f}%)</span>
                    <span>Stop ₹{rec["stop"]:.0f} (-{rec["dn"]:.0f}%)</span>
                </div>
            </div>
            ''', unsafe_allow_html=True)
            
            # Tabs
            t1,t2,t3,t4 = st.tabs(["Chart","Technical","Company","News"])
            
            with t1:
                per = st.select_slider("Period", ["1m","3m","6m","1y","2y"], label_visibility="collapsed")
                st.plotly_chart(make_chart(tech, per), use_container_width=True)
            
            with t2:
                c1,c2 = st.columns(2)
                with c1:
                    st.markdown("##### Indicators")
                    rsi = tech["rsi"]
                    rt = "bull" if rsi < 30 else ("bear" if rsi > 70 else "neut")
                    st.markdown(f"RSI: <span class='tag {rt}'>{rsi:.0f}</span>", unsafe_allow_html=True)
                    mt = "bull" if tech["macd"] > tech["macd_s"] else "bear"
                    st.markdown(f"MACD: <span class='tag {mt}'>{'Bull' if tech['macd']>tech['macd_s'] else 'Bear'}</span>", unsafe_allow_html=True)
                    st.markdown(f"MA20: ₹{tech['m20']:.0f}")
                    st.markdown(f"MA50: ₹{tech['m50']:.0f}")
                    if tech["m200"]: st.markdown(f"MA200: ₹{tech['m200']:.0f}")
                with c2:
                    st.markdown("##### Signals")
                    for s,t in rec["sigs"]:
                        ic = "🟢" if t=="bull" else ("🔴" if t=="bear" else "🟡")
                        st.markdown(f"{ic} {s}")
            
            with t3:
                c1,c2 = st.columns(2)
                with c1:
                    st.markdown("##### Company")
                    st.markdown(f"**{info.get('longName',sym.upper())}**")
                    st.markdown(f"**Sector:** {info.get('sector','N/A')}")
                    st.markdown(f"**Industry:** {info.get('industry','N/A')}")
                with c2:
                    st.markdown("##### Metrics")
                    eps = info.get("trailingEps")
                    st.markdown(f"**EPS:** ₹{eps:.2f}" if eps else "**EPS:** N/A")
                    dy = (info.get("dividendYield",0) or 0)*100
                    st.markdown(f"**Div Yield:** {dy:.1f}%")
                    st.markdown(f"**Beta:** {info.get('beta',0):.2f}")
            
            with t4:
                if news:
                    for n in news:
                        st.markdown(f"""
                        <div class="news">
                            <div class="news-t">" + n['title'] + "</div>
                            <div class="news-s">{n['source']}</div>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.warning("No news found. Try manually:")
                    st.markdown(f"[Moneycontrol {sym.upper()}](https://www.moneycontrol.com/stocks/cp_search/?search={sym.upper()})")
            
            st.caption("⚠️ Not financial advice.")
            
    except Exception as e:
        st.error(f"Error: {e}")
else:
    st.info("Enter a stock symbol above")
    st.markdown("##### Popular: RELIANCE, TCS, INFY, HDFCBANK, ICICIBANK, SBIN, KOTAKBANK, HUL")

st.markdown('</div>', unsafe_allow_html=True)