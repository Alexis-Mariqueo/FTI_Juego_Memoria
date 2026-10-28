"""
Módulo de Tarjetas / Cartas del Memotest con animación suave de volteo.
"""

import pygame
from typing import Tuple

# Estados de la carta
STATE_FACE_DOWN = "FACE_DOWN"
STATE_FLIPPING_UP = "FLIPPING_UP"
STATE_FACE_UP = "FACE_UP"
STATE_FLIPPING_DOWN = "FLIPPING_DOWN"
STATE_MATCHED = "MATCHED"


class Card:
    """Representa una carta individual del tablero de juego."""

    FLIP_DURATION = 0.22  # Segundos para completar el volteo

    def __init__(
        self,
        card_id: int,
        pair_id: str,
        front_image: pygame.Surface,
        back_image: pygame.Surface,
        rect: pygame.Rect,
    ):
        self.card_id = card_id
        self.pair_id = pair_id
        self.front_image = front_image
        self.back_image = back_image
        self.rect = rect
        self.original_width = rect.width
        self.original_height = rect.height

        self.state = STATE_FACE_DOWN
        self.flip_progress = 0.0  # de 0.0 a 1.0 durante la animación
        self.is_hovered = False

    def can_click(self) -> bool:
        """Determina si la carta puede ser seleccionada válidamente."""
        return self.state == STATE_FACE_DOWN

    def is_face_up(self) -> bool:
        """Indica si la carta está volteada (boca arriba) o emparejada."""
        return self.state in {STATE_FACE_UP, STATE_MATCHED} or (
            self.state == STATE_FLIPPING_UP and self.flip_progress >= 0.5
        ) or (
            self.state == STATE_FLIPPING_DOWN and self.flip_progress < 0.5
        )

    def flip_up(self):
        """Inicia la animación de voltear hacia arriba."""
        if self.state == STATE_FACE_DOWN:
            self.state = STATE_FLIPPING_UP
            self.flip_progress = 0.0

    def flip_down(self):
        """Inicia la animación de voltear hacia abajo."""
        if self.state == STATE_FACE_UP:
            self.state = STATE_FLIPPING_DOWN
            self.flip_progress = 0.0

    def set_matched(self):
        """Marca la carta como emparejada exitosamente."""
        self.state = STATE_MATCHED

    def update(self, dt: float):
        """Actualiza la animación de giro con el tiempo delta en segundos."""
        if self.state in {STATE_FLIPPING_UP, STATE_FLIPPING_DOWN}:
            self.flip_progress += dt / self.FLIP_DURATION
            if self.flip_progress >= 1.0:
                self.flip_progress = 1.0
                if self.state == STATE_FLIPPING_UP:
                    self.state = STATE_FACE_UP
                elif self.state == STATE_FLIPPING_DOWN:
                    self.state = STATE_FACE_DOWN

    def draw(self, surface: pygame.Surface):
        """Dibuja la carta en la superficie con su animación y bordes acordes a su estado."""
        # Determinar qué cara mostrar y el ancho aparente según el progreso
        if self.state in {STATE_FLIPPING_UP, STATE_FLIPPING_DOWN}:
            # Simulación de giro en perspectiva: escala horizontal entre 1.0 -> 0.0 -> 1.0
            if self.flip_progress < 0.5:
                scale_x = 1.0 - (self.flip_progress * 2.0)
                showing_front = (self.state == STATE_FLIPPING_DOWN)
            else:
                scale_x = (self.flip_progress - 0.5) * 2.0
                showing_front = (self.state == STATE_FLIPPING_UP)
        elif self.state in {STATE_FACE_UP, STATE_MATCHED}:
            scale_x = 1.0
            showing_front = True
        else:  # STATE_FACE_DOWN
            scale_x = 1.0
            showing_front = False

        current_width = max(2, int(self.original_width * scale_x))
        x_center = self.rect.centerx
        draw_rect = pygame.Rect(0, 0, current_width, self.original_height)
        draw_rect.center = (x_center, self.rect.centery)

        # Superficie de la cara
        target_img = self.front_image if showing_front else self.back_image
        if current_width != self.original_width or self.original_height != target_img.get_height():
            rendered_surf = pygame.transform.smoothscale(target_img, (current_width, self.original_height))
        else:
            rendered_surf = target_img

        # Sombra sutil
        shadow_rect = draw_rect.copy()
        shadow_rect.x += 3
        shadow_rect.y += 4
        shadow_surf = pygame.Surface((draw_rect.width, draw_rect.height), pygame.SRCALPHA)
        shadow_surf.fill((0, 0, 0, 60))
        surface.blit(shadow_surf, shadow_rect)

        # Dibujar la carta
        surface.blit(rendered_surf, draw_rect)

        # Bordes destacados según estado
        if self.state == STATE_MATCHED:
            # Borde verde esmeralda / dorado para pares resueltos
            pygame.draw.rect(surface, (46, 204, 113), draw_rect, width=3, border_radius=6)
        elif self.state == STATE_FACE_UP:
            # Borde cian vibrante para la carta actualmente seleccionada
            pygame.draw.rect(surface, (52, 152, 219), draw_rect, width=3, border_radius=6)
        elif self.is_hovered and self.state == STATE_FACE_DOWN:
            # Borde sutil al pasar el cursor
            pygame.draw.rect(surface, (241, 196, 15), draw_rect, width=2, border_radius=6)
        else:
            # Borde normal oscuro fino
            pygame.draw.rect(surface, (40, 50, 70), draw_rect, width=1, border_radius=6)

