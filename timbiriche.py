import streamlit as st
import numpy as np
import random
import math
import wave
import struct
import io
import base64
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="Timbiriche: Tutu vs Abuelita", layout="wide")

# Refresco suave
st_autorefresh(interval=8000, key="datarefresh")

# -------------------- CSS --------------------
st.markdown("""
<style>
.stApp {
    background: radial-gradient(circle at top, #07152b 0%, #020814 60%, #01040d 100%);
}

div[data-testid="stHorizontalBlock"] {
    gap: 0.25rem !important;
}

.element-container {
    margin-top: 0rem !important;
    margin-bottom: 0rem !important;
}

section[data-testid="stSidebar"] {
    background: rgba(255,255,255,0.04);
    border-right: 1px solid rgba(255,255,255,0.06);
}

div[data-testid="stButton"] {
    margin: 0 !important;
    padding: 0 !important;
    background: transparent !important;
    box-shadow: none !important;
    border: none !important;
}

div[data-testid="stButton"] > button {
    width: 100% !important;
    height: 50px !important;
    min-height: 50px !important;
    display: block !important;
    background: transparent !important;
    background-color: transparent !important;
    border: none !important;
    outline: none !important;
    padding: 0 !important;
    margin: 0 !important;
    box-shadow: none !important;
    cursor: pointer !important;
    border-radius: 8px !important;
    appearance: none !important;
    -webkit-appearance: none !important;
    color: transparent !important;
    transition: background-color 0.12s ease !important;
}

div[data-testid="stButton"] > button p {
    color: transparent !important;
    margin: 0 !important;
    padding: 0 !important;
    line-height: 0 !important;
    font-size: 0 !important;
}

div[data-testid="stButton"] > button:hover {
    background: rgba(255,255,255,0.06) !important;
    box-shadow: none !important;
    outline: none !important;
    border: none !important;
    cursor: pointer !important;
}

div[data-testid="stButton"] > button:focus,
div[data-testid="stButton"] > button:focus-visible,
div[data-testid="stButton"] > button:active {
    background: rgba(255,255,255,0.04) !important;
    box-shadow: none !important;
    outline: none !important;
    border: none !important;
}

h1 {
    text-align: center;
    color: white !important;
    font-size: 3rem !important;
    margin-bottom: 0.5rem !important;
}

.mensaje-final {
    text-align: center;
    font-size: 44px;
    font-weight: 800;
    margin: 10px 0 18px 0;
    text-shadow: 0 0 12px rgba(255,255,255,0.15);
}

.corona {
    font-size: 48px;
    margin-right: 8px;
}

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
    border-top: 6px solid #D8D8D8;
    border-radius: 10px;
    box-shadow: 0 0 4px rgba(255,255,255,0.10);
}

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
    border-left: 6px solid #D8D8D8;
    border-radius: 10px;
    box-shadow: 0 0 4px rgba(255,255,255,0.10);
}

.cuadro-tutu, .cuadro-abuelita {
    display: flex;
    align-items: center;
    justify-content: center;
    height: 50px;
    width: 100%;
    border-radius: 8px;
    font-size: 20px;
    font-weight: bold;
    color: white;
    margin: 0;
    padding: 0;
    box-sizing: border-box;
    letter-spacing: 1px;
}

.cuadro-tutu {
    background: linear-gradient(135deg, #6A4CFF 0%, #4F46D7 100%);
    box-shadow: 0 0 14px rgba(106,76,255,0.28);
}

.cuadro-abuelita {
    background: linear-gradient(135deg, #9A3D10 0%, #7A2E10 100%);
    box-shadow: 0 0 14px rgba(154,61,16,0.22);
}

.fx-layer {
    position: fixed;
    inset: 0;
    pointer-events: none;
    overflow: hidden;
    z-index: 9999;
}

.fx-item {
    position: absolute;
    top: -8vh;
    animation-name: caer;
    animation-timing-function: linear;
    animation-iteration-count: infinite;
    opacity: 0.95;
}

@keyframes caer {
    0% {
        transform: translateY(-10vh) rotate(0deg) scale(0.9);
        opacity: 0;
    }
    10% {
        opacity: 1;
    }
    100% {
        transform: translateY(115vh) rotate(360deg) scale(1.1);
        opacity: 0;
    }
}
</style>
""", unsafe_allow_html=True)

# -------------------- AUDIO --------------------
def crear_tono_wav_base64(frecuencias, duracion=0.22, volumen=0.35, sample_rate=22050):
    if isinstance(frecuencias, (int, float)):
        frecuencias = [frecuencias]

    n_samples = int(sample_rate * duracion)
    buffer = io.BytesIO()

    with wave.open(buffer, "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)

        for i in range(n_samples):
            t = i / sample_rate
            value = 0.0

            for f in frecuencias:
                value += math.sin(2 * math.pi * f * t)

            value /= max(len(frecuencias), 1)

            fade = int(0.02 * sample_rate)
            env = 1.0
            if i < fade:
                env = i / max(fade, 1)
            elif i > n_samples - fade:
                env = max((n_samples - i) / max(fade, 1), 0)

            sample = int(32767 * volumen * env * value)
            wav_file.writeframes(struct.pack("<h", sample))

    return base64.b64encode(buffer.getvalue()).decode("utf-8")


SONIDO_CUADRO = crear_tono_wav_base64([660, 880], duracion=0.18, volumen=0.30)
SONIDO_VICTORIA = crear_tono_wav_base64([523, 659, 784], duracion=0.55, volumen=0.34)


def reproducir_sonido(base64_audio, autoplay=True):
    auto = "autoplay" if autoplay else ""
    st.markdown(
        f"""
        <audio {auto} style="display:none;">
            <source src="data:audio/wav;base64,{base64_audio}" type="audio/wav">
        </audio>
        """,
        unsafe_allow_html=True
    )

# -------------------- MEMORIA DEL JUEGO --------------------
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

# -------------------- SESSION STATE --------------------
TOTAL_CUADROS = 16

if "ultimo_conteo" not in st.session_state:
    st.session_state.ultimo_conteo = 0

if "globos_pendientes" not in st.session_state:
    st.session_state.globos_pendientes = 0

if "fin_festejado" not in st.session_state:
    st.session_state.fin_festejado = False

if "fx_html" not in st.session_state:
    st.session_state.fx_html = ""

if "sonido_cuadro_pendiente" not in st.session_state:
    st.session_state.sonido_cuadro_pendiente = 0

if "sonido_victoria_pendiente" not in st.session_state:
    st.session_state.sonido_victoria_pendiente = False

# -------------------- EFECTOS FINALES --------------------
def crear_fx_html(cantidad=36):
    simbolos = ["⭐", "✨", "🌟", "🎉", "💜", "🎊"]
    piezas = ['<div class="fx-layer">']

    for _ in range(cantidad):
        left = random.randint(0, 96)
        delay = round(random.uniform(0, 2.5), 2)
        dur = round(random.uniform(3.5, 6.5), 2)
        size = random.randint(20, 38)
        simb = random.choice(simbolos)

        piezas.append(f'''
<div class="fx-item"
style="
left:{left}%;
animation-delay:{delay}s;
animation-duration:{dur}s;
font-size:{size}px;
">
{simb}
</div>
''')

    piezas.append("</div>")
    return "\n".join(piezas)

# -------------------- LÓGICA DEL JUEGO --------------------
def registrar(tipo, r, c):
    if tipo == "h":
        juego["lineas_h"][r, c] = True
    else:
        juego["lineas_v"][r, c] = True

    h = juego["lineas_h"]
    v = juego["lineas_v"]
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
        st.session_state.sonido_cuadro_pendiente += cuadros_nuevos

    if not formo:
        juego["turno"] = "Abuelita" if juego["turno"] == "Tutu" else "Tutu"

# -------------------- GLOBOS Y SONIDO DE CUADROS --------------------
conteo_actual = len(juego["cuadros"])

if conteo_actual > st.session_state.ultimo_conteo:
    nuevos = conteo_actual - st.session_state.ultimo_conteo
    faltantes = max(0, nuevos - st.session_state.globos_pendientes)
    st.session_state.globos_pendientes += faltantes
    st.session_state.ultimo_conteo = conteo_actual

if st.session_state.globos_pendientes > 0:
    st.balloons()
    st.session_state.globos_pendientes -= 1

if st.session_state.sonido_cuadro_pendiente > 0:
    reproducir_sonido(SONIDO_CUADRO)
    st.session_state.sonido_cuadro_pendiente -= 1

# -------------------- FIN DEL JUEGO --------------------
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
    st.session_state.fx_html = crear_fx_html()
    st.session_state.fin_festejado = True
    st.session_state.sonido_victoria_pendiente = True

if st.session_state.sonido_victoria_pendiente:
    reproducir_sonido(SONIDO_VICTORIA)
    st.session_state.sonido_victoria_pendiente = False

if fin_del_juego and st.session_state.fx_html:
    st.markdown(st.session_state.fx_html, unsafe_allow_html=True)

# -------------------- SIDEBAR --------------------
st.sidebar.write(f"## Turno de: {juego['turno']}")
st.sidebar.metric("🔵 Tutu", juego["puntos"]["Tutu"])
st.sidebar.metric("🔴 Abuelita", juego["puntos"]["Abuelita"])

# -------------------- TÍTULO --------------------
st.title("🕹️ Timbiriche: Tutu vs Abuelita")

# -------------------- MENSAJE FINAL --------------------
if fin_del_juego:
    if ganador == "Empate":
        st.markdown("""
        <div class="mensaje-final" style="color:#FFD700;">
            ⭐ ¡Empate! ⭐
        </div>
        """, unsafe_allow_html=True)
    else:
        color_ganador = "#6A4CFF" if ganador == "Tutu" else "#A1400F"
        st.markdown(f"""
        <div class="mensaje-final" style="color:{color_ganador};">
            <span class="corona">👑</span> ¡Ganó {ganador}!
        </div>
        """, unsafe_allow_html=True)

# -------------------- TABLERO --------------------
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
                    cols_v[c * 2 + 1].markdown("<div style='height:50px;'></div>", unsafe_allow_html=True)

# -------------------- BOTÓN FINAL --------------------
st.markdown("<div style='height:18px;'></div>", unsafe_allow_html=True)

if fin_del_juego:
    c1, c2, c3 = st.columns([2, 2.8, 2])
    with c2:
        if st.button("🎮 JUGAR OTRA VEZ", key="nuevo_juego_final", use_container_width=True):
            juego["puntos"] = {"Tutu": 0, "Abuelita": 0}
            juego["turno"] = "Tutu"
            juego["lineas_h"].fill(False)
            juego["lineas_v"].fill(False)
            juego["cuadros"].clear()

            st.session_state.ultimo_conteo = 0
            st.session_state.globos_pendientes = 0
            st.session_state.fin_festejado = False
            st.session_state.fx_html = ""
            st.session_state.sonido_cuadro_pendiente = 0
            st.session_state.sonido_victoria_pendiente = False

            st.rerun()

# -------------------- REINICIO SIDEBAR --------------------
if st.sidebar.button("Reiniciar Juego"):
    juego["puntos"] = {"Tutu": 0, "Abuelita": 0}
    juego["turno"] = "Tutu"
    juego["lineas_h"].fill(False)
    juego["lineas_v"].fill(False)
    juego["cuadros"].clear()

    st.session_state.ultimo_conteo = 0
    st.session_state.globos_pendientes = 0
    st.session_state.fin_festejado = False
    st.session_state.fx_html = ""
    st.session_state.sonido_cuadro_pendiente = 0
    st.session_state.sonido_victoria_pendiente = False

    st.rerun()
