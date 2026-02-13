import streamlit as st
import pandas as pd

# 1. Configuration
st.set_page_config(page_title="Basket Pro Tracker", layout="wide")

# 2. CSS - Focus sur la séparation et la clarté
st.markdown("""
    <style>
    /* Séparation nette entre les joueurs sur le terrain */
    [data-testid="column"] {
        background-color: #ffffff;
        padding: 15px !important;
        border: 3px solid #f0f2f6; /* Bordure plus épaisse pour séparer */
        border-radius: 15px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }
    /* Style des boutons de réussite (Vert) et échec (Rouge) */
    .stButton>button[key^="m_"] { background-color: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
    .stButton>button[key^="a_"] { background-color: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
    
    .player-title {
        text-align: center;
        color: #1f3b4d;
        font-size: 1.2em;
        margin-bottom: 10px;
        border-bottom: 2px solid #1f3b4d;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. Données
PLAYERS_DATA = [
    {"num": 4, "name": "Timéo"}, {"num": 5, "name": "Yehya"}, 
    {"num": 6, "name": "Yannis"}, {"num": 7, "name": "Ronice"}, 
    {"num": 8, "name": "Keran"}, {"num": 9, "name": "M'Baye"}, 
    {"num": 10, "name": "Jobin"}, {"num": 11, "name": "Klérance"}, 
    {"num": 12, "name": "Franck"}, {"num": 13, "name": "Johan"}, 
    {"num": 14, "name": "Lucas"}, {"num": 15, "name": "Mehdi"}, 
    {"num": 16, "name": "Antoine"}
]

if 'stats' not in st.session_state:
    st.session_state.stats = {p["name"]: {
        "2pts_M": 0, "2pts_A": 0, "3pts_M": 0, "3pts_A": 0, "LF_M": 0, "LF_A": 0,
        "REB_OFF": 0, "REB_DEF": 0, "AST": 0, "TO": 0, "FTS": 0
    } for p in PLAYERS_DATA}

if 'on_court' not in st.session_state:
    st.session_state.on_court = []

# 4. Fonctions de mise à jour
def add_stat(player, key, is_made=False, is_miss=False):
    if is_made:
        st.session_state.stats[player][key + "_M"] += 1
        st.session_state.stats[player][key + "_A"] += 1
    elif is_miss:
        st.session_state.stats[player][key + "_A"] += 1
    else:
        st.session_state.stats[player][key] += 1

def toggle_court(player):
    if player in st.session_state.on_court:
        st.session_state.on_court.remove(player)
    else:
        if len(st.session_state.on_court) < 5:
            st.session_state.on_court.append(player)

# --- SCORE ---
total_score = sum((s["2pts_M"] * 2) + (s["3pts_M"] * 3) + s["LF_M"] for s in st.session_state.stats.values())
st.title("🏀 Basket Pro Tracker")
st.subheader(f"SCORE ÉQUIPE : {total_score}")

# --- SECTION TERRAIN ---
cols = st.columns(5)
for i in range(5):
    with cols[i]:
        if i < len(st.session_state.on_court):
            p_name = st.session_state.on_court[i]
            p_num = next(p["num"] for p in PLAYERS_DATA if p["name"] == p_name)
            s = st.session_state.stats[p_name]
            
            st.markdown(f"<div class='player-title'><b>#{p_num} {p_name}</b></div>", unsafe_allow_html=True)
            
            for shot in ["2pts", "3pts", "LF"]:
                c1, c2 = st.columns([2, 1])
                c1.button(f"✅ {shot}", key=f"m_{p_name}_{shot}", on_click=add_stat, args=(p_name, shot, True))
                c2.button(f"❌", key=f"a_{p_name}_{shot}", on_click=add_stat, args=(p_name, shot, False, True))
            
            st.write("**Rebonds**")
            r1, r2 = st.columns(2)
            r1.button(f"OFF:{s['REB_OFF']}", key=f"o_{p_name}", on_click=add_stat, args=(p_name, "REB_OFF"))
            r2.button(f"DEF:{s['REB_DEF']}", key=f"d_{p_name}", on_click=add_stat, args=(p_name, "REB_DEF"))
            
            st.write("**Jeu**")
            j1, j2, j3 = st.columns(3)
            j1.button("AS", key=f"as_{p_name}", on_click=add_stat, args=(p_name, "AST"), help="Assists")
            j2.button("BP", key=f"bp_{p_name}", on_click=add_stat, args=(p_name, "TO"), help="Balles Perdues")
            j3.button("F", key=f"f_{p_name}", on_click=add_stat, args=(p_name, "FTS"), help="Fautes")
            
            st.button("🔄 SORTIR", key=f"out_{p_name}", on_click=toggle_court, args=(p_name,), type="primary", use_container_width=True)
        else:
            st.info("Emplacement vide")

# --- SECTION BANC ---
st.divider()
st.subheader("🪑 Banc (Entrée)")
bench = [p for p in PLAYERS_DATA if p["name"] not in st.session_state.on_court]
b_cols = st.columns(7)
for idx, p in enumerate(bench):
    with b_cols[idx % 7]:
        st.button(f"{p['num']} {p['name']}", key=f"bench_{p['name']}", on_click=toggle_court, args=(p['name'],), use_container_width=True)

# --- BOX SCORE DÉTAILLÉ ---
st.divider()
st.subheader("📊 Box Score Complet")

final_data = []
for p in PLAYERS_DATA:
    name = p["name"]
    s = st.session_state.stats[name]
    
    pts = (s["2pts_M"] * 2) + (s["3pts_M"] * 3) + s["LF_M"]
    fg_m = s["2pts_M"] + s["3pts_M"]
    fg_a = s["2pts_A"] + s["3pts_A"]
    fg_pct = (fg_m / fg_a * 100) if fg_a > 0 else 0
    
    final_data.append({
        "N°": p["num"],
        "Joueur": name,
        "Pts": pts,
        "FG (M/A)": f"{fg_m}/{fg_a}",
        "FG%": f"{fg_pct:.1f}%",
        "2P (M/A)": f"{s['2pts_M']}/{s['2pts_A']}",
        "3P (M/A)": f"{s['3pts_M']}/{s['3pts_A']}",
        "LF (M/A)": f"{s['LF_M']}/{s['LF_A']}",
        "REB OFF": s["REB_OFF"],
        "REB DEF": s["REB_DEF"],
        "REB TOT": s["REB_OFF"] + s["REB_DEF"],
        "AST": s["AST"],
        "TO": s["TO"],
        "FTS": s["FTS"]
    })

st.dataframe(pd.DataFrame(final_data), use_container_width=True)

# Sidebar
if st.sidebar.button("🗑️ Réinitialiser le match"):
    st.session_state.clear()
    st.rerun()
