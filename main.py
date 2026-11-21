"""
Punto de Entrada Principal (Main) para el Juego de la Memoria (Memotest).
Fundamentos Teóricos de Informática - UNPSJB - Grupo N°2 (2026)
Integrantes: Alexis Mariqueo, Cesar Millavanque, Daniel Enegron, Kadir Martinez
"""

import json
import os
import sys
import pygame
from game_manager import GameManager


def main():
    # Inicialización de Pygame
    pygame.init()
    pygame.display.set_caption("Juego de la Memoria (Memotest) - FTI Grupo N°2")

    window_size = (1280, 720)

    # Cargar preferencia de pantalla completa desde display_settings.json si existe
    is_fullscreen = False
    try:
        if os.path.exists("display_settings.json"):
            with open("display_settings.json", "r", encoding="utf-8") as f:
                is_fullscreen = json.load(f).get("fullscreen", False)
    except Exception:
        pass

    flags = pygame.SCALED
    if is_fullscreen:
        flags |= pygame.FULLSCREEN

    screen = pygame.display.set_mode(window_size, flags)
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

        # Obtener la superficie de pantalla activa (soporta cambios dinámicos ventana/fullscreen)
        current_screen = pygame.display.get_surface() or screen
        game_manager.draw(current_screen)
        pygame.display.flip()

    # Guardar configuración de audio, pantalla y partida al salir
    try:
        game_manager.sound.save_config()
        game_manager._save_display_config()
        game_manager._save_game_config()
    except Exception:
        pass

    pygame.quit()
    sys.exit(0)


if __name__ == "__main__":
    main()

