import streamlit as st
import numpy as np
import math
import wave
import struct
import io
import base64
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="Timbiriche · Tutu vs Abuelita", layout="wide")

# Mantener sincronizado (cada 2 segundos)
st_autorefresh(interval=2000, key="datarefresh")

# ────────────────────────────────────────────
# ESTILO CSS (FIJO PARA EVITAR SALTOS)
# ────────────────────────────────────────────
st.markdown(f"""
<style>
.stApp {{ background: radial-gradient(ellipse at 20% 0%, #0d1b3e 0%, #020814 55%, #01040d 100%); }}
div[data-testid="stHorizontalBlock"] {{ gap: 0px !important; align-items: center; }}
[data-testid="column"] {{ min-width:0px !important; flex-basis:auto !important; padding: 0px 2px !important; }}
.punto {{ display:flex; align-items:center; justify-content:center; height:50px; width:100%; font-size:16px; color:rgba(255,255,255,0.6); }}
.linea-h-tutu::before {{ content:""; display:block; width:90%; border-top:6px solid #6A4CFF; border-radius:10px; }}
.linea-h-abuelita::before{{ content:""; display:block; width:90%; border-top:6px solid #E05B20; border-radius:10px; }}
.linea-v-tutu::before {{ content:""; display:block; height:90%; border-left:6px solid #6A4CFF; border-radius:10px; }}
.linea-v-abuelita::before{{ content:""; display:block; height:90%; border-left:6px solid #E05B20; border-radius:10px; }}
.cuadro-tutu {{ background: linear-gradient(135deg, #6A4CFFcc 0%, #4F46D7cc 100%); height:50px; width:100%; border-radius:8px; display:flex; align-items:center; justify-content:center; color:white; font-weight:700; }}
.cuadro-abuelita {{ background: linear-gradient(135deg, #E05B20cc 0%, #9A3D10cc 100%); height:50px; width:100%; border-radius:8px; display:flex; align-items:center; justify-content:center; color:white; font-weight:700; }}
button[kind="secondary"] {{ width:100% !important; height:50px !important; background:transparent !important; border:1px solid rgba(255,255,255,0.04) !important; color:transparent !important; margin:0 !important; cursor:pointer !important; }}
button[kind="secondary"]:hover:not(:disabled) {{ background:rgba(255,255,255,0.08) !important; }}
.scorecard {{ background:rgba(255,255,255,0.05); border:1px solid rgba(255,255,255,0.1); border-radius:14px; padding:10px 20px; margin-bottom:10px; }}
h1 {{ color: white !important; text-align: center; }}
</style>
""", unsafe_allow_html=True)

# ────────────────────────────────────────────
# AUDIO
# ────────────────────────────────────────────
@st.cache_data
def _gen_audio(frec):
    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as f:
        f.setnchannels(1); f.setsampwidth(2); f.setframerate(22050)
        for i in range(int(22050 * 0.2)):
            t = i / 22050
            val = int(32767 * 0.3 * math.sin(2 * math.pi * frec * t))
            f.writeframes(struct.pack("<h", val))
    return base64.b64encode(buffer.getvalue()).decode()

SND_CUADRO = _gen_audio(880)
SND_VICTORIA = _gen_audio(523)

# ────────────────────────────────────────────
# ESTADO COMPARTIDO
# ────────────────────────────────────────────
@st.cache_resource
def get_juego():
    return {
        "puntos": {"Tutu": 0, "Abuelita": 0}, "turno": "Tutu",
        "lineas_h": np.zeros((5, 4), dtype=bool), "lineas_v": np.zeros((4, 5), dtype=bool),
        "duenos_h": np.full((5, 4), "", dtype=object), "duenos_v": np.full((4, 5), "", dtype=object),
        "cuadros": {}
    }

juego = get_juego()

# ────────────────────────────────────────────
# LÓGICA DE EFECTOS (GLOBOS Y ESTRELLAS)
# ────────────────────────────────────────────
if "puntos_vistos" not in st.session_state:
    st.session_state.puntos_vistos = 0
if "victoria_festejada" not in st.session_state:
    st.session_state.victoria_festejada = False

total_puntos = sum(juego["puntos"].values())
fin = len(juego["cuadros"]) == 16

# ¿Alguien anotó un cuadro nuevo? -> Globos
if total_puntos > st.session_state.puntos_vistos:
    st.balloons()
    st.markdown(f'<audio autoplay style="display:none;"><source src="data:audio/wav;base64,{SND_CUADRO}"></audio>', unsafe_allow_html=True)
    st.session_state.puntos_vistos = total_puntos

# ¿Se acabó el juego? -> Estrellas (Snow)
if fin and not st.session_state.victoria_festejada:
    st.snow()
    st.markdown(f'<audio autoplay style="display:none;"><source src="data:audio/wav;base64,{SND_VICTORIA}"></audio>', unsafe_allow_html=True)
    st.session_state.victoria_festejada = True

# ────────────────────────────────────────────
# LÓGICA DE MOVIMIENTO
# ────────────────────────────────────────────
def registrar(tipo, r, c):
    h, v = juego["lineas_h"], juego["lineas_v"]
    jugador = juego["turno"]
    if tipo == "h": h[r, c] = True; juego["duenos_h"][r, c] = jugador
    else: v[r, c] = True; juego["duenos_v"][r, c] = jugador
    
    anoto = False
    for row in range(4):
        for col in range(4):
            if (row, col) not in juego["cuadros"]:
                if h[row, col] and h[row+1, col] and v[row, col] and v[row, col+1]:
                    juego["cuadros"][(row, col)] = jugador
                    juego["puntos"][jugador] += 1
                    anoto = True
    if not anoto:
        juego["turno"] = "Abuelita" if jugador == "Tutu" else "Tutu"

# ────────────────────────────────────────────
# SIDEBAR E INTERFAZ
# ────────────────────────────────────────────
with st.sidebar:
    st.title("⚙️ Jugador")
    usuario = st.radio("¿Quién eres?", ["Tutu", "Abuelita"], horizontal=True)
    st.divider()
    st.write(f"### Turno de: **{juego['turno']}**")
    for j in ["Tutu", "Abuelita"]:
        color = "#6A4CFF" if j == "Tutu" else "#E05B20"
        st.markdown(f'<div class="scorecard" style="border-color:{color}; color:{color};"><strong>{j}</strong>: {juego["puntos"][j]} pts</div>', unsafe_allow_html=True)
    
    if st.button("🔄 Reiniciar Todo", type="primary"):
        juego["puntos"] = {"Tutu": 0, "Abuelita": 0}; juego["cuadros"].clear()
        juego["lineas_h"].fill(False); juego["lineas_v"].fill(False)
        st.session_state.puntos_vistos = 0; st.session_state.victoria_festejada = False
        st.rerun()

st.title("🕹️ Timbiriche")
es_mi_turno = (usuario == juego["turno"]) and not fin

# Dibujar Tablero
col_widths = [0.6, 3] * 4 + [0.6]
for r in range(5):
    cols = st.columns(col_widths)
    for c in range(4):
        cols[c*2].markdown("<div class='punto'>●</div>", unsafe_allow_html=True)
        if juego["lineas_h"][r, c]:
            clase = "linea-h-tutu" if juego["duenos_h"][r, c] == "Tutu" else "linea-h-abuelita"
            cols[c*2+1].markdown(f"<div class='{clase}'></div>", unsafe_allow_html=True)
        else:
            if cols[c*2+1].button(" ", key=f"h{r}{c}", disabled=not es_mi_turno):
                registrar("h", r, c); st.rerun()
    cols[8].markdown("<div class='punto'>●</div>", unsafe_allow_html=True)

    if r < 4:
        cols_v = st.columns(col_widths)
        for c in range(5):
            if juego["lineas_v"][r, c]:
                clase = "linea-v-tutu" if juego["duenos_v"][r, c] == "Tutu" else "linea-v-abuelita"
                cols_v[c*2].markdown(f"<div class='{clase}'></div>", unsafe_allow_html=True)
            else:
                if cols_v[c*2].button(" ", key=f"v{r}{c}", disabled=not es_mi_turno):
                    registrar("v", r, c); st.rerun()
            if c < 4:
                if (r, c) in juego["cuadros"]:
                    own = juego["cuadros"][(r, c)]
                    cols_v[c*2+1].markdown(f"<div class='cuadro-{'tutu' if own=='Tutu' else 'abuelita'}'>{own[0]}</div>", unsafe_allow_html=True)
                else:
                    cols_v[c*2+1].markdown("<div style='height:50px;'></div>", unsafe_allow_html=True)

if fin:
    st.success(f"👑 ¡FIN DE LA PARTIDA!")
