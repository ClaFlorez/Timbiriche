import streamlit as st
import numpy as np
import math
import wave
import struct
import io
import base64
import random
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="Timbiriche ✨ Tutu vs Abuelita", layout="wide")
st_autorefresh(interval=2000, key="datarefresh")

FILAS = 4
COLS  = 4
JUGADORES  = ["Tutu", "Abuelita"]
EMOJIS     = {"Tutu": "🔵", "Abuelita": "🔴"}
COLOR_TUTU     = "#6A4CFF"
COLOR_ABUELITA = "#E05B20"

# ── CSS ──────────────────────────────────────
st.markdown(f"""
<style>
.stApp {{ background: radial-gradient(ellipse at 20% 0%, #0d1b3e 0%, #020814 55%, #01040d 100%); }}
div[data-testid="stHorizontalBlock"] {{
    display:flex !important; flex-direction:row !important;
    flex-wrap:nowrap !important; gap:0px !important;
    align-items:center; width:100% !important;
}}
[data-testid="column"] {{
    min-width:0px !important; flex-basis:auto !important;
    flex-grow:1 !important; padding:0px 1px !important;
}}
.punto {{ display:flex; align-items:center; justify-content:center;
    height:45px; width:100%; font-size:16px; color:white; font-weight:bold; }}
.linea-h-tutu::before {{
    content:""; display:block; width:100%;
    border-top:8px solid {COLOR_TUTU}; border-radius:10px; box-shadow:0 0 14px {COLOR_TUTU}; }}
.linea-h-abuelita::before {{
    content:""; display:block; width:100%;
    border-top:8px solid {COLOR_ABUELITA}; border-radius:10px; box-shadow:0 0 14px {COLOR_ABUELITA}; }}
.linea-v-tutu, .linea-v-abuelita {{ display:flex; justify-content:center; height:45px; width:100%; }}
.linea-v-tutu::before {{
    content:""; display:block; height:100%;
    border-left:8px solid {COLOR_TUTU}; border-radius:10px; box-shadow:0 0 14px {COLOR_TUTU}; }}
.linea-v-abuelita::before {{
    content:""; display:block; height:100%;
    border-left:8px solid {COLOR_ABUELITA}; border-radius:10px; box-shadow:0 0 14px {COLOR_ABUELITA}; }}
.cuadro-tutu {{
    background:linear-gradient(135deg,{COLOR_TUTU},{COLOR_TUTU}bb);
    height:45px; width:100%; border-radius:6px;
    display:flex; align-items:center; justify-content:center;
    color:white; font-weight:900; font-size:18px; animation:pop .25s ease; }}
.cuadro-abuelita {{
    background:linear-gradient(135deg,{COLOR_ABUELITA},{COLOR_ABUELITA}bb);
    height:45px; width:100%; border-radius:6px;
    display:flex; align-items:center; justify-content:center;
    color:white; font-weight:900; font-size:18px; animation:pop .25s ease; }}
@keyframes pop {{
    0%   {{ transform:scale(0.6); opacity:0; }}
    70%  {{ transform:scale(1.1); }}
    100% {{ transform:scale(1);   opacity:1; }}
}}
button[kind="secondary"] {{
    width:100% !important; height:45px !important;
    background:transparent !important;
    border:1px solid rgba(255,255,255,0.05) !important;
    color:transparent !important; margin:0 !important; transition:background .12s !important; }}
button[kind="secondary"]:hover:not(:disabled) {{
    background:rgba(255,255,255,0.12) !important;
    border:1px solid rgba(255,255,255,0.3) !important; }}
.scorecard {{
    background:rgba(255,255,255,0.05); border:1px solid rgba(255,255,255,0.12);
    border-radius:14px; padding:12px 16px; margin-bottom:8px; }}
.sc-label {{ font-size:11px; color:rgba(255,255,255,0.45); text-transform:uppercase; letter-spacing:1px; }}
.sc-pts   {{ font-size:36px; font-weight:900; line-height:1.1; }}
.turno-badge {{
    display:inline-block; padding:5px 14px; border-radius:20px;
    font-size:13px; font-weight:700; margin-bottom:8px; }}
h1 {{ color:white !important; text-align:center; font-size:1.8rem !important; margin-bottom:2px !important; }}
.subtitulo {{ text-align:center; color:rgba(255,255,255,0.4); font-size:12px; margin-bottom:14px; }}
.corona-final  {{ font-size:90px; text-align:center; margin:0; line-height:1.1; }}
.texto-ganador {{
    font-size:2.8rem; font-weight:900; text-align:center; color:#FFD700;
    text-shadow:0 0 30px #FFD700; animation:brillar 1s infinite alternate; }}
.marcador-final {{ text-align:center; font-size:1.3rem; font-weight:700; color:rgba(255,255,255,0.8); margin-top:8px; }}
@keyframes brillar {{
    from {{ opacity:.75; text-shadow:0 0 10px #FFD70066; }}
    to   {{ opacity:1;   text-shadow:0 0 35px #FFD700; }}
}}
.fx-layer {{ position:fixed; inset:0; pointer-events:none; z-index:9999; overflow:hidden; }}
.star-fx  {{ position:absolute; top:50%; left:50%; font-size:28px;
    animation:volar 2.8s ease-out forwards; opacity:0; }}
@keyframes volar {{
    0%   {{ transform:translate(-50%,-50%) scale(0) rotate(0deg); opacity:1; }}
    60%  {{ opacity:1; }}
    100% {{ transform:translate(calc(-50% + var(--tw)), calc(-50% + var(--th))) scale(1.4) rotate(var(--tr)); opacity:0; }}
}}
</style>
""", unsafe_allow_html=True)

# ── AUDIO ─────────────────────────────────────
@st.cache_data
def _gen_audio(frec, dur=0.22):
    buf = io.BytesIO()
    rate = 22050
    with wave.open(buf, "wb") as f:
        f.setnchannels(1); f.setsampwidth(2); f.setframerate(rate)
        for i in range(int(rate * dur)):
            t   = i / rate
            env = 1 - (i / (rate * dur)) ** 1.5
            val = int(32767 * 0.32 * env * math.sin(2 * math.pi * frec * t))
            f.writeframes(struct.pack("<h", val))
    return base64.b64encode(buf.getvalue()).decode()

SND_LINEA    = _gen_audio(660)
SND_CUADRO   = _gen_audio(1046)
SND_VICTORIA = _gen_audio(784)

def play(b64):
    st.markdown(f'<audio autoplay style="display:none;"><source src="data:audio/wav;base64,{b64}"></audio>', unsafe_allow_html=True)

# ── ESTADO COMPARTIDO ─────────────────────────
@st.cache_resource
def get_juego():
    return {
        "puntos":    {"Tutu": 0, "Abuelita": 0},
        "turno":     "Tutu",
        "lineas_h":  np.zeros((FILAS + 1, COLS), dtype=bool),
        "lineas_v":  np.zeros((FILAS, COLS + 1), dtype=bool),
        "duenos_h":  np.full((FILAS + 1, COLS), "", dtype=object),
        "duenos_v":  np.full((FILAS, COLS + 1), "", dtype=object),
        "cuadros":   {},
        "historial": [],
    }

juego = get_juego()

# ── TRACKING LOCAL ────────────────────────────
if "p_locales" not in st.session_state: st.session_state.p_locales = 0
if "fin_visto" not in st.session_state: st.session_state.fin_visto = False

total = sum(juego["puntos"].values())
fin   = len(juego["cuadros"]) == FILAS * COLS

if total > st.session_state.p_locales and not fin:
    st.balloons()
    play(SND_CUADRO)
    st.session_state.p_locales = total

if total == 0 and len(juego["cuadros"]) == 0:
    st.session_state.p_locales = 0
    st.session_state.fin_visto = False

# ── LÓGICA ────────────────────────────────────
def registrar(tipo, r, c):
    h, v    = juego["lineas_h"], juego["lineas_v"]
    jugador = juego["turno"]
    if tipo == "h":
        if h[r, c]: return 0
        h[r, c] = True; juego["duenos_h"][r, c] = jugador
    else:
        if v[r, c]: return 0
        v[r, c] = True; juego["duenos_v"][r, c] = jugador
    formados = 0
    for row in range(FILAS):
        for col in range(COLS):
            if (row, col) not in juego["cuadros"]:
                if h[row,col] and h[row+1,col] and v[row,col] and v[row,col+1]:
                    juego["cuadros"][(row,col)] = jugador
                    juego["puntos"][jugador]   += 1
                    juego["historial"].append(f"{EMOJIS[jugador]} **{jugador}** completó ({row+1},{col+1})")
                    formados += 1
    if formados == 0:
        juego["turno"] = JUGADORES[1 - JUGADORES.index(jugador)]
    else:
        juego["historial"].append(f"  ↳ +{formados} cuadro{'s' if formados>1 else ''}, sigue {EMOJIS[jugador]}")
    return formados

def reiniciar():
    juego["puntos"]   = {"Tutu": 0, "Abuelita": 0}
    juego["turno"]    = "Tutu"
    juego["lineas_h"].fill(False); juego["lineas_v"].fill(False)
    juego["duenos_h"].fill("");    juego["duenos_v"].fill("")
    juego["cuadros"].clear();      juego["historial"].clear()

# ── SIDEBAR ───────────────────────────────────
with st.sidebar:
    st.markdown("## ⚙️ Jugador")
    usuario = st.radio("¿Quién eres tú?", JUGADORES, horizontal=True)
    st.divider()

    ct = COLOR_TUTU if juego["turno"] == "Tutu" else COLOR_ABUELITA
    st.markdown(
        f"<div class='turno-badge' style='background:{ct}33;border:1.5px solid {ct};color:white;'>"
        f"{EMOJIS[juego['turno']]} Turno de <strong>{juego['turno']}</strong></div>",
        unsafe_allow_html=True)

    for j in JUGADORES:
        cj = COLOR_TUTU if j == "Tutu" else COLOR_ABUELITA
        st.markdown(
            f"<div class='scorecard' style='border-color:{cj}66;'>"
            f"<div class='sc-label'>{EMOJIS[j]} {j}</div>"
            f"<div class='sc-pts' style='color:{cj};'>{juego['puntos'][j]}</div>"
            f"<div class='sc-label'>cuadros</div></div>",
            unsafe_allow_html=True)

    st.divider()
    total_lineas = (FILAS+1)*COLS + FILAS*(COLS+1)
    marcadas = int(juego["lineas_h"].sum()) + int(juego["lineas_v"].sum())
    st.markdown("**Progreso**")
    st.progress(marcadas / total_lineas)
    st.caption(f"{marcadas}/{total_lineas} líneas · {len(juego['cuadros'])}/{FILAS*COLS} cuadros")
    st.divider()

    if st.button("🔄 Reiniciar partida", use_container_width=True, type="primary"):
        reiniciar()
        st.session_state.p_locales = 0
        st.session_state.fin_visto = False
        st.rerun()

    if juego["historial"]:
        with st.expander("📜 Historial"):
            for line in reversed(juego["historial"][-20:]):
                st.markdown(line)

# ── ÁREA PRINCIPAL ────────────────────────────
es_mi_turno = (usuario == juego["turno"]) and not fin

st.markdown("<h1>🕹️ Timbiriche</h1>", unsafe_allow_html=True)
st.markdown(f"<div class='subtitulo'>{EMOJIS['Tutu']} Tutu &nbsp;vs&nbsp; Abuelita {EMOJIS['Abuelita']}</div>", unsafe_allow_html=True)

if not fin:
    if es_mi_turno:
        st.success(f"✅ ¡Es tu turno, {usuario}!", icon="🎯")
    else:
        st.info(f"⏳ Esperando a **{juego['turno']}**...", icon="👀")

# ── TABLERO ───────────────────────────────────
col_w = [1, 3, 1, 3, 1, 3, 1, 3, 1]
h  = juego["lineas_h"]; v  = juego["lineas_v"]
dh = juego["duenos_h"]; dv = juego["duenos_v"]

for r in range(FILAS + 1):
    cols = st.columns(col_w)
    for c in range(COLS):
        cols[c*2].markdown("<div class='punto'>●</div>", unsafe_allow_html=True)
        if h[r, c]:
            color = "tutu" if dh[r,c] == "Tutu" else "abuelita"
            cols[c*2+1].markdown(f"<div class='linea-h-{color}'></div>", unsafe_allow_html=True)
        else:
            if cols[c*2+1].button(" ", key=f"h{r}{c}", disabled=not es_mi_turno):
                n = registrar("h", r, c)
                play(SND_CUADRO if n > 0 else SND_LINEA)
                st.rerun()
    cols[8].markdown("<div class='punto'>●</div>", unsafe_allow_html=True)

    if r < FILAS:
        cols_v = st.columns(col_w)
        for c in range(COLS + 1):
            if v[r, c]:
                color = "tutu" if dv[r,c] == "Tutu" else "abuelita"
                cols_v[c*2].markdown(f"<div class='linea-v-{color}'></div>", unsafe_allow_html=True)
            else:
                if cols_v[c*2].button(" ", key=f"v{r}{c}", disabled=not es_mi_turno):
                    n = registrar("v", r, c)
                    play(SND_CUADRO if n > 0 else SND_LINEA)
                    st.rerun()
            if c < COLS:
                if (r, c) in juego["cuadros"]:
                    own   = juego["cuadros"][(r, c)]
                    color = "tutu" if own == "Tutu" else "abuelita"
                    cols_v[c*2+1].markdown(f"<div class='cuadro-{color}'>{own[0]}</div>", unsafe_allow_html=True)
                else:
                    cols_v[c*2+1].markdown("<div style='height:45px;'></div>", unsafe_allow_html=True)

# ── PANTALLA FINAL ────────────────────────────
if fin:
    pt, pa = juego["puntos"]["Tutu"], juego["puntos"]["Abuelita"]
    if   pt > pa: ganador, cg = "Tutu",     COLOR_TUTU
    elif pa > pt: ganador, cg = "Abuelita", COLOR_ABUELITA
    else:         ganador, cg = "¡Empate!", "#FFD700"

    if not st.session_state.fin_visto:
        play(SND_VICTORIA)
        st.balloons()
        fx = '<div class="fx-layer">'
        for _ in range(80):
            tw    = random.randint(-800, 800)
            th    = random.randint(-600, 600)
            tr    = random.randint(0, 720)
            delay = round(random.uniform(0, 0.8), 2)
            emoji = random.choice(["⭐", "🌟", "✨", "💫"])
            fx += f'<div class="star-fx" style="--tw:{tw}px;--th:{th}px;--tr:{tr}deg;animation-delay:{delay}s;">{emoji}</div>'
        fx += '</div>'
        st.markdown(fx, unsafe_allow_html=True)
        st.session_state.fin_visto = True

    st.markdown(f"""
    <div style="text-align:center; padding:28px 20px 20px;
        background:linear-gradient(135deg,{cg}22,{cg}08);
        border:2px solid {cg}88; border-radius:20px; margin-top:16px;">
      <div class="corona-final">👑</div>
      <div class="texto-ganador">¡{ganador} ganó!</div>
      <div class="marcador-final">
        {EMOJIS['Tutu']} Tutu <span style="font-size:1.8rem;color:white;">{pt}</span>
        &nbsp;–&nbsp;
        <span style="font-size:1.8rem;color:white;">{pa}</span> Abuelita {EMOJIS['Abuelita']}
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🔄 Nueva partida", type="primary", use_container_width=True):
        reiniciar()
        st.session_state.p_locales = 0
        st.session_state.fin_visto = False
        st.rerun()
