import streamlit as st
import numpy as np

st.set_page_config(page_title="Timbiriche: Tutu vs Abuelita", layout="centered")

# --- CSS PARA FORZAR LA CUADRÍCULA ---
st.markdown("""
    <style>
    .timbiriche-table { border-collapse: collapse; margin: auto; }
    .punto { font-size: 24px; color: white; width: 20px; height: 20px; text-align: center; line-height: 20px; }
    
    /* Botones de línea */
    .stButton > button {
        width: 100% !important; height: 30px !important;
        padding: 0px !important; background-color: #262730; border: 1px solid #444;
    }
    
    /* Líneas horizontales */
    .linea-h-llena { border-bottom: 6px solid #AAAAAA; width: 60px; height: 15px; }
    /* Líneas verticales */
    .linea-v-llena { border-left: 6px solid #AAAAAA; height: 60px; margin: auto; width: 6px; }
    
    /* Cuadros ganados */
    .cuadro-tutu { background-color: #005A87; width: 60px; height: 60px; display: flex; align-items: center; justify-content: center; font-weight: bold; border-radius: 4px; color: white; }
    .cuadro-abuelita { background-color: #7A2E16; width: 60px; height: 60px; display: flex; align-items: center; justify-content: center; font-weight: bold; border-radius: 4px; color: white; }
    </style>
    """, unsafe_allow_html=True)

if 'puntos' not in st.session_state:
    st.session_state.puntos = {"Tutu": 0, "Abuelita": 0}
    st.session_state.turno = "Tutu"
    st.session_state.lineas_h = np.zeros((5, 4), dtype=bool)
    st.session_state.lineas_v = np.zeros((4, 5), dtype=bool)
    st.session_state.cuadros = {}
    st.session_state.globos = False

if st.session_state.globos:
    st.balloons()
    st.session_state.globos = False

def registrar(tipo, r, c):
    if tipo == 'h': st.session_state.lineas_h[r, c] = True
    else: st.session_state.lineas_v[r, c] = True
    h, v = st.session_state.lineas_h, st.session_state.lineas_v
    formo = False
    for row in range(4):
        for col in range(4):
            if (row, col) not in st.session_state.cuadros:
                if h[row, col] and h[row+1, col] and v[row, col] and v[row, col+1]:
                    st.session_state.cuadros[(row, col)] = st.session_state.turno
                    st.session_state.puntos[st.session_state.turno] += 1
                    formo = True
                    st.session_state.globos = True
    if not formo:
        st.session_state.turno = "Abuelita" if st.session_state.turno == "Tutu" else "Tutu"

# --- INTERFAZ ---
st.title("🕹️ Timbiriche: Tutu vs Abuelita")
st.sidebar.header(f"Turno de: {st.session_state.turno}")
st.sidebar.metric("🔵 Puntos Tutu", st.session_state.puntos["Tutu"])
st.sidebar.metric("🔴 Puntos Abuelita", st.session_state.puntos["Abuelita"])

# Dibujamos usando columnas pero con anchos fijos que NO se desajusten
for r in range(5):
    # Fila horizontal
    row_cols = st.columns([1, 3, 1, 3, 1, 3, 1, 3, 1])
    for c in range(4):
        row_cols[c*2].markdown("<div class='punto'>●</div>", unsafe_allow_html=True)
        if st.session_state.lineas_h[r, c]:
            row_cols[c*2+1].markdown("<div class='linea-h-llena'></div>", unsafe_allow_html=True)
        else:
            if row_cols[c*2+1].button(" ", key=f"h{r}{c}"):
                registrar('h', r, c)
                st.rerun()
    row_cols[8].markdown("<div class='punto'>●</div>", unsafe_allow_html=True)

    # Fila vertical y Cuadros
    if r < 4:
        row_cols_v = st.columns([1, 3, 1, 3, 1, 3, 1, 3, 1])
        for c in range(5):
            if st.session_state.lineas_v[r, c]:
                row_cols_v[c*2].markdown("<div class='linea-v-llena'></div>", unsafe_allow_html=True)
            else:
                if row_cols_v[c*2].button(" ", key=f"v{r}{c}"):
                    registrar('v', r, c)
                    st.rerun()
            if c < 4 and (r, c) in st.session_state.cuadros:
                own = st.session_state.cuadros[(r, c)]
                clase = "cuadro-tutu" if own == "Tutu" else "cuadro-abuelita"
                label = "T" if own == "Tutu" else "A"
                row_cols_v[c*2+1].markdown(f"<div class='{clase}'>{label}</div>", unsafe_allow_html=True)

if st.sidebar.button("Reiniciar"):
    st.session_state.clear()
    st.rerun()
