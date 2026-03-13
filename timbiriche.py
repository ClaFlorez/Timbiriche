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

# Sincronización constante entre dispositivos
st_autorefresh(interval=2000, key="datarefresh")

# ────────────────────────────────────────────
# CSS MAESTRO (RESPONSIVE + FIXED TABLERO)
# ────────────────────────────────────────────
st.markdown("""
<style>
.stApp { background: radial-gradient(ellipse at 20% 0%, #0d1b3e 0%, #020814 55%, #01040d 100%); }

/* --- MAGIA RESPONSIVE: Forzar fila única en cualquier pantalla --- */
div[data-testid="stHorizontalBlock"] {
    display: flex !important;
    flex-direction: row !important;
    flex-wrap: nowrap !important;
    gap: 0px !important;
    align-items: center;
    width: 100% !important;
}

[data-testid="column"] {
    min-width: 0px !important;
    flex-basis: auto !important;
    flex-grow: 1 !important;
    padding: 0px 1px !important;
}

/* Puntos y Líneas adaptables */
.punto { display:flex; align-items:center; justify-content:center; height:45px; width:100%; font-size:16px; color:white; font-weight:bold; }

/* Líneas Neón Gruesas (8px) */
.linea-h-tutu::before { content:""; display:block; width:100%; border-top:8px solid #6A4CFF; border-radius:10px; box-shadow: 0 0 15px #6A4CFF; }
.linea-h-abuelita::before { content:""; display:block; width:100%; border-top:8px solid #E05B20; border-radius:10px; box-shadow: 0 0 15px #E05B20; }

.linea-v-tutu, .linea-v-abuelita { display:flex; justify-content:center; height:45px; width:100%; }
.linea-v-tutu::before { content:""; display:block; height:100%; border-left:8px solid #6A4CFF; border-radius:10px; box-shadow: 0 0 15px #6A4CFF; }
.linea-v-abuelita::before { content:""; display:block; height:100%; border-left:8px solid #E05B20; border-radius:10px; box-shadow: 0 0 15px #E05B20; }

/* Cuadros Conquistados */
.cuadro-tutu { background: linear-gradient(135deg, #6A4CFF 0%, #4F46D7 100%); height:45px; width:100%; border-radius:6px; display:flex; align-items:center; justify-content:center; color:white; font-weight:bold; font-size:18px; }
.cuadro-abuelita { background: linear-gradient(135deg, #E05B20 0%, #9A3D10 100%); height:45px; width:100%; border-radius:6px; display:flex; align-items:center; justify-content:center; color:white; font-weight:bold; font-size:18px; }

/* Botones invisibles pero con tamaño fijo para que no salte el tablero */
button[kind="secondary"] { 
    width:100% !important; height:45px !important; 
    background:transparent !important; 
    border:1px solid rgba(255,255,255,0.05) !important; 
    color:transparent !important; margin:0 !important; 
}

/* Efectos Finales */
.corona-final { font-size: 100px; text-align: center; margin: 10px 0; }
.texto-ganador { font-size: 45px; font-weight: 900; text-align: center; color: #FFD700; text-shadow: 0 0 30px #FFD700; }

/* Capa de Estrellas ⭐ */
.fx-layer { position: fixed; inset: 0; pointer-events: none; z-index: 9999; overflow: hidden; }
.star-fx { position: absolute; font-size: 30px; animation: volar 3s ease-out forwards; top: 50%; left: 50%; }
@keyframes volar {
    0% { transform: translate(-50%, -50%) scale(0); opacity: 1; }
    100% { transform: translate(var(--tw), var(--th)) rotate(var(--tr)) scale(2); opacity: 0; }
}
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
            val = int(32767 * 0.3 * math.sin(2 * math.pi * frec * (i/22050)))
            f.writeframes(struct.pack("<h", val))
    return base64.b64encode(buffer.getvalue()).decode()

SND_CUADRO = _gen_audio(1000)
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

if "p_locales" not in st.session_state: st.session_state.p_locales = 0
if "fin_visto" not in st.session_state: st.session_state.fin_visto = False

# Lanzar globos nativos al anotar
total = sum(juego["puntos"].values())
if total > st.session_state.p_locales:
    st.balloons()
    st.markdown(f'<audio autoplay style="display:none;"><source src="data:audio/wav;base64,{SND_CUADRO}"></audio>', unsafe_allow_html=True)
    st.session_state.p_locales = total

# ────────────────────────────────────────────
# LÓGICA DE REGISTRO
# ────────────────────────────────────────────
def registrar(tipo, r, c):
    h, v = juego["lineas_h"], juego["lineas_v"]
    jug = juego["turno"]
    if tipo == "h": h[r, c] = True; juego["duenos_h"][r, c] = jug
    else: v[r, c] = True; juego["duenos_v"][r, c] = jug
    ok = False
    for row in range(4):
        for col in range(4):
            if (row, col) not in juego["cuadros"]:
                if h[row, col] and h[row+1, col] and v[row, col] and v[row, col+1]:
                    juego["cuadros"][(row, col)] = jug
                    juego["puntos"][jug] += 1
                    ok = True
    if not ok: juego["turno"] = "Abuelita" if jug == "Tutu" else "Tutu"

# ────────────────────────────────────────────
# SIDEBAR
# ────────────────────────────────────────────
with st.sidebar:
    st.title("⚙️ Jugador")
    usuario = st.radio("¿Quién eres tú?", ["Tutu", "Abuelita"], horizontal=True)
    st.divider()
    st.write(f"### Turno de: **{juego['turno']}**")
    st.metric("🔵 Tutu", f"{juego['puntos']['Tutu']} pts")
    st.metric("🔴 Abuelita", f"{juego['puntos']['Abuelita']} pts")
    if st.button("🔄 Reiniciar Partida", type="primary", use_container_width=True):
        juego["puntos"] = {"Tutu": 0, "Abuelita": 0}; juego["cuadros"].clear()
        juego["lineas_h"].fill(False); juego["lineas_v"].fill(False)
        st.session_state.p_locales = 0; st.session_state.fin_visto = False
        st.rerun()

# ────────────────────────────────────────────
# TABLERO ADAPTATIVO
# ────────────────────────────────────────────
st.title("🕹️ Timbiriche")
fin = len(juego["cuadros"]) == 16
es_mi_turno = (usuario == juego["turno"]) and not fin

# Definir anchos de columna (1 para punto, 3 para línea)
col_w = [1, 3, 1, 3, 1, 3, 1, 3, 1]

for r in range(5):
    # Filas Horizontales
    cols = st.columns(col_w)
    for c in range(4):
        cols[c*2].markdown("<div class='punto'>●</div>", unsafe_allow_html=True)
        if juego["lineas_h"][r, c]:
            color = 'tutu' if juego['duenos_h'][r,c]=='Tutu' else 'abuelita'
            cols[c*2+1].markdown(f"<div class='linea-h-{color}'></div>", unsafe_allow_html=True)
        else:
            if cols[c*2+1].button(" ", key=f"h{r}{c}", disabled=not es_mi_turno):
                registrar("h", r, c); st.rerun()
    cols[8].markdown("<div class='punto'>●</div>", unsafe_allow_html=True)

    # Filas Verticales y Cuadros
    if r < 4:
        cols_v = st.columns(col_w)
        for c in range(5):
            if juego["lineas_v"][r, c]:
                color = 'tutu' if juego['duenos_v'][r,c]=='Tutu' else 'abuelita'
                cols_v[c*2].markdown(f"<div class='linea-v-{color}'></div>", unsafe_allow_html=True)
            else:
                if cols_v[c*2].button(" ", key=f"v{r}{c}", disabled=not es_mi_turno):
                    registrar("v", r, c); st.rerun()
            
            if c < 4:
                if (r, c) in juego["cuadros"]:
                    own = juego["cuadros"][(r, c)]
                    cols_v[c*2+1].markdown(f"<div class='cuadro-{'tutu' if own=='Tutu' else 'abuelita'}'>{own[0]}</div>", unsafe_allow_html=True)
                else:
                    cols_v[c*2+1].markdown("<div style='height:45px;'></div>", unsafe_allow_html=True)

# ────────────────────────────────────────────
# FINAL CON CORONA Y ESTRELLAS ⭐
# ────────────────────────────────────────────
if fin:
    if not st.session_state.fin_visto:
        st.markdown(f'<audio autoplay style="display:none;"><source src="data:audio/wav;base64,{SND_VICTORIA}"></audio>', unsafe_allow_html=True)
        # Explosión de estrellas ⭐
        fx = '<div class="fx-layer">'
        for _ in range(65):
            fx += f'<div class="star-fx" style="--tw:{random.randint(-500,500)}px; --th:{random.randint(-500,500)}px; --tr:{random.randint(0,720)}deg;">⭐</div>'
        st.markdown(fx + '</div>', unsafe_allow_html=True)
        st.session_state.fin_visto = True
    
    ganador = "Tutu" if juego["puntos"]["Tutu"] > juego["puntos"]["Abuelita"] else "Abuelita"
    if juego["puntos"]["Tutu"] == juego["puntos"]["Abuelita"]: ganador = "Empate"
    
    st.markdown(f'<div class="corona-final">👑</div><div class="texto-ganador">¡GANÓ {ganador.upper()}!</div>', unsafe_allow_html=True)
