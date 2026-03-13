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

# ────────────────────────────────────────────
# CONSTANTES
# ────────────────────────────────────────────
FILAS = 4
COLS  = 4
JUGADORES = ["Tutu", "Abuelita"]
EMOJIS    = {"Tutu": "🔵", "Abuelita": "🔴"}
COLOR_TUTU     = "#6A4CFF"
COLOR_ABUELITA = "#E05B20"

# ────────────────────────────────────────────
# CSS
# ────────────────────────────────────────────
st.markdown(f"""
<style>
.stApp {{ background: radial-gradient(ellipse at 20% 0%, #0d1b3e 0%, #020814 55%, #01040d 100%); }}

div[data-testid="stHorizontalBlock"] {{ gap:0px !important; align-items:center; }}
[data-testid="column"] {{ min-width:0px !important; flex-basis:auto !important; padding:0px 1px !important; }}

/* ── Puntos ── */
.punto {{ display:flex; align-items:center; justify-content:center;
    height:60px; width:100%; font-size:20px; color:white; font-weight:bold; }}

/* ── Líneas horizontales ── */
.linea-h-tutu, .linea-h-abuelita {{
    height:60px; display:flex; align-items:center; justify-content:center;
}}
.linea-h-tutu::before {{
    content:""; display:block; width:100%;
    border-top:8px solid {COLOR_TUTU}; border-radius:10px;
    box-shadow:0 0 12px {COLOR_TUTU}99;
}}
.linea-h-abuelita::before {{
    content:""; display:block; width:100%;
    border-top:8px solid {COLOR_ABUELITA}; border-radius:10px;
    box-shadow:0 0 12px {COLOR_ABUELITA}99;
}}

/* ── Líneas verticales ── */
.linea-v-tutu, .linea-v-abuelita {{
    display:flex; justify-content:center; height:60px; width:100%;
}}
.linea-v-tutu::before {{
    content:""; display:block; height:100%;
    border-left:8px solid {COLOR_TUTU}; border-radius:10px; margin:auto;
    box-shadow:0 0 12px {COLOR_TUTU}99;
}}
.linea-v-abuelita::before {{
    content:""; display:block; height:100%;
    border-left:8px solid {COLOR_ABUELITA}; border-radius:10px; margin:auto;
    box-shadow:0 0 12px {COLOR_ABUELITA}99;
}}

/* ── Cuadros conquistados ── */
.cuadro-tutu {{
    background:linear-gradient(135deg,{COLOR_TUTU},{COLOR_TUTU}99);
    height:60px; width:100%; border-radius:8px;
    display:flex; align-items:center; justify-content:center;
    color:white; font-weight:900; font-size:22px; animation:pop .25s ease;
}}
.cuadro-abuelita {{
    background:linear-gradient(135deg,{COLOR_ABUELITA},{COLOR_ABUELITA}99);
    height:60px; width:100%; border-radius:8px;
    display:flex; align-items:center; justify-content:center;
    color:white; font-weight:900; font-size:22px; animation:pop .25s ease;
}}
@keyframes pop {{
    0%   {{ transform:scale(0.6); opacity:0; }}
    70%  {{ transform:scale(1.1); }}
    100% {{ transform:scale(1);   opacity:1; }}
}}

/* ── Botones del tablero ── */
button[kind="secondary"] {{
    width:100% !important; height:60px !important;
    background:transparent !important;
    border:1px solid rgba(255,255,255,0.08) !important;
    color:transparent !important; margin:0 !important;
    transition:background .15s !important;
}}
button[kind="secondary"]:hover:not(:disabled) {{
    background:rgba(255,255,255,0.15) !important;
    border:1px solid rgba(255,255,255,0.35) !important;
}}

/* ── Sidebar scorecards ── */
.scorecard {{
    background:rgba(255,255,255,0.05);
    border:1px solid rgba(255,255,255,0.12);
    border-radius:14px; padding:14px 18px; margin-bottom:10px;
}}
.sc-label {{ font-size:11px; color:rgba(255,255,255,0.45);
    text-transform:uppercase; letter-spacing:1px; }}
.sc-pts   {{ font-size:38px; font-weight:900; line-height:1.1; }}

/* ── Turno badge ── */
.turno-badge {{
    display:inline-block; padding:6px 16px; border-radius:20px;
    font-size:14px; font-weight:700; margin-bottom:8px;
}}

/* ── Título ── */
h1 {{ color:white !important; text-align:center;
    font-size:2rem !important; letter-spacing:-.5px; margin-bottom:4px !important; }}
.subtitulo {{ text-align:center; color:rgba(255,255,255,0.4);
    font-size:13px; margin-bottom:20px; }}

/* ── Pantalla final ── */
.corona-gigante {{ font-size:90px; text-align:center; margin:0; line-height:1.1; }}
.texto-ganador  {{
    font-size:3rem; font-weight:900; text-align:center;
    color:#FFD700; text-shadow:0 0 30px #FFD700;
    animation:brillar 1s infinite alternate;
}}
.marcador-final {{
    text-align:center; font-size:1.4rem; font-weight:700;
    color:rgba(255,255,255,0.8); margin-top:10px;
}}
@keyframes brillar {{
    from {{ opacity:.75; text-shadow:0 0 10px #FFD70066; }}
    to   {{ opacity:1;   text-shadow:0 0 35px #FFD700;   }}
}}

/* ── Estrellas CSS explosión desde el centro ── */
.fx-layer {{ position:fixed; inset:0; pointer-events:none; z-index:9999; overflow:hidden; }}
.fx-star  {{
    position:absolute; top:50%; left:50%; font-size:28px;
    animation:volarEstrella 2.8s ease-out forwards; opacity:0;
}}
@keyframes volarEstrella {{
    0%   {{ transform:translate(-50%,-50%) scale(0) rotate(0deg); opacity:1; }}
    60%  {{ opacity:1; }}
    100% {{ transform:translate(calc(-50% + var(--tw)), calc(-50% + var(--th))) scale(1.2) rotate(var(--tr)); opacity:0; }}
}}
</style>
""", unsafe_allow_html=True)

# ────────────────────────────────────────────
# SINCRONIZACIÓN
# ────────────────────────────────────────────
st_autorefresh(interval=2000, key="datarefresh")

# ────────────────────────────────────────────
# AUDIO
# ────────────────────────────────────────────
@st.cache_data
def _gen_audio(frec: float, dur: float = 0.22) -> str:
    buf = io.BytesIO()
    rate = 22050
    with wave.open(buf, "wb") as f:
        f.setnchannels(1); f.setsampwidth(2); f.setframerate(rate)
        for i in range(int(rate * dur)):
            t = i / rate
            env = 1 - (i / (rate * dur)) ** 1.5
            val = int(32767 * 0.32 * env * math.sin(2 * math.pi * frec * t))
            f.writeframes(struct.pack("<h", val))
    return base64.b64encode(buf.getvalue()).decode()

SND_LINEA    = _gen_audio(660)
SND_CUADRO   = _gen_audio(1046)
SND_VICTORIA = _gen_audio(784)

def play(b64: str):
    st.markdown(
        f'<audio autoplay style="display:none;"><source src="data:audio/wav;base64,{b64}"></audio>',
        unsafe_allow_html=True)

# ────────────────────────────────────────────
# ESTADO COMPARTIDO
# ────────────────────────────────────────────
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

# ────────────────────────────────────────────
# TRACKING LOCAL DE EFECTOS
# ────────────────────────────────────────────
if "pts_vistos" not in st.session_state:
    st.session_state.pts_vistos = 0
if "fin_festejado" not in st.session_state:
    st.session_state.fin_festejado = False

total_pts = sum(juego["puntos"].values())
fin       = len(juego["cuadros"]) == FILAS * COLS

# 🎈 Globos nativos de Streamlit al anotar — siempre funcionan
if total_pts > st.session_state.pts_vistos and not fin:
    st.balloons()
    play(SND_CUADRO)
    st.session_state.pts_vistos = total_pts

# Reset al reiniciar
if total_pts == 0 and len(juego["cuadros"]) == 0:
    st.session_state.pts_vistos    = 0
    st.session_state.fin_festejado = False

# ────────────────────────────────────────────
# LÓGICA DEL JUEGO
# ────────────────────────────────────────────
def registrar(tipo: str, r: int, c: int) -> int:
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
                    juego["historial"].append(
                        f"{EMOJIS[jugador]} **{jugador}** completó ({row+1},{col+1})")
                    formados += 1
    if formados == 0:
        juego["turno"] = JUGADORES[1 - JUGADORES.index(jugador)]
    else:
        juego["historial"].append(
            f"  ↳ +{formados} cuadro{'s' if formados>1 else ''}, sigue {EMOJIS[jugador]}")
    return formados

def reiniciar():
    juego["puntos"]   = {"Tutu": 0, "Abuelita": 0}
    juego["turno"]    = "Tutu"
    juego["lineas_h"].fill(False); juego["lineas_v"].fill(False)
    juego["duenos_h"].fill("");    juego["duenos_v"].fill("")
    juego["cuadros"].clear();      juego["historial"].clear()

# ────────────────────────────────────────────
# SIDEBAR
# ────────────────────────────────────────────
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
        st.markdown(f"""
        <div class="scorecard" style="border-color:{cj}66;">
          <div class="sc-label">{EMOJIS[j]} {j}</div>
          <div class="sc-pts" style="color:{cj};">{juego['puntos'][j]}</div>
          <div class="sc-label">cuadros</div>
        </div>""", unsafe_allow_html=True)

    st.divider()
    total_lineas = (FILAS+1)*COLS + FILAS*(COLS+1)
    marcadas = int(juego["lineas_h"].sum()) + int(juego["lineas_v"].sum())
    st.markdown("**Progreso**")
    st.progress(marcadas / total_lineas)
    st.caption(f"{marcadas}/{total_lineas} líneas · {len(juego['cuadros'])}/{FILAS*COLS} cuadros")
    st.divider()

    if st.button("🔄 Reiniciar partida", use_container_width=True, type="primary"):
        reiniciar()
        st.session_state.pts_vistos    = 0
        st.session_state.fin_festejado = False
        st.rerun()

    if juego["historial"]:
        with st.expander("📜 Historial"):
            for line in reversed(juego["historial"][-20:]):
                st.markdown(line)

# ────────────────────────────────────────────
# ÁREA PRINCIPAL
# ────────────────────────────────────────────
es_mi_turno = (usuario == juego["turno"]) and not fin

st.markdown("<h1>🕹️ Timbiriche</h1>", unsafe_allow_html=True)
st.markdown(
    f"<div class='subtitulo'>{EMOJIS['Tutu']} Tutu &nbsp;vs&nbsp; Abuelita {EMOJIS['Abuelita']}</div>",
    unsafe_allow_html=True)

if not fin:
    if es_mi_turno:
        st.success(f"✅ ¡Es tu turno, {usuario}! Haz click en una línea libre.", icon="🎯")
    else:
        st.info(f"⏳ Esperando a que juegue **{juego['turno']}**...", icon="👀")

# ────────────────────────────────────────────
# TABLERO
# ────────────────────────────────────────────
col_widths = []
for _ in range(COLS):
    col_widths += [0.6, 3]
col_widths.append(0.6)

h  = juego["lineas_h"]; v  = juego["lineas_v"]
dh = juego["duenos_h"]; dv = juego["duenos_v"]

for r in range(FILAS + 1):
    cols = st.columns(col_widths)
    for c in range(COLS):
        cols[c*2].markdown("<div class='punto'>●</div>", unsafe_allow_html=True)
        if h[r, c]:
            clase = "linea-h-tutu" if dh[r,c]=="Tutu" else "linea-h-abuelita"
            cols[c*2+1].markdown(f"<div class='{clase}'></div>", unsafe_allow_html=True)
        else:
            if cols[c*2+1].button(" ", key=f"h{r}{c}", disabled=not es_mi_turno):
                n = registrar("h", r, c)
                play(SND_CUADRO if n > 0 else SND_LINEA)
                st.rerun()
    cols[COLS*2].markdown("<div class='punto'>●</div>", unsafe_allow_html=True)

    if r < FILAS:
        cols_v = st.columns(col_widths)
        for c in range(COLS + 1):
            if v[r, c]:
                clase = "linea-v-tutu" if dv[r,c]=="Tutu" else "linea-v-abuelita"
                cols_v[c*2].markdown(f"<div class='{clase}'></div>", unsafe_allow_html=True)
            else:
                if cols_v[c*2].button(" ", key=f"v{r}{c}", disabled=not es_mi_turno):
                    n = registrar("v", r, c)
                    play(SND_CUADRO if n > 0 else SND_LINEA)
                    st.rerun()
            if c < COLS:
                if (r, c) in juego["cuadros"]:
                    own = juego["cuadros"][(r, c)]
                    cls = "cuadro-tutu" if own=="Tutu" else "cuadro-abuelita"
                    cols_v[c*2+1].markdown(
                        f"<div class='{cls}'>{own[0]}</div>", unsafe_allow_html=True)
                else:
                    cols_v[c*2+1].markdown(
                        "<div style='height:60px;'></div>", unsafe_allow_html=True)

# ────────────────────────────────────────────
# PANTALLA FINAL
# ────────────────────────────────────────────
if fin:
    pt, pa = juego["puntos"]["Tutu"], juego["puntos"]["Abuelita"]
    if   pt > pa: ganador, cg = "Tutu",     COLOR_TUTU
    elif pa > pt: ganador, cg = "Abuelita", COLOR_ABUELITA
    else:         ganador, cg = "¡Empate!", "#FFD700"

    # Efectos solo la primera vez
    if not st.session_state.fin_festejado:
        play(SND_VICTORIA)
        st.snow()  # ⭐ nieve/estrellas nativas — cubre toda la pantalla garantizado

        # Estrellas extra: explosión desde el centro con CSS
        stars = '<div class="fx-layer">'
        for _ in range(60):
            tw    = random.randint(-700, 700)
            th    = random.randint(-500, 500)
            tr    = random.randint(0, 720)
            delay = round(random.uniform(0, 0.7), 2)
            stars += (
                f'<div class="fx-star" style="--tw:{tw}px;--th:{th}px;--tr:{tr}deg;'
                f'animation-delay:{delay}s;">⭐</div>'
            )
        stars += '</div>'
        st.markdown(stars, unsafe_allow_html=True)
        st.session_state.fin_festejado = True

    # Banner ganador
    st.markdown(f"""
    <div style="text-align:center; padding:32px 20px 24px;
        background:linear-gradient(135deg,{cg}22,{cg}08);
        border:2px solid {cg}88; border-radius:20px; margin-top:20px;">
      <div class="corona-gigante">👑</div>
      <div class="texto-ganador">¡{ganador} ganó!</div>
      <div class="marcador-final">
        {EMOJIS['Tutu']} Tutu
        <span style="font-size:2rem;color:white;">{pt}</span>
        &nbsp;–&nbsp;
        <span style="font-size:2rem;color:white;">{pa}</span>
        Abuelita {EMOJIS['Abuelita']}
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🔄 Nueva partida", type="primary", use_container_width=True):
        reiniciar()
        st.session_state.pts_vistos    = 0
        st.session_state.fin_festejado = False
        st.rerun()
