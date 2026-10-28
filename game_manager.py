"""
Módulo de Gestión de Juego (GameManager) para el Memotest con Autómatas.
Controla el flujo de estados, cronómetro, puntuación, interacción con cartas,
reproducción de sonidos y sincronización con el controlador de autómatas.
"""

import os
import random
import pygame
from typing import Dict, List, Optional, Tuple

from automata_engine import AutomataGameController
from card import Card, STATE_FACE_DOWN, STATE_FACE_UP, STATE_MATCHED
from sound_effects import SoundManager
from ui_components import (
    Button,
    DFAGraphVisualizer,
    ModalDialog,
    SegmentedSelector,
    SoundSettingsModal,
    StackVisualizer,
    WordHistoryView,
    get_font,
)

# Estados generales de la aplicación
STATE_MENU = "MENU"
STATE_PLAYING = "PLAYING"
STATE_VICTORY = "VICTORY"
STATE_GAME_OVER = "GAME_OVER"


class GameManager:
    """Administrador central de la lógica del juego y la interfaz."""

    def __init__(self, screen_size: Tuple[int, int] = (1280, 720)):
        self.screen_width, self.screen_height = screen_size
        self.state = STATE_MENU

        # Configuraciones de partida
        self.difficulty = "facil"  # 'facil' (4 pares) o 'dificil' (8 pares)
        self.time_mode_seconds = 300.0  # 300s (5 min) o 600s (10 min)

        # Variables de partida
        self.score = 200
        self.time_remaining = self.time_mode_seconds
        self.total_errors = 0
        self.total_matches = 0
        self.total_invalids = 0
        self.status_message = "Selecciona dos cartas para buscar una coincidencia."
        self.status_message_color = (200, 215, 235)

        # Cartas y tablero
        self.cards: List[Card] = []
        self.first_selected: Optional[Card] = None
        self.second_selected: Optional[Card] = None
        self.mismatch_wait_timer: float = 0.0

        # Autómatas y audio
        self.automata = AutomataGameController(pairs_count=4)
        self.sound = SoundManager(enabled=True)
        self.is_running = True

        # Iniciar música del menú principal
        self.sound.play_menu_music()

        # Recursos gráficos
        self.front_images: Dict[str, pygame.Surface] = {}
        self.back_image: Optional[pygame.Surface] = None
        self._load_card_assets()

        # Componentes UI de la pantalla de juego
        self.hud_rect = pygame.Rect(820, 80, 440, 76)
        self.word_view = WordHistoryView(pygame.Rect(820, 166, 440, 68))
        self.dfa_view = DFAGraphVisualizer(pygame.Rect(820, 244, 440, 98))
        self.stack_view = StackVisualizer(pygame.Rect(820, 352, 440, 206))
        
        # Botones HUD en juego (4 botones compactos)
        btn_y = 568
        btn_w = 102
        gap = 10
        self.btn_restart = Button(
            pygame.Rect(820, btn_y, btn_w, 40),
            "Reiniciar",
            callback=self.restart_current_game,
            bg_color=(39, 174, 96),
            hover_color=(46, 204, 113),
            font_size=13,
        )
        self.btn_menu = Button(
            pygame.Rect(820 + btn_w + gap, btn_y, btn_w, 40),
            "Menú",
            callback=self.go_to_menu,
            bg_color=(41, 128, 185),
            hover_color=(52, 152, 219),
            font_size=13,
        )
        self.btn_hud_sound = Button(
            pygame.Rect(820 + (btn_w + gap) * 2, btn_y, btn_w, 40),
            "Sonido 🔊",
            callback=self.open_sound_settings,
            bg_color=(230, 126, 34),
            hover_color=(243, 156, 18),
            font_size=13,
        )
        self.btn_theory = Button(
            pygame.Rect(820 + (btn_w + gap) * 3, btn_y, btn_w, 40),
            "Teoría FTI",
            callback=self.show_theoretical_info,
            bg_color=(142, 68, 173),
            hover_color=(155, 89, 182),
            font_size=13,
        )

        # Ventana modal activa (Victoria, Derrota o Información)
        self.active_modal: Optional[ModalDialog] = None

        # Componentes del Menú Principal
        self._init_menu_components()

    def _load_card_assets(self):
        """Carga las imágenes de las cartas desde la carpeta assets/cartas."""
        assets_dir = os.path.join("assets", "cartas")
        if not os.path.exists(assets_dir):
            raise FileNotFoundError(f"No se encontró el directorio de cartas: {assets_dir}")

        for fname in os.listdir(assets_dir):
            if fname.lower().endswith(".png"):
                full_p = os.path.join(assets_dir, fname)
                loaded_img = pygame.image.load(full_p).convert_alpha()
                if fname == "dorso-carta.png":
                    self.back_image = loaded_img
                else:
                    # Usar nombre limpio como ID de par (ej: 'python', 'java', etc.)
                    pair_key = fname.replace("Carta ", "").replace(".png", "").strip()
                    self.front_images[pair_key] = loaded_img

        if not self.back_image:
            raise FileNotFoundError("No se encontró la imagen dorso-carta.png en assets/cartas")

    def _init_menu_components(self):
        """Inicializa los elementos interactivos del menú principal."""
        center_x = self.screen_width // 2

        # Selector de dificultad
        self.diff_selector = SegmentedSelector(
            x=center_x - 220,
            y=276,
            width=440,
            height=44,
            options=[
                ("Fácil (8 cartas - 4 pares)", "facil"),
                ("Difícil (16 cartas - 8 pares)", "dificil"),
            ],
            selected_value=self.difficulty,
            on_change=lambda val: setattr(self, "difficulty", val),
        )

        # Selector de tiempo
        self.time_selector = SegmentedSelector(
            x=center_x - 220,
            y=356,
            width=440,
            height=44,
            options=[
                ("Tiempo Corto (5 min)", "300"),
                ("Tiempo Normal (10 min)", "600"),
            ],
            selected_value=str(int(self.time_mode_seconds)),
            on_change=lambda val: setattr(self, "time_mode_seconds", float(val)),
        )

        # Fila 1: Botón para Iniciar Partida
        self.btn_start = Button(
            rect=pygame.Rect(center_x - 220, 424, 440, 48),
            text="INICIAR PARTIDA",
            callback=self.start_game,
            bg_color=(39, 174, 96),
            hover_color=(46, 204, 113),
            font_size=18,
            border_radius=10,
        )

        # Fila 2: Botón de Sonido y Botón de Fundamentos Teóricos
        self.btn_sound = Button(
            rect=pygame.Rect(center_x - 220, 484, 215, 42),
            text="Ajustes de Sonido 🔊",
            callback=self.open_sound_settings,
            bg_color=(41, 128, 185),
            hover_color=(52, 152, 219),
            font_size=14,
            border_radius=8,
        )

        self.btn_menu_theory = Button(
            rect=pygame.Rect(center_x + 5, 484, 215, 42),
            text="Fundamentos Teóricos",
            callback=self.show_theoretical_info,
            bg_color=(142, 68, 173),
            hover_color=(155, 89, 182),
            font_size=14,
            border_radius=8,
        )

        # Fila 3: Botón para Salir del Juego
        self.btn_quit = Button(
            rect=pygame.Rect(center_x - 220, 538, 440, 38),
            text="Salir del Juego ✕",
            callback=self.quit_game,
            bg_color=(192, 57, 43),
            hover_color=(231, 76, 60),
            font_size=14,
            border_radius=8,
        )

    def open_sound_settings(self):
        """Abre la ventana modal interactiva de ajustes de audio."""
        self.active_modal = SoundSettingsModal(
            screen_size=(self.screen_width, self.screen_height),
            sound_manager=self.sound,
            on_close=lambda: setattr(self, "active_modal", None),
        )

    def quit_game(self):
        """Cierra la aplicación de forma limpia."""
        self.is_running = False
        pygame.event.post(pygame.event.Event(pygame.QUIT))

    def start_game(self):
        """Prepara e inicia una nueva partida con la configuración elegida."""
        pairs_count = 4 if self.difficulty == "facil" else 8
        self.automata.reset(pairs_count)

        self.score = 200
        self.time_remaining = self.time_mode_seconds
        self.total_errors = 0
        self.total_matches = 0
        self.total_invalids = 0
        self.status_message = "¡Partida iniciada! Encuentra todos los pares."
        self.status_message_color = (200, 215, 235)

        self.first_selected = None
        self.second_selected = None
        self.mismatch_wait_timer = 0.0
        self.active_modal = None

        self._build_board(pairs_count)
        self.state = STATE_PLAYING

        # Iniciar música durante la partida
        self.sound.play_game_music()

    def restart_current_game(self):
        """Reinicia la partida actual con las mismas configuraciones."""
        self.start_game()

    def go_to_menu(self):
        """Regresa al menú principal."""
        self.active_modal = None
        self.first_selected = None
        self.second_selected = None
        self.state = STATE_MENU

        # Volver a la música del menú principal
        self.sound.play_menu_music()

    def _build_board(self, pairs_count: int):
        """Genera y distribuye las cartas aleatoriamente en la cuadrícula correspondiente."""
        self.cards.clear()

        # Seleccionar las imágenes necesarias
        all_keys = list(self.front_images.keys())
        if pairs_count == 4:
            chosen_keys = random.sample(all_keys, 4)
        else:
            chosen_keys = all_keys[:8]

        # Crear dos cartas por cada par (coincidentes)
        card_items = []
        for p_id in chosen_keys:
            card_items.append(p_id)
            card_items.append(p_id)
        random.shuffle(card_items)

        # Disposición en cuadrícula
        # Fácil: 4 columnas x 2 filas
        # Difícil: 4 columnas x 4 filas
        cols = 4
        rows = 2 if pairs_count == 4 else 4

        card_w = 120 if pairs_count == 4 else 105
        card_h = 144 if pairs_count == 4 else 126
        gap_x = 26 if pairs_count == 4 else 16
        gap_y = 28 if pairs_count == 4 else 16

        total_w = cols * card_w + (cols - 1) * gap_x
        total_h = rows * card_h + (rows - 1) * gap_y

        # Centrar en el área del tablero (x: 20..800, y: 80..710)
        center_board_x = 410
        center_board_y = 395
        start_x = center_board_x - (total_w // 2)
        start_y = center_board_y - (total_h // 2)

        for idx, p_id in enumerate(card_items):
            c = idx % cols
            r = idx // cols
            rx = start_x + c * (card_w + gap_x)
            ry = start_y + r * (card_h + gap_y)
            rect = pygame.Rect(rx, ry, card_w, card_h)

            card_obj = Card(
                card_id=idx,
                pair_id=p_id,
                front_image=self.front_images[p_id],
                back_image=self.back_image,
                rect=rect,
            )
            self.cards.append(card_obj)

    def handle_event(self, event: pygame.event.Event):
        """Maneja los eventos de ratón y teclado."""
        # Si hay una ventana modal abierta, ella tiene la prioridad exclusiva
        if self.active_modal:
            self.active_modal.handle_event(event)
            return

        if self.state == STATE_MENU:
            self.diff_selector.handle_event(event)
            self.time_selector.handle_event(event)
            self.btn_start.handle_event(event)
            self.btn_sound.handle_event(event)
            self.btn_menu_theory.handle_event(event)
            self.btn_quit.handle_event(event)
            return

        if self.state == STATE_PLAYING:
            self.btn_restart.handle_event(event)
            self.btn_menu.handle_event(event)
            self.btn_hud_sound.handle_event(event)
            self.btn_theory.handle_event(event)

            # Hover en cartas
            if event.type == pygame.MOUSEMOTION:
                for c in self.cards:
                    c.is_hovered = c.rect.collidepoint(event.pos)

            # Clic en cartas
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for c in self.cards:
                    if c.rect.collidepoint(event.pos):
                        self._on_card_clicked(c)
                        break

    def _on_card_clicked(self, card: Card):
        """Gestiona el intento de seleccionar una carta y aplica las reglas del autómata."""
        # 1. Si está esperando a que se volteen cartas erróneas
        if self.mismatch_wait_timer > 0.0:
            self._register_invalid_move("Carta tocada durante espera de animación ('x')")
            return

        # 2. Si la carta ya está emparejada o ya está boca arriba
        if not card.can_click():
            self._register_invalid_move("Carta ya descubierta o en juego ('x')")
            return

        # 3. Primera carta del turno
        if self.first_selected is None:
            self.first_selected = card
            card.flip_up()
            self.sound.play("flip")
            self.status_message = f"Primera carta volteada: {card.pair_id}. Busca su pareja."
            self.status_message_color = (241, 196, 15)
            return

        # 4. Segunda carta del turno (no puede ser la misma primera carta)
        if card == self.first_selected:
            self._register_invalid_move("No puedes volver a pulsar la misma carta ('x')")
            return

        self.second_selected = card
        card.flip_up()
        self.sound.play("flip")

        # Comparar las dos cartas
        if self.first_selected.pair_id == self.second_selected.pair_id:
            self._handle_match()
        else:
            self._handle_mismatch()

    def _register_invalid_move(self, reason: str):
        """Registra una jugada inválida (símbolo 'x') en los autómatas."""
        self.total_invalids += 1
        res = self.automata.step("x")
        self.sound.play("invalid")
        self.status_message = f"Jugada inválida ('x'): {reason}"
        self.status_message_color = (243, 156, 18)

    def _handle_match(self):
        """Gestiona un acierto ('a'): las cartas quedan fijadas y el AFD avanza."""
        self.first_selected.set_matched()
        self.second_selected.set_matched()
        self.total_matches += 1

        res = self.automata.step("a")
        self.sound.play("match")

        self.status_message = f"¡Par coincidente encontrado ({self.first_selected.pair_id})! Progreso en AFD: {self.automata.dfa_state}"
        self.status_message_color = (46, 204, 113)

        self.first_selected = None
        self.second_selected = None

        # Comprobar si se completó la partida (AFD en estado de aceptación final)
        if self.automata.is_victory:
            self._handle_victory()

    def _handle_mismatch(self):
        """Gestiona un error ('e'): descuenta puntos y desapila una vida en el AP."""
        self.total_errors += 1
        self.score = max(0, self.score - 40)

        res = self.automata.step("e")
        self.sound.play("error")

        self.status_message = f"¡No coinciden! -40 puntos. Vida desapilada del AP ({self.automata.lives} restantes)."
        self.status_message_color = (231, 76, 60)

        # Esperar un momento antes de voltearlas hacia abajo
        self.mismatch_wait_timer = 0.85

        # Comprobar si se consumieron las 5 vidas (Pila vacía en el AP)
        if self.automata.is_defeat_by_errors:
            self._handle_defeat_by_errors()

    def _handle_victory(self):
        """Desencadena el final de la partida por Victoria."""
        self.state = STATE_VICTORY
        self.sound.stop_music()
        self.sound.play("win")

        mins_spent = int((self.time_mode_seconds - self.time_remaining) // 60)
        secs_spent = int((self.time_mode_seconds - self.time_remaining) % 60)
        time_spent_str = f"{mins_spent:02d}:{secs_spent:02d}"

        lines = [
            f"## ¡ENHORABUENA! HAS COMPLETADO EL MEMOTEST",
            f"• Puntaje Final: {self.score} puntos",
            f"• Tiempo empleado: {time_spent_str}",
            f"• Errores cometidos: {self.total_errors} (Vidas conservadas: {self.automata.lives}/5)",
            f"• Jugadas inválidas (x): {self.total_invalids}",
            f"• Estado del AFD: {self.automata.dfa_state} (ESTADO DE ACEPTACIÓN)",
            f"• Cadena procesada w: {self.automata.word_history}",
            f"El autómata determinista validó con éxito todos los aciertos requeridos.",
        ]

        self.active_modal = ModalDialog(
            width=620,
            height=390,
            screen_size=(self.screen_width, self.screen_height),
            title="¡VICTORIA!",
            content_lines=lines,
            buttons=[
                ("Jugar Otra Vez", self.start_game),
                ("Menú Principal", self.go_to_menu),
            ],
            title_color=(46, 204, 113),
        )

    def _handle_defeat_by_errors(self):
        """Desencadena el fin de juego cuando se consumen las 5 vidas (Pila vacía en AP)."""
        self.state = STATE_GAME_OVER
        self.score = 0
        self.sound.stop_music()
        self.sound.play("lose")

        lines = [
            f"## LÍMITE DE ERRORES ALCANZADO (5 FALLOS)",
            f"• El Autómata de Pila (AP) consumió todas las 'V' de la pila.",
            f"• Se ejecutó la transición λ, Z ; λ alcanzando el estado q2.",
            f"• Condición de aceptación por PILA VACÍA cumplida (Derrota formal).",
            f"• Puntaje final: 0 puntos",
            f"• Aciertos logrados: {self.automata.pairs_found} / {self.automata.pairs_count}",
            f"• Cadena procesada w: {self.automata.word_history}",
        ]

        self.active_modal = ModalDialog(
            width=620,
            height=370,
            screen_size=(self.screen_width, self.screen_height),
            title="FIN DEL JUEGO (DERROTA)",
            content_lines=lines,
            buttons=[
                ("Reintentar", self.start_game),
                ("Menú Principal", self.go_to_menu),
            ],
            title_color=(231, 76, 60),
        )

    def _handle_defeat_by_time(self):
        """Desencadena el fin de juego por tiempo agotado."""
        self.state = STATE_GAME_OVER
        self.score = 0
        self.sound.stop_music()
        self.sound.play("lose")

        lines = [
            f"## TIEMPO AGOTADO (00:00)",
            f"• El temporizador llegó a cero antes de completar el tablero.",
            f"• Según las reglas del proyecto, el puntaje general pasa a ser 0.",
            f"• Pares descubiertos: {self.automata.pairs_found} / {self.automata.pairs_count}",
            f"• Errores cometidos: {self.total_errors}",
            f"• Cadena procesada w: {self.automata.word_history}",
        ]

        self.active_modal = ModalDialog(
            width=620,
            height=350,
            screen_size=(self.screen_width, self.screen_height),
            title="TIEMPO AGOTADO",
            content_lines=lines,
            buttons=[
                ("Reintentar", self.start_game),
                ("Menú Principal", self.go_to_menu),
            ],
            title_color=(231, 76, 60),
        )

    def show_theoretical_info(self):
        """Muestra el diálogo explicativo de los modelos teóricos y el equipo."""
        lines = [
            f"## FUNDAMENTOS TEÓRICOS DE INFORMÁTICA - GRUPO N°2",
            f"Integrantes: Alexis Mariqueo, Cesar Millavanque, Daniel Enegron, Kadir Martinez (2026)",
            f"• Alfabeto de Entrada: Σ = {{a, e, x}} (a: acierto, e: error, x: inválido)",
            f"• AFD de Progreso: Quíntupla (Σ, Q, δ, q0, F). Estados {{q0..qN, q_sumidero}}.",
            f"  Avanza únicamente con el símbolo 'a'. Los errores y jugadas inválidas permanecen en el estado.",
            f"• AP de Control de Vidas: Estados {{q0, q1, q2}}, Alfabeto Pila {{Z, V}}.",
            f"  Inicia con 5 vidas (VVVVVZ). Cada error 'e' desapila una 'V'. Al 5to error, se desapila 'Z'",
            f"  y la pila queda totalmente vacía (Aceptación por Pila Vacía = Derrota).",
            f"• Expresión Regular Ganadora (Fácil): (e+x)* a (e+x)* a (e+x)* a (e+x)* a",
        ]

        self.active_modal = ModalDialog(
            width=700,
            height=430,
            screen_size=(self.screen_width, self.screen_height),
            title="FUNDAMENTOS TEÓRICOS (AUTÓMATAS)",
            content_lines=lines,
            buttons=[
                ("Entendido / Volver", lambda: setattr(self, "active_modal", None)),
            ],
            title_color=(241, 196, 15),
        )

    def update(self, dt: float):
        """Actualiza el temporizador, animaciones y transiciones temporales."""
        # Actualizar cartas siempre para que completen sus animaciones de volteo
        for c in self.cards:
            c.update(dt)

        if self.state == STATE_PLAYING:
            # 1. Temporizador de cuenta regresiva
            self.time_remaining -= dt
            if self.time_remaining <= 0.0:
                self.time_remaining = 0.0
                self._handle_defeat_by_time()
                return

            # 2. Temporizador de espera tras error
            if self.mismatch_wait_timer > 0.0:
                self.mismatch_wait_timer -= dt
                if self.mismatch_wait_timer <= 0.0:
                    self.mismatch_wait_timer = 0.0
                    if self.first_selected:
                        self.first_selected.flip_down()
                        self.sound.play("flip")
                    if self.second_selected:
                        self.second_selected.flip_down()
                    self.first_selected = None
                    self.second_selected = None

    def draw(self, surface: pygame.Surface):
        """Renderiza la pantalla activa."""
        surface.fill((16, 20, 30))

        if self.state == STATE_MENU:
            self._draw_menu(surface)
        else:
            self._draw_game_screen(surface)

        # Si hay una ventana modal emergente
        if self.active_modal:
            self.active_modal.draw(surface)

    def _draw_menu(self, surface: pygame.Surface):
        """Dibuja la pantalla inicial del menú."""
        center_x = self.screen_width // 2

        # Cabecera Institucional
        font_sub = get_font(13, bold=False)
        sub_surf = font_sub.render(
            "UNIVERSIDAD NACIONAL DE LA PATAGONIA SAN JUAN BOSCO — FUNDAMENTOS TEÓRICOS DE INFORMÁTICA",
            True,
            (140, 160, 190),
        )
        surface.blit(sub_surf, sub_surf.get_rect(center=(center_x, 60)))

        # Título Principal
        font_title = get_font(38, bold=True)
        title_surf = font_title.render("JUEGO DE LA MEMORIA (MEMOTEST)", True, (236, 240, 241))
        surface.blit(title_surf, title_surf.get_rect(center=(center_x, 110)))

        # Subtítulo de Autómatas
        font_model = get_font(16, bold=True)
        model_surf = font_model.render(
            "Modelado Formal mediante Autómata Finito Determinista (AFD) y Autómata de Pila (AP)",
            True,
            (52, 152, 219),
        )
        surface.blit(model_surf, model_surf.get_rect(center=(center_x, 150)))

        # Cuadro de Integrantes (Grupo N°2)
        group_rect = pygame.Rect(center_x - 300, 185, 600, 70)
        pygame.draw.rect(surface, (23, 28, 42), group_rect, border_radius=10)
        pygame.draw.rect(surface, (45, 55, 78), group_rect, width=1, border_radius=10)

        g_title = get_font(13, bold=True).render("GRUPO N°2 (2026):", True, (241, 196, 15))
        surface.blit(g_title, g_title.get_rect(center=(center_x, 205)))

        members = "Alexis Mariqueo  •  Cesar Millavanque  •  Daniel Enegron  •  Kadir Martinez"
        m_surf = get_font(14, bold=False).render(members, True, (210, 225, 245))
        surface.blit(m_surf, m_surf.get_rect(center=(center_x, 230)))

        # Etiquetas de selectores
        lbl_diff = get_font(15, bold=True).render("Selecciona la Dificultad del Tablero:", True, (220, 230, 242))
        surface.blit(lbl_diff, (center_x - 220, 252))
        self.diff_selector.draw(surface)

        lbl_time = get_font(15, bold=True).render("Selecciona el Modo de Tiempo:", True, (220, 230, 242))
        surface.blit(lbl_time, (center_x - 220, 332))
        self.time_selector.draw(surface)

        # Botones de inicio, sonido, teoría y salir
        self.btn_start.draw(surface)
        self.btn_sound.draw(surface)
        self.btn_menu_theory.draw(surface)
        self.btn_quit.draw(surface)

    def _draw_game_screen(self, surface: pygame.Surface):
        """Dibuja la pantalla de juego con el tablero y el panel de autómatas."""
        # 1. Barra superior
        self._draw_top_bar(surface)

        # 2. Área del tablero de cartas
        board_panel = pygame.Rect(20, 80, 780, 620)
        pygame.draw.rect(surface, (21, 26, 38), board_panel, border_radius=12)
        pygame.draw.rect(surface, (40, 50, 72), board_panel, width=1, border_radius=12)

        # Dibujar cada carta
        for c in self.cards:
            c.draw(surface)

        # 3. Panel derecho: HUD de estadísticas
        self._draw_hud(surface)

        # 4. Panel derecho: Historial de la cadena de entrada
        self.word_view.draw(surface, self.automata.word_history, self.automata.last_symbol)

        # 5. Panel derecho: Visualizador del AFD
        self.dfa_view.draw(
            surface,
            self.automata.dfa_state,
            self.automata.pairs_count,
            self.automata.last_transition_dfa,
        )

        # 6. Panel derecho: Visualizador de la Pila (AP)
        self.stack_view.draw(
            surface,
            self.automata.pda_stack,
            self.automata.pda_state,
            self.automata.lives,
            self.automata.last_transition_pda,
        )

        # 7. Botones de acción
        self.btn_restart.draw(surface)
        self.btn_menu.draw(surface)
        self.btn_hud_sound.draw(surface)
        self.btn_theory.draw(surface)

        # 8. Barra de mensaje de estado
        msg_panel = pygame.Rect(820, 620, 440, 45)
        pygame.draw.rect(surface, (23, 28, 42), msg_panel, border_radius=8)
        pygame.draw.rect(surface, (45, 55, 78), msg_panel, width=1, border_radius=8)

        msg_font = get_font(12, bold=True)
        msg_surf = msg_font.render(self.status_message, True, self.status_message_color)
        surface.blit(msg_surf, msg_surf.get_rect(center=msg_panel.center))

    def _draw_top_bar(self, surface: pygame.Surface):
        """Barra de encabezado superior."""
        header_rect = pygame.Rect(0, 0, self.screen_width, 60)
        pygame.draw.rect(surface, (23, 28, 42), header_rect)
        pygame.draw.line(surface, (45, 55, 78), (0, 60), (self.screen_width, 60), 2)

        title_font = get_font(20, bold=True)
        title_surf = title_font.render("Juego de la Memoria (Memotest)", True, (236, 240, 241))
        surface.blit(title_surf, (24, 18))

        sub_font = get_font(13, bold=False)
        sub_text = "FTI - UNPSJB | Grupo N°2 (A. Mariqueo, C. Millavanque, D. Enegron, K. Martinez)"
        sub_surf = sub_font.render(sub_text, True, (140, 160, 190))
        surface.blit(sub_surf, (self.screen_width - sub_surf.get_width() - 24, 22))

    def _draw_hud(self, surface: pygame.Surface):
        """Dibuja el panel con Puntaje, Tiempo y Vidas."""
        pygame.draw.rect(surface, (23, 28, 42), self.hud_rect, border_radius=10)
        pygame.draw.rect(surface, (45, 55, 78), self.hud_rect, width=1, border_radius=10)

        # 1. Puntaje
        lbl_font = get_font(12, bold=False)
        val_font = get_font(20, bold=True)

        lbl_score = lbl_font.render("PUNTAJE", True, (140, 155, 180))
        val_score = val_font.render(f"{self.score} pts", True, (241, 196, 15))
        surface.blit(lbl_score, (self.hud_rect.x + 18, self.hud_rect.y + 12))
        surface.blit(val_score, (self.hud_rect.x + 18, self.hud_rect.y + 34))

        # 2. Tiempo Restante
        mins = int(self.time_remaining // 60)
        secs = int(self.time_remaining % 60)
        time_str = f"{mins:02d}:{secs:02d}"
        time_col = (231, 76, 60) if self.time_remaining <= 60 else (52, 152, 219)

        lbl_time = lbl_font.render("TIEMPO", True, (140, 155, 180))
        val_time = val_font.render(time_str, True, time_col)
        surface.blit(lbl_time, (self.hud_rect.x + 160, self.hud_rect.y + 12))
        surface.blit(val_time, (self.hud_rect.x + 160, self.hud_rect.y + 34))

        # 3. Vidas Restantes
        lbl_lives = lbl_font.render("VIDAS (PILA)", True, (140, 155, 180))
        val_lives = val_font.render(f"{self.automata.lives} / 5", True, (46, 204, 113) if self.automata.lives > 1 else (231, 76, 60))
        surface.blit(lbl_lives, (self.hud_rect.x + 300, self.hud_rect.y + 12))
        surface.blit(val_lives, (self.hud_rect.x + 300, self.hud_rect.y + 34))

