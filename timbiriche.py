import streamlit as st
import streamlit.components.v1 as components
import numpy as np
import math
import wave
import struct
import io
import base64
import time
from streamlit_autorefresh import st_autorefresh

st.set_page_config(
    page_title="Timbiriche · Tutu vs Abuelita",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ────────────────────────────────────────────
# CONSTANTES
# ────────────────────────────────────────────
FILAS = 4
COLS = 4
JUGADORES = ["Tutu", "Abuelita"]
EMOJIS = {"Tutu": "🔵", "Abuelita": "🔴"}
COLOR_TUTU = "#6A4CFF"
COLOR_ABUELITA = "#E05B20"

# ────────────────────────────────────────────
# CSS OPTIMIZADO PARA NO SALTAR
# ────────────────────────────────────────────
st.markdown(f"""
<style>
.stApp {{ background: radial-gradient(ellipse at 20% 0%, #0d1b3e 0%, #020814 55%, #01040d 100%); }}
div[data-testid="stHorizontalBlock"] {{ gap: 0px !important; align-items: center; }}
[data-testid="column"] {{ min-width:0px !important; flex-basis:auto !important; padding: 0px 2px !important; }}

.punto {{ display:flex; align-items:center; justify-content:center; height:50px; width:100%; font-size:16px; color:rgba(255,255,255,0.6); }}

.linea-h-tutu::before {{ content:""; display:block; width:90%; border-top:6px solid {COLOR_TUTU}; border-radius:10px; }}
.linea-h-abuelita::before{{ content:""; display:block; width:90%; border-top:6px solid {COLOR_ABUELITA}; border-radius:10px; }}
.linea-v-tutu::before {{ content:""; display:block; height:90%; border-left:6px solid {COLOR_TUTU}; border-radius:10px; }}
.linea-v-abuelita::before{{ content:""; display:block; height:90%; border-left:6px solid {COLOR_ABUELITA}; border-radius:10px; }}

.cuadro-tutu {{ background: linear-gradient(135deg, {COLOR_TUTU}cc 0%, #4F46D7cc 100%); height:50px; width:100%; border-radius:8px; display:flex; align-items:center; justify-content:center; color:white; font-weight:700; }}
.cuadro-abuelita {{ background: linear-gradient(135deg, {COLOR_ABUELITA}cc 0%, #9A3D10cc 100%); height:50px; width:100%; border-radius:8px; display:flex; align-items:center; justify-content:center; color:white; font-weight:700; }}

button[kind="secondary"] {{ width:100% !important; height:50px !important; background:transparent !important; border:1px solid rgba(255,255,255,0.04) !important; color:transparent !important; margin:0 !important; cursor:pointer !important; }}
button[kind="secondary"]:hover:not(:disabled) {{ background:rgba(255,255,255,0.08) !important; }}
button[kind="primary"] {{ background: linear-gradient(135deg,#6A4CFF,#4F46D7) !important; font-size:16px !important; border-radius:10px !important; }}

.scorecard {{ background:rgba(255,255,255,0.05); border:1px solid rgba(255,255,255,0.1); border-radius:14px; padding:16px 20px; margin-bottom:10px; }}
.scorecard-pts {{ font-size:36px; font-weight:800; color:white; }}
.turno-badge {{ display:inline-block; padding:6px 18px; border-radius:20px; font-size:14px; font-weight:700; margin-bottom:8px; }}
h1 {{ color: white !important; text-align: center; font-size: 2rem !important; }}
</style>
""", unsafe_allow_html=True)

st_autorefresh(interval=2000, key="datarefresh")

# ────────────────────────────────────────────
# AUDIO Y EFECTOS (CORREGIDOS)
# ────────────────────────────────────────────
@st.cache_data
def _gen_audio(frec: float) -> str:
    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as f:
        f.setnchannels(1); f.setsampwidth(2); f.setframerate(22050)
        for i in range(int(22050 * 0.2)):
            t = i / 22050
            env = 1 - (i / (22050 * 0.2)) ** 2
            val = int(32767 * 0.35 * env * math.sin(2 * math.pi * frec * t))
            f.writeframes(struct.pack("<h", val))
    return base64.b64encode(buffer.getvalue()).decode()

SND_CUADRO = _gen_audio(1046)
SND_VICTORIA = _gen_audio(523)

def lanzar_globos():
    components.html(f"""
    <div style="position:fixed;inset:0;pointer-events:none;z-index:999;overflow:hidden;">
        {"".join([f'<div style="position:absolute;left:{i*5}%;bottom:-50px;font-size:40px;animation:subir {2+i%2}s linear forwards;">🎈</div>' for i in range(20)])}
    </div>
    <style>@keyframes subir {{ to {{ transform:translateY(-120vh) rotate({time.time()%30}deg); opacity:0; }} }}</style>
    <script>var fr = window.frameElement; if(fr) {{ fr.style.cssText = 'position:fixed;inset:0;width:100vw;height:100vh;border:none;pointer-events:none;z-index:9999;'; }}</script>
    """, height=0)

def lanzar_estrellas():
    components.html(f"""
    <div style="position:fixed;inset:0;pointer-events:none;z-index:999;overflow:hidden;">
        {"".join([f'<div style="position:absolute;left:{np.random.randint(0,100)}%;top:-50px;font-size:30px;animation:caer {3+i%3}s linear forwards;">⭐</div>' for i in range(40)])}
    </div>
    <style>@keyframes caer {{ to {{ transform:translateY(110vh) rotate(360deg); opacity:0; }} }}</style>
    <script>var fr = window.frameElement; if(fr) {{ fr.style.cssText = 'position:fixed;inset:0;width:100vw;height:100vh;border:none;pointer-events:none;z-index:9999;'; }}</script>
    """, height=0)

# ────────────────────────────────────────────
# ESTADO COMPARTIDO
# ────────────────────────────────────────────
@st.cache_resource
def get_juego():
    return {
        "puntos": {"Tutu": 0, "Abuelita": 0}, "turno": "Tutu",
        "lineas_h": np.zeros((FILAS + 1, COLS), dtype=bool),
        "lineas_v": np.zeros((FILAS, COLS + 1), dtype=bool),
        "duenos_h": np.full((FILAS + 1, COLS), "", dtype=object),
        "duenos_v": np.full((FILAS, COLS + 1), "", dtype=object),
        "cuadros": {}, "historial": []
    }

juego = get_juego()

if "cuadros_vistos" not in st.session_state:
    st.session_state.cuadros_vistos = 0

# ACTIVAR GLOBOS
if len(juego["cuadros"]) > st.session_state.cuadros_vistos:
    lanzar_globos()
    st.session_state.cuadros_vistos = len(juego["cuadros"])
    st.markdown(f'<audio autoplay style="display:none;"><source src="data:audio/wav;base64,{SND_CUADRO}"></audio>', unsafe_allow_html=True)

# ────────────────────────────────────────────
# LÓGICA Y SIDEBAR
# ────────────────────────────────────────────
def registrar(tipo, r, c):
    h, v = juego["lineas_h"], juego["lineas_v"]
    jugador = juego["turno"]
    if tipo == "h": h[r, c] = True; juego["duenos_h"][r, c] = jugador
    else: v[r, c] = True; juego["duenos_v"][r, c] = jugador
    formados = 0
    for row in range(FILAS):
        for col in range(COLS):
            if (row, col) not in juego["cuadros"]:
                if h[row, col] and h[row+1, col] and v[row, col] and v[row, col+1]:
                    juego["cuadros"][(row, col)] = jugador
                    juego["puntos"][jugador] += 1
                    formados += 1
    if formados == 0:
        juego["turno"] = "Abuelita" if jugador == "Tutu" else "Tutu"

with st.sidebar:
    st.markdown("## ⚙️ Jugador")
    usuario = st.radio("¿Quién eres tú?", JUGADORES, horizontal=True)
    st.divider()
    color_turno = COLOR_TUTU if juego["turno"] == "Tutu" else COLOR_ABUELITA
    st.markdown(f"<div class='turno-badge' style='background:{color_turno}33; border:1.5px solid {color_turno}; color:white;'>{EMOJIS[juego['turno']]} Turno de <strong>{juego['turno']}</strong></div>", unsafe_allow_html=True)
    for j in JUGADORES:
        col_j = COLOR_TUTU if j == "Tutu" else COLOR_ABUELITA
        st.markdown(f'<div class="scorecard" style="border-color:{col_j}55;"><div class="scorecard-pts" style="color:{col_j};">{juego["puntos"][j]}</div><div class="scorecard-label">{EMOJIS[j]} {j}</div></div>', unsafe_allow_html=True)
    if st.button("🔄 Reiniciar partida", type="primary", use_container_width=True):
        juego["puntos"] = {"Tutu": 0, "Abuelita": 0}; juego["cuadros"].clear()
        juego["lineas_h"].fill(False); juego["lineas_v"].fill(False)
        st.session_state.cuadros_vistos = 0; st.rerun()

# ────────────────────────────────────────────
# TABLERO Y PANTALLA FINAL
# ────────────────────────────────────────────
fin = len(juego["cuadros"]) == FILAS * COLS
es_mi_turno = (usuario == juego["turno"]) and not fin

st.markdown("<h1>🕹️ Timbiriche</h1>", unsafe_allow_html=True)

col_widths = [0.6, 3] * COLS + [0.6]
for r in range(FILAS + 1):
    cols = st.columns(col_widths)
    for c in range(COLS):
        cols[c*2].markdown("<div class='punto'>●</div>", unsafe_allow_html=True)
        if juego["lineas_h"][r, c]:
            clase = "linea-h-tutu" if juego["duenos_h"][r, c] == "Tutu" else "linea-h-abuelita"
            cols[c*2+1].markdown(f"<div class='{clase}'></div>", unsafe_allow_html=True)
        else:
            if cols[c*2+1].button(" ", key=f"h{r}{c}", disabled=not es_mi_turno):
                registrar("h", r, c); st.rerun()
    cols[COLS*2].markdown("<div class='punto'>●</div>", unsafe_allow_html=True)

    if r < FILAS:
        cols_v = st.columns(col_widths)
        for c in range(COLS + 1):
            if juego["lineas_v"][r, c]:
                clase = "linea-v-tutu" if juego["duenos_v"][r, c] == "Tutu" else "linea-v-abuelita"
                cols_v[c*2].markdown(f"<div class='{clase}'></div>", unsafe_allow_html=True)
            else:
                if cols_v[c*2].button(" ", key=f"v{r}{c}", disabled=not es_mi_turno):
                    registrar("v", r, c); st.rerun()
            if c < COLS:
                if (r, c) in juego["cuadros"]:
                    own = juego["cuadros"][(r, c)]
                    cols_v[c*2+1].markdown(f"<div class='cuadro-{'tutu' if own=='Tutu' else 'abuelita'}'>{own[0]}</div>", unsafe_allow_html=True)
                else:
                    cols_v[c*2+1].markdown("<div style='height:50px;'></div>", unsafe_allow_html=True)

if fin:
    lanzar_estrellas()
    st.markdown(f'<audio autoplay style="display:none;"><source src="data:audio/wav;base64,{SND_VICTORIA}"></audio>', unsafe_allow_html=True)
    ganador = "Tutu" if juego["puntos"]["Tutu"] > juego["puntos"]["Abuelita"] else "Abuelita"
    st.success(f"👑 ¡Ganó {ganador}! {juego['puntos']['Tutu']} - {juego['puntos']['Abuelita']}")
