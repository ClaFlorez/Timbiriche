import streamlit as st
import numpy as np
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="Timbiriche: Tutu vs Abuelita", layout="centered")

# Auto-refresco cada 2 segundos para sincronizar
st_autorefresh(interval=5000, key="datarefresh")

# --- CSS PARA CUADROS Y PUNTOS ---
st.markdown("""
    <style>
    .stButton > button { width: 100% !important; height: 35px !important; background-color: #262730 !important; border: 1px solid #444 !important; padding: 0px !important; }
    .punto { font-size: 26px; color: white; text-align: center; line-height: 35px; height: 35px; }
    .linea-h-llena { border-bottom: 6px solid #AAAAAA; width: 100%; height: 18px; }
    .linea-v-llena { border-left: 6px solid #AAAAAA; height: 50px; margin: auto; width: 6px; }
    .cuadro-tutu { background-color: #6A4CFF; color: white; text-align: center; font-weight: bold; border-radius: 4px; line-height: 50px; height: 50px; width: 100%; font-size: 20px; }
    .cuadro-abuelita { background-color: #7A2E16; color: white; text-align: center; font-weight: bold; border-radius: 4px; line-height: 50px; height: 50px; width: 100%; font-size: 20px; }
    </style>
    """, unsafe_allow_html=True)

# --- MEMORIA COMPARTIDA ---
@st.cache_resource
def obtener_juego_compartido():
    return {
        "puntos": {"Tutu": 0, "Abuelita": 0},
        "turno": "Tutu",
        "lineas_h": np.zeros((5, 4), dtype=bool),
        "lineas_v": np.zeros((4, 5), dtype=bool),
        "cuadros": {},
        "total_cuadros": 0
    }

juego = obtener_juego_compartido()

# --- LÓGICA DE GLOBOS LOCAL ---
# Si el número de cuadros en el juego aumentó, lanzamos globos en esta pantalla
if "ultimo_conteo" not in st.session_state:
    st.session_state.ultimo_conteo = 0

if len(juego["cuadros"]) > st.session_state.ultimo_conteo:
    st.balloons()
    st.session_state.ultimo_conteo = len(juego["cuadros"])

def registrar(tipo, r, c):
    if tipo == 'h': juego["lineas_h"][r, c] = True
    else: juego["lineas_v"][r, c] = True
    
    h, v = juego["lineas_h"], juego["lineas_v"]
    formo = False
    for row in range(4):
        for col in range(4):
            if (row, col) not in juego["cuadros"]:
                if h[row, col] and h[row+1, col] and v[row, col] and v[row, col+1]:
                    juego["cuadros"][(row, col)] = juego["turno"]
                    juego["puntos"][juego["turno"]] += 1
                    formo = True
    
    if not formo:
        juego["turno"] = "Abuelita" if juego["turno"] == "Tutu" else "Tutu"

# --- INTERFAZ ---
st.title("🕹️ Timbiriche: Tutu vs Abuelita")
st.sidebar.write(f"### Turno de: **{juego['turno']}**")
st.sidebar.metric("🔵 Tutu", juego["puntos"]["Tutu"])
st.sidebar.metric("🔴 Abuelita", juego["puntos"]["Abuelita"])

for r in range(5):
    cols = st.columns([1, 4, 1, 4, 1, 4, 1, 4, 1])
    for c in range(4):
        cols[c*2].markdown("<div class='punto'>●</div>", unsafe_allow_html=True)
        if juego["lineas_h"][r, c]:
            cols[c*2+1].markdown("<div class='linea-h-llena'></div>", unsafe_allow_html=True)
        else:
            if cols[c*2+1].button(" ", key=f"h{r}{c}"):
                registrar('h', r, c)
                st.rerun()
    cols[8].markdown("<div class='punto'>●</div>", unsafe_allow_html=True)

    if r < 4:
        cols_v = st.columns([1, 4, 1, 4, 1, 4, 1, 4, 1])
        for c in range(5):
            if juego["lineas_v"][r, c]:
                cols_v[c*2].markdown("<div class='linea-v-llena'></div>", unsafe_allow_html=True)
            else:
                if cols_v[c*2].button(" ", key=f"v{r}{c}"):
                    registrar('v', r, c)
                    st.rerun()
            if c < 4 and (r, c) in juego["cuadros"]:
                own = juego["cuadros"][(r, c)]
                clase = "cuadro-tutu" if own == "Tutu" else "cuadro-abuelita"
                cols_v[c*2+1].markdown(f"<div class='{clase}'>{own[0]}</div>", unsafe_allow_html=True)

if st.sidebar.button("Reiniciar Juego"):
    juego["puntos"] = {"Tutu": 0, "Abuelita": 0}
    juego["turno"] = "Tutu"
    juego["lineas_h"].fill(False)
    juego["lineas_v"].fill(False)
    juego["cuadros"].clear()
    st.session_state.ultimo_conteo = 0
    st.rerun()
