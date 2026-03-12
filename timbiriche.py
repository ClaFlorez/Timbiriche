import streamlit as st
import numpy as np
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="Timbiriche: Tutu vs Abuelita", layout="centered")

# --- AUTO-REFRESCO: Revisa cambios cada 2 segundos ---
st_autorefresh(interval=2000, key="datarefresh")

# --- CSS Original ---
st.markdown("""
    <style>
    .stButton > button { width: 100%; padding: 0px; height: 35px; background-color: #262730; border: 1px solid #444; }
    .punto { font-size: 25px; text-align: center; line-height: 35px; color: white; }
    .linea-h-llena { border-bottom: 6px solid #AAAAAA; margin-top: 15px; }
    .linea-v-llena { border-left: 6px solid #AAAAAA; height: 40px; margin-left: 50%; }
    .cuadro-tutu { background-color: #005A87; display: flex; align-items: center; justify-content: center; height: 40px; border-radius: 4px; font-weight: bold; }
    .cuadro-abuelita { background-color: #7A2E16; display: flex; align-items: center; justify-content: center; height: 40px; border-radius: 4px; font-weight: bold; }
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
        "lanzar_globos": False
    }

juego = obtener_juego_compartido()

# LANZAR GLOBOS SI ALGUIEN ANOTÓ
if juego["lanzar_globos"]:
    st.balloons()
    juego["lanzar_globos"] = False

def registrar_movimiento(tipo, r, c):
    if tipo == 'h': juego["lineas_h"][r, c] = True
    else: juego["lineas_v"][r, c] = True
    
    h, v = juego["lineas_h"], juego["lineas_v"]
    formo_cuadro = False
    for row in range(4):
        for col in range(4):
            if (row, col) not in juego["cuadros"]:
                if h[row, col] and h[row+1, col] and v[row, col] and v[row, col+1]:
                    juego["cuadros"][(row, col)] = juego["turno"]
                    juego["puntos"][juego["turno"]] += 1
                    formo_cuadro = True
                    juego["lanzar_globos"] = True
    
    if not formo_cuadro:
        juego["turno"] = "Abuelita" if juego["turno"] == "Tutu" else "Tutu"

# --- Interfaz del Tablero ---
st.title("🕹️ Timbiriche: Tutu vs Abuelita")
st.sidebar.header(f"Turno de: {juego['turno']}")
st.sidebar.metric("🔵 Puntos Tutu", juego["puntos"]["Tutu"])
st.sidebar.metric("🔴 Puntos Abuelita", juego["puntos"]["Abuelita"])

for r in range(5):
    cols = st.columns([1, 4, 1, 4, 1, 4, 1, 4, 1])
    for c in range(4):
        cols[c*2].markdown("<div class='punto'>●</div>", unsafe_allow_html=True)
        if juego["lineas_h"][r, c]:
            cols[c*2+1].markdown("<div class='linea-h-llena'></div>", unsafe_allow_html=True)
        else:
            if cols[c*2+1].button(" ", key=f"h_{r}_{c}"):
                registrar_movimiento('h', r, c)
                st.rerun()
    cols[8].markdown("<div class='punto'>●</div>", unsafe_allow_html=True)

    if r < 4:
        cols_v = st.columns([1, 4, 1, 4, 1, 4, 1, 4, 1])
        for c in range(5):
            if juego["lineas_v"][r, c]:
                cols_v[c*2].markdown("<div class='linea-v-llena'></div>", unsafe_allow_html=True)
            else:
                if cols_v[c*2].button(" ", key=f"v_{r}_{c}"):
                    registrar_movimiento('v', r, c)
                    st.rerun()
            if c < 4 and (r, c) in juego["cuadros"]:
                owner = juego["cuadros"][(r, c)]
                clase = "cuadro-tutu" if owner == "Tutu" else "cuadro-abuelita"
                label = "T" if owner == "Tutu" else "A"
                cols_v[c*2+1].markdown(f"<div class={clase}>{label}</div>", unsafe_allow_html=True)

if st.sidebar.button("Reiniciar Juego para Todos"):
    juego["puntos"] = {"Tutu": 0, "Abuelita": 0}
    juego["turno"] = "Tutu"
    juego["lineas_h"].fill(False)
    juego["lineas_v"].fill(False)
    juego["cuadros"].clear()
    st.rerun()
