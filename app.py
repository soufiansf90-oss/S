import streamlit as st import pandas as pd import plotly.express as px import plotly.graph_objects as go from datetime import datetime, timedelta import sqlite3 import calendar import base64 from io import BytesIO from PIL import Image

--- 1. SETTINGS & ADVANCED NEON UI ---

st.set_page_config(page_title="369 SHADOW V44", layout="wide")

st.markdown("""

<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@700&family=Inter:wght@400;600&display=swap');

.stApp { background: #05070a; color: #e6edf3; font-family: 'Inter', sans-serif; }

/* Welcome Message */
.welcome-text { font-family: 'Orbitron'; color: #00f5ff; font-size: 1.6rem; text-align: center; margin-bottom: 25px; text-shadow: 0 0 20px rgba(0,245,255,0.8); letter-spacing: 2px; }

/* Animation */
.content-fade { animation: slideUp 0.5s ease-out; }
@keyframes slideUp { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }

/* Sidebar Navigation Styling */
[data-testid="stSidebar"] { background-color: #080b10; border-right: 2px solid #00f5ff33; }

div[data-testid="stSidebar"] .stRadio > label { display: none; }
div[data-testid="stSidebar"] .stRadio div[role="radiogroup"] { gap: 20px; padding-top: 20px; }
div[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label { background: rgba(255,255,255,0.03); border: 1px solid rgba(0,245,255,0.2); padding: 18px 25px !important; border-radius: 12px !important; transition: 0.3s all; width: 100%; color: #8b949e; font-family: 'Orbitron'; text-transform: uppercase; font-size: 0.95rem; }

div[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label[data-baseweb="radio"]:has(input:checked) { background: rgba(0,245,255,0.1) !important; border: 1px solid #00f5ff !important; color: #00f5ff !important; box-shadow: 0 0 20px rgba(0,245,255,0.4); }

/* Journal Styling */
.journal-win { border-left: 5px solid #34d399 !important; background: rgba(52, 211, 153, 0.05) !important; }
.journal-loss { border-left: 5px solid #ef4444 !important; background: rgba(239, 68, 68, 0.05) !important; }
.journal-be { border-left: 5px solid #fbbf24 !important; background: rgba(251, 191, 36, 0.05) !important; }

/* Performance Grid */
.perf-card { background: rgba(22, 27, 34, 0.7); border: 1px solid rgba(0, 245, 255, 0.1); padding: 22px; border-radius: 15px; text-align: center; transition: 0.3s; }
.perf-card:hover { border-color: #00f5ff; box-shadow: 0 0 20px rgba(0, 245, 255, 0.2); }
.perf-val { font-size: 1.9rem; font-weight: bold; font-family: 'Orbitron'; color: #e6edf3; }
.perf-label { font-size: 0.8rem; color: #00f5ff; text-transform: uppercase; letter-spacing: 2px; margin-top: 5px; }
</style>""", unsafe_allow_html=True)

--- 2. DATABASE ---

conn = sqlite3.connect('elite_v44.db', check_same_thread=False) c = conn.cursor() c.execute('''CREATE TABLE IF NOT EXISTS trades (id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT, pair TEXT, outcome TEXT, pnl REAL, rr REAL, balance REAL, mindset TEXT, setup TEXT, image TEXT)''') conn.commit()

--- 3. DATA PREP ---

df = pd.read_sql_query("SELECT * FROM trades", conn) current_balance = df['balance'].iloc[-1] if not df.empty else 1000.0

if not df.empty: df['date_dt'] = pd.to_datetime(df['date']) df = df.sort_values(by=['date_dt','id']) df['cum_pnl'] = df['pnl'].cumsum() df['equity_curve'] = df['balance'].iloc[0] + df['cum_pnl']

--- 4. SIDEBAR NAVIGATION ---

with st.sidebar: st.markdown('<div style="text-align:center; padding: 20px 0;"><span style="font-family:Orbitron; color:#00f5ff; font-size:1.6rem; text-shadow: 0 0 20px #00f5ff88;">SHADOW SYSTEM</span></div>', unsafe_allow_html=True) st.metric("ACCOUNT BALANCE", f"${current_balance:,.2f}") st.divider() choice = st.radio("MENU", ["TERMINAL", "CALENDAR", "PERFORMANCE", "ANALYZERS", "JOURNAL", "LAST 12 MONTHS"], index=0) st.divider()

--- 5. WELCOME ---

st.markdown('<div class="welcome-text">WHAT'S UP SHADOW, LET'S SEE WHAT HAPPENED TODAY.</div>', unsafe_allow_html=True)

--- 6. MAIN CONTENT ---

st.markdown('<div class="content-fade">', unsafe_allow_html=True)

if choice == "TERMINAL": c1, c2 = st.columns([1, 2.3]) with c1: with st.form("entry_form"): st.markdown("### 📥 LOG ENTRY") d_in = st.date_input("Date", datetime.now()) asset = st.text_input("Pair", "NAS100").upper() res = st.selectbox("Outcome", ["WIN", "LOSS", "BE"]) p_val = st.number_input("P&L ($)", value=0.0) r_val = st.number_input("RR Ratio", value=0.0) setup = st.text_input("Setup").upper() mind = st.selectbox("Mindset", ["Focused", "Impulsive", "Revenge", "Bored"]) img_file = st.file_uploader("Screenshot", type=['png','jpg','jpeg']) if st.form_submit_button("LOCK TRADE"): img_data = base64.b64encode(img_file.read()).decode() if img_file else None c.execute("INSERT INTO trades (date,pair,outcome,pnl,rr,balance,mindset,setup,image) VALUES (?,?,?,?,?,?,?,?,?)", (str(d_in), asset, res, p_val, r_val, current_balance, mind, setup, img_data)) conn.commit() st.experimental_rerun() with c2: if not df.empty: fig = go.Figure(go.Scatter(x=list(range(len(df))), y=df['equity_curve'], mode='lines+markers', line=dict(color='#00f5ff', width=3, shape='spline'), fill='tonexty', fillcolor='rgba(0,245,255,0.05)')) fig.update_layout(template="plotly_dark", height=480, title="ACCOUNT GROWTH CURVE", transition={'duration':500}) st.plotly_chart(fig, use_container_width=True)

elif choice == "CALENDAR": if not df.empty: today = datetime.now() cal = calendar.monthcalendar(today.year, today.month) cols = st.columns(7) for i, d_name in enumerate(["MON","TUE","WED","THU","FRI","SAT","SUN"]): cols[i].markdown(f"<p style='text-align:center; color:#00f5ff; font-family:Orbitron; font-size:0.8rem;'>{d_name}</p>", unsafe_allow_html=True) for week in cal: cols = st.columns(7) for i, day in enumerate(week): if day==0: cols[i].markdown('<div style="opacity:0.1"> </div>', unsafe_allow_html=True) else: d_str = datetime(today.year,today.month,day).strftime('%Y-%m-%d') day_df = df[df['date']==d_str] p_sum = day_df['pnl'].sum() if not day_df.empty else 0 style = 'journal-win' if p_sum>0 else 'journal-loss' if p_sum<0 else 'journal-be' if not day_df.empty else '' cols[i].markdown(f'<div class="{style}" style="padding:5px; border-radius:8px;"><div style="text-align:center; font-size:0.8rem; color:#8b949e">{day}</div><div style="text-align:center; font-weight:bold; font-size:0.9rem;">${p_sum:,.0f}</div></div>', unsafe_allow_html=True)

elif choice == "PERFORMANCE": if not df.empty: wins = df[df['pnl']>0] losses = df[df['pnl']<0] wr = len(wins)/len(df)*100 if len(df)>0 else 0 pf = wins['pnl'].sum()/abs(losses['pnl'].sum()) if not losses.empty else 0

st.markdown('#### ⚡ PRIMARY METRICS')
    g1,g2,g3,g4 = st.columns(4)
    metrics = [f'{wr:.1f}%', f'{pf:.2f}', f'{df['rr'].mean():.2f}', f'${df['pnl'].sum():,.0f}']
    labels = ["Win Rate","Profit Factor","Avg RR","Net P&L"]
    for col,val,label in zip([g1,g2,g3,g4], metrics, labels):
        col.markdown(f'<div class="perf-card"><div class="perf-val">{val}</div><div class="perf-label">{label}</div></div>', unsafe_allow_html=True)
    
    st.markdown('#### 🛡️ RISK & STREAKS', unsafe_allow_html=True)
    g5,g6,g7,g8 = st.columns(4)
    outcomes = [1 if x>0 else -1 if x<0 else 0 for x in df['pnl']]
    mw,ml,cw,cl = 0,0,0,0
    for r in outcomes:
        if r==1: cw+=1; cl=0; mw=max(mw,cw)
        elif r==-1: cl+=1; cw=0; ml=max(ml,cl)
    streaks = [f'${df['pnl'].max():,.0f}', f'${df['pnl'].min():,.0f}', f'{mw} 🔥', f'{ml} 💀']
    labels2 = ["Best Day","Worst Day","Max Win Streak","Max Loss Streak"]
    for col,val,label in zip([g5,g6,g7,g8], streaks, labels2):
        col.markdown(f'<div class="perf-card"><div class="perf-val">{val}</div><div class="perf-label">{label}</div></div>', unsafe_allow_html=True)

elif choice == "JOURNAL": if not df.empty: st.markdown('### 📜 TRADE ARCHIVE') for _,row in df.sort_values('id',ascending=False).iterrows(): j_class = 'journal-win' if row['pnl']>0 else 'journal-loss' if row['pnl']<0 else 'journal-be' with st.container(): st.markdown(f'<div class="{j_class}" style="padding:10px; border-radius:8px; margin-bottom:10px;">', unsafe_allow_html=True) with st.expander(f'● {row['date']} | {row['pair']} | P&L: ${row['pnl']:,.2f} | Setup: {row['setup']}'): tx,im = st.columns([1,2]) with tx: st.write(f'Outcome: {row['outcome']}') st.write(f'RR: {row['rr']} | Mindset: {row['mindset']}') with im: if row['image']: st.image(base64.b64decode(row['image']), use_container_width=True) st.markdown('</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
