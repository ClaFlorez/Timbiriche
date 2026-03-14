import streamlit as st
import numpy as np
import random

st.set_page_config(page_title="Timbiriche Mágico: Tutu vs Abuelita", layout="centered")

# --- CSS Brillante y Divertido y Responsivo ---
st.markdown("""
    <style>
    @keyframes pop {
        0% { transform: scale(0.2) rotate(-10deg); opacity: 0; }
        70% { transform: scale(1.2) rotate(5deg); }
        100% { transform: scale(1) rotate(0deg); opacity: 1; }
    }
    @keyframes latido {
        0% { transform: scale(1); }
        50% { transform: scale(1.2); }
        100% { transform: scale(1); }
    }
    @keyframes deslizar {
        from { opacity: 0; transform: translateY(-10px); }
        to { opacity: 1; transform: translateY(0); }
    }

    .stApp {
        background-color: #FFF0F5;
        background-image: radial-gradient(#FFB6C1 2px, transparent 2px);
        background-size: 30px 30px;
    }

    .stButton > button { 
        width: 100%; 
        padding: 0px; 
        height: clamp(25px, 5vw, 35px);
        background-color: transparent; 
        border: 2px dashed #FF69B4 !important; 
        border-radius: 15px;
        transition: all 0.2s ease-in-out;
    }
    .stButton > button:hover {
        background-color: #FFB6C1 !important;
        transform: scale(1.1);
        border: 2px solid #FF1493 !important;
        box-shadow: 0 0 10px #FF1493;
    }

    .punto { 
        font-size: clamp(16px, 4vw, 30px); 
        text-align: center; 
        line-height: clamp(25px, 5vw, 35px); 
        animation: latido 2s infinite;
    }

    .linea-h-llena { 
        border-bottom: clamp(5px, 1.2vw, 8px) solid #00E5FF; 
        margin-top: clamp(10px, 2.5vw, 15px); 
        border-radius: 10px;
        box-shadow: 0 0 15px #00E5FF, 0 0 5px #00E5FF;
        animation: deslizar 0.3s ease-out;
    }
    .linea-v-llena { 
        border-left: clamp(5px, 1.2vw, 8px) solid #00E5FF; 
        height: clamp(28px, 6vw, 40px); 
        margin-left: 50%; 
        border-radius: 10px;
        box-shadow: 0 0 15px #00E5FF, 0 0 5px #00E5FF;
        animation: deslizar 0.3s ease-out;
    }

    .cuadro-tutu, .cuadro-abuelita { 
        display: flex; align-items: center; justify-content: center; 
        height: clamp(28px, 6vw, 40px); 
        border-radius: 10px; 
        font-size: clamp(14px, 3.5vw, 26px);
        border: 2px solid #FFF;
        animation: pop 0.5s cubic-bezier(0.175, 0.885, 0.32, 1.275) both;
    }
    .cuadro-tutu { 
        background: linear-gradient(135deg, #FF1493, #FF69B4);
        box-shadow: 0 0 20px #FF1493;
    }
    .cuadro-abuelita { 
        background: linear-gradient(135deg, #8A2BE2, #9370DB);
        box-shadow: 0 0 20px #8A2BE2;
    }

    h1 {
        color: #FF1493 !important;
        text-align: center;
        text-shadow: 2px 2px 0px #FFF, 3px 3px 0px #FFB6C1;
        font-family: 'Comic Sans MS', cursive, sans-serif;
        font-size: clamp(24px, 5vw, 40px) !important;
    }
    
    h3 {
        font-size: clamp(18px, 4vw, 24px) !important;
    }

    /* 📱 RESPONSIVIDAD PARA CELULARES Y TABLETS */
    @media (max-width: 768px) {
        /* Evitar que Streamlit colapsar las columnas en celulares */
        [data-testid="stMain"] [data-testid="stHorizontalBlock"] {
            flex-direction: row !important;
            flex-wrap: nowrap !important;
            gap: 2px !important;
        }
        
        /* Proporciones correctas: puntos/vertical=1 (impar), lineas/cuadros=4 (par) */
        [data-testid="stMain"] [data-testid="column"]:nth-child(odd) {
            flex: 1 1 0 !important;
            min-width: 0 !important;
            width: auto !important;
        }
        [data-testid="stMain"] [data-testid="column"]:nth-child(even) {
            flex: 4 1 0 !important;
            min-width: 0 !important;
            width: auto !important;
        }

        /* Maximizar el espacio de la pantalla */
        [data-testid="block-container"] {
            padding-left: 5px !important;
            padding-right: 5px !important;
            padding-top: 30px !important;
            max-width: 100% !important;
        }
    }
    </style>
    """, unsafe_allow_html=True)

if 'puntos' not in st.session_state:
    st.session_state.puntos = {"Tutu": 0, "Abuelita": 0}
    st.session_state.turno = "Tutu"
    st.session_state.lineas_h = np.zeros((5, 4), dtype=bool)
    st.session_state.lineas_v = np.zeros((4, 5), dtype=bool)
    st.session_state.cuadros = {}
    st.session_state.animacion = None
    st.session_state.mensaje_ganador = ""

if st.session_state.animacion == "balloons":
    st.balloons()
    st.session_state.animacion = None
elif st.session_state.animacion == "snow":
    st.snow()
    st.session_state.animacion = None

if st.session_state.mensaje_ganador:
    st.success(st.session_state.mensaje_ganador, icon="🎉" if "Tutu" in st.session_state.mensaje_ganador else "👵")
    st.session_state.mensaje_ganador = ""

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
                    
                    if st.session_state.turno == "Tutu":
                        st.session_state.animacion = "balloons"
                        mensajes_tutu = ["¡Bravo Tutu! 🦄✨", "¡Súper Estrella Tutu! ⭐", "¡Magia Pura Tutu! 💖"]
                        st.session_state.mensaje_ganador = random.choice(mensajes_tutu)
                    else:
                        st.session_state.animacion = "snow"
                        st.session_state.mensaje_ganador = "¡Punto para Abuelita! 👵❄️"
    
    if not formo_cuadro:
        st.session_state.turno = "Abuelita" if st.session_state.turno == "Tutu" else "Tutu"

# --- Interfaz ---
st.title("💖 ✨ Timbiriche Mágico ✨ 💖")
st.markdown("<h3 style='text-align: center; color: #8A2BE2;'>🦄 Tutu vs Abuelita 👵</h3>", unsafe_allow_html=True)

st.sidebar.markdown(f"<h2>🔮 Turno: <br><span style='color: {'#FF1493' if st.session_state.turno == 'Tutu' else '#8A2BE2'};'>{st.session_state.turno}</span></h2>", unsafe_allow_html=True)

st.sidebar.divider()
st.sidebar.metric("🦄 Puntos Tutu", f"{st.session_state.puntos['Tutu']} ✨")
st.sidebar.metric("👵 Puntos Abuelita", f"{st.session_state.puntos['Abuelita']} 🌟")
st.sidebar.divider()

for r in range(5):
    cols = st.columns([1, 4, 1, 4, 1, 4, 1, 4, 1])
    for c in range(4):
        cols[c*2].markdown("<div class='punto'>🌸</div>", unsafe_allow_html=True)
        if st.session_state.lineas_h[r, c]:
            cols[c*2+1].markdown("<div class='linea-h-llena'></div>", unsafe_allow_html=True)
        else:
            if cols[c*2+1].button(" ", key=f"h_{r}_{c}"):
                registrar_movimiento('h', r, c)
                st.rerun()
    cols[8].markdown("<div class='punto'>🌸</div>", unsafe_allow_html=True)

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
                label = "🦄" if owner == "Tutu" else "👵"
                cols_v[c*2+1].markdown(f"<div class={clase}>{label}</div>", unsafe_allow_html=True)

st.write("")
col1, col2, col3 = st.columns([1, 2, 1])
if col2.button("✨ Reiniciar Magia ✨", use_container_width=True):
    st.session_state.clear()
    st.rerun()
   
