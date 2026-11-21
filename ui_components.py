"""
Componentes gráficos y visualizadores teóricos para la interfaz del Memotest.
Estética: Pixel art cozy y cálido, iluminación ambiental suave, paleta de colores pastel y tierra,
sin bordes negros duros (lineless o selective outline).
Incluye visualizador gráfico del AFD, visualizador gráfico de la Pila (AP),
botones interactivos, panel de historial de símbolos y modales de diálogo.
"""

from typing import Callable, List, Optional, Tuple
import pygame

# Paleta global cozy (Pastel & Colores Tierra cálidos)
COZY_PANEL_BG = (48, 36, 44)
COZY_PANEL_BORDER = (88, 68, 76)
COZY_TEXT_MAIN = (252, 246, 238)
COZY_TEXT_MUTED = (205, 185, 175)
COZY_TEXT_GOLD = (248, 214, 138)
COZY_GREEN_SAGE = (128, 172, 132)
COZY_GREEN_HOVER = (146, 192, 150)
COZY_TERRACOTTA = (208, 112, 100)
COZY_TERRACOTTA_HOVER = (226, 128, 115)
COZY_AMBER = (235, 172, 102)
COZY_AMBER_HOVER = (248, 188, 120)
COZY_SLATE_PURPLE = (142, 118, 152)
COZY_SLATE_PURPLE_HOVER = (160, 136, 170)


def get_font(size: int, bold: bool = False) -> pygame.font.Font:
    """Retorna una fuente de sistema agradable o la fuente por defecto de Pygame."""
    try:
        return pygame.font.SysFont("Segoe UI", size, bold=bold)
    except Exception:
        return pygame.font.Font(None, size)


def draw_cozy_panel(
    surface: pygame.Surface,
    rect: pygame.Rect,
    border_radius: int = 10,
    bg_color: Tuple[int, int, int] = COZY_PANEL_BG,
    border_color: Tuple[int, int, int] = COZY_PANEL_BORDER,
    alpha: int = 225,
):
    """Dibuja un panel con estética pixel art cozy, bordes suaves y tinte ambiental cálido."""
    panel_surf = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    panel_surf.fill((*bg_color, alpha))
    surface.blit(panel_surf, rect.topleft)

    # Selective outline suave (sin bordes negros duros)
    pygame.draw.rect(surface, border_color, rect, width=1, border_radius=border_radius)

    # Línea superior de luz ambiental sutil
    if rect.width > 6:
        hi_rect = pygame.Rect(rect.x + 3, rect.y + 1, rect.width - 6, 1)
        hi_surf = pygame.Surface((hi_rect.width, 1), pygame.SRCALPHA)
        hi_surf.fill((255, 240, 220, 35))
        surface.blit(hi_surf, hi_rect.topleft)


class Button:
    """Botón interactivo con estética pixel art cozy, selective outline y relieve sutil."""

    def __init__(
        self,
        rect: pygame.Rect,
        text: str,
        callback: Optional[Callable] = None,
        bg_color: Tuple[int, int, int] = COZY_GREEN_SAGE,
        hover_color: Tuple[int, int, int] = COZY_GREEN_HOVER,
        text_color: Tuple[int, int, int] = COZY_TEXT_MAIN,
        font_size: int = 18,
        border_radius: int = 8,
    ):
        self.rect = rect
        self.text = text
        self.callback = callback
        self.bg_color = bg_color
        self.hover_color = hover_color
        self.text_color = text_color
        self.font = get_font(font_size, bold=True)
        self.border_radius = border_radius
        self.is_hovered = False
        self.is_active = False

    def handle_event(self, event: pygame.event.Event) -> bool:
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                if self.callback:
                    self.callback()
                return True
        return False

    def draw(self, surface: pygame.Surface):
        color = self.hover_color if self.is_hovered or self.is_active else self.bg_color

        # Sombra sutil cálida (sin negro duro)
        shadow_rect = self.rect.copy()
        shadow_rect.y += 2
        shadow_surf = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        shadow_surf.fill((32, 20, 26, 60))
        surface.blit(shadow_surf, shadow_rect.topleft)

        # Superficie principal
        pygame.draw.rect(surface, color, self.rect, border_radius=self.border_radius)

        # Selective outline: tono adaptativo más claro arriba y armónico alrededor
        border_color = (255, 246, 232, 110) if (self.is_hovered or self.is_active) else (
            max(0, color[0] - 28),
            max(0, color[1] - 28),
            max(0, color[2] - 28),
        )
        pygame.draw.rect(surface, border_color, self.rect, width=1, border_radius=self.border_radius)

        # Brillo superior sutil de iluminación ambiental
        if self.rect.width > 4:
            hi_rect = pygame.Rect(self.rect.x + 2, self.rect.y + 1, self.rect.width - 4, 2)
            hi_surf = pygame.Surface((hi_rect.width, 2), pygame.SRCALPHA)
            hi_surf.fill((255, 255, 255, 55 if self.is_hovered else 25))
            surface.blit(hi_surf, hi_rect.topleft)

        text_surf = self.font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)


class SegmentedSelector:
    """Selector estilo pills/tabs con estética cálida de madera y arcilla pastel."""

    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        options: List[Tuple[str, str]],  # [(label, value), ...]
        selected_value: str,
        on_change: Optional[Callable[[str], None]] = None,
    ):
        self.rect = pygame.Rect(x, y, width, height)
        self.options = options
        self.selected_value = selected_value
        self.on_change = on_change
        self.font = get_font(16, bold=True)
        self.sub_font = get_font(12, bold=False)

    def handle_event(self, event: pygame.event.Event) -> bool:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                seg_w = self.rect.width / len(self.options)
                idx = int((event.pos[0] - self.rect.x) / seg_w)
                idx = max(0, min(len(self.options) - 1, idx))
                val = self.options[idx][1]
                if val != self.selected_value:
                    self.selected_value = val
                    if self.on_change:
                        self.on_change(val)
                return True
        return False

    def draw(self, surface: pygame.Surface):
        # Contenedor con selective outline cálido
        draw_cozy_panel(surface, self.rect, border_radius=8, bg_color=(42, 32, 40), border_color=(84, 65, 74))

        seg_w = self.rect.width / len(self.options)
        for i, (label, val) in enumerate(self.options):
            seg_rect = pygame.Rect(
                int(self.rect.x + i * seg_w + 3),
                self.rect.y + 3,
                int(seg_w - 6),
                self.rect.height - 6,
            )
            is_selected = (val == self.selected_value)
            if is_selected:
                pygame.draw.rect(surface, (198, 126, 96), seg_rect, border_radius=6)
                pygame.draw.rect(surface, (250, 220, 196), seg_rect, width=1, border_radius=6)
                txt_color = (255, 252, 248)
            else:
                txt_color = (195, 178, 172)

            txt_surf = self.font.render(label, True, txt_color)
            txt_rect = txt_surf.get_rect(center=seg_rect.center)
            surface.blit(txt_surf, txt_rect)


class DFAGraphVisualizer:
    """Visualizador interactivo de los estados del AFD con colores pastel y halo suave."""

    def __init__(self, rect: pygame.Rect):
        self.rect = rect
        self.title_font = get_font(15, bold=True)
        self.state_font = get_font(13, bold=True)
        self.info_font = get_font(12, bold=False)

    def draw(
        self,
        surface: pygame.Surface,
        current_state: str,
        total_pairs: int,
        last_transition: str,
    ):
        draw_cozy_panel(surface, self.rect, border_radius=10, bg_color=(46, 36, 44), border_color=(90, 70, 78))

        # Título
        title_surf = self.title_font.render("AFD: Progreso de Aciertos", True, COZY_TEXT_GOLD)
        surface.blit(title_surf, (self.rect.x + 14, self.rect.y + 10))

        # Indicador de pares
        pairs_found = total_pairs if current_state == "q_sumidero" else (
            int(current_state.replace("q", "")) if current_state.startswith("q") and current_state != "q_sumidero" else 0
        )
        badge_text = f"{pairs_found} / {total_pairs} Pares"
        badge_surf = self.info_font.render(badge_text, True, (142, 198, 142) if pairs_found == total_pairs else (210, 190, 182))
        surface.blit(badge_surf, (self.rect.right - badge_surf.get_width() - 14, self.rect.y + 12))

        # Nodos de estados
        num_states = total_pairs + 1
        available_w = self.rect.width - 40
        node_radius = 16 if total_pairs == 4 else 13
        spacing = available_w / (num_states - 1) if num_states > 1 else available_w

        nodes_y = self.rect.y + 48

        # Línea de conexión de fondo en tono tierra suave
        line_start = (int(self.rect.x + 20), nodes_y)
        line_end = (int(self.rect.x + 20 + (num_states - 1) * spacing), nodes_y)
        pygame.draw.line(surface, (88, 68, 76), line_start, line_end, width=3)

        for i in range(num_states):
            st_name = f"q{i}"
            cx = int(self.rect.x + 20 + i * spacing)
            cy = nodes_y
            is_current = (current_state == st_name)
            is_final = (i == total_pairs)
            is_passed = False
            try:
                cur_num = int(current_state.replace("q", ""))
                is_passed = (i < cur_num)
            except ValueError:
                is_passed = True

            # Colores en paleta cálida pastel
            if is_current:
                bg_col = (138, 188, 142) if is_final else (238, 178, 108)
                border_col = (255, 246, 220)
                text_col = (42, 30, 25)
            elif is_passed:
                bg_col = (110, 156, 114) if is_final else (138, 112, 134)
                border_col = (142, 198, 142) if is_final else (168, 138, 162)
                text_col = (245, 238, 230)
            else:
                bg_col = (58, 45, 54)
                border_col = (88, 68, 76)
                text_col = (165, 145, 152)

            # Si es final, tiene doble círculo
            if is_final:
                pygame.draw.circle(surface, border_col, (cx, cy), node_radius + 4, width=2)

            # Halo de iluminación ambiental suave si es el nodo actual
            if is_current:
                glow_surf = pygame.Surface((node_radius * 4, node_radius * 4), pygame.SRCALPHA)
                pygame.draw.circle(glow_surf, (250, 210, 130, 55), (node_radius * 2, node_radius * 2), node_radius + 5)
                surface.blit(glow_surf, (cx - node_radius * 2, cy - node_radius * 2))

            pygame.draw.circle(surface, bg_col, (cx, cy), node_radius)
            pygame.draw.circle(surface, border_col, (cx, cy), node_radius, width=2)

            lbl = self.state_font.render(st_name, True, text_col)
            surface.blit(lbl, lbl.get_rect(center=(cx, cy)))

        # Detalle de última transición
        trans_surf = self.info_font.render(f"Última transición: {last_transition}", True, COZY_TEXT_GOLD)
        surface.blit(trans_surf, (self.rect.x + 14, self.rect.y + 74))


class StackVisualizer:
    """Visualizador interactivo de la Pila del Autómata de Pila (AP) con estética cálida."""

    def __init__(self, rect: pygame.Rect):
        self.rect = rect
        self.title_font = get_font(15, bold=True)
        self.elem_font = get_font(14, bold=True)
        self.info_font = get_font(12, bold=False)

    def draw(
        self,
        surface: pygame.Surface,
        stack: List[str],
        pda_state: str,
        lives: int,
        last_transition: str,
    ):
        draw_cozy_panel(surface, self.rect, border_radius=10, bg_color=(46, 36, 44), border_color=(90, 70, 78))

        # Cabecera
        title_surf = self.title_font.render("AP: Autómata de Pila (Vidas)", True, COZY_TEXT_GOLD)
        surface.blit(title_surf, (self.rect.x + 14, self.rect.y + 10))

        # Indicador de estado del AP
        st_color = (212, 112, 100) if pda_state == "q2" else (138, 178, 198)
        state_badge = self.info_font.render(f"Estado: {pda_state} | Vidas: {lives}/5", True, st_color)
        surface.blit(state_badge, (self.rect.right - state_badge.get_width() - 14, self.rect.y + 12))

        # Contenedor de la pila vertical
        box_w = 120
        box_h = 160
        box_x = self.rect.x + 20
        box_y = self.rect.y + 38

        # Soporte con textura cálida selective outline
        wall_col = (118, 92, 102)
        pygame.draw.line(surface, wall_col, (box_x, box_y), (box_x, box_y + box_h), width=3)
        pygame.draw.line(surface, wall_col, (box_x + box_w, box_y), (box_x + box_w, box_y + box_h), width=3)
        pygame.draw.line(surface, wall_col, (box_x - 3, box_y + box_h), (box_x + box_w + 3, box_y + box_h), width=4)

        elem_h = 22
        start_y = box_y + box_h - elem_h - 4

        if not stack:
            empty_msg = self.elem_font.render("[ PILA VACÍA ]", True, (212, 112, 100))
            surface.blit(empty_msg, empty_msg.get_rect(center=(box_x + box_w // 2, box_y + box_h // 2)))
        else:
            for i, sym in enumerate(stack):
                ey = start_y - (i * (elem_h + 3))
                elem_rect = pygame.Rect(box_x + 6, ey, box_w - 12, elem_h)

                if sym == "V":
                    col = (128, 172, 132)  # Verde salvia pastel
                    border_col = (168, 206, 172)
                    txt = "V (Vida)"
                else:
                    col = (156, 122, 154)  # Malva ciruela suave para Z
                    border_col = (186, 152, 184)
                    txt = "Z (Fondo)"

                pygame.draw.rect(surface, col, elem_rect, border_radius=4)
                pygame.draw.rect(surface, border_col, elem_rect, width=1, border_radius=4)

                elem_surf = self.elem_font.render(txt, True, (255, 252, 248))
                surface.blit(elem_surf, elem_surf.get_rect(center=elem_rect.center))

                # Señalador de TOPE en el último elemento
                if i == len(stack) - 1:
                    arrow_x = box_x + box_w + 10
                    arrow_y = ey + elem_h // 2
                    top_label = self.info_font.render("TOPE", True, COZY_TEXT_GOLD)
                    surface.blit(top_label, (arrow_x, arrow_y - 8))

        # Panel explicativo al lado derecho de la pila
        info_x = box_x + box_w + 80
        info_y = box_y + 10

        desc_lines = [
            "Condición: Aceptación por pila vacía",
            f"Regla actual: {last_transition}",
            f"Vidas activas: {lives}/5",
        ]
        for line in desc_lines:
            ln_surf = self.info_font.render(line, True, (222, 208, 198))
            surface.blit(ln_surf, (info_x, info_y))
            info_y += 24

        if pda_state == "q2" and not stack:
            warn_surf = self.title_font.render("¡Pila Vacía alcanzada! DERROTA", True, (218, 118, 106))
            surface.blit(warn_surf, (info_x, info_y + 6))


class WordHistoryView:
    """Muestra la palabra w generada en el alfabeto Σ = {a, e, x} con insignias de tono pastel."""

    def __init__(self, rect: pygame.Rect):
        self.rect = rect
        self.title_font = get_font(14, bold=True)
        self.badge_font = get_font(13, bold=True)
        self.info_font = get_font(11, bold=False)

    def draw(self, surface: pygame.Surface, word: str, last_symbol: Optional[str]):
        draw_cozy_panel(surface, self.rect, border_radius=10, bg_color=(46, 36, 44), border_color=(90, 70, 78))

        # Título
        title_surf = self.title_font.render(
            f"Cadena w (Longitud: {len(word)})", True, COZY_TEXT_GOLD
        )
        surface.blit(title_surf, (self.rect.x + 14, self.rect.y + 8))

        # Leyenda de símbolos
        legend_txt = "a: Acierto  •  e: Error  •  x: Inválido"
        leg_surf = self.info_font.render(legend_txt, True, COZY_TEXT_MUTED)
        surface.blit(leg_surf, (self.rect.right - leg_surf.get_width() - 14, self.rect.y + 10))

        # Chips de símbolos
        badge_size = 22
        spacing = 5
        start_x = self.rect.x + 14
        start_y = self.rect.y + 34
        max_symbols = int((self.rect.width - 28) / (badge_size + spacing))

        display_word = word[-max_symbols:] if len(word) > max_symbols else word

        for i, char in enumerate(display_word):
            bx = start_x + i * (badge_size + spacing)
            by = start_y
            b_rect = pygame.Rect(bx, by, badge_size, badge_size)

            if char == "a":
                b_col = (128, 172, 132)  # Verde salvia pastel
            elif char == "e":
                b_col = (208, 112, 100)  # Terracota pastel
            else:  # 'x'
                b_col = (235, 172, 102)  # Ámbar suave

            pygame.draw.rect(surface, b_col, b_rect, border_radius=5)
            # Resaltar con selective outline si es el último ingresado
            if i == len(display_word) - 1:
                pygame.draw.rect(surface, (255, 245, 215), b_rect, width=2, border_radius=5)

            t_surf = self.badge_font.render(char, True, (255, 252, 248))
            surface.blit(t_surf, t_surf.get_rect(center=b_rect.center))

        if not word:
            empty_lbl = self.info_font.render("Esperando primer movimiento del jugador...", True, (175, 155, 150))
            surface.blit(empty_lbl, (start_x, start_y + 4))


class ModalDialog:
    """Ventana emergente para Fin de Partida y Explicación Teórica con estética acogedora."""

    def __init__(
        self,
        width: int,
        height: int,
        screen_size: Tuple[int, int],
        title: str,
        content_lines: List[str],
        buttons: List[Tuple[str, Callable]],
        title_color: Tuple[int, int, int] = COZY_TEXT_GOLD,
    ):
        self.screen_size = screen_size
        self.rect = pygame.Rect(
            (screen_size[0] - width) // 2,
            (screen_size[1] - height) // 2,
            width,
            height,
        )
        self.title = title
        self.content_lines = content_lines
        self.title_color = title_color
        self.title_font = get_font(22, bold=True)
        self.line_font = get_font(14, bold=False)
        self.strong_font = get_font(15, bold=True)

        # Crear botones
        self.btn_objects: List[Button] = []
        n_btns = len(buttons)
        btn_w = 170
        btn_h = 42
        total_w = n_btns * btn_w + (n_btns - 1) * 20
        start_btn_x = self.rect.centerx - total_w // 2
        btn_y = self.rect.bottom - btn_h - 22

        for i, (text, cb) in enumerate(buttons):
            bx = start_btn_x + i * (btn_w + 20)
            btn = Button(
                rect=pygame.Rect(bx, btn_y, btn_w, btn_h),
                text=text,
                callback=cb,
                bg_color=COZY_GREEN_SAGE if i == 0 else COZY_SLATE_PURPLE,
                hover_color=COZY_GREEN_HOVER if i == 0 else COZY_SLATE_PURPLE_HOVER,
                font_size=15,
            )
            self.btn_objects.append(btn)

    def handle_event(self, event: pygame.event.Event) -> bool:
        for btn in self.btn_objects:
            if btn.handle_event(event):
                return True
        return False

    def draw(self, surface: pygame.Surface):
        # Capa ambiental cálida de fondo
        overlay = pygame.Surface(self.screen_size, pygame.SRCALPHA)
        overlay.fill((30, 20, 26, 205))
        surface.blit(overlay, (0, 0))

        # Sombra sutil
        shadow_rect = self.rect.copy()
        shadow_rect.y += 4
        shadow_surf = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        shadow_surf.fill((18, 10, 14, 100))
        surface.blit(shadow_surf, shadow_rect.topleft)

        # Cuadro principal del diálogo
        draw_cozy_panel(surface, self.rect, border_radius=14, bg_color=(48, 36, 44), border_color=(105, 82, 92), alpha=245)

        # Título
        title_surf = self.title_font.render(self.title, True, self.title_color)
        title_rect = title_surf.get_rect(center=(self.rect.centerx, self.rect.y + 36))
        surface.blit(title_surf, title_rect)

        # Separador decorativo
        sep_y = self.rect.y + 64
        pygame.draw.line(surface, (88, 68, 76), (self.rect.x + 30, sep_y), (self.rect.right - 30, sep_y), 2)

        # Contenido
        cur_y = sep_y + 16
        for line in self.content_lines:
            is_header = line.startswith("## ")
            is_bullet = line.startswith("• ")

            if is_header:
                clean_text = line.replace("## ", "")
                txt_surf = self.strong_font.render(clean_text, True, COZY_TEXT_GOLD)
                surface.blit(txt_surf, (self.rect.x + 30, cur_y))
                cur_y += 24
            else:
                fnt = self.line_font
                txt_surf = fnt.render(line, True, (244, 232, 222) if is_bullet else (210, 195, 185))
                surface.blit(txt_surf, (self.rect.x + 30, cur_y))
                cur_y += 21

        # Botones
        for btn in self.btn_objects:
            btn.draw(surface)


class SoundSettingsModal:
    """Ventana interactiva de Ajustes de Audio: volumen, mute de música y efectos con guardado JSON."""

    def __init__(self, screen_size: Tuple[int, int], sound_manager, on_close: Callable):
        self.screen_size = screen_size
        self.sound = sound_manager
        self.on_close = on_close

        width = 640
        height = 350
        self.rect = pygame.Rect(
            (screen_size[0] - width) // 2,
            (screen_size[1] - height) // 2,
            width,
            height,
        )

        self.title_font = get_font(22, bold=True)
        self.section_font = get_font(16, bold=True)
        self.label_font = get_font(14, bold=False)
        self.val_font = get_font(15, bold=True)

        self._build_controls()

    def _build_controls(self):
        """Crea los botones de control de volumen y opciones con estilo cozy."""
        self.buttons: List[Button] = []

        # 1. Controles de Música
        row1_y = self.rect.y + 115
        self.btn_mus_down = Button(
            rect=pygame.Rect(self.rect.x + 40, row1_y, 45, 34),
            text=" - ",
            callback=lambda: self.sound.change_music_volume(-0.1),
            bg_color=(75, 58, 68),
            hover_color=(92, 72, 84),
            font_size=18,
        )
        self.buttons.append(self.btn_mus_down)

        self.btn_mus_up = Button(
            rect=pygame.Rect(self.rect.x + 285, row1_y, 45, 34),
            text=" + ",
            callback=lambda: self.sound.change_music_volume(+0.1),
            bg_color=(75, 58, 68),
            hover_color=(92, 72, 84),
            font_size=18,
        )
        self.buttons.append(self.btn_mus_up)

        self.btn_mus_mute = Button(
            rect=pygame.Rect(self.rect.x + 360, row1_y, 220, 34),
            text="Silenciar Música",
            callback=self._toggle_music_mute,
            bg_color=COZY_TERRACOTTA,
            hover_color=COZY_TERRACOTTA_HOVER,
            font_size=14,
        )
        self.buttons.append(self.btn_mus_mute)

        # 2. Controles de Efectos (SFX)
        row2_y = self.rect.y + 205
        self.btn_sfx_down = Button(
            rect=pygame.Rect(self.rect.x + 40, row2_y, 45, 34),
            text=" - ",
            callback=lambda: (self.sound.change_sfx_volume(-0.1), self.sound.play("match")),
            bg_color=(75, 58, 68),
            hover_color=(92, 72, 84),
            font_size=18,
        )
        self.buttons.append(self.btn_sfx_down)

        self.btn_sfx_up = Button(
            rect=pygame.Rect(self.rect.x + 285, row2_y, 45, 34),
            text=" + ",
            callback=lambda: (self.sound.change_sfx_volume(+0.1), self.sound.play("match")),
            bg_color=(75, 58, 68),
            hover_color=(92, 72, 84),
            font_size=18,
        )
        self.buttons.append(self.btn_sfx_up)

        self.btn_sfx_mute = Button(
            rect=pygame.Rect(self.rect.x + 360, row2_y, 220, 34),
            text="Silenciar Efectos",
            callback=self._toggle_sfx_mute,
            bg_color=COZY_TERRACOTTA,
            hover_color=COZY_TERRACOTTA_HOVER,
            font_size=14,
        )
        self.buttons.append(self.btn_sfx_mute)

        # 3. Fila inferior: Guardar y Salir
        row3_y = self.rect.bottom - 54
        self.btn_close = Button(
            rect=pygame.Rect(self.rect.centerx - 110, row3_y, 220, 40),
            text="Guardar y Salir",
            callback=self._save_and_close,
            bg_color=COZY_GREEN_SAGE,
            hover_color=COZY_GREEN_HOVER,
            font_size=15,
        )
        self.buttons.append(self.btn_close)

    def _save_and_close(self):
        """Guarda la configuración en el JSON al salir y cierra el diálogo."""
        self.sound.save_config()
        self.on_close()

    def _toggle_music_mute(self):
        self.sound.toggle_music_mute()

    def _toggle_sfx_mute(self):
        self.sound.toggle_sfx_mute()

    def handle_event(self, event: pygame.event.Event) -> bool:
        for btn in self.buttons:
            if btn.handle_event(event):
                return True
        return False

    def draw(self, surface: pygame.Surface):
        # Fondo ambiental cálido
        overlay = pygame.Surface(self.screen_size, pygame.SRCALPHA)
        overlay.fill((30, 20, 26, 205))
        surface.blit(overlay, (0, 0))

        # Ventana del modal
        draw_cozy_panel(surface, self.rect, border_radius=14, bg_color=(48, 36, 44), border_color=(105, 82, 92), alpha=245)

        # Título
        title_surf = self.title_font.render("AJUSTE DE SONIDO", True, COZY_TEXT_GOLD)
        title_rect = title_surf.get_rect(center=(self.rect.centerx, self.rect.y + 34))
        surface.blit(title_surf, title_rect)

        # Separador decorativo
        sep_y = self.rect.y + 60
        pygame.draw.line(surface, (88, 68, 76), (self.rect.x + 30, sep_y), (self.rect.right - 30, sep_y), 2)

        # ----------------- SECCIÓN 1: MÚSICA DE FONDO -----------------
        sec1_y = self.rect.y + 78
        sec1_surf = self.section_font.render("Música de Fondo (Menú y Juego)", True, COZY_TEXT_MAIN)
        surface.blit(sec1_surf, (self.rect.x + 40, sec1_y))

        pct_mus = int(self.sound.music_volume * 100)
        mus_status = "MUTED" if self.sound.music_muted else f"{pct_mus}%"
        mus_col = COZY_TERRACOTTA if self.sound.music_muted else (138, 188, 218)
        vol_mus_surf = self.val_font.render(mus_status, True, mus_col)
        surface.blit(vol_mus_surf, (self.rect.x + 360, sec1_y + 2))

        # Barra visual de volumen música
        bar1_rect = pygame.Rect(self.rect.x + 95, self.rect.y + 121, 180, 22)
        pygame.draw.rect(surface, (36, 26, 32), bar1_rect, border_radius=6)
        pygame.draw.rect(surface, (84, 65, 74), bar1_rect, width=1, border_radius=6)

        fill1_w = int(bar1_rect.width * (0.0 if self.sound.music_muted else self.sound.music_volume))
        if fill1_w > 0:
            fill1_rect = pygame.Rect(bar1_rect.x + 2, bar1_rect.y + 2, max(4, fill1_w - 4), bar1_rect.height - 4)
            pygame.draw.rect(surface, (138, 188, 218), fill1_rect, border_radius=4)

        # Actualizar texto de botón mute música
        self.btn_mus_mute.text = "Activar Música" if self.sound.music_muted else "Silenciar Música"
        self.btn_mus_mute.bg_color = COZY_GREEN_SAGE if self.sound.music_muted else COZY_TERRACOTTA
        self.btn_mus_mute.hover_color = COZY_GREEN_HOVER if self.sound.music_muted else COZY_TERRACOTTA_HOVER

        # ----------------- SECCIÓN 2: EFECTOS DE SONIDO -----------------
        sec2_y = self.rect.y + 168
        sec2_surf = self.section_font.render("Efectos de Sonido (Acierto, Fallo, Cartas)", True, COZY_TEXT_MAIN)
        surface.blit(sec2_surf, (self.rect.x + 40, sec2_y))

        pct_sfx = int(self.sound.sfx_volume * 100)
        sfx_status = "MUTED" if self.sound.sfx_muted else f"{pct_sfx}%"
        sfx_col = COZY_TERRACOTTA if self.sound.sfx_muted else COZY_GREEN_SAGE
        vol_sfx_surf = self.val_font.render(sfx_status, True, sfx_col)
        surface.blit(vol_sfx_surf, (self.rect.x + 360, sec2_y + 2))

        # Barra visual de volumen efectos
        bar2_rect = pygame.Rect(self.rect.x + 95, self.rect.y + 211, 180, 22)
        pygame.draw.rect(surface, (36, 26, 32), bar2_rect, border_radius=6)
        pygame.draw.rect(surface, (84, 65, 74), bar2_rect, width=1, border_radius=6)

        fill2_w = int(bar2_rect.width * (0.0 if self.sound.sfx_muted else self.sound.sfx_volume))
        if fill2_w > 0:
            fill2_rect = pygame.Rect(bar2_rect.x + 2, bar2_rect.y + 2, max(4, fill2_w - 4), bar2_rect.height - 4)
            pygame.draw.rect(surface, COZY_GREEN_SAGE, fill2_rect, border_radius=4)

        # Actualizar texto de botón mute SFX
        self.btn_sfx_mute.text = "Activar Efectos" if self.sound.sfx_muted else "Silenciar Efectos"
        self.btn_sfx_mute.bg_color = COZY_GREEN_SAGE if self.sound.sfx_muted else COZY_TERRACOTTA
        self.btn_sfx_mute.hover_color = COZY_GREEN_HOVER if self.sound.sfx_muted else COZY_TERRACOTTA_HOVER

        # Dibujar todos los botones
        for btn in self.buttons:
            btn.draw(surface)


class SettingsHubModal:
    """Ventana central de Ajustes con accesos a Ajuste de Sonido, Ajuste de Pantalla y Ajuste de Partida."""

    def __init__(
        self,
        screen_size: Tuple[int, int],
        on_open_sound: Callable[[], None],
        on_open_screen: Callable[[], None],
        on_open_game: Callable[[], None],
        on_close: Callable[[], None],
    ):
        self.screen_size = screen_size
        self.on_open_sound = on_open_sound
        self.on_open_screen = on_open_screen
        self.on_open_game = on_open_game
        self.on_close = on_close

        width = 480
        height = 410
        self.rect = pygame.Rect(
            (screen_size[0] - width) // 2,
            (screen_size[1] - height) // 2,
            width,
            height,
        )

        self.title_font = get_font(24, bold=True)
        self.desc_font = get_font(14, bold=False)

        btn_w = 320
        btn_h = 44
        cx = self.rect.centerx - btn_w // 2

        self.buttons: List[Button] = [
            Button(
                rect=pygame.Rect(cx, self.rect.y + 105, btn_w, btn_h),
                text="Ajuste de Sonido",
                callback=self.on_open_sound,
                bg_color=COZY_AMBER,
                hover_color=COZY_AMBER_HOVER,
                font_size=16,
                border_radius=10,
            ),
            Button(
                rect=pygame.Rect(cx, self.rect.y + 162, btn_w, btn_h),
                text="Ajuste de Pantalla",
                callback=self.on_open_screen,
                bg_color=COZY_SLATE_PURPLE,
                hover_color=COZY_SLATE_PURPLE_HOVER,
                font_size=16,
                border_radius=10,
            ),
            Button(
                rect=pygame.Rect(cx, self.rect.y + 219, btn_w, btn_h),
                text="Ajuste de Partida",
                callback=self.on_open_game,
                bg_color=COZY_GREEN_SAGE,
                hover_color=COZY_GREEN_HOVER,
                font_size=16,
                border_radius=10,
            ),
            Button(
                rect=pygame.Rect(cx, self.rect.y + 300, btn_w, 40),
                text="Volver",
                callback=self.on_close,
                bg_color=COZY_TERRACOTTA,
                hover_color=COZY_TERRACOTTA_HOVER,
                font_size=15,
                border_radius=8,
            ),
        ]

    def handle_event(self, event: pygame.event.Event) -> bool:
        for btn in self.buttons:
            if btn.handle_event(event):
                return True
        return False

    def draw(self, surface: pygame.Surface):
        # Capa ambiental cálida de fondo
        overlay = pygame.Surface(self.screen_size, pygame.SRCALPHA)
        overlay.fill((30, 20, 26, 205))
        surface.blit(overlay, (0, 0))

        # Cuadro principal
        draw_cozy_panel(surface, self.rect, border_radius=14, bg_color=(48, 36, 44), border_color=(105, 82, 92), alpha=245)

        # Título
        title_surf = self.title_font.render("AJUSTES", True, COZY_TEXT_GOLD)
        surface.blit(title_surf, title_surf.get_rect(center=(self.rect.centerx, self.rect.y + 34)))

        # Separador decorativo
        sep_y = self.rect.y + 60
        pygame.draw.line(surface, (88, 68, 76), (self.rect.x + 30, sep_y), (self.rect.right - 30, sep_y), 2)

        # Descripción
        desc_surf = self.desc_font.render("Selecciona la categoría que deseas configurar:", True, COZY_TEXT_MUTED)
        surface.blit(desc_surf, desc_surf.get_rect(center=(self.rect.centerx, self.rect.y + 82)))

        # Botones
        for btn in self.buttons:
            btn.draw(surface)


class GameSettingsModal:
    """Ventana interactiva de Ajuste de Partida: opción de mostrar cartas al inicio."""

    def __init__(
        self,
        screen_size: Tuple[int, int],
        mostrar_cartas: bool,
        on_change_preview: Callable[[bool], None],
        on_close: Callable[[], None],
    ):
        self.screen_size = screen_size
        self.mostrar_cartas = mostrar_cartas
        self.on_change_preview = on_change_preview
        self.on_close = on_close

        width = 580
        height = 370
        self.rect = pygame.Rect(
            (screen_size[0] - width) // 2,
            (screen_size[1] - height) // 2,
            width,
            height,
        )

        self.title_font = get_font(22, bold=True)
        self.section_font = get_font(16, bold=True)
        self.info_font = get_font(13, bold=False)

        # Botón selector de activación
        self.btn_toggle = Button(
            rect=pygame.Rect(self.rect.x + 360, self.rect.y + 110, 180, 40),
            text="Activado" if self.mostrar_cartas else "Desactivado",
            callback=self._toggle_preview,
            bg_color=COZY_GREEN_SAGE if self.mostrar_cartas else COZY_TERRACOTTA,
            hover_color=COZY_GREEN_HOVER if self.mostrar_cartas else COZY_TERRACOTTA_HOVER,
            font_size=15,
            border_radius=8,
        )

        # Botón de Volver a la pantalla de ajustes
        btn_w = 220
        btn_h = 42
        self.btn_back = Button(
            rect=pygame.Rect(self.rect.centerx - btn_w // 2, self.rect.bottom - 58, btn_w, btn_h),
            text="Volver",
            callback=self.on_close,
            bg_color=COZY_TERRACOTTA,
            hover_color=COZY_TERRACOTTA_HOVER,
            font_size=15,
            border_radius=8,
        )

    def _toggle_preview(self):
        self.mostrar_cartas = not self.mostrar_cartas
        self.btn_toggle.text = "Activado" if self.mostrar_cartas else "Desactivado"
        self.btn_toggle.bg_color = COZY_GREEN_SAGE if self.mostrar_cartas else COZY_TERRACOTTA
        self.btn_toggle.hover_color = COZY_GREEN_HOVER if self.mostrar_cartas else COZY_TERRACOTTA_HOVER
        self.on_change_preview(self.mostrar_cartas)

    def handle_event(self, event: pygame.event.Event) -> bool:
        if self.btn_toggle.handle_event(event):
            return True
        if self.btn_back.handle_event(event):
            return True
        return False

    def draw(self, surface: pygame.Surface):
        # Capa ambiental cálida de fondo
        overlay = pygame.Surface(self.screen_size, pygame.SRCALPHA)
        overlay.fill((30, 20, 26, 205))
        surface.blit(overlay, (0, 0))

        # Ventana del modal
        draw_cozy_panel(surface, self.rect, border_radius=14, bg_color=(48, 36, 44), border_color=(105, 82, 92), alpha=245)

        # Título
        title_surf = self.title_font.render("AJUSTE DE PARTIDA", True, COZY_TEXT_GOLD)
        surface.blit(title_surf, title_surf.get_rect(center=(self.rect.centerx, self.rect.y + 34)))

        # Separador decorativo
        sep_y = self.rect.y + 60
        pygame.draw.line(surface, (88, 68, 76), (self.rect.x + 30, sep_y), (self.rect.right - 30, sep_y), 2)

        # Etiqueta de la opción
        sec_surf = self.section_font.render("Mostrar cartas al inicio", True, COZY_TEXT_MAIN)
        surface.blit(sec_surf, (self.rect.x + 40, self.rect.y + 118))

        # Dibujar botón de activación
        self.btn_toggle.draw(surface)

        # Explicación
        info_lines = [
            "• Al estar activado, todas las cartas del tablero se revelan",
            "  durante 3 segundos al inicio de la partida para memorizarlas.",
            "• Al estar desactivado, las cartas inician cubiertas directamente.",
        ]
        cur_y = self.rect.y + 175
        for line in info_lines:
            txt_col = (250, 226, 182) if "3 segundos" in line else (210, 195, 185)
            line_surf = self.info_font.render(line, True, txt_col)
            surface.blit(line_surf, (self.rect.x + 40, cur_y))
            cur_y += 24

        # Botón Volver
        self.btn_back.draw(surface)


class ScreenSettingsModal:
    """Ventana interactiva de Ajuste de Pantalla: Modo Ventana y Pantalla Completa adaptativa."""

    def __init__(
        self,
        screen_size: Tuple[int, int],
        is_fullscreen: bool,
        on_save_and_exit: Callable[[bool], None],
    ):
        self.screen_size = screen_size
        self.is_fullscreen = is_fullscreen
        self.selected_mode = "fullscreen" if is_fullscreen else "window"
        self.on_save_and_exit = on_save_and_exit

        width = 600
        height = 420
        self.rect = pygame.Rect(
            (screen_size[0] - width) // 2,
            (screen_size[1] - height) // 2,
            width,
            height,
        )

        self.title_font = get_font(22, bold=True)
        self.section_font = get_font(15, bold=True)
        self.info_font = get_font(13, bold=False)

        # Selector de modo de pantalla
        self.selector = SegmentedSelector(
            x=self.rect.x + 40,
            y=self.rect.y + 115,
            width=520,
            height=46,
            options=[
                ("Modo Ventana (1280x720)", "window"),
                ("Pantalla Completa", "fullscreen"),
            ],
            selected_value=self.selected_mode,
            on_change=self._on_mode_change,
        )

        # Botón Guardar y Salir
        btn_w = 240
        btn_h = 42
        self.btn_save_exit = Button(
            rect=pygame.Rect(self.rect.centerx - btn_w // 2, self.rect.bottom - 58, btn_w, btn_h),
            text="Guardar y Salir",
            callback=self._apply_and_close,
            bg_color=COZY_GREEN_SAGE,
            hover_color=COZY_GREEN_HOVER,
            font_size=15,
            border_radius=8,
        )

    def _on_mode_change(self, val: str):
        self.selected_mode = val

    def _apply_and_close(self):
        new_fullscreen = (self.selected_mode == "fullscreen")
        self.on_save_and_exit(new_fullscreen)

    def handle_event(self, event: pygame.event.Event) -> bool:
        if self.selector.handle_event(event):
            return True
        if self.btn_save_exit.handle_event(event):
            return True
        return False

    def draw(self, surface: pygame.Surface):
        # Capa ambiental cálida de fondo
        overlay = pygame.Surface(self.screen_size, pygame.SRCALPHA)
        overlay.fill((30, 20, 26, 205))
        surface.blit(overlay, (0, 0))

        # Ventana del modal
        draw_cozy_panel(surface, self.rect, border_radius=14, bg_color=(48, 36, 44), border_color=(105, 82, 92), alpha=245)

        # Título
        title_surf = self.title_font.render("AJUSTE DE PANTALLA", True, COZY_TEXT_GOLD)
        surface.blit(title_surf, title_surf.get_rect(center=(self.rect.centerx, self.rect.y + 34)))

        # Separador decorativo
        sep_y = self.rect.y + 60
        pygame.draw.line(surface, (88, 68, 76), (self.rect.x + 30, sep_y), (self.rect.right - 30, sep_y), 2)

        # Subtítulo de sección
        sec_surf = self.section_font.render("Selecciona el formato de visualización:", True, COZY_TEXT_MAIN)
        surface.blit(sec_surf, (self.rect.x + 40, self.rect.y + 80))

        # Selector interactivo
        self.selector.draw(surface)

        # Panel explicativo adaptativo a cualquier resolución
        info_lines = [
            "• Modo Ventana: Ejecuta el juego en ventana estándar a 1280x720 píxeles.",
            "• Pantalla Completa: Se adapta automáticamente a cualquier monitor",
            "  de computadora (Full HD, 2K, 4K, laptops) manteniendo la proporción",
            "  16:9 con escalado nítido (pixel perfect) sin distorsión.",
        ]
        cur_y = self.rect.y + 185
        for line in info_lines:
            txt_col = (250, 226, 182) if ("Pantalla Completa:" in line or "Modo Ventana:" in line) else (210, 195, 185)
            line_surf = self.info_font.render(line, True, txt_col)
            surface.blit(line_surf, (self.rect.x + 40, cur_y))
            cur_y += 24

        # Botón Guardar y Salir
        self.btn_save_exit.draw(surface)


class PlaySetupModal:
    """Ventana interactiva para configurar Dificultad, Tiempo y Previsualización antes de jugar."""

    def __init__(
        self,
        screen_size: Tuple[int, int],
        initial_difficulty: str,
        initial_time: float,
        mostrar_cartas: bool,
        on_change_difficulty: Callable[[str], None],
        on_change_time: Callable[[float], None],
        on_change_preview: Callable[[bool], None],
        on_start_game: Callable[[], None],
        on_close: Callable[[], None],
    ):
        self.screen_size = screen_size
        self.difficulty = initial_difficulty
        self.time_seconds = initial_time
        self.mostrar_cartas = mostrar_cartas
        self.on_change_difficulty = on_change_difficulty
        self.on_change_time = on_change_time
        self.on_change_preview = on_change_preview
        self.on_start_game = on_start_game
        self.on_close = on_close

        width = 620
        height = 510
        self.rect = pygame.Rect(
            (screen_size[0] - width) // 2,
            (screen_size[1] - height) // 2,
            width,
            height,
        )

        self.title_font = get_font(23, bold=True)
        self.section_font = get_font(15, bold=True)
        self.desc_font = get_font(12, bold=False)

        # 1. Selector de Dificultad
        sel_w = 520
        sel_x = self.rect.centerx - sel_w // 2
        self.diff_selector = SegmentedSelector(
            x=sel_x,
            y=self.rect.y + 105,
            width=sel_w,
            height=44,
            options=[
                ("Fácil (8 cartas - 4 pares)", "facil"),
                ("Difícil (16 cartas - 8 pares)", "dificil"),
            ],
            selected_value=self.difficulty,
            on_change=self._on_diff_changed,
        )

        # 2. Selector de Tiempo
        self.time_selector = SegmentedSelector(
            x=sel_x,
            y=self.rect.y + 195,
            width=sel_w,
            height=44,
            options=[
                ("Tiempo Corto (5 min)", "300"),
                ("Tiempo Normal (10 min)", "600"),
            ],
            selected_value=str(int(self.time_seconds)),
            on_change=self._on_time_changed,
        )

        # 3. Opción de previsualización de cartas al inicio
        btn_prev_w = 170
        btn_prev_h = 38
        self.btn_preview = Button(
            rect=pygame.Rect(self.rect.x + 390, self.rect.y + 275, btn_prev_w, btn_prev_h),
            text="Activado" if self.mostrar_cartas else "Desactivado",
            callback=self._toggle_preview,
            bg_color=COZY_GREEN_SAGE if self.mostrar_cartas else COZY_TERRACOTTA,
            hover_color=COZY_GREEN_HOVER if self.mostrar_cartas else COZY_TERRACOTTA_HOVER,
            font_size=14,
            border_radius=8,
        )

        # 4. Botones inferiores: Volver e Iniciar Partida
        btn_bottom_w = 230
        btn_bottom_h = 46
        bottom_y = self.rect.bottom - 64

        self.btn_back = Button(
            rect=pygame.Rect(self.rect.x + 50, bottom_y, btn_bottom_w, btn_bottom_h),
            text="Volver",
            callback=self.on_close,
            bg_color=COZY_TERRACOTTA,
            hover_color=COZY_TERRACOTTA_HOVER,
            font_size=16,
            border_radius=10,
        )

        self.btn_start = Button(
            rect=pygame.Rect(self.rect.right - 50 - btn_bottom_w, bottom_y, btn_bottom_w, btn_bottom_h),
            text="INICIAR PARTIDA",
            callback=self._on_start_clicked,
            bg_color=COZY_GREEN_SAGE,
            hover_color=COZY_GREEN_HOVER,
            font_size=16,
            border_radius=10,
        )

    def _on_diff_changed(self, val: str):
        self.difficulty = val
        self.on_change_difficulty(val)

    def _on_time_changed(self, val: str):
        self.time_seconds = float(val)
        self.on_change_time(self.time_seconds)

    def _toggle_preview(self):
        self.mostrar_cartas = not self.mostrar_cartas
        self.btn_preview.text = "Activado" if self.mostrar_cartas else "Desactivado"
        self.btn_preview.bg_color = COZY_GREEN_SAGE if self.mostrar_cartas else COZY_TERRACOTTA
        self.btn_preview.hover_color = COZY_GREEN_HOVER if self.mostrar_cartas else COZY_TERRACOTTA_HOVER
        self.on_change_preview(self.mostrar_cartas)

    def _on_start_clicked(self):
        self.on_start_game()

    def handle_event(self, event: pygame.event.Event) -> bool:
        if self.diff_selector.handle_event(event):
            return True
        if self.time_selector.handle_event(event):
            return True
        if self.btn_preview.handle_event(event):
            return True
        if self.btn_back.handle_event(event):
            return True
        if self.btn_start.handle_event(event):
            return True
        return False

    def draw(self, surface: pygame.Surface):
        # Capa ambiental cálida de fondo
        overlay = pygame.Surface(self.screen_size, pygame.SRCALPHA)
        overlay.fill((30, 20, 26, 205))
        surface.blit(overlay, (0, 0))

        # Panel contenedor
        draw_cozy_panel(surface, self.rect, border_radius=16, bg_color=(48, 36, 44), border_color=(105, 82, 92), alpha=245)

        # Título
        title_surf = self.title_font.render("PREPARAR PARTIDA", True, COZY_TEXT_GOLD)
        surface.blit(title_surf, title_surf.get_rect(center=(self.rect.centerx, self.rect.y + 34)))

        # Separador decorativo
        sep_y = self.rect.y + 58
        pygame.draw.line(surface, (88, 68, 76), (self.rect.x + 30, sep_y), (self.rect.right - 30, sep_y), 2)

        # 1. Sección Dificultad
        lbl_diff = self.section_font.render("1. Dificultad del Tablero:", True, COZY_TEXT_MAIN)
        surface.blit(lbl_diff, (self.rect.x + 50, self.rect.y + 78))
        self.diff_selector.draw(surface)

        # 2. Sección Tiempo
        lbl_time = self.section_font.render("2. Modo de Tiempo:", True, COZY_TEXT_MAIN)
        surface.blit(lbl_time, (self.rect.x + 50, self.rect.y + 168))
        self.time_selector.draw(surface)

        # 3. Sección Previsualización
        lbl_prev = self.section_font.render("3. Mostrar cartas al inicio:", True, COZY_TEXT_MAIN)
        surface.blit(lbl_prev, (self.rect.x + 50, self.rect.y + 282))
        self.btn_preview.draw(surface)

        sub_desc = self.desc_font.render(
            "(Descubre las cartas durante 3 segundos al iniciar)", True, COZY_TEXT_MUTED
        )
        surface.blit(sub_desc, (self.rect.x + 50, self.rect.y + 316))

        # Separador inferior
        sep2_y = self.rect.bottom - 82
        pygame.draw.line(surface, (78, 58, 66), (self.rect.x + 40, sep2_y), (self.rect.right - 40, sep2_y), 1)

        # Botones inferiores: Volver e Iniciar Partida
        self.btn_back.draw(surface)
        self.btn_start.draw(surface)
