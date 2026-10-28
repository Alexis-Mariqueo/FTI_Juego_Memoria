"""
Componentes gráficos y visualizadores teóricos para la interfaz del Memotest.
Incluye visualizador gráfico del AFD, visualizador gráfico de la Pila (AP),
botones interactivos, panel de historial de símbolos y modales de diálogo.
"""

import pygame
from typing import Callable, List, Optional, Tuple


def get_font(size: int, bold: bool = False) -> pygame.font.Font:
    """Retorna una fuente de sistema agradable o la fuente por defecto de Pygame."""
    try:
        return pygame.font.SysFont("Segoe UI", size, bold=bold)
    except Exception:
        return pygame.font.Font(None, size)


class Button:
    """Botón con animación al pasar el cursor y responder a eventos."""

    def __init__(
        self,
        rect: pygame.Rect,
        text: str,
        callback: Optional[Callable] = None,
        bg_color: Tuple[int, int, int] = (41, 128, 185),
        hover_color: Tuple[int, int, int] = (52, 152, 219),
        text_color: Tuple[int, int, int] = (255, 255, 255),
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
        pygame.draw.rect(surface, color, self.rect, border_radius=self.border_radius)
        
        # Borde sutil
        border_color = (255, 255, 255, 80) if (self.is_hovered or self.is_active) else (20, 30, 45)
        pygame.draw.rect(surface, border_color, self.rect, width=2, border_radius=self.border_radius)

        text_surf = self.font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)


class SegmentedSelector:
    """Selector estilo pills/tabs para opciones como Dificultad o Tiempo."""

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
        # Fondo contenedor
        pygame.draw.rect(surface, (28, 35, 51), self.rect, border_radius=8)
        pygame.draw.rect(surface, (50, 60, 85), self.rect, width=2, border_radius=8)

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
                pygame.draw.rect(surface, (41, 128, 185), seg_rect, border_radius=6)
                txt_color = (255, 255, 255)
            else:
                txt_color = (160, 175, 200)

            txt_surf = self.font.render(label, True, txt_color)
            txt_rect = txt_surf.get_rect(center=seg_rect.center)
            surface.blit(txt_surf, txt_rect)


class DFAGraphVisualizer:
    """Visualizador interactivo de los estados del AFD de Progreso."""

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
        # Fondo del contenedor
        pygame.draw.rect(surface, (23, 28, 42), self.rect, border_radius=10)
        pygame.draw.rect(surface, (45, 55, 78), self.rect, width=1, border_radius=10)

        # Título
        title_surf = self.title_font.render("AFD: Progreso de Aciertos", True, (236, 240, 241))
        surface.blit(title_surf, (self.rect.x + 14, self.rect.y + 10))

        # Indicador de pares
        pairs_found = total_pairs if current_state == "q_sumidero" else (
            int(current_state.replace("q", "")) if current_state.startswith("q") and current_state != "q_sumidero" else 0
        )
        badge_text = f"{pairs_found} / {total_pairs} Pares"
        badge_surf = self.info_font.render(badge_text, True, (46, 204, 113) if pairs_found == total_pairs else (189, 195, 199))
        surface.blit(badge_surf, (self.rect.right - badge_surf.get_width() - 14, self.rect.y + 12))

        # Dibujar los nodos en una línea o cuadrícula compacta
        # Estados: q0 -> q1 -> ... -> qN
        num_states = total_pairs + 1
        available_w = self.rect.width - 40
        node_radius = 16 if total_pairs == 4 else 13
        spacing = available_w / (num_states - 1) if num_states > 1 else available_w

        nodes_y = self.rect.y + 48

        # Línea de conexión de fondo
        line_start = (int(self.rect.x + 20), nodes_y)
        line_end = (int(self.rect.x + 20 + (num_states - 1) * spacing), nodes_y)
        pygame.draw.line(surface, (60, 75, 105), line_start, line_end, width=3)

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

            # Colores de nodo
            if is_current:
                bg_col = (46, 204, 113) if is_final else (52, 152, 219)
                border_col = (255, 255, 255)
                text_col = (255, 255, 255)
            elif is_passed:
                bg_col = (39, 174, 96) if is_final else (30, 90, 140)
                border_col = (46, 204, 113) if is_final else (41, 128, 185)
                text_col = (200, 220, 240)
            else:
                bg_col = (35, 42, 60)
                border_col = (70, 85, 115)
                text_col = (130, 145, 170)

            # Si es final, tiene doble círculo
            if is_final:
                pygame.draw.circle(surface, border_col, (cx, cy), node_radius + 4, width=2)

            pygame.draw.circle(surface, bg_col, (cx, cy), node_radius)
            pygame.draw.circle(surface, border_col, (cx, cy), node_radius, width=2)

            # Texto del estado
            lbl = self.state_font.render(st_name, True, text_col)
            surface.blit(lbl, lbl.get_rect(center=(cx, cy)))

        # Detalle de última transición
        trans_surf = self.info_font.render(f"Última transición: {last_transition}", True, (241, 196, 15))
        surface.blit(trans_surf, (self.rect.x + 14, self.rect.y + 74))


class StackVisualizer:
    """Visualizador interactivo de la Pila del Autómata de Pila (AP)."""

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
        # Contenedor
        pygame.draw.rect(surface, (23, 28, 42), self.rect, border_radius=10)
        pygame.draw.rect(surface, (45, 55, 78), self.rect, width=1, border_radius=10)

        # Cabecera
        title_surf = self.title_font.render("AP: Autómata de Pila (Vidas)", True, (236, 240, 241))
        surface.blit(title_surf, (self.rect.x + 14, self.rect.y + 10))

        # Indicador de estado del AP
        st_color = (231, 76, 60) if pda_state == "q2" else (52, 152, 219)
        state_badge = self.info_font.render(f"Estado: {pda_state} | Vidas: {lives}/5", True, st_color)
        surface.blit(state_badge, (self.rect.right - state_badge.get_width() - 14, self.rect.y + 12))

        # Contenedor de la pila vertical
        box_w = 120
        box_h = 160
        box_x = self.rect.x + 20
        box_y = self.rect.y + 38

        # Dibujar vaso de la pila (bordes izquierdo, derecho e inferior)
        wall_col = (100, 115, 145)
        # Línea izquierda
        pygame.draw.line(surface, wall_col, (box_x, box_y), (box_x, box_y + box_h), width=3)
        # Línea derecha
        pygame.draw.line(surface, wall_col, (box_x + box_w, box_y), (box_x + box_w, box_y + box_h), width=3)
        # Base
        pygame.draw.line(surface, wall_col, (box_x - 3, box_y + box_h), (box_x + box_w + 3, box_y + box_h), width=4)

        # Dibujar los elementos de la pila desde el fondo ('Z') hacia el tope ('V')
        # En la lista, el índice 0 es el fondo ('Z') y el último índice es el tope
        elem_h = 22
        start_y = box_y + box_h - elem_h - 4

        if not stack:
            empty_msg = self.elem_font.render("[ PILA VACÍA ]", True, (231, 76, 60))
            surface.blit(empty_msg, empty_msg.get_rect(center=(box_x + box_w // 2, box_y + box_h // 2)))
        else:
            for i, sym in enumerate(stack):
                ey = start_y - (i * (elem_h + 3))
                elem_rect = pygame.Rect(box_x + 6, ey, box_w - 12, elem_h)

                if sym == "V":
                    col = (46, 204, 113)  # Verde esmeralda para vidas
                    txt = "V (Vida)"
                else:
                    col = (142, 68, 173)  # Violeta para Z fondo de pila
                    txt = "Z (Fondo)"

                pygame.draw.rect(surface, col, elem_rect, border_radius=4)
                pygame.draw.rect(surface, (255, 255, 255, 120), elem_rect, width=1, border_radius=4)

                elem_surf = self.elem_font.render(txt, True, (255, 255, 255))
                surface.blit(elem_surf, elem_surf.get_rect(center=elem_rect.center))

                # Señalador de TOPE en el último elemento
                if i == len(stack) - 1:
                    arrow_x = box_x + box_w + 10
                    arrow_y = ey + elem_h // 2
                    top_label = self.info_font.render("◀ TOPE", True, (241, 196, 15))
                    surface.blit(top_label, (arrow_x, arrow_y - 8))

        # Panel explicativo al lado derecho de la pila
        info_x = box_x + box_w + 80
        info_y = box_y + 10

        desc_lines = [
            f"Condición: Aceptación por pila vacía",
            f"Regla actual: {last_transition}",
            f"Vidas activas: {'❤️ ' * lives}{'🖤 ' * (5 - lives)}",
        ]
        for line in desc_lines:
            ln_surf = self.info_font.render(line, True, (200, 210, 225))
            surface.blit(ln_surf, (info_x, info_y))
            info_y += 24

        if pda_state == "q2" and not stack:
            warn_surf = self.title_font.render("¡Pila Vacía alcanzada! DERROTA", True, (231, 76, 60))
            surface.blit(warn_surf, (info_x, info_y + 6))


class WordHistoryView:
    """Muestra la palabra w generada en el alfabeto Σ = {a, e, x} con insignias de color."""

    def __init__(self, rect: pygame.Rect):
        self.rect = rect
        self.title_font = get_font(14, bold=True)
        self.badge_font = get_font(13, bold=True)
        self.info_font = get_font(11, bold=False)

    def draw(self, surface: pygame.Surface, word: str, last_symbol: Optional[str]):
        pygame.draw.rect(surface, (23, 28, 42), self.rect, border_radius=10)
        pygame.draw.rect(surface, (45, 55, 78), self.rect, width=1, border_radius=10)

        # Título
        title_surf = self.title_font.render(
            f"Cadena de Entrada w ∈ Σ* (Longitud: {len(word)})", True, (236, 240, 241)
        )
        surface.blit(title_surf, (self.rect.x + 14, self.rect.y + 8))

        # Leyenda de símbolos
        legend_txt = "a: Acierto  |  e: Error  |  x: Inválido"
        leg_surf = self.info_font.render(legend_txt, True, (140, 155, 180))
        surface.blit(leg_surf, (self.rect.right - leg_surf.get_width() - 14, self.rect.y + 10))

        # Mostrar últimos 22 símbolos de la palabra como chips de color
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
                b_col = (46, 204, 113)  # Verde
            elif char == "e":
                b_col = (231, 76, 60)  # Rojo
            else:  # 'x'
                b_col = (243, 156, 18)  # Naranja

            pygame.draw.rect(surface, b_col, b_rect, border_radius=5)
            # Resaltar si es el último ingresado
            if i == len(display_word) - 1:
                pygame.draw.rect(surface, (255, 255, 255), b_rect, width=2, border_radius=5)

            t_surf = self.badge_font.render(char, True, (255, 255, 255))
            surface.blit(t_surf, t_surf.get_rect(center=b_rect.center))

        if not word:
            empty_lbl = self.info_font.render("Esperando primer movimiento del jugador...", True, (120, 135, 160))
            surface.blit(empty_lbl, (start_x, start_y + 4))


class ModalDialog:
    """Ventana emergente para Fin de Partida (Victoria / Derrota) y Explicación Teórica."""

    def __init__(
        self,
        width: int,
        height: int,
        screen_size: Tuple[int, int],
        title: str,
        content_lines: List[str],
        buttons: List[Tuple[str, Callable]],
        title_color: Tuple[int, int, int] = (255, 255, 255),
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
                bg_color=(41, 128, 185) if i == 0 else (44, 62, 80),
                hover_color=(52, 152, 219) if i == 0 else (52, 73, 94),
                font_size=15,
            )
            self.btn_objects.append(btn)

    def handle_event(self, event: pygame.event.Event) -> bool:
        for btn in self.btn_objects:
            if btn.handle_event(event):
                return True
        return False

    def draw(self, surface: pygame.Surface):
        # Capa semitransparente oscura de fondo
        overlay = pygame.Surface(self.screen_size, pygame.SRCALPHA)
        overlay.fill((10, 14, 23, 195))
        surface.blit(overlay, (0, 0))

        # Cuadro principal del diálogo
        pygame.draw.rect(surface, (28, 35, 51), self.rect, border_radius=14)
        pygame.draw.rect(surface, (60, 75, 105), self.rect, width=2, border_radius=14)

        # Sombra sutil del título
        title_surf = self.title_font.render(self.title, True, self.title_color)
        title_rect = title_surf.get_rect(center=(self.rect.centerx, self.rect.y + 36))
        surface.blit(title_surf, title_rect)

        # Separador decorativo
        sep_y = self.rect.y + 64
        pygame.draw.line(surface, (50, 65, 90), (self.rect.x + 30, sep_y), (self.rect.right - 30, sep_y), 2)

        # Contenido
        cur_y = sep_y + 16
        for line in self.content_lines:
            is_header = line.startswith("## ")
            is_bullet = line.startswith("• ")
            
            if is_header:
                clean_text = line.replace("## ", "")
                txt_surf = self.strong_font.render(clean_text, True, (241, 196, 15))
                surface.blit(txt_surf, (self.rect.x + 30, cur_y))
                cur_y += 24
            else:
                fnt = self.line_font
                txt_surf = fnt.render(line, True, (220, 230, 242) if is_bullet else (180, 195, 215))
                surface.blit(txt_surf, (self.rect.x + 30, cur_y))
                cur_y += 21

        # Botones
        for btn in self.btn_objects:
            btn.draw(surface)


class SoundSettingsModal:
    """Ventana interactiva de Ajustes de Audio: volumen y mute de música y efectos."""

    def __init__(self, screen_size: Tuple[int, int], sound_manager, on_close: Callable):
        self.screen_size = screen_size
        self.sound = sound_manager
        self.on_close = on_close

        width = 640
        height = 420
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
        """Crea los botones de ajuste de volumen y silenciamiento."""
        self.buttons: List[Button] = []

        # 1. Controles de Música
        row1_y = self.rect.y + 120
        # Botón [-] Música
        self.btn_mus_down = Button(
            rect=pygame.Rect(self.rect.x + 40, row1_y, 45, 34),
            text=" - ",
            callback=lambda: self.sound.change_music_volume(-0.1),
            bg_color=(44, 62, 80),
            hover_color=(52, 73, 94),
            font_size=18,
        )
        self.buttons.append(self.btn_mus_down)

        # Botón [+] Música
        self.btn_mus_up = Button(
            rect=pygame.Rect(self.rect.x + 285, row1_y, 45, 34),
            text=" + ",
            callback=lambda: self.sound.change_music_volume(+0.1),
            bg_color=(44, 62, 80),
            hover_color=(52, 73, 94),
            font_size=18,
        )
        self.buttons.append(self.btn_mus_up)

        # Botón Mute Música
        self.btn_mus_mute = Button(
            rect=pygame.Rect(self.rect.x + 360, row1_y, 220, 34),
            text="Silenciar Música",
            callback=self._toggle_music_mute,
            bg_color=(192, 57, 43),
            hover_color=(231, 76, 60),
            font_size=14,
        )
        self.buttons.append(self.btn_mus_mute)

        # 2. Controles de Efectos (SFX)
        row2_y = self.rect.y + 225
        # Botón [-] SFX
        self.btn_sfx_down = Button(
            rect=pygame.Rect(self.rect.x + 40, row2_y, 45, 34),
            text=" - ",
            callback=lambda: (self.sound.change_sfx_volume(-0.1), self.sound.play("match")),
            bg_color=(44, 62, 80),
            hover_color=(52, 73, 94),
            font_size=18,
        )
        self.buttons.append(self.btn_sfx_down)

        # Botón [+] SFX
        self.btn_sfx_up = Button(
            rect=pygame.Rect(self.rect.x + 285, row2_y, 45, 34),
            text=" + ",
            callback=lambda: (self.sound.change_sfx_volume(+0.1), self.sound.play("match")),
            bg_color=(44, 62, 80),
            hover_color=(52, 73, 94),
            font_size=18,
        )
        self.buttons.append(self.btn_sfx_up)

        # Botón Mute SFX
        self.btn_sfx_mute = Button(
            rect=pygame.Rect(self.rect.x + 360, row2_y, 220, 34),
            text="Silenciar Efectos",
            callback=self._toggle_sfx_mute,
            bg_color=(192, 57, 43),
            hover_color=(231, 76, 60),
            font_size=14,
        )
        self.buttons.append(self.btn_sfx_mute)

        # 3. Fila inferior: Probar sonido y Cerrar
        row3_y = self.rect.bottom - 58
        self.btn_close = Button(
            rect=pygame.Rect(self.rect.centerx + 20, row3_y, 190, 40),
            text="Guardar y Cerrar",
            callback=self.on_close,
            bg_color=(39, 174, 96),
            hover_color=(46, 204, 113),
            font_size=14,
        )
        self.buttons.append(self.btn_close)

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
        # Fondo oscuro
        overlay = pygame.Surface(self.screen_size, pygame.SRCALPHA)
        overlay.fill((10, 14, 23, 195))
        surface.blit(overlay, (0, 0))

        # Ventana del modal
        pygame.draw.rect(surface, (28, 35, 51), self.rect, border_radius=14)
        pygame.draw.rect(surface, (60, 75, 105), self.rect, width=2, border_radius=14)

        # Título
        title_surf = self.title_font.render("AJUSTES DE AUDIO Y VOLUMEN", True, (241, 196, 15))
        title_rect = title_surf.get_rect(center=(self.rect.centerx, self.rect.y + 34))
        surface.blit(title_surf, title_rect)

        # Separador decorativo
        sep_y = self.rect.y + 60
        pygame.draw.line(surface, (50, 65, 90), (self.rect.x + 30, sep_y), (self.rect.right - 30, sep_y), 2)

        # ----------------- SECCIÓN 1: MÚSICA DE FONDO -----------------
        sec1_y = self.rect.y + 78
        sec1_surf = self.section_font.render("Música de Fondo (Menú y Juego)", True, (236, 240, 241))
        surface.blit(sec1_surf, (self.rect.x + 40, sec1_y))

        # Texto porcentaje
        pct_mus = int(self.sound.music_volume * 100)
        mus_status = "MUTED" if self.sound.music_muted else f"{pct_mus}%"
        mus_col = (231, 76, 60) if self.sound.music_muted else (52, 152, 219)
        vol_mus_surf = self.val_font.render(mus_status, True, mus_col)
        surface.blit(vol_mus_surf, (self.rect.x + 360, sec1_y + 2))

        # Barra visual de volumen música (entre btn - y btn +)
        bar1_rect = pygame.Rect(self.rect.x + 95, self.rect.y + 126, 180, 22)
        pygame.draw.rect(surface, (20, 25, 36), bar1_rect, border_radius=6)
        pygame.draw.rect(surface, (60, 75, 105), bar1_rect, width=1, border_radius=6)

        fill1_w = int(bar1_rect.width * (0.0 if self.sound.music_muted else self.sound.music_volume))
        if fill1_w > 0:
            fill1_rect = pygame.Rect(bar1_rect.x + 2, bar1_rect.y + 2, max(4, fill1_w - 4), bar1_rect.height - 4)
            pygame.draw.rect(surface, (52, 152, 219), fill1_rect, border_radius=4)

        # Actualizar texto del botón de mute música
        self.btn_mus_mute.text = "Activar Música 🔊" if self.sound.music_muted else "Silenciar Música 🔇"
        self.btn_mus_mute.bg_color = (39, 174, 96) if self.sound.music_muted else (192, 57, 43)
        self.btn_mus_mute.hover_color = (46, 204, 113) if self.sound.music_muted else (231, 76, 60)

        # ----------------- SECCIÓN 2: EFECTOS DE SONIDO -----------------
        sec2_y = self.rect.y + 180
        sec2_surf = self.section_font.render("Efectos de Sonido (Acierto, Fallo, Cartas)", True, (236, 240, 241))
        surface.blit(sec2_surf, (self.rect.x + 40, sec2_y))

        pct_sfx = int(self.sound.sfx_volume * 100)
        sfx_status = "MUTED" if self.sound.sfx_muted else f"{pct_sfx}%"
        sfx_col = (231, 76, 60) if self.sound.sfx_muted else (46, 204, 113)
        vol_sfx_surf = self.val_font.render(sfx_status, True, sfx_col)
        surface.blit(vol_sfx_surf, (self.rect.x + 360, sec2_y + 2))

        # Barra visual de volumen efectos
        bar2_rect = pygame.Rect(self.rect.x + 95, self.rect.y + 231, 180, 22)
        pygame.draw.rect(surface, (20, 25, 36), bar2_rect, border_radius=6)
        pygame.draw.rect(surface, (60, 75, 105), bar2_rect, width=1, border_radius=6)

        fill2_w = int(bar2_rect.width * (0.0 if self.sound.sfx_muted else self.sound.sfx_volume))
        if fill2_w > 0:
            fill2_rect = pygame.Rect(bar2_rect.x + 2, bar2_rect.y + 2, max(4, fill2_w - 4), bar2_rect.height - 4)
            pygame.draw.rect(surface, (46, 204, 113), fill2_rect, border_radius=4)

        # Actualizar texto del botón de mute SFX
        self.btn_sfx_mute.text = "Activar Efectos 🔔" if self.sound.sfx_muted else "Silenciar Efectos 🔕"
        self.btn_sfx_mute.bg_color = (39, 174, 96) if self.sound.sfx_muted else (192, 57, 43)
        self.btn_sfx_mute.hover_color = (46, 204, 113) if self.sound.sfx_muted else (231, 76, 60)

        # Dibujar todos los botones
        for btn in self.buttons:
            btn.draw(surface)


