# 🕹️ Timbiriche Multiplayer: Tutu vs Abuelita (Edición Estelar ✨)

<p align="center">
  <!-- Reemplaza esta ruta por la de tu logo real en el repo -->
  <img src="docs/images/claudia-logo.png" alt="Logo Claud-IA" width="220"/>
</p>

¡Bienvenido a la versión definitiva de **Timbiriche Pro**! Este proyecto transforma el clásico juego de puntos y líneas en una experiencia digital competitiva, diseñada para que **Tutu** y su **Abuelita** jueguen en tiempo real con efectos visuales de alta calidad.

## 🚀 Innovaciones Técnicas
Para lograr esta experiencia en **Streamlit**, implementamos soluciones avanzadas de desarrollo web:

* **Sincronización en Tiempo Real:** Uso de `@st.cache_resource` y `st_autorefresh` para que los movimientos se reflejen en ambos dispositivos cada 2 segundos.
* **Diseño 100% Responsivo:** Implementación de CSS con `flex-wrap: nowrap` y unidades adaptables para que el tablero mantenga su forma perfecta tanto en computadoras como en teléfonos móviles.
* **Interfaz "Zero-Jump":** Estructura rígida que evita que el tablero se mueva o cambie de tamaño al marcar las líneas.
* **Sistema de Identidad:** Selector de jugador que bloquea el tablero cuando no es tu turno, evitando errores o jugadas dobles.

---

## ✨ Características Especiales

### 🎨 Estética Neón y Moderna
* **Líneas de 8px:** Trazos gruesos con efectos de brillo (Glow) en Púrpura y Naranja.
* **Animaciones Pop:** Los cuadros conquistados aparecen con un efecto visual elástico.
* **Fondo Dinámico:** Gradiente radial profundo para una atmósfera de juego nocturno.

### 🎊 Efectos de Celebración
* **Globos de Punto:** Lluvia de globos cada vez que un jugador completa un cuadro.
* **Explosión Estelar ⭐:** Al finalizar, 80 estrellas doradas vuelan desde el centro de la pantalla celebrando al ganador.
* **Corona Real 👑:** Un panel final gigante con el nombre del campeón y el marcador definitivo.

### 🔊 Paisaje Sonoro
* Generación de audio en tiempo real para sonidos de clic, cierre de cuadro y fanfarria de victoria.

---

## 🛠️ Instalación y Uso (Anaconda)

Si quieres ejecutar este juego localmente o seguir desarrollándolo:

1.  **Crea el entorno:**
    ```bash
    conda create --name timbiriche python=3.10
    conda activate timbiriche
    ```
2.  **Instala las dependencias:**
    ```bash
    pip install streamlit numpy streamlit-autorefresh
    ```
3.  **Lanza el juego:**
    ```bash
    streamlit run timbiriche.py
    ```

---

## 📖 Reglas del Juego
1.  **Selecciona tu bando:** En la barra lateral, elige si eres **Tutu** o la **Abuelita**.
2.  **Marca líneas:** Haz clic en los espacios grises entre los puntos.
3.  **Repite turno:** Si cierras un cuadro, sumas un punto y ¡tienes un tiro extra!
4.  **Gana el mejor:** Al completar los 16 cuadros, el sistema coronará al ganador.

---
*Desarrollado con ❤️ para demostrar que la tecnología no tiene edad cuando se trata de divertirse en familia.*
