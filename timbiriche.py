import streamlit as st
import numpy as np

st.set_page_config(page_title="Timbiriche: Tutu vs Abuelita", layout="centered")

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

if 'puntos' not in st.session_state:
    st.session_state.puntos = {"Tutu": 0, "Abuelita": 0}
    st.session_state.turno = "Tutu"
    st.session_state.lineas_h = np.zeros((5, 4), dtype=bool)
    st.session_state.lineas_v = np.zeros((4, 5), dtype=bool)
    st.session_state.cuadros = {}
    st.session_state.lanzar_globos = False # Nueva memoria para globos

# SI HAY GLOBOS PENDIENTES, LOS LANZAMOS AHORA
if st.session_state.lanzar_globos:
    st.balloons()
    st.session_state.lanzar_globos = False

def registrar_movimiento(tipo, r, c):
    if tipo == 'h': st.session_state.lineas_h[r, c] = True
    else: st.session_state.lineas_v[r, c] = True
    
    h, v = st.session_state.lineas_h, st.session_state.lineas_v
    formo_cuadro = False
    for row in range(4):
        for col in range(4):
            if (row, col) not in st.session_state.cuadros:
                if h[row, col] and h[row+1, col] and v[row, col] and v[row, col+1]:
                    st.session_state.cuadros[(row, col)] = st.session_state.turno
                    st.session_state.puntos[st.session_state.turno] += 1
                    formo_cuadro = True
                    st.session_state.lanzar_globos = True # Marcamos que ganaste globos
    
    if not formo_cuadro:
        st.session_state.turno = "Abuelita" if st.session_state.turno == "Tutu" else "Tutu"

# --- Interfaz del Tablero ---
st.title("🕹️ Timbiriche: Tutu vs Abuelita")
st.sidebar.header(f"Turno de: {st.session_state.turno}")
st.sidebar.metric("🔵 Puntos Tutu", st.session_state.puntos["Tutu"])
st.sidebar.metric("🔴 Puntos Abuelita", st.session_state.puntos["Abuelita"])

for r in range(5):
    cols = st.columns([1, 4, 1, 4, 1, 4, 1, 4, 1])
    for c in range(4):
        cols[c*2].markdown("<div class='punto'>●</div>", unsafe_allow_html=True)
        if st.session_state.lineas_h[r, c]:
            cols[c*2+1].markdown("<div class='linea-h-llena'></div>", unsafe_allow_html=True)
        else:
            if cols[c*2+1].button(" ", key=f"h_{r}_{c}"):
                registrar_movimiento('h', r, c)
                st.rerun()
    cols[8].markdown("<div class='punto'>●</div>", unsafe_allow_html=True)

    if r < 4:
        cols_v = st.columns([1, 4, 1, 4, 1, 4, 1, 4, 1])
        for c in range(5):
            if st.session_state.lineas_v[r, c]:
                cols_v[c*2].markdown("<div class='linea-v-llena'></div>", unsafe_allow_html=True)
            else:
                if cols_v[c*2].button(" ", key=f"v_{r}_{c}"):
                    registrar_movimiento('v', r, c)
                    st.rerun()
            if c < 4 and (r, c) in st.session_state.cuadros:
                owner = st.session_state.cuadros[(r, c)]
                clase = "cuadro-tutu" if owner == "Tutu" else "cuadro-abuelita"
                label = "T" if owner == "Tutu" else "A"
                cols_v[c*2+1].markdown(f"<div class={clase}>{label}</div>", unsafe_allow_html=True)

if st.sidebar.button("Reiniciar Juego"):
    st.session_state.clear()
    st.rerun()
