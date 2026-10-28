# Juego de la Memoria (Memotest) con Autómatas Finitos

**Universidad Nacional de la Patagonia San Juan Bosco (UNPSJB)**  
**Cátedra:** Fundamentos Teóricos de Informática  
**Grupo N°2 (2026):**
- Alexis Mariqueo
- Cesar Millavanque
- Daniel Enegron
- Kadir Martinez

---

## 📌 Descripción del Proyecto
Este proyecto es una implementación completa e interactiva del clásico juego **Memotest (Juego de la Memoria)**, desarrollado en **Python** utilizando **Pygame** y respaldado formalmente por la teoría de autómatas mediante la biblioteca **`automata-lib`**:
1. **Autómata Finito Determinista (AFD):** Gobierna y valida el progreso de los aciertos hacia el estado final de victoria.
2. **Autómata de Pila Determinista (AP / DPDA):** Modela el sistema regresivo de 5 vidas; ante 5 errores consecutivos o acumulados, el autómata vacía su pila aceptando la cadena por pila vacía (lo cual equivale formalmente a la Derrota).

---

## ⚙️ Reglas y Configuración del Juego

### 1. Niveles de Dificultad
- **Fácil:** Tablero de 8 cartas (4 pares únicos). Cuadrícula de 4x2.
- **Difícil:** Tablero de 16 cartas (8 pares únicos). Cuadrícula de 4x4.

### 2. Modos de Tiempo
- **Opción Corta:** Temporizador de 5 minutos (300 segundos).
- **Opción Normal:** Temporizador de 10 minutos (600 segundos).

### 3. Sistema de Puntuación
- El jugador inicia con un puntaje base de **200 puntos**.
- Cada fallo / error (símbolo `'e'`) resta **40 puntos**.
- Si el jugador alcanza los 5 fallos o el tiempo llega a `00:00`, el puntaje final es **0 puntos**.
- En caso de victoria, se conserva el puntaje restante: $200 - (40 \times \text{errores})$.

---

## 🧠 Modelado Formal con `automata-lib`

### 1. Alfabeto de Entrada ($\Sigma = \{a, e, x\}$)
- **`a` (Acierto):** Se seleccionan dos cartas idénticas (par coincidente).
- **`e` (Error):** Se seleccionan dos cartas distintas (no coinciden).
- **`x` (Inválido):** Se interactúa con una carta ya volteada, ya resuelta o durante la animación de volteo.

---

### 2. Autómata Finito Determinista (AFD) — Progreso de Aciertos
El AFD se define mediante la quíntupla:
$$\text{AFD} = (\Sigma, Q, \delta, q_0, F)$$

- **Alfabeto ($\Sigma$):** $\{a, e, x\}$
- **Conjunto de Estados ($Q$):**
  - **Fácil:** $\{q_0, q_1, q_2, q_3, q_4, q_{\text{sumidero}}\}$
  - **Difícil:** $\{q_0, q_1, q_2, q_3, q_4, q_5, q_6, q_7, q_8, q_{\text{sumidero}}\}$
- **Estado Inicial:** $q_0$
- **Estados Finales ($F$):**
  - Fácil: $\{q_4\}$
  - Difícil: $\{q_8\}$
- **Función de Transición ($\delta$):**
  - $\delta(q_i, a) = q_{i+1}$ (Avanza con cada par encontrado)
  - $\delta(q_i, e) = q_i$ (Mantiene el estado)
  - $\delta(q_i, x) = q_i$ (Mantiene el estado)
  - $\delta(q_{\text{final}}, \sigma) = q_{\text{sumidero}} \quad \forall \sigma \in \{a, e, x\}$
  - $\delta(q_{\text{sumidero}}, \sigma) = q_{\text{sumidero}} \quad \forall \sigma \in \{a, e, x\}$

#### Expresiones Regulares del Lenguaje Ganador:
- **Nivel Fácil (4 pares):**
  $$ER_{\text{ganador}} = (e+x)^* \cdot a \cdot (e+x)^* \cdot a \cdot (e+x)^* \cdot a \cdot (e+x)^* \cdot a$$
- **Nivel Difícil (8 pares):**
  $$ER_{\text{ganador}} = ((e+x)^* \cdot a)^8$$

---

### 3. Autómata de Pila (AP / DPDA) — Control de Vidas
- **Conjunto de Estados ($Q$):** $\{q_0, q_1, q_2\}$
- **Alfabeto de Entrada ($\Sigma_E$):** $\{a, e, x\}$
- **Alfabeto de la Pila ($\Sigma_P$):** $\{Z, V\}$
  - `Z`: Marcador de fondo de pila.
  - `V`: Representa una vida disponible.
- **Estado Inicial:** $q_0$
- **Símbolo Inicial de Pila:** $Z$
- **Condición de Aceptación:** Por **Pila Vacía** (`acceptance_mode='empty_stack'`). La aceptación por pila vacía modela la **Derrota** del jugador al agotar sus 5 vidas.

#### Tabla de Transiciones del AP:
| Estado actual | Símbolo leído | Desapilar (POP) | Estado nuevo | Apilar (PUSH) | Significado |
|---|---|---|---|---|---|
| $q_0$ | $\lambda$ | $Z$ | $q_1$ | $VVVVVZ$ | Carga inicial de 5 vidas |
| $q_1$ | $a$ | $V$ | $q_1$ | $V$ | Acierto: saldo de vidas intacto |
| $q_1$ | $x$ | $V$ | $q_1$ | $V$ | Jugada inválida: saldo intacto |
| $q_1$ | $e$ | $V$ | $q_1$ | $\lambda$ | Error: consume una vida de la pila |
| $q_1$ | $\lambda$ | $Z$ | $q_2$ | $\lambda$ | 5to error: consume $Z$, pila vacía (Derrota) |

---

## 🎨 Características de la Interfaz Gráfica

- **Visualización en Vivo del AFD:** Muestra el diagrama de nodos ($q_0 \to q_1 \to \dots \to q_N$), destacando en tiempo real el estado actual activo.
- **Visualizador Gráfico de la Pila (AP):** Dibuja la estructura física vertical de la pila con los bloques `[ V ]`, el fondo `[ Z ]`, y el puntero al `◀ TOPE`.
- **Registro de la Cadena de Entrada ($\omega \in \Sigma^*$):** Visualiza los símbolos ingresados (`a`, `e`, `x`) con insignias de colores diferenciados.
- **Música y Efectos de Sonido Integrados:**
  - Música de fondo en el menú principal (`menu_principal.mp3`) y durante el juego (`juego_principal.mp3`).
  - Efectos de sonido MP3: acierto al emparejar (`acierto.mp3`) y fallo en desacierto (`fallo.mp3`).
  - Efectos procedimentales complementarios (giro de carta, jugada inválida, fanfarria de victoria y derrota).
  - Modal interactivo de **Ajustes de Sonido** para regular y silenciar (mute) música y efectos de forma independiente tanto en el menú como durante la partida.
- **Botón de Salida:** Cierre limpio del juego desde el menú principal (`Salir del Juego`).
- **Animación Fluida de Giro 3D:** Efecto de perspectiva y volteo para cada carta al interactuar con ella.

---

## 🚀 Instalación y Ejecución

### Prerrequisitos
Tener instalado Python 3.10 o superior.

### 1. Instalar dependencias
```bash
pip install pygame-ce automata-lib
```

### 2. Ejecutar el juego
```bash
python main.py
```
*También puedes hacer doble clic directamente sobre `iniciar_juego.bat` en Windows.*

---

## 📂 Estructura del Código Fuente
```
Prueba Juego de memoria/
├── assets/
│   ├── cartas/               # Imágenes frontales de cartas y dorso
│   │   ├── Carta hmtl5.png
│   │   ├── Carta java.png
│   │   ├── Carta javascript.png
│   │   ├── Carta php.png
│   │   ├── Carta postgresql.png
│   │   ├── Carta python.png
│   │   ├── Carta ubuntu.png
│   │   ├── Carta windows.png
│   │   └── dorso-carta.png
│   └── musica/               # Pistas musicales y efectos sonoros
│       ├── menu_principal.mp3
│       ├── juego_principal.mp3
│       ├── acierto.mp3
│       └── fallo.mp3
├── automata_engine.py         # Modelado formal con automata-lib (AFD y AP)
├── card.py                    # Objeto carta, lógica de volteo y animación
├── game_manager.py            # Máquina de estados del juego y cuadrícula
├── ui_components.py           # Componentes visuales (grafos, pila, botones, modales)
├── sound_effects.py           # Manejador de música MP3, volumen y efectos
├── main.py                    # Bucle principal de ejecución Pygame
├── iniciar_juego.bat          # Lanzador directo para Windows
└── README.md                  # Documentación teórica y técnica
```
├── sound_effects.py           # Sintetizador procedural de audio en memoria
├── main.py                    # Bucle principal de ejecución Pygame
├── iniciar_juego.bat          # Lanzador directo para Windows
└── README.md                  # Documentación teórica y técnica
```

