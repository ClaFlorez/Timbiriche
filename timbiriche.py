import streamlit as st
import numpy as np
import random
import math
import wave
import struct
import io
import base64
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="Timbiriche: Tutu vs Abuelita", layout="wide")

# Refresco para sincronizar ambos jugadores cada 2 segundos
st_autorefresh(interval=2000, key="datarefresh")

# -------------------- CSS PROFESIONAL --------------------
st.markdown("""
<style>
.stApp {
    background: radial-gradient(circle at top, #07152b 0%, #020814 60%, #01040d 100%);
}

/* Evita que las columnas se muevan */
div[data-testid="stHorizontalBlock"] {
    gap: 0px !important;
    align-items: center;
}

[data-testid="column"] {
    min-width: 0px !important;
    flex-basis: auto !important;
}

/* Estilo de botones del tablero */
button[kind="secondary"] {
    width: 100% !important;
    height: 50px !important;
    background: transparent !important;
    border: 1px solid rgba(255,255,255,0.05) !important;
    color: transparent !important;
    margin: 0 !important;
    cursor: pointer !important;
}

button[kind="secondary"]:hover:not(:disabled) {
    background: rgba(255,255,255,0.1) !important;
}

/* Botón de reinicio */
button[kind="primary"] {
    background: linear-gradient(135deg, #6A4CFF 0%, #4F46D7 100%) !important;
    font-size: 20px !important;
    border-radius: 12px !important;
}

.punto {
    display: flex; align-items: center; justify-content: center;
    height: 50px; font-size: 24px; color: white;
}

.linea-h-llena {
    height: 50px; display: flex; align-items: center; justify-content: center;
}
.linea-h-llena::before {
    content: ""; display: block; width: 100%; border-top: 6px solid #D8D8D8; border-radius: 10px;
}

.linea-v-llena {
    width: 100%; height: 50px; display: flex; align-items: center; justify-content: center;
}
.linea-v-llena::before {
    content: ""; display: block; height: 100%; border-left: 6px solid #D8D8D8; border-radius: 10px;
}

.cuadro-tutu { background: linear-gradient(135deg, #6A4CFF 0%, #4F46D7 100%); height: 50px; width: 100%; border-radius: 8px; display: flex; align-items: center; justify-content: center; color: white; font-weight: bold; }
.cuadro-abuelita { background: linear-gradient(135deg, #9A3D10 0%, #7A2E10 100%); height: 50px; width: 100%; border-radius: 8px; display: flex; align-items: center; justify-content: center; color: white; font-weight: bold; }

/* Animación de confeti final */
.fx-layer { position: fixed; inset: 0; pointer-events: none; z-index: 999; }
.fx-item { position: absolute; top: -10vh; animation: caer linear infinite; }
@keyframes caer {
    0% { transform: translateY(-10vh) rotate(0deg); opacity: 0; }
    10% { opacity: 1; }
    100% { transform: translateY(110vh) rotate(360deg); opacity: 0; }
}
</style>
""", unsafe_allow_html=True)

# -------------------- AUDIO --------------------
def crear_audio_64(frec):
    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as f:
        f.setnchannels(1); f.setsampwidth(2); f.setframerate(22050)
        for i in range(int(22050 * 0.2)):
            t = i / 22050
            val = int(32767 * 0.3 * math.sin(2 * math.pi * frec * t))
            f.writeframes(struct.pack("<h", val))
    return base64.b64encode(buffer.getvalue()).decode()

SONIDO_CUADRO = crear_audio_64(880)

# -------------------- ESTADO COMPARTIDO --------------------
@st.cache_resource
def get_juego():
    return {
        "puntos": {"Tutu": 0, "Abuelita": 0},
        "turno": "Tutu",
        "lineas_h": np.zeros((5, 4), dtype=bool),
        "lineas_v": np.zeros((4, 5), dtype=bool),
        "cuadros": {}
    }

juego = get_juego()

# Conteo de globos local
if "ultimo_conteo" not in st.session_state:
    st.session_state.ultimo_conteo = 0

if len(juego["cuadros"]) > st.session_state.ultimo_conteo:
    st.balloons()
    st.session_state.ultimo_conteo = len(juego["cuadros"])
    st.markdown(f'<audio autoplay style="display:none;"><source src="data:audio/wav;base64,{SONIDO_CUADRO}"></audio>', unsafe_allow_html=True)

# -------------------- LÓGICA --------------------
def registrar(tipo, r, c):
    if tipo == "h": juego["lineas_h"][r, c] = True
    else: juego["lineas_v"][r, c] = True
    
    formo = False
    h, v = juego["lineas_h"], juego["lineas_v"]
    for row in range(4):
        for col in range(4):
            if (row, col) not in juego["cuadros"]:
                if h[row, col] and h[row+1, col] and v[row, col] and v[row, col+1]:
                    juego["cuadros"][(row, col)] = juego["turno"]
                    juego["puntos"][juego["turno"]] += 1
                    formo = True
    if not formo:
        juego["turno"] = "Abuelita" if juego["turno"] == "Tutu" else "Tutu"

# -------------------- SIDEBAR --------------------
st.sidebar.title("Configuración")
usuario = st.sidebar.radio("¿Quién eres tú?", ["Tutu", "Abuelita"])
st.sidebar.divider()
st.sidebar.write(f"### Turno de: **{juego['turno']}**")
st.sidebar.metric("🔵 Puntos Tutu", juego["puntos"]["Tutu"])
st.sidebar.metric("🔴 Puntos Abuelita", juego["puntos"]["Abuelita"])

if st.sidebar.button("Reiniciar Tablero"):
    juego["puntos"] = {"Tutu": 0, "Abuelita": 0}
    juego["turno"] = "Tutu"
    juego["lineas_h"].fill(False)
    juego["lineas_v"].fill(False)
    juego["cuadros"].clear()
    st.rerun()

# -------------------- TABLERO --------------------
st.title("🕹️ Timbiriche: Tutu vs Abuelita")
es_mi_turno = (usuario == juego["turno"])
fin = len(juego["cuadros"]) == 16

for r in range(5):
    # Filas Horizontales
    cols = st.columns([0.6, 3, 0.6, 3, 0.6, 3, 0.6, 3, 0.6])
    for c in range(4):
        cols[c*2].markdown("<div class='punto'>●</div>", unsafe_allow_html=True)
        if juego["lineas_h"][r, c]:
            cols[c*2+1].markdown("<div class='linea-h-llena'></div>", unsafe_allow_html=True)
        else:
            # Botón bloqueado si no es tu turno
            if cols[c*2+1].button(" ", key=f"h{r}{c}", disabled=not es_mi_turno or fin):
                registrar("h", r, c)
                st.rerun()
    cols[8].markdown("<div class='punto'>●</div>", unsafe_allow_html=True)

    # Filas Verticales y Cuadros
    if r < 4:
        cols_v = st.columns([0.6, 3, 0.6, 3, 0.6, 3, 0.6, 3, 0.6])
        for c in range(5):
            if juego["lineas_v"][r, c]:
                cols_v[c*2].markdown("<div class='linea-v-llena'></div>", unsafe_allow_html=True)
            else:
                if cols_v[c*2].button(" ", key=f"v{r}{c}", disabled=not es_mi_turno or fin):
                    registrar("v", r, c)
                    st.rerun()
            if c < 4:
                if (r, c) in juego["cuadros"]:
                    own = juego["cuadros"][(r, c)]
                    clase = "cuadro-tutu" if own == "Tutu" else "cuadro-abuelita"
                    cols_v[c*2+1].markdown(f"<div class='{clase}'>{own[0]}</div>", unsafe_allow_html=True)

if fin:
    ganador = "Tutu" if juego["puntos"]["Tutu"] > juego["puntos"]["Abuelita"] else "Abuelita"
    st.balloons()
    st.success(f"👑 ¡Felicidades! Ganó {ganador}")
