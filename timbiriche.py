import streamlit as st
import numpy as np

st.set_page_config(page_title="Timbiriche: Tutu vs Abuelita", layout="centered")

# --- CSS PARA ARREGLAR EL DECALAJE ---
st.markdown("""
    <style>
    .timbiriche-container {
        display: grid;
        grid-template-columns: repeat(4, 30px 60px) 30px;
        align-items: center;
        justify-content: center;
        gap: 0px;
        margin: auto;
    }
    .punto { font-size: 24px; text-align: center; color: white; width: 30px; height: 30px; line-height: 30px; }
    
    /* Botones invisibles para las líneas */
    .stButton > button {
        padding: 0px !important;
        background-color: #262730;
        border: 1px solid #444;
        border-radius: 4px;
    }
    
    /* Líneas llenas */
    .linea-h-llena { border-bottom: 6px solid #AAAAAA; width: 50px; margin: auto; }
    .linea-v-llena { border-left: 6px solid #AAAAAA; height: 50px; margin: auto; }
    
    /* Cuadros con iniciales */
    .cuadro-t { background-color: #005A87; height: 50px; display: flex; align-items: center; justify-content: center; border-radius: 4px; font-weight: bold; }
    .cuadro-a { background-color: #7A2E16; height: 50px; display: flex; align-items: center; justify-content: center; border-radius: 4px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

if 'puntos' not in st.session_state:
    st.session_state.puntos = {"Tutu": 0, "Abuelita": 0}
    st.session_state.turno = "Tutu"
    st.session_state.lineas_h = np.zeros((5, 4), dtype=bool)
    st.session_state.lineas_v = np.zeros((4, 5), dtype=bool)
    st.session_state.cuadros = {}
    st.session_state.lanzar_globos = False

if st.session_state.lanzar_globos:
    st.balloons()
    st.session_state.lanzar_globos = False

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
                    st.session_state.lanzar_globos = True
    if not formo:
        st.session_state.turno = "Abuelita" if st.session_state.turno == "Tutu" else "Tutu"

# --- INTERFAZ ---
st.title("🕹️ Timbiriche: Tutu vs Abuelita")
st.sidebar.header(f"Turno de: {st.session_state.turno}")
st.sidebar.metric("🔵 Puntos Tutu", st.session_state.puntos["Tutu"])
st.sidebar.metric("🔴 Puntos Abuelita", st.session_state.puntos["Abuelita"])

# Dibujamos usando un contenedor manual para que no se mueva
for r in range(5):
    # Fila Horizontal
    cols = st.columns([1, 2, 1, 2, 1, 2, 1, 2, 1])
    for c in range(4):
        cols[c*2].markdown("<div class='punto'>●</div>", unsafe_allow_html=True)
        if st.session_state.lineas_h[r, c]:
            cols[c*2+1].markdown("<div class='linea-h-llena'></div>", unsafe_allow_html=True)
        else:
            if cols[c*2+1].button(" ", key=f"h{r}{c}"):
                registrar('h', r, c)
                st.rerun()
    cols[8].markdown("<div class='punto'>●</div>", unsafe_allow_html=True)

    # Fila Vertical y Cuadros
    if r < 4:
        cols_v = st.columns([1, 2, 1, 2, 1, 2, 1, 2, 1])
        for c in range(5):
            if st.session_state.lineas_v[r, c]:
                cols_v[c*2].markdown("<div class='linea-v-llena'></div>", unsafe_allow_html=True)
            else:
                if cols_v[c*2].button(" ", key=f"v{r}{c}"):
                    registrar('v', r, c)
                    st.rerun()
            if c < 4 and (r, c) in st.session_state.cuadros:
                own = st.session_state.cuadros[(r, c)]
                clase = "cuadro-t" if own == "Tutu" else "cuadro-a"
                label = "T" if own == "Tutu" else "A"
                cols_v[c*2+1].markdown(f"<div class='{clase}'>{label}</div>", unsafe_allow_html=True)

if st.sidebar.button("Reiniciar"):
    st.session_state.clear()
    st.rerun()
