"""
Punto de Entrada Principal (Main) para el Juego de la Memoria (Memotest).
Fundamentos Teóricos de Informática - UNPSJB - Grupo N°2 (2026)
Integrantes: Alexis Mariqueo, Cesar Millavanque, Daniel Enegron, Kadir Martinez
"""

import sys
import pygame
from game_manager import GameManager


def main():
    # Inicialización de Pygame
    pygame.init()
    pygame.display.set_caption("Juego de la Memoria (Memotest) - FTI Grupo N°2")

    window_size = (1280, 720)
    screen = pygame.display.set_mode(window_size)
    clock = pygame.time.Clock()

    # Intentar cargar ícono de la ventana desde los assets si está disponible
    try:
        icon = pygame.image.load("assets/cartas/Carta python.png")
        pygame.display.set_icon(icon)
    except Exception:
        pass

    game_manager = GameManager(screen_size=window_size)

    running = True
    while running and game_manager.is_running:
        dt = clock.tick(60) / 1000.0  # Delta time en segundos a 60 FPS

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if game_manager.active_modal:
                        game_manager.active_modal = None
                    elif game_manager.state != "MENU":
                        game_manager.go_to_menu()
                    else:
                        running = False
                        break

            game_manager.handle_event(event)
            if not game_manager.is_running:
                running = False
                break

        game_manager.update(dt)
        game_manager.draw(screen)
        pygame.display.flip()

    pygame.quit()
    sys.exit(0)


if __name__ == "__main__":
    main()

