import streamlit as st
import numpy as np
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="Timbiriche: Tutu vs Abuelita", layout="centered")

# Auto-refresco
st_autorefresh(interval=5000, key="datarefresh")

# --- CSS CORREGIDO PARA ALINEACIÓN ---
st.markdown("""
<style>
/* Menos separación entre columnas */
div[data-testid="stHorizontalBlock"] {
    gap: 0.25rem !important;
}

/* Evitar márgenes raros de markdown */
.element-container {
    margin-top: 0rem !important;
    margin-bottom: 0rem !important;
}

/* Botones de líneas vacías */
.stButton > button {
    width: 100% !important;
    height: 50px !important;
    min-height: 50px !important;
    background-color: transparent !important;
    border: none !important;
    padding: 0 !important;
    margin: 0 !important;
    box-shadow: none !important;
}

/* Punto */
.punto {
    display: flex;
    align-items: center;
    justify-content: center;
    height: 26px;
    font-size: 22px;
    color: white;
    margin: 0;
    padding: 0;
}

/* Línea horizontal */
.linea-h-llena {
    height: 50px;
    display: flex;
    align-items: center;
    justify-content: center;
    margin: 0;
    padding: 0;
}
.linea-h-llena::before {
    content: "";
    display: block;
    width: 100%;
    border-top: 6px solid #C8C8C8;
}

/* Línea vertical */
.linea-v-llena {
    width: 100%;
    height: 50px;
    display: flex;
    align-items: center;
    justify-content: center;
    margin: 0;
    padding: 0;
}
.linea-v-llena::before {
    content: "";
    display: block;
    height: 100%;
    border-left: 6px solid #C8C8C8;
}

/* Cuadros */
.cuadro-tutu, .cuadro-abuelita {
    display: flex;
    align-items: center;
    justify-content: center;
    height: 50px;
    width: 100%;
    border-radius: 6px;
    font-size: 20px;
    font-weight: bold;
    color: white;
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

.cuadro-tutu {
    background-color: #5A4FCF;   /* azul morado */
}

.cuadro-abuelita {
    background-color: #7A2E10;
}
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
        "cuadros": {}
    }

juego = obtener_juego_compartido()

# --- GLOBOS ---
if "ultimo_conteo" not in st.session_state:
    st.session_state.ultimo_conteo = 0

if len(juego["cuadros"]) > st.session_state.ultimo_conteo:
    st.balloons()
    st.session_state.ultimo_conteo = len(juego["cuadros"])

def registrar(tipo, r, c):
    if tipo == "h":
        juego["lineas_h"][r, c] = True
    else:
        juego["lineas_v"][r, c] = True

    h, v = juego["lineas_h"], juego["lineas_v"]
    formo = False

    for row in range(4):
        for col in range(4):
            if (row, col) not in juego["cuadros"]:
                if h[row, col] and h[row + 1, col] and v[row, col] and v[row, col + 1]:
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
    cols = st.columns([0.6, 3, 0.6, 3, 0.6, 3, 0.6, 3, 0.6])

    for c in range(4):
        cols[c * 2].markdown("<div class='punto'>●</div>", unsafe_allow_html=True)

        if juego["lineas_h"][r, c]:
            cols[c * 2 + 1].markdown("<div class='linea-h-llena'></div>", unsafe_allow_html=True)
        else:
            if cols[c * 2 + 1].button(" ", key=f"h{r}{c}"):
                registrar("h", r, c)
                st.rerun()

    cols[8].markdown("<div class='punto'>●</div>", unsafe_allow_html=True)

    if r < 4:
        cols_v = st.columns([0.6, 3, 0.6, 3, 0.6, 3, 0.6, 3, 0.6])

        for c in range(5):
            if juego["lineas_v"][r, c]:
                cols_v[c * 2].markdown("<div class='linea-v-llena'></div>", unsafe_allow_html=True)
            else:
                if cols_v[c * 2].button(" ", key=f"v{r}{c}"):
                    registrar("v", r, c)
                    st.rerun()

            if c < 4:
                if (r, c) in juego["cuadros"]:
                    own = juego["cuadros"][(r, c)]
                    clase = "cuadro-tutu" if own == "Tutu" else "cuadro-abuelita"
                    cols_v[c * 2 + 1].markdown(
                        f"<div class='{clase}'>{own[0]}</div>",
                        unsafe_allow_html=True
                    )
                else:
                    cols_v[c * 2 + 1].markdown("<div style='height:50px;'></div>", unsafe_allow_html=True)

if st.sidebar.button("Reiniciar Juego"):
    juego["puntos"] = {"Tutu": 0, "Abuelita": 0}
    juego["turno"] = "Tutu"
    juego["lineas_h"].fill(False)
    juego["lineas_v"].fill(False)
    juego["cuadros"].clear()
    st.session_state.ultimo_conteo = 0
    st.rerun()
