import streamlit as st
import numpy as np

st.set_page_config(page_title="Timbiriche: Tutu vs Abuelita", layout="centered")

# --- CSS RADICAL PARA FIJAR POSICIONES ---
st.markdown("""
    <style>
    /* Centrar todo el tablero */
    .tablero-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        background-color: #0E1117;
        padding: 20px;
        border-radius: 10px;
    }
    /* Estilo de los botones para que no tengan margen */
    .stButton > button {
        width: 100% !important;
        height: 100% !important;
        padding: 0px !important;
        margin: 0px !important;
        min-height: 25px !important;
        background-color: #262730;
        border: 1px solid #444;
    }
    .punto { font-size: 24px; color: white; text-align: center; line-height: 25px; }
    
    /* Líneas horizontales llenas */
    .linea-h-llena { border-bottom: 5px solid #AAAAAA; width: 100%; height: 12px; }
    /* Líneas verticales llenas */
    .linea-v-llena { border-left: 5px solid #AAAAAA; height: 100%; width: 5px; margin: auto; }
    
    /* Cuadros llenos */
    .cuadro-tutu { background-color: #005A87; width: 100%; height: 100%; display: flex; align-items: center; justify-content: center; font-weight: bold; border-radius: 4px; color: white; }
    .cuadro-abuelita { background-color: #7A2E16; width: 100%; height: 100%; display: flex; align-items: center; justify-content: center; font-weight: bold; border-radius: 4px; color: white; }
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
st.sidebar.metric("🔵 Tutu", st.session_state.puntos["Tutu"])
st.sidebar.metric("🔴 Abuelita", st.session_state.puntos["Abuelita"])

# Contenedor principal
with st.container():
    for r in range(5):
        # Fila horizontal: Punto - Línea - Punto
        # Ajustamos los anchos para que sean proporcionales
        cols = st.columns([1, 3, 1, 3, 1, 3, 1, 3, 1], gap="small")
        for c in range(4):
            cols[c*2].markdown("<div class='punto'>●</div>", unsafe_allow_html=True)
            if st.session_state.lineas_h[r, c]:
                cols[c*2+1].markdown("<div class='linea-h-llena'></div>", unsafe_allow_html=True)
            else:
                if cols[c*2+1].button(" ", key=f"h{r}{c}"):
                    registrar('h', r, c)
                    st.rerun()
        cols[8].markdown("<div class='punto'>●</div>", unsafe_allow_html=True)

        # Fila vertical: Línea - Cuadro - Línea
        if r < 4:
            cols_v = st.columns([1, 3, 1, 3, 1, 3, 1, 3, 1], gap="small")
            for c in range(5):
                if st.session_state.lineas_v[r, c]:
                    cols_v[c*2].markdown("<div class='linea-v-llena'></div>", unsafe_allow_html=True)
                else:
                    if cols_v[c*2].button(" ", key=f"v{r}{c}"):
                        registrar('v', r, c)
                        st.rerun()
                
                # Cuadro Central
                if c < 4 and (r, c) in st.session_state.cuadros:
                    own = st.session_state.cuadros[(r, c)]
                    clase = "cuadro-tutu" if own == "Tutu" else "cuadro-abuelita"
                    cols_v[c*2+1].markdown(f"<div class='{clase}'>{own[0]}</div>", unsafe_allow_html=True)

if st.sidebar.button("Reiniciar"):
    st.session_state.clear()
    st.rerun()
