import streamlit as st
import streamlit.components.v1 as components
import numpy as np
import math
import wave
import struct
import io
import base64
from streamlit_autorefresh import st_autorefresh

st.set_page_config(
    page_title="Timbiriche · Tutu vs Abuelita",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ────────────────────────────────────────────
# CONSTANTES
# ────────────────────────────────────────────
FILAS = 4          # cuadros por eje
COLS = 4
JUGADORES = ["Tutu", "Abuelita"]
EMOJIS = {"Tutu": "🔵", "Abuelita": "🔴"}

COLOR_TUTU     = "#6A4CFF"
COLOR_ABUELITA = "#E05B20"

# ────────────────────────────────────────────
# CSS
# ────────────────────────────────────────────
st.markdown(f"""
<style>
/* Fondo oscuro de la app */
.stApp {{
    background: radial-gradient(ellipse at 20% 0%, #0d1b3e 0%, #020814 55%, #01040d 100%);
}}

/* ---- PUNTOS DEL TABLERO ---- */
.punto {{
    display:flex; align-items:center; justify-content:center;
    height:50px; width:100%;
    font-size:16px; color:rgba(255,255,255,0.6);
    user-select:none;
}}

/* ---- LÍNEAS HORIZONTALES LLENAS ---- */
.linea-h-tutu, .linea-h-abuelita, .linea-h-neutra {{
    height:50px; display:flex; align-items:center; justify-content:center;
}}
.linea-h-tutu::before    {{ content:""; display:block; width:90%; border-top:6px solid {COLOR_TUTU};     border-radius:10px; }}
.linea-h-abuelita::before{{ content:""; display:block; width:90%; border-top:6px solid {COLOR_ABUELITA}; border-radius:10px; }}
.linea-h-neutra::before  {{ content:""; display:block; width:90%; border-top:6px solid rgba(200,200,200,0.55); border-radius:10px; }}

/* ---- LÍNEAS VERTICALES LLENAS ---- */
.linea-v-tutu, .linea-v-abuelita, .linea-v-neutra {{
    width:100%; height:50px; display:flex; align-items:center; justify-content:center;
}}
.linea-v-tutu::before    {{ content:""; display:block; height:90%; border-left:6px solid {COLOR_TUTU};     border-radius:10px; }}
.linea-v-abuelita::before{{ content:""; display:block; height:90%; border-left:6px solid {COLOR_ABUELITA}; border-radius:10px; }}
.linea-v-neutra::before  {{ content:""; display:block; height:90%; border-left:6px solid rgba(200,200,200,0.55); border-radius:10px; }}

/* ---- CUADROS CONQUISTADOS ---- */
.cuadro-tutu {{
    background: linear-gradient(135deg, {COLOR_TUTU}cc 0%, #4F46D7cc 100%);
    height:50px; width:100%; border-radius:8px;
    display:flex; align-items:center; justify-content:center;
    color:white; font-weight:700; font-size:13px;
    animation: pop 0.25s ease;
}}
.cuadro-abuelita {{
    background: linear-gradient(135deg, {COLOR_ABUELITA}cc 0%, #9A3D10cc 100%);
    height:50px; width:100%; border-radius:8px;
    display:flex; align-items:center; justify-content:center;
    color:white; font-weight:700; font-size:13px;
    animation: pop 0.25s ease;
}}
@keyframes pop {{
    0%   {{ transform:scale(0.7); opacity:0; }}
    70%  {{ transform:scale(1.08); }}
    100% {{ transform:scale(1);   opacity:1; }}
}}

/* ---- BOTONES DEL TABLERO ---- */
button[kind="secondary"] {{
    width:100% !important; height:50px !important;
    background:transparent !important;
    border:1px solid rgba(255,255,255,0.04) !important;
    color:transparent !important;
    margin:0 !important; cursor:pointer !important;
    transition: background 0.15s !important;
}}
button[kind="secondary"]:hover:not(:disabled) {{
    background:rgba(255,255,255,0.08) !important;
}}

/* ---- BOTONES ESPECIALES ---- */
button[kind="primary"] {{
    background: linear-gradient(135deg,#6A4CFF,#4F46D7) !important;
    font-size:16px !important; border-radius:10px !important;
}}

/* ---- SCORECARD (sidebar) ---- */
.scorecard {{
    background:rgba(255,255,255,0.05);
    border:1px solid rgba(255,255,255,0.1);
    border-radius:14px; padding:16px 20px;
    margin-bottom:10px;
}}
.scorecard-name  {{ font-size:15px; font-weight:600; color:white; }}
.scorecard-pts   {{ font-size:36px; font-weight:800; color:white; line-height:1.1; }}
.scorecard-label {{ font-size:11px; color:rgba(255,255,255,0.45); text-transform:uppercase; letter-spacing:1px; }}

/* ---- TURNO BADGE ---- */
.turno-badge {{
    display:inline-block;
    padding:6px 18px; border-radius:20px;
    font-size:14px; font-weight:700;
    margin-bottom:8px;
}}

/* ---- TÍTULO ---- */
h1 {{
    color: white !important;
    text-align: center;
    font-size: 2rem !important;
    letter-spacing: -0.5px;
    margin-bottom: 4px !important;
}}
.subtitulo {{
    text-align:center; color:rgba(255,255,255,0.4);
    font-size:13px; margin-bottom:20px;
}}

/* ---- COLUMNAS SIN SEPARACIÓN ---- */
div[data-testid="stHorizontalBlock"] {{
    gap: 0px !important;
    align-items: center;
}}
[data-testid="column"] {{
    min-width:0px !important;
    flex-basis:auto !important;
    padding-left:2px !important;
    padding-right:2px !important;
}}

/* ---- BANNER FINAL ---- */
.banner-fin {{
    text-align:center;
    padding:24px 0;
    font-size:2rem;
    font-weight:800;
    color:white;
    animation: brillar 1.2s ease-in-out infinite alternate;
}}
@keyframes brillar {{
    from {{ text-shadow: 0 0 8px rgba(255,215,0,0.4); }}
    to   {{ text-shadow: 0 0 24px rgba(255,215,0,1); }}
}}
</style>
""", unsafe_allow_html=True)

# ────────────────────────────────────────────
# AUTO-REFRESH cada 2 s (multiplayer sync)
# ────────────────────────────────────────────
st_autorefresh(interval=2000, key="datarefresh")

# ────────────────────────────────────────────
# AUDIO
# ────────────────────────────────────────────
@st.cache_data
def _gen_audio(frec: float, duracion: float = 0.18) -> str:
    """Genera un beep y lo devuelve como base64 WAV."""
    buffer = io.BytesIO()
    rate = 22050
    with wave.open(buffer, "wb") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(rate)
        for i in range(int(rate * duracion)):
            t = i / rate
            # Ligero fade-out para suavizar el sonido
            env = 1 - (i / (rate * duracion)) ** 2
            val = int(32767 * 0.35 * env * math.sin(2 * math.pi * frec * t))
            f.writeframes(struct.pack("<h", val))
    return base64.b64encode(buffer.getvalue()).decode()

SND_LINEA   = _gen_audio(660)   # colocar línea
SND_CUADRO  = _gen_audio(1046)  # completar cuadro  (Do5 = 1047 Hz ≈)
SND_VICTORIA = _gen_audio(523)  # fin de partida    (Do4)

def play(b64: str):
    st.markdown(
        f'<audio autoplay style="display:none;"><source src="data:audio/wav;base64,{b64}"></audio>',
        unsafe_allow_html=True,
    )

# ────────────────────────────────────────────
# ESTADO COMPARTIDO (cache_resource = global)
# ────────────────────────────────────────────
@st.cache_resource
def get_juego():
    return {
        "puntos":    {"Tutu": 0, "Abuelita": 0},
        "turno":     "Tutu",
        "lineas_h":  np.zeros((FILAS + 1, COLS), dtype=bool),  # (5,4)
        "lineas_v":  np.zeros((FILAS, COLS + 1), dtype=bool),  # (4,5)
        "duenos_h":  np.full((FILAS + 1, COLS), "", dtype=object),
        "duenos_v":  np.full((FILAS, COLS + 1), "", dtype=object),
        "cuadros":   {},   # (r,c) -> "Tutu"|"Abuelita"
        "historial": [],   # lista de strings para el log
    }

juego = get_juego()

# ────────────────────────────────────────────
# TRACKING DE EFECTOS (por sesión, no global)
# ────────────────────────────────────────────
if "cuadros_vistos" not in st.session_state:
    st.session_state.cuadros_vistos = 0

total_cuadros_ahora = len(juego["cuadros"])
fin_ahora = total_cuadros_ahora == FILAS * COLS

nuevo_cuadro = total_cuadros_ahora > st.session_state.cuadros_vistos
if nuevo_cuadro:
    st.session_state.cuadros_vistos = total_cuadros_ahora

# ── Efectos visuales con components.html (único método que ejecuta JS real en Streamlit) ──
def lanzar_globos(seed: int):
    """22 globos: el iframe se hace fullscreen desde adentro via JS."""
    globos = ""
    for i in range(22):
        left  = (i * 41 + i * i * 17 + seed * 3) % 100
        delay = round(((i * 190 + seed) % 2200) / 1000, 2)
        dur   = round(2.4 + (i % 5) * 0.3, 2)
        sz    = 24 + (i % 5) * 10
        globos += f'<div style="position:fixed;left:{left}%;bottom:-90px;font-size:{sz}px;animation:subirG {dur}s {delay}s ease-in forwards;pointer-events:none;">🎈</div>'
    components.html(f"""
    <style>
      * {{ margin:0; padding:0; box-sizing:border-box; }}
      html, body {{ width:100%; height:100%; background:transparent !important; overflow:hidden; }}
      @keyframes subirG {{
        0%   {{ transform:translateY(0) rotate(-12deg); opacity:1; }}
        60%  {{ transform:translateY(-65vh) rotate(12deg) scale(1.1); opacity:1; }}
        100% {{ transform:translateY(-130vh) rotate(-5deg); opacity:0; }}
      }}
    </style>
    <script>
      // Hacer el iframe fullscreen desde adentro
      try {{
        var fr = window.frameElement;
        if(fr) {{
          fr.style.cssText = 'position:fixed!important;inset:0!important;width:100vw!important;height:100vh!important;border:none!important;pointer-events:none!important;z-index:99999!important;background:transparent!important;';
        }}
      }} catch(e) {{}}
    </script>
    {globos}
    <script>setTimeout(function(){{
      try{{ var fr=window.frameElement; if(fr) fr.style.display='none'; }}catch(e){{}}
      document.body.innerHTML='';
    }}, 5500);</script>
    """, height=1, scrolling=False)

def lanzar_estrellas(seed: int):
    """50 estrellas: el iframe se hace fullscreen desde adentro via JS."""
    chars = ['⭐','🌟','✨','💫','🌟','✨','⭐','💫','🌟','✨']
    items = ""
    for i in range(50):
        left  = (i * 43 + i * 7) % 100
        delay = round(((i * 130 + seed) % 4500) / 1000, 2)
        dur   = round(2.5 + (i % 7) * 0.45, 2)
        sz    = 16 + (i % 6) * 9
        ch    = chars[i % len(chars)]
        items += f'<div style="position:fixed;left:{left}%;top:-80px;font-size:{sz}px;animation:caerE {dur}s {delay}s linear forwards;pointer-events:none;">{ch}</div>'
    components.html(f"""
    <style>
      * {{ margin:0; padding:0; box-sizing:border-box; }}
      html, body {{ width:100%; height:100%; background:transparent !important; overflow:hidden; }}
      @keyframes caerE {{
        0%   {{ transform:translateY(-90px) rotate(0deg);  opacity:0; }}
        8%   {{ opacity:1; }}
        88%  {{ opacity:1; }}
        100% {{ transform:translateY(200vh) rotate(420deg); opacity:0; }}
      }}
    </style>
    <script>
      try {{
        var fr = window.frameElement;
        if(fr) {{
          fr.style.cssText = 'position:fixed!important;inset:0!important;width:100vw!important;height:100vh!important;border:none!important;pointer-events:none!important;z-index:99999!important;background:transparent!important;';
        }}
      }} catch(e) {{}}
    </script>
    {items}
    <script>setTimeout(function(){{
      try{{ var fr=window.frameElement; if(fr) fr.style.display='none'; }}catch(e){{}}
      document.body.innerHTML='';
    }}, 10000);</script>
    """, height=1, scrolling=False)

def limpiar_efectos():
    pass  # Los iframes de components.html desaparecen solos al hacer st.rerun()

if nuevo_cuadro and not fin_ahora:
    lanzar_globos(total_cuadros_ahora)

# ────────────────────────────────────────────
# LÓGICA DEL JUEGO
# ────────────────────────────────────────────
def registrar(tipo: str, r: int, c: int):
    """Marca una línea y verifica cuadros completados. Devuelve cuántos cuadros se formaron."""
    h, v = juego["lineas_h"], juego["lineas_v"]
    jugador = juego["turno"]

    if tipo == "h":
        if h[r, c]:
            return 0   # ya está marcada (doble clic)
        h[r, c] = True
        juego["duenos_h"][r, c] = jugador
    else:
        if v[r, c]:
            return 0
        v[r, c] = True
        juego["duenos_v"][r, c] = jugador

    # ¿Se formaron cuadros?
    formados = 0
    for row in range(FILAS):
        for col in range(COLS):
            if (row, col) not in juego["cuadros"]:
                if h[row, col] and h[row + 1, col] and v[row, col] and v[row, col + 1]:
                    juego["cuadros"][(row, col)] = jugador
                    juego["puntos"][jugador] += 1
                    juego["historial"].append(
                        f"{EMOJIS[jugador]} **{jugador}** completó cuadro ({row+1},{col+1})"
                    )
                    formados += 1

    if formados == 0:
        # Cambiar turno solo si no completó cuadro
        otro = JUGADORES[1 - JUGADORES.index(jugador)]
        juego["turno"] = otro
    else:
        juego["historial"].append(
            f"  ↳ +{formados} cuadro{'s' if formados>1 else ''}, sigue jugando {EMOJIS[jugador]}"
        )

    return formados

def reiniciar():
    juego["puntos"]   = {"Tutu": 0, "Abuelita": 0}
    juego["turno"]    = "Tutu"
    juego["lineas_h"].fill(False)
    juego["lineas_v"].fill(False)
    juego["duenos_h"].fill("")
    juego["duenos_v"].fill("")
    juego["cuadros"].clear()
    juego["historial"].clear()

# ────────────────────────────────────────────
# SIDEBAR
# ────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚙️ Jugador")
    usuario = st.radio("¿Quién eres tú?", JUGADORES, horizontal=True)

    st.divider()

    # Turno actual
    color_turno = COLOR_TUTU if juego["turno"] == "Tutu" else COLOR_ABUELITA
    st.markdown(
        f"<div class='turno-badge' style='background:{color_turno}33; "
        f"border:1.5px solid {color_turno}; color:white;'>"
        f"{EMOJIS[juego['turno']]} Turno de <strong>{juego['turno']}</strong></div>",
        unsafe_allow_html=True,
    )

    # Marcador
    for j in JUGADORES:
        col_j = COLOR_TUTU if j == "Tutu" else COLOR_ABUELITA
        st.markdown(f"""
        <div class="scorecard" style="border-color:{col_j}55;">
            <div class="scorecard-label">{EMOJIS[j]} {j}</div>
            <div class="scorecard-pts" style="color:{col_j};">{juego['puntos'][j]}</div>
            <div class="scorecard-label">cuadros</div>
        </div>""", unsafe_allow_html=True)

    st.divider()

    # Progreso de la partida
    total_lineas = (FILAS + 1) * COLS + FILAS * (COLS + 1)  # 40 líneas
    marcadas = int(juego["lineas_h"].sum()) + int(juego["lineas_v"].sum())
    st.markdown("**Progreso**")
    st.progress(marcadas / total_lineas)
    st.caption(f"{marcadas}/{total_lineas} líneas · {len(juego['cuadros'])}/{FILAS*COLS} cuadros")

    st.divider()

    if st.button("🔄 Reiniciar partida", use_container_width=True, type="primary"):
        limpiar_efectos()
        reiniciar()
        st.session_state.cuadros_vistos = 0
        st.rerun()

    # Historial de jugadas (últimas 10)
    if juego["historial"]:
        with st.expander("📜 Historial de jugadas"):
            for line in reversed(juego["historial"][-20:]):
                st.markdown(line)

# ────────────────────────────────────────────
# ÁREA PRINCIPAL
# ────────────────────────────────────────────
fin = len(juego["cuadros"]) == FILAS * COLS
es_mi_turno = (usuario == juego["turno"]) and not fin

st.markdown("<h1>🕹️ Timbiriche</h1>", unsafe_allow_html=True)
st.markdown(
    f"<div class='subtitulo'>{EMOJIS['Tutu']} Tutu &nbsp;vs&nbsp; Abuelita {EMOJIS['Abuelita']}</div>",
    unsafe_allow_html=True,
)

# ────────────────────────────────────────────
# AVISO DE TURNO
# ────────────────────────────────────────────
if not fin:
    if es_mi_turno:
        st.success(f"✅ Es **tu** turno, {usuario}! Haz click en una línea libre.", icon="🎯")
    else:
        otro = JUGADORES[1 - JUGADORES.index(usuario)]
        st.info(f"⏳ Esperando a que juegue **{juego['turno']}**...", icon="👀")

# ────────────────────────────────────────────
# TABLERO
# ────────────────────────────────────────────
# Columnas: [punto, linea, punto, linea, ... punto]
# Ratio: 0.5 para puntos, 3 para líneas/cuadros
col_widths = []
for _ in range(COLS):
    col_widths += [0.5, 3]
col_widths.append(0.5)  # último punto

h  = juego["lineas_h"]
v  = juego["lineas_v"]
dh = juego["duenos_h"]
dv = juego["duenos_v"]

for r in range(FILAS + 1):
    # ── Fila de puntos y líneas HORIZONTALES ──
    cols = st.columns(col_widths)
    for c in range(COLS):
        # Punto
        cols[c * 2].markdown("<div class='punto'>●</div>", unsafe_allow_html=True)
        # Línea horizontal
        if h[r, c]:
            dueno = dh[r, c]
            clase = f"linea-h-tutu" if dueno == "Tutu" else "linea-h-abuelita"
            cols[c * 2 + 1].markdown(f"<div class='{clase}'></div>", unsafe_allow_html=True)
        else:
            if cols[c * 2 + 1].button(" ", key=f"h{r}{c}", disabled=not es_mi_turno):
                n = registrar("h", r, c)
                if n > 0:
                    play(SND_CUADRO)
                else:
                    play(SND_LINEA)
                st.rerun()
    # Último punto de la fila
    cols[COLS * 2].markdown("<div class='punto'>●</div>", unsafe_allow_html=True)

    # ── Fila de líneas VERTICALES y CUADROS ──
    if r < FILAS:
        cols_v = st.columns(col_widths)
        for c in range(COLS + 1):
            if v[r, c]:
                dueno = dv[r, c]
                clase = "linea-v-tutu" if dueno == "Tutu" else "linea-v-abuelita"
                cols_v[c * 2].markdown(f"<div class='{clase}'></div>", unsafe_allow_html=True)
            else:
                if cols_v[c * 2].button(" ", key=f"v{r}{c}", disabled=not es_mi_turno):
                    n = registrar("v", r, c)
                    if n > 0:
                        play(SND_CUADRO)
                    else:
                        play(SND_LINEA)
                    st.rerun()
            if c < COLS:
                if (r, c) in juego["cuadros"]:
                    own = juego["cuadros"][(r, c)]
                    clase = "cuadro-tutu" if own == "Tutu" else "cuadro-abuelita"
                    cols_v[c * 2 + 1].markdown(
                        f"<div class='{clase}'>{own[0]}</div>",
                        unsafe_allow_html=True,
                    )
                else:
                    # Celda vacía para mantener layout
                    cols_v[c * 2 + 1].markdown(
                        "<div style='height:50px;'></div>",
                        unsafe_allow_html=True,
                    )

# ────────────────────────────────────────────
# PANTALLA FINAL
# ────────────────────────────────────────────
if fin_ahora:
    pt, pa = juego["puntos"]["Tutu"], juego["puntos"]["Abuelita"]
    if pt > pa:
        ganador = "Tutu"
        color_g = COLOR_TUTU
    elif pa > pt:
        ganador = "Abuelita"
        color_g = COLOR_ABUELITA
    else:
        ganador = None
        color_g = "#FFD700"

    # Lanzar estrellas siempre al mostrar pantalla final
    # El seed cambia cada vez que se completa la partida (total_cuadros_ahora)
    # Streamlit re-renderiza components.html solo si el contenido cambia
    play(SND_VICTORIA)
    lanzar_estrellas(total_cuadros_ahora * 1000 + juego["puntos"]["Tutu"])

    # Banner con corona y nombre del ganador
    if ganador:
        st.markdown(f"""
        <div style="
            text-align:center;
            padding: 36px 20px 28px;
            margin-top: 24px;
            background: linear-gradient(135deg, {color_g}22, {color_g}08);
            border: 2px solid {color_g}88;
            border-radius: 20px;
        ">
            <div style="font-size:72px; line-height:1; margin-bottom:10px;">👑</div>
            <div style="
                font-size: 3rem;
                font-weight: 900;
                color: {color_g};
                letter-spacing: -1px;
                text-shadow: 0 0 30px {color_g}88;
                animation: brillar 1.2s ease-in-out infinite alternate;
            ">¡{ganador} ganó!</div>
            <div style="
                font-size: 1.3rem;
                color: rgba(255,255,255,0.7);
                margin-top: 12px;
                font-weight: 600;
            ">
                {EMOJIS['Tutu']} Tutu <span style="color:white; font-size:1.6rem; font-weight:900;">{pt}</span>
                &nbsp;–&nbsp;
                <span style="color:white; font-size:1.6rem; font-weight:900;">{pa}</span> Abuelita {EMOJIS['Abuelita']}
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div style="
            text-align:center; padding:36px 20px 28px; margin-top:24px;
            background: linear-gradient(135deg, #FFD70022, #FFD70008);
            border: 2px solid #FFD70088; border-radius:20px;
        ">
            <div style="font-size:72px; line-height:1; margin-bottom:10px;">🤝</div>
            <div style="font-size:3rem; font-weight:900; color:#FFD700;">¡Empate!</div>
            <div style="font-size:1.3rem; color:rgba(255,255,255,0.7); margin-top:12px; font-weight:600;">
                {EMOJIS['Tutu']} Tutu <span style="color:white; font-size:1.6rem; font-weight:900;">{pt}</span>
                &nbsp;–&nbsp;
                <span style="color:white; font-size:1.6rem; font-weight:900;">{pa}</span> Abuelita {EMOJIS['Abuelita']}
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🔄 Nueva partida", type="primary", use_container_width=True):
        limpiar_efectos()
        reiniciar()
        st.session_state.cuadros_vistos = 0
        st.rerun()
