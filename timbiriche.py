import streamlit as st
import numpy as np
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="Timbiriche: Tutu vs Abuelita", layout="wide")

# Auto-refresco un poco más lento para no interferir tanto con efectos
st_autorefresh(interval=8000, key="datarefresh")

# --- CSS ---
st.markdown("""
<style>
/* Fondo general */
.stApp {
    background: linear-gradient(90deg, #050b18 0%, #020814 100%);
}

/* Menos espacio entre columnas */
div[data-testid="stHorizontalBlock"] {
    gap: 0.25rem !important;
}

/* Quitar márgenes extras de los bloques */
.element-container {
    margin-top: 0rem !important;
    margin-bottom: 0rem !important;
}

/* Botones invisibles pero clicables */
.stButton > button {
    width: 100% !important;
    height: 50px !important;
    min-height: 50px !important;
    background-color: transparent !important;
    border: none !important;
    padding: 0 !important;
    margin: 0 !important;
    box-shadow: none !important;
    cursor: pointer !important;
    border-radius: 6px !important;
}

/* Resaltar zona clicable */
.stButton > button:hover {
    cursor: pointer !important;
    background-color: rgba(255,255,255,0.06) !important;
    border-radius: 6px !important;
}

/* Título principal */
h1 {
    text-align: center;
    color: white !important;
    font-size: 3rem !important;
    margin-bottom: 1rem !important;
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

/* Línea horizontal llena */
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
    border-top: 6px solid #CFCFCF;
}

/* Línea vertical llena */
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
    border-left: 6px solid #CFCFCF;
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
    background-color: #5A4FCF;
}

.cuadro-abuelita {
    background-color: #8A320D;
}

/* Mensaje final */
.mensaje-final {
    text-align: center;
    font-size: 42px;
    font-weight: bold;
    margin: 18px 0 20px 0;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background-color: rgba(255,255,255,0.03);
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

# --- SESSION STATE ---
TOTAL_CUADROS = 16

if "ultimo_conteo" not in st.session_state:
    st.session_state.ultimo_conteo = 0

if "globos_pendientes" not in st.session_state:
    st.session_state.globos_pendientes = 0

if "fin_festejado" not in st.session_state:
    st.session_state.fin_festejado = False

# --- LÓGICA ---
def registrar(tipo, r, c):
    if tipo == "h":
        juego["lineas_h"][r, c] = True
    else:
        juego["lineas_v"][r, c] = True

    h, v = juego["lineas_h"], juego["lineas_v"]
    formo = False
    cuadros_nuevos = 0

    for row in range(4):
        for col in range(4):
            if (row, col) not in juego["cuadros"]:
                if h[row, col] and h[row + 1, col] and v[row, col] and v[row, col + 1]:
                    juego["cuadros"][(row, col)] = juego["turno"]
                    juego["puntos"][juego["turno"]] += 1
                    formo = True
                    cuadros_nuevos += 1

    if cuadros_nuevos > 0:
        st.session_state.globos_pendientes += cuadros_nuevos

    if not formo:
        juego["turno"] = "Abuelita" if juego["turno"] == "Tutu" else "Tutu"

# --- GLOBOS ESTABLES ---
conteo_actual = len(juego["cuadros"])

if conteo_actual > st.session_state.ultimo_conteo:
    nuevos = conteo_actual - st.session_state.ultimo_conteo
    st.session_state.globos_pendientes += max(0, nuevos - st.session_state.globos_pendientes)
    st.session_state.ultimo_conteo = conteo_actual

if st.session_state.globos_pendientes > 0:
    st.balloons()
    st.session_state.globos_pendientes -= 1

# --- FIN DEL JUEGO ---
fin_del_juego = len(juego["cuadros"]) == TOTAL_CUADROS

ganador = None
if fin_del_juego:
    puntos_tutu = juego["puntos"]["Tutu"]
    puntos_abuelita = juego["puntos"]["Abuelita"]

    if puntos_tutu > puntos_abuelita:
        ganador = "Tutu"
    elif puntos_abuelita > puntos_tutu:
        ganador = "Abuelita"
    else:
        ganador = "Empate"

if fin_del_juego and not st.session_state.fin_festejado:
    st.snow()
    st.session_state.fin_festejado = True

# --- SIDEBAR ---
st.sidebar.write(f"## Turno de: {juego['turno']}")
st.sidebar.metric("🔵 Tutu", juego["puntos"]["Tutu"])
st.sidebar.metric("🔴 Abuelita", juego["puntos"]["Abuelita"])

if st.sidebar.button("Reiniciar Juego"):
    juego["puntos"] = {"Tutu": 0, "Abuelita": 0}
    juego["turno"] = "Tutu"
    juego["lineas_h"].fill(False)
    juego["lineas_v"].fill(False)
    juego["cuadros"].clear()

    st.session_state.ultimo_conteo = 0
    st.session_state.globos_pendientes = 0
    st.session_state.fin_festejado = False

    st.rerun()

# --- TÍTULO ---
st.title("🕹️ Timbiriche: Tutu vs Abuelita")

# --- MENSAJE FINAL ---
if fin_del_juego:
    if ganador == "Empate":
        st.markdown("""
        <div class="mensaje-final" style="color:#FFD700;">
            ⭐ ¡Empate! ⭐
        </div>
        """, unsafe_allow_html=True)
    else:
        color_ganador = "#5A4FCF" if ganador == "Tutu" else "#A1400F"
        st.markdown(f"""
        <div class="mensaje-final" style="color:{color_ganador};">
            ⭐ ¡Ganó {ganador}! ⭐
        </div>
        """, unsafe_allow_html=True)

# --- TABLERO ---
for r in range(5):
    cols = st.columns([0.6, 3, 0.6, 3, 0.6, 3, 0.6, 3, 0.6])

    for c in range(4):
        cols[c * 2].markdown("<div class='punto'>●</div>", unsafe_allow_html=True)

        if juego["lineas_h"][r, c]:
            cols[c * 2 + 1].markdown("<div class='linea-h-llena'></div>", unsafe_allow_html=True)
        else:
            if not fin_del_juego:
                if cols[c * 2 + 1].button(" ", key=f"h{r}{c}"):
                    registrar("h", r, c)
                    st.rerun()
            else:
                cols[c * 2 + 1].markdown("<div style='height:50px;'></div>", unsafe_allow_html=True)

    cols[8].markdown("<div class='punto'>●</div>", unsafe_allow_html=True)

    if r < 4:
        cols_v = st.columns([0.6, 3, 0.6, 3, 0.6, 3, 0.6, 3, 0.6])

        for c in range(5):
            if juego["lineas_v"][r, c]:
                cols_v[c * 2].markdown("<div class='linea-v-llena'></div>", unsafe_allow_html=True)
            else:
                if not fin_del_juego:
                    if cols_v[c * 2].button(" ", key=f"v{r}{c}"):
                        registrar("v", r, c)
                        st.rerun()
                else:
                    cols_v[c * 2].markdown("<div style='height:50px;'></div>", unsafe_allow_html=True)

            if c < 4:
                if (r, c) in juego["cuadros"]:
                    own = juego["cuadros"][(r, c)]
                    clase = "cuadro-tutu" if own == "Tutu" else "cuadro-abuelita"
                    cols_v[c * 2 + 1].markdown(
                        f"<div class='{clase}'>{own[0]}</div>",
                        unsafe_allow_html=True
                    )
                else:
                    cols_v[c * 2 + 1].markdown(
                        "<div style='height:50px;'></div>",
                        unsafe_allow_html=True
                    )
