import streamlit as st
import numpy as np

st.set_page_config(page_title="Timbiriche: Tutu vs Abuelita")
st.title("🕹️ Timbiriche: Tutu vs Abuelita")

# 1. Inicializar el estado del juego
if 'puntos' not in st.session_state:
    st.session_state.puntos = {"Tutu": 0, "Abuelita": 0}
    st.session_state.turno = "Tutu"
    st.session_state.lineas_h = np.zeros((5, 4), dtype=bool)
    st.session_state.lineas_v = np.zeros((4, 5), dtype=bool)
    st.session_state.cuadros = {}

def registrar_movimiento(tipo, r, c):
    if tipo == 'h':
        st.session_state.lineas_h[r, c] = True
    else:
        st.session_state.lineas_v[r, c] = True
    
    # Si forma un cuadrado, se anota y sigue jugando (turno extra)
    formo_cuadro = False
    h = st.session_state.lineas_h
    v = st.session_state.lineas_v
    for row in range(4):
        for col in range(4):
            if (row, col) not in st.session_state.cuadros:
                if h[row, col] and h[row+1, col] and v[row, col] and v[row, col+1]:
                    st.session_state.cuadros[(row, col)] = st.session_state.turno
                    st.session_state.puntos[st.session_state.turno] += 1
                    formo_cuadro = True
    
    if not formo_cuadro:
        st.session_state.turno = "Abuelita" if st.session_state.turno == "Tutu" else "Tutu"

# 2. Interfaz Visual (La versión que funcionaba bien)
st.write(f"### Turno de: **{st.session_state.turno}**")
st.sidebar.metric("Puntos Tutu", st.session_state.puntos["Tutu"])
st.sidebar.metric("Puntos Abuelita", st.session_state.puntos["Abuelita"])

# Dibujar el tablero con botones simples
for r in range(5):
    # Fila de puntos y líneas horizontales
    cols = st.columns(9) 
    for c in range(4):
        cols[c*2].write("●") 
        if st.session_state.lineas_h[r, c]:
            cols[c*2+1].write("—")
        else:
            if cols[c*2+1].button(" ", key=f"h_{r}_{c}"):
                registrar_movimiento('h', r, c)
                st.rerun()
    cols[8].write("●")

    # Fila de líneas verticales y centros de cuadros
    if r < 4:
        cols_v = st.columns(9)
        for c in range(5):
            if st.session_state.lineas_v[r, c]:
                cols_v[c*2].write("|")
            else:
                if cols_v[c*2].button(" ", key=f"v_{r}_{c}"):
                    registrar_movimiento('v', r, c)
                    st.rerun()
            
            # Dibujar inicial si el cuadro está completo
            if c < 4:
                if (r, c) in st.session_state.cuadros:
                    owner = st.session_state.cuadros[(r, c)]
                    label = "T" if owner == "Tutu" else "A"
                    cols_v[c*2+1].write(f"**{label}**")

if st.sidebar.button("Reiniciar Juego"):
    st.session_state.clear()
    st.rerun()
