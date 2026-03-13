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

# Sincronización cada 2 segundos
st_autorefresh(interval=2000, key="datarefresh")

# ────────────────────────────────────────────
# CSS OPTIMIZADO (ESTRELLAS Y LÍNEAS VISIBLES)
# ────────────────────────────────────────────
st.markdown("""
<style>
.stApp { background: radial-gradient(ellipse at 20% 0%, #0d1b3e 0%, #020814 55%, #01040d 100%); }

/* Forzar que las columnas no se muevan ni oculten nada */
div[data-testid="stHorizontalBlock"] { gap: 0px !important; align-items: center; }
[data-testid="column"] { min-width:0px !important; flex-basis:auto !important; padding: 0px 1px !important; }

/* Puntos blancos */
.punto { display:flex; align-items:center; justify-content:center; height:60px; width:100%; font-size:20px; color:white; font-weight:bold; }

/* Líneas MUY GORDAS y visibles (8px) */
.linea-h-tutu::before { content:""; display:block; width:100%; border-top:8px solid #6A4CFF; border-radius:10px; box-shadow: 0 0 15px #6A4CFF; }
.linea-h-abuelita::before { content:""; display:block; width:100%; border-top:8px solid #E05B20; border-radius:10px; box-shadow: 0 0 15px #E05B20; }

/* Líneas verticales: Asegurar que ocupen todo el alto */
.linea-v-tutu, .linea-v-abuelita { display:flex; justify-content:center; height:60px; width:100%; }
.linea-v-tutu::before { content:""; display:block; height:100%; border-left:8px solid #6A4CFF; border-radius:10px; margin: auto; box-shadow: 0 0 15px #6A4CFF; }
.linea-v-abuelita::before { content:""; display:block; height:100%; border-left:8px solid #E05B20; border-radius:10px; margin: auto; box-shadow: 0 0 15px #E05B20; }

/* Cuadros ganados */
.cuadro-tutu { background: linear-gradient(135deg, #6A4CFF 0%, #4F46D7 100%); height:60px; width:100%; border-radius:8px; display:flex; align-items:center; justify-content:center; color:white; font-weight:bold; font-size:24px; }
.cuadro-abuelita { background: linear-gradient(135deg, #E05B20 0%, #9A3D10 100%); height:60px; width:100%; border-radius:8px; display:flex; align-items:center; justify-content:center; color:white; font-weight:bold; font-size:24px; }

/* Botones invisibles: FIJAR ALTURA A 60PX */
button[kind="secondary"] { width:100% !important; height:60px !important; background:transparent !important; border:1px solid rgba(255,255,255,0.1) !important; color:transparent !important; margin:0 !important; }
button[kind="secondary"]:hover:not(:disabled) { background:rgba(255,255,255,0.2) !important; border:1px solid white !important; }

/* Corona y Mensajes Finales */
.corona-gigante { font-size: 100px; text-align: center; margin: 0; }
.texto-ganador { font-size: 50px; font-weight: 900; text-align: center; color: #FFD700; text-shadow: 0 0 30px #FFD700; animation: brillar 1s infinite alternate; }
@keyframes brillar { from { opacity: 0.8; } to { opacity: 1; } }

/* ANIMACIÓN DE ESTRELLAS (⭐) */
.fx-layer { position: fixed; inset: 0; pointer-events: none; z-index: 999; overflow: hidden; }
.fx-star { position: absolute; font-size: 30px; color: #FFD700; animation: volarEstrella 3s ease-out forwards; opacity: 0; }
@keyframes volarEstrella {
    0% { transform: translate(-50%, -50%) scale(0); top: 50%; left: 50%; opacity: 1; }
    100% { transform: translate(var(--tw), var(--th)) scale(1) rotate(var(--tr)); top: 50%; left: 50%; opacity: 0; }
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
        for i in range(int(22050 * 0.25)):
            t = i / 22050
            env = 1 - (i / (22050 * 0.25))
            val = int(32767 * 0.3 * env * math.sin(2 * math.pi * frec * t))
            f.writeframes(struct.pack("<h", val))
    return base64.b64encode(buffer.getvalue()).decode()

SND_CUADRO = _gen_audio(1000)
SND_VICTORIA = _gen_audio(523)

# ────────────────────────────────────────────
# ESTADO DEL JUEGO
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

# Lógica de efectos local
if "puntos_locales" not in st.session_state:
    st.session_state.puntos_locales = 0
if "fin_festejado" not in st.session_state:
    st.session_state.fin_festejado = False

# Globos si alguien anotó
total_actual = sum(juego["puntos"].values())
if total_actual > st.session_state.puntos_locales:
    st.balloons()
    st.markdown(f'<audio autoplay style="display:none;"><source src="data:audio/wav;base64,{SND_CUADRO}"></audio>', unsafe_allow_html=True)
    st.session_state.puntos_locales = total_actual

# ────────────────────────────────────────────
# LÓGICA DE REGISTRO
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
# INTERFAZ
# ────────────────────────────────────────────
with st.sidebar:
    st.title("⚙️ Jugador")
    usuario = st.radio("¿Quién eres tú?", ["Tutu", "Abuelita"], horizontal=True)
    st.divider()
    st.write(f"### Turno de: {juego['turno']}")
    st.metric("🔵 Tutu", f"{juego['puntos']['Tutu']} pts")
    st.metric("🔴 Abuelita", f"{juego['puntos']['Abuelita']} pts")
    if st.button("🔄 Reiniciar Todo", type="primary", use_container_width=True):
        juego["puntos"] = {"Tutu": 0, "Abuelita": 0}; juego["cuadros"].clear()
        juego["lineas_h"].fill(False); juego["lineas_v"].fill(False)
        st.session_state.puntos_locales = 0; st.session_state.fin_festejado = False
        st.rerun()

st.title("🕹️ Timbiriche")
fin = len(juego["cuadros"]) == 16
es_mi_turno = (usuario == juego["turno"]) and not fin

# Dibujar Tablero (Ratio 0.6 para puntos, 3 para líneas)
col_widths = [0.6, 3] * 4 + [0.6]
for r in range(5):
    # Fila Horizontal
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

    # Fila Vertical
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
                    cols_v[c*2+1].markdown("<div style='height:60px;'></div>", unsafe_allow_html=True)

# ────────────────────────────────────────────
# FINAL DE PARTIDA (CON CORONA Y ESTRELLAS ⭐)
# ────────────────────────────────────────────
if fin:
    if not st.session_state.fin_festejado:
        st.markdown(f'<audio autoplay style="display:none;"><source src="data:audio/wav;base64,{SND_VICTORIA}"></audio>', unsafe_allow_html=True)
        
        # EFECTO DE ESTRELLAS ⭐ PERSONALIZADO
        estrellas_html = '<div class="fx-layer">'
        for _ in range(50):
            tw = random.randint(-500, 500) # Dirección X
            th = random.randint(-500, 500) # Dirección Y
            tr = random.randint(0, 720)    # Rotación
            estrellas_html += f'<div class="fx-star" style="--tw:{tw}px; --th:{th}px; --tr:{tr}deg;">⭐</div>'
        estrellas_html += '</div>'
        st.markdown(estrellas_html, unsafe_allow_html=True)
        
        st.session_state.fin_festejado = True
    
    ganador = "Tutu" if juego["puntos"]["Tutu"] > juego["puntos"]["Abuelita"] else "Abuelita"
    if juego["puntos"]["Tutu"] == juego["puntos"]["Abuelita"]: ganador = "Empate"
    
    st.markdown(f"""
    <div class="corona-gigante">👑</div>
    <div class="texto-ganador">¡GANÓ {ganador.upper()}! ✨</div>
    """, unsafe_allow_html=True)
