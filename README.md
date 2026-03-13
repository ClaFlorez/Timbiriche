# 🕹️ Timbiriche Multiplayer: Tutu vs Abuelita

¡Bienvenido al repositorio de **Timbiriche Pro**! Este proyecto transforma el clásico juego de lápiz y papel en una experiencia web moderna, sincronizada y llena de efectos visuales, diseñada específicamente para que **Tutu** y su **Abuelita** puedan jugar juntos en tiempo real.

## 🚀 El Desafío Técnico
Crear un juego de mesa interactivo en **Streamlit** requirió soluciones creativas para superar las limitaciones de una plataforma pensada originalmente para datos:

* **Sincronización Global:** Uso de `@st.cache_resource` para crear una memoria compartida en el servidor, permitiendo que ambos jugadores vean los mismos movimientos al instante.
* **Interfaz Inmóvil:** Implementación de CSS avanzado para fijar el tamaño de celdas y columnas, evitando que el tablero "salte" o se mueva al marcar líneas.
* **Sistema de Turnos con Bloqueo:** Selector de identidad que desactiva los botones para el jugador que no tiene el turno, garantizando un juego justo y ordenado.

---

## ✨ Características Principales

### 🎨 Diseño Visual de Alto Impacto
* **Líneas Neón:** Trazos de **8px** con efectos de brillo (glow) en Púrpura (Tutu) y Naranja (Abuelita).
* **Tablero Rígido:** Una cuadrícula perfectamente alineada de 4x4 cuadros.
* **Animaciones Pop:** Los cuadros cerrados aparecen con un efecto elástico suave.

### 🎊 Efectos Especiales y Sonido
* **Lluvia de Globos:** Cada vez que un jugador conquista un cuadro, una ráfaga de globos inunda su pantalla.
* **Explosión de Estrellas ⭐:** Al finalizar la partida, una lluvia de estrellas doradas celebra al ganador.
* **Corona Real 👑:** Mensaje final gigante con el nombre del campeón.
* **Audio Integrado:** Sonidos de clic para líneas y fanfarria para la victoria.

---

## 🛠️ Guía de Instalación Local (Paso a paso con Anaconda)

Para replicar este entorno de desarrollo en tu computadora, seguimos estos pasos utilizando la terminal de **Anaconda Prompt**:

1.  **Crear el entorno virtual:**
    Creamos un espacio aislado para evitar conflictos con otras librerías.
    ```bash
    conda create --name timbiriche python=3.10
    ```

2.  **Activar el entorno:**
    ```bash
    conda activate timbiriche
    ```

3.  **Instalar dependencias necesarias:**
    Instalamos el motor web y las herramientas de cálculo y sincronización.
    ```bash
    pip install streamlit numpy streamlit-autorefresh
    ```

4.  **Ejecutar el juego:**
    Navega hasta la carpeta del proyecto y lanza la aplicación.
    ```bash
    streamlit run timbiriche.py
    ```

---

## 🌍 Despliegue (Deploy)
El juego está optimizado para ser alojado en **Streamlit Cloud**. Para ello, el repositorio incluye:
* `timbiriche.py`: El código fuente principal.
* `requirements.txt`: La lista de librerías para que el servidor sepa qué instalar automáticamente.

## 📖 Reglas del Juego
1.  **Identidad:** Selecciona quién eres en la barra lateral (**Tutu** o **Abuelita**).
2.  **Turnos:** Solo puedes marcar una línea cuando el sistema indique que es tu turno.
3.  **Puntos:** Si cierras un cuadro, ganas un punto y **vuelves a tirar**.
4.  **Victoria:** El juego termina cuando se completan los 16 cuadros. ¡El que tenga más puntos se lleva la corona!

---
*Desarrollado con ❤️ para unir a la familia a través de la tecnología.*
