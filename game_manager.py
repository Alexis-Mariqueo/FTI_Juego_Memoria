"""
Módulo de Gestión de Juego (GameManager) para el Memotest con Autómatas.
Controla el flujo de estados, cronómetro, puntuación, interacción con cartas,
reproducción de sonidos y sincronización con el controlador de autómatas.
"""

import json
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
    GameSettingsModal,
    ModalDialog,
    PlaySetupModal,
    ScreenSettingsModal,
    SegmentedSelector,
    SettingsHubModal,
    SoundSettingsModal,
    StackVisualizer,
    WordHistoryView,
    draw_cozy_panel,
    get_font,
    COZY_GREEN_SAGE,
    COZY_GREEN_HOVER,
    COZY_TERRACOTTA,
    COZY_TERRACOTTA_HOVER,
    COZY_AMBER,
    COZY_AMBER_HOVER,
    COZY_SLATE_PURPLE,
    COZY_SLATE_PURPLE_HOVER,
    COZY_TEXT_GOLD,
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
        self.mostrar_cartas_al_inicio = False
        self.game_config_path = "game_settings.json"
        self._load_game_config()

        # Variables de partida
        self.score = 200
        self.time_remaining = self.time_mode_seconds
        self.total_errors = 0
        self.total_matches = 0
        self.total_invalids = 0
        self.status_message = "Selecciona dos cartas para buscar una coincidencia."
        self.status_message_color = (244, 232, 222)

        # Cartas y tablero
        self.cards: List[Card] = []
        self.first_selected: Optional[Card] = None
        self.second_selected: Optional[Card] = None
        self.mismatch_wait_timer: float = 0.0
        self.preview_time_remaining: Optional[float] = None

        # Autómatas y audio
        self.automata = AutomataGameController(pairs_count=4)
        self.sound = SoundManager(enabled=True)
        self.is_running = True

        # Iniciar música del menú principal
        self.sound.play_menu_music()

        # Configuración de pantalla completa adaptativa
        self.is_fullscreen = False
        self.display_config_path = "display_settings.json"
        self._load_display_config()

        # Fondos Pixel Art acogedores
        self.menu_bg: Optional[pygame.Surface] = None
        self.game_bg: Optional[pygame.Surface] = None
        self._load_backgrounds()

        # Recursos gráficos de cartas
        self.front_images: Dict[str, pygame.Surface] = {}
        self.back_image: Optional[pygame.Surface] = None
        self._load_card_assets()

        # Componentes UI de la pantalla de juego
        self.hud_rect = pygame.Rect(820, 80, 440, 76)
        self.word_view = WordHistoryView(pygame.Rect(820, 166, 440, 68))
        self.dfa_view = DFAGraphVisualizer(pygame.Rect(820, 244, 440, 98))
        self.stack_view = StackVisualizer(pygame.Rect(820, 352, 440, 206))
        
        # Botones HUD en juego (4 botones compactos con estética pixel art cozy)
        btn_y = 568
        btn_w = 102
        gap = 10
        self.btn_restart = Button(
            pygame.Rect(820, btn_y, btn_w, 40),
            "Reiniciar",
            callback=self.restart_current_game,
            bg_color=COZY_GREEN_SAGE,
            hover_color=COZY_GREEN_HOVER,
            font_size=13,
        )
        self.btn_menu = Button(
            pygame.Rect(820 + btn_w + gap, btn_y, btn_w, 40),
            "Menú",
            callback=self.go_to_menu,
            bg_color=COZY_SLATE_PURPLE,
            hover_color=COZY_SLATE_PURPLE_HOVER,
            font_size=13,
        )
        self.btn_hud_sound = Button(
            pygame.Rect(820 + (btn_w + gap) * 2, btn_y, btn_w, 40),
            "Ajustes",
            callback=self.open_settings_hub,
            bg_color=COZY_AMBER,
            hover_color=COZY_AMBER_HOVER,
            font_size=13,
        )
        self.btn_theory = Button(
            pygame.Rect(820 + (btn_w + gap) * 3, btn_y, btn_w, 40),
            "Teoría FTI",
            callback=self.show_theoretical_info,
            bg_color=COZY_TERRACOTTA,
            hover_color=COZY_TERRACOTTA_HOVER,
            font_size=13,
        )

        # Ventana modal activa (Victoria, Derrota o Información)
        self.active_modal: Optional[ModalDialog] = None

        # Componentes del Menú Principal
        self._init_menu_components()

    def _load_backgrounds(self):
        """Carga y adapta los fondos en pixel art para el menú y el juego."""
        menu_path = os.path.join("assets", "backgrounds", "menu_bg.png")
        game_path = os.path.join("assets", "backgrounds", "game_bg.png")

        try:
            if os.path.exists(menu_path):
                img = pygame.image.load(menu_path).convert()
                self.menu_bg = pygame.transform.scale(img, (self.screen_width, self.screen_height))
        except Exception as e:
            print(f"Aviso: No se pudo cargar menu_bg.png: {e}")
            self.menu_bg = None

        try:
            if os.path.exists(game_path):
                img = pygame.image.load(game_path).convert()
                self.game_bg = pygame.transform.scale(img, (self.screen_width, self.screen_height))
        except Exception as e:
            print(f"Aviso: No se pudo cargar game_bg.png: {e}")
            self.game_bg = None

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

        # Fila 1: Botón para Jugar (abre la pantalla de preparación de partida)
        self.btn_start = Button(
            rect=pygame.Rect(center_x - 220, 294, 440, 52),
            text="JUGAR",
            callback=self.open_play_modal,
            bg_color=COZY_GREEN_SAGE,
            hover_color=COZY_GREEN_HOVER,
            font_size=20,
            border_radius=10,
        )

        # Fila 2: Botón de Ajustes (Sonido, Pantalla, Partida) y Botón de Fundamentos Teóricos
        self.btn_sound = Button(
            rect=pygame.Rect(center_x - 220, 360, 215, 44),
            text="Ajustes",
            callback=self.open_settings_hub,
            bg_color=COZY_AMBER,
            hover_color=COZY_AMBER_HOVER,
            font_size=15,
            border_radius=8,
        )

        self.btn_menu_theory = Button(
            rect=pygame.Rect(center_x + 5, 360, 215, 44),
            text="Fundamentos Teóricos",
            callback=self.show_theoretical_info,
            bg_color=COZY_SLATE_PURPLE,
            hover_color=COZY_SLATE_PURPLE_HOVER,
            font_size=14,
            border_radius=8,
        )

        # Fila 3: Botón para Salir del Juego
        self.btn_quit = Button(
            rect=pygame.Rect(center_x - 220, 418, 440, 42),
            text="Salir del Juego",
            callback=self.quit_game,
            bg_color=COZY_TERRACOTTA,
            hover_color=COZY_TERRACOTTA_HOVER,
            font_size=14,
            border_radius=8,
        )

    def _load_display_config(self):
        """Carga la configuración de pantalla completa desde display_settings.json."""
        if os.path.exists(self.display_config_path):
            try:
                with open(self.display_config_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.is_fullscreen = bool(data.get("fullscreen", False))
            except Exception as e:
                print(f"Aviso: No se pudo leer {self.display_config_path}: {e}")
        else:
            self._save_display_config()

    def _save_display_config(self):
        """Guarda la configuración de pantalla completa en display_settings.json."""
        try:
            with open(self.display_config_path, "w", encoding="utf-8") as f:
                json.dump({"fullscreen": self.is_fullscreen}, f, indent=4)
        except Exception as e:
            print(f"Error guardando {self.display_config_path}: {e}")

    def apply_display_mode(self):
        """Aplica la resolución con escalado automático para cualquier pantalla."""
        flags = pygame.SCALED
        if self.is_fullscreen:
            flags |= pygame.FULLSCREEN
        pygame.display.set_mode((self.screen_width, self.screen_height), flags)

    def open_play_modal(self):
        """Abre la pantalla de configuración previa al juego (dificultad, tiempo, previsualización)."""
        self.active_modal = PlaySetupModal(
            screen_size=(self.screen_width, self.screen_height),
            initial_difficulty=self.difficulty,
            initial_time=self.time_mode_seconds,
            mostrar_cartas=self.mostrar_cartas_al_inicio,
            on_change_difficulty=lambda d: setattr(self, "difficulty", d),
            on_change_time=lambda t: setattr(self, "time_mode_seconds", t),
            on_change_preview=self.set_card_preview,
            on_start_game=self.start_game,
            on_close=lambda: setattr(self, "active_modal", None),
        )

    def open_settings_hub(self):
        """Abre el menú principal de Ajustes (con botones para Ajuste de Sonido, Ajuste de Pantalla y Ajuste de Partida)."""
        self.active_modal = SettingsHubModal(
            screen_size=(self.screen_width, self.screen_height),
            on_open_sound=self.open_sound_settings,
            on_open_screen=self.open_screen_settings,
            on_open_game=self.open_game_settings,
            on_close=lambda: setattr(self, "active_modal", None),
        )

    def open_sound_settings(self):
        """Abre la ventana modal interactiva de ajustes de audio. Guardar y Salir regresa al hub de ajustes."""
        self.active_modal = SoundSettingsModal(
            screen_size=(self.screen_width, self.screen_height),
            sound_manager=self.sound,
            on_close=self.open_settings_hub,
        )

    def open_game_settings(self):
        """Abre la ventana modal de ajustes de partida (opción de mostrar cartas al inicio)."""
        self.active_modal = GameSettingsModal(
            screen_size=(self.screen_width, self.screen_height),
            mostrar_cartas=self.mostrar_cartas_al_inicio,
            on_change_preview=self.set_card_preview,
            on_close=self.open_settings_hub,
        )

    def open_screen_settings(self):
        """Abre la ventana modal de ajustes de pantalla (modo ventana o pantalla completa adaptativa)."""
        self.active_modal = ScreenSettingsModal(
            screen_size=(self.screen_width, self.screen_height),
            is_fullscreen=self.is_fullscreen,
            on_save_and_exit=self.on_screen_settings_saved,
        )

    def on_screen_settings_saved(self, new_fullscreen: bool):
        """Aplica el nuevo modo de pantalla, persiste en JSON y regresa al menú de ajustes."""
        if new_fullscreen != self.is_fullscreen:
            self.is_fullscreen = new_fullscreen
            self.apply_display_mode()
        self._save_display_config()
        self.open_settings_hub()

    def _load_game_config(self):
        """Carga los ajustes de partida (previsualización de cartas) desde game_settings.json."""
        if os.path.exists(self.game_config_path):
            try:
                with open(self.game_config_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.mostrar_cartas_al_inicio = bool(data.get("mostrar_cartas_al_inicio", False))
            except Exception as e:
                print(f"Aviso: No se pudo leer {self.game_config_path}: {e}")
        else:
            self._save_game_config()

    def _save_game_config(self):
        """Guarda los ajustes de partida en game_settings.json."""
        try:
            with open(self.game_config_path, "w", encoding="utf-8") as f:
                json.dump({"mostrar_cartas_al_inicio": self.mostrar_cartas_al_inicio}, f, indent=4)
        except Exception as e:
            print(f"Error guardando {self.game_config_path}: {e}")

    def set_card_preview(self, enabled: bool):
        self.mostrar_cartas_al_inicio = enabled
        self._save_game_config()

    def quit_game(self):
        """Cierra la aplicación de forma limpia y asegura el guardado de configuraciones JSON."""
        try:
            self.sound.save_config()
            self._save_display_config()
            self._save_game_config()
        except Exception:
            pass
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
        self.preview_time_remaining= None
        if self.mostrar_cartas_al_inicio:
            self.preview_time_remaining = 3.0
            self.status_message= "Memoriza las cartas.."
            for card in self.cards:
                card.flip_up()
        
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

        if self.preview_time_remaining is not None:
            return  # Ignorar clics durante la previsualización de cartas

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
            title_color=COZY_GREEN_SAGE,
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
            title_color=COZY_TERRACOTTA,
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
            title_color=COZY_TERRACOTTA,
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
            title_color=COZY_TEXT_GOLD,
        )

    def update(self, dt: float):
        """Actualiza el temporizador, animaciones y transiciones temporales."""
        # Actualizar cartas siempre para que completen sus animaciones de volteo
        for c in self.cards:
            c.update(dt)

        if self.state == STATE_PLAYING:
            if self.preview_time_remaining is not None:
                if self.preview_time_remaining > 0:
                    self.preview_time_remaining = max(
                        0.0, self.preview_time_remaining - dt
                    )
                    if self.preview_time_remaining == 0:
                        for card in self.cards:
                            card.flip_down()
                elif all(card.can_click() for card in self.cards):
                    self.preview_time_remaining = None
                    self.status_message = "¡Comienza el juego! Selecciona dos cartas para buscar una coincidencia."
                return  # No actualizar temporizador ni esperar errores durante la previsualización
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
        """Renderiza la pantalla activa con fondos pixel art y paneles cozy."""
        if self.state == STATE_MENU:
            self._draw_menu(surface)
        else:
            self._draw_game_screen(surface)

        # Si hay una ventana modal emergente
        if self.active_modal:
            self.active_modal.draw(surface)

    def _draw_menu(self, surface: pygame.Surface):
        """Dibuja la pantalla inicial del menú con fondo pixel art cozy y paneles cálidos."""
        if self.menu_bg:
            surface.blit(self.menu_bg, (0, 0))
            # Velo ambiental cálido translúcido para asegurar máxima legibilidad y ambiente acogedor
            dim_overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
            dim_overlay.fill((30, 20, 26, 120))
            surface.blit(dim_overlay, (0, 0))
        else:
            surface.fill((40, 30, 38))

        center_x = self.screen_width // 2

        # Panel contenedor central del menú estilo tarjeta cálida selective outline
        menu_box = pygame.Rect(center_x - 320, 80, 640, 425)
        draw_cozy_panel(surface, menu_box, border_radius=16, bg_color=(44, 34, 42), border_color=(92, 72, 80), alpha=235)

        # Cabecera Institucional
        font_sub = get_font(12, bold=False)
        sub_surf = font_sub.render(
            "UNIVERSIDAD NACIONAL DE LA PATAGONIA SAN JUAN BOSCO — FUNDAMENTOS TEÓRICOS DE INFORMÁTICA",
            True,
            (215, 195, 185),
        )
        surface.blit(sub_surf, sub_surf.get_rect(center=(center_x, 106)))

        # Título Principal
        font_title = get_font(35, bold=True)
        title_surf = font_title.render("JUEGO DE LA MEMORIA (MEMOTEST)", True, COZY_TEXT_GOLD)
        surface.blit(title_surf, title_surf.get_rect(center=(center_x, 145)))

        # Subtítulo de Autómatas
        font_model = get_font(14, bold=True)
        model_surf = font_model.render(
            "Modelado Formal mediante Autómata Finito Determinista (AFD) y Autómata de Pila (AP)",
            True,
            (245, 195, 165),
        )
        surface.blit(model_surf, model_surf.get_rect(center=(center_x, 180)))

        # Cuadro de Integrantes (Grupo N°2)
        group_rect = pygame.Rect(center_x - 280, 204, 560, 64)
        draw_cozy_panel(surface, group_rect, border_radius=10, bg_color=(52, 40, 48), border_color=(98, 76, 86), alpha=240)

        g_title = get_font(13, bold=True).render("GRUPO N°2 (2026):", True, COZY_TEXT_GOLD)
        surface.blit(g_title, g_title.get_rect(center=(center_x, 220)))

        members = "Alexis Mariqueo  •  Cesar Millavanque  •  Daniel Enegron  •  Kadir Martinez"
        m_surf = get_font(14, bold=False).render(members, True, (244, 235, 226))
        surface.blit(m_surf, m_surf.get_rect(center=(center_x, 246)))

        # Botones de inicio, sonido, teoría y salir
        self.btn_start.draw(surface)
        self.btn_sound.draw(surface)
        self.btn_menu_theory.draw(surface)
        self.btn_quit.draw(surface)

    def _draw_game_screen(self, surface: pygame.Surface):
        """Dibuja la pantalla de juego con fondo pixel art, tablero y panel de autómatas."""
        if self.game_bg:
            surface.blit(self.game_bg, (0, 0))
            # Velo ambiental translúcido suave
            dim_overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
            dim_overlay.fill((28, 18, 24, 115))
            surface.blit(dim_overlay, (0, 0))
        else:
            surface.fill((40, 30, 38))

        # 1. Barra superior
        self._draw_top_bar(surface)

        # 2. Área del tablero de cartas con panel cálido selective outline
        board_panel = pygame.Rect(20, 80, 780, 620)
        draw_cozy_panel(surface, board_panel, border_radius=12, bg_color=(42, 32, 40), border_color=(88, 68, 76), alpha=235)

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
        draw_cozy_panel(surface, msg_panel, border_radius=8, bg_color=(46, 36, 44), border_color=(90, 70, 78), alpha=240)

        msg_font = get_font(12, bold=True)
        msg_surf = msg_font.render(self.status_message, True, self.status_message_color)
        surface.blit(msg_surf, msg_surf.get_rect(center=msg_panel.center))

    def _draw_top_bar(self, surface: pygame.Surface):
        """Barra de encabezado superior con diseño cozy cálido."""
        header_rect = pygame.Rect(0, 0, self.screen_width, 60)
        draw_cozy_panel(surface, header_rect, border_radius=0, bg_color=(42, 32, 40), border_color=(84, 65, 74), alpha=245)
        pygame.draw.line(surface, (98, 76, 86), (0, 60), (self.screen_width, 60), 2)

        title_font = get_font(20, bold=True)
        title_surf = title_font.render("Juego de la Memoria (Memotest)", True, COZY_TEXT_GOLD)
        surface.blit(title_surf, (24, 18))

        sub_font = get_font(13, bold=False)
        sub_text = "FTI - UNPSJB | Grupo N°2 (A. Mariqueo, C. Millavanque, D. Enegron, K. Martinez)"
        sub_surf = sub_font.render(sub_text, True, (215, 195, 185))
        surface.blit(sub_surf, (self.screen_width - sub_surf.get_width() - 24, 22))

    def _draw_hud(self, surface: pygame.Surface):
        """Dibuja el panel con Puntaje, Tiempo y Vidas con estética pastel cálida."""
        draw_cozy_panel(surface, self.hud_rect, border_radius=10, bg_color=(46, 36, 44), border_color=(90, 70, 78), alpha=240)

        # 1. Puntaje
        lbl_font = get_font(12, bold=False)
        val_font = get_font(20, bold=True)

        lbl_score = lbl_font.render("PUNTAJE", True, (200, 180, 172))
        val_score = val_font.render(f"{self.score} pts", True, COZY_TEXT_GOLD)
        surface.blit(lbl_score, (self.hud_rect.x + 18, self.hud_rect.y + 12))
        surface.blit(val_score, (self.hud_rect.x + 18, self.hud_rect.y + 34))

        # 2. Tiempo Restante
        mins = int(self.time_remaining // 60)
        secs = int(self.time_remaining % 60)
        time_str = f"{mins:02d}:{secs:02d}"
        time_col = COZY_TERRACOTTA if self.time_remaining <= 60 else (138, 188, 218)

        lbl_time = lbl_font.render("TIEMPO", True, (200, 180, 172))
        val_time = val_font.render(time_str, True, time_col)
        surface.blit(lbl_time, (self.hud_rect.x + 160, self.hud_rect.y + 12))
        surface.blit(val_time, (self.hud_rect.x + 160, self.hud_rect.y + 34))

        # 3. Vidas Restantes
        lbl_lives = lbl_font.render("VIDAS (PILA)", True, (200, 180, 172))
        val_lives = val_font.render(
            f"{self.automata.lives} / 5",
            True,
            COZY_GREEN_SAGE if self.automata.lives > 1 else COZY_TERRACOTTA,
        )
        surface.blit(lbl_lives, (self.hud_rect.x + 300, self.hud_rect.y + 12))
        surface.blit(val_lives, (self.hud_rect.x + 300, self.hud_rect.y + 34))

