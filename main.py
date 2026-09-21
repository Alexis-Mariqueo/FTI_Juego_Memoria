import pygame
import sys

# Inicializar Pygame
pygame.init()

# 1. Configuración de pantallas (Resolución retro y escala)
INTERNAL_WIDTH, INTERNAL_HEIGHT = 320, 240  # Resolución clásica de pixel art
WINDOW_SCALE = 2  # Tamaño final de la ventana (se multiplicará por 2 -> 640x480)
screen = pygame.display.set_mode((INTERNAL_WIDTH * WINDOW_SCALE, INTERNAL_HEIGHT * WINDOW_SCALE))

# Superficie interna donde dibujaremos todo en baja resolución
canvas = pygame.Surface((INTERNAL_WIDTH, INTERNAL_HEIGHT))

pygame.display.set_caption("Memotest Pixel Art")
clock = pygame.time.Clock()

# 2. Cargar recursos (Sprites / Imágenes)
# .convert_alpha() optimiza la imagen y respeta las transparencias (fondo transparente)
dorso_carta = pygame.image.load("assets/cartas/dorso.png").convert_alpha()

# Coordenadas de ejemplo para dibujar una carta en el tablero virtual
carta_x, carta_y = 50, 50

# 3. Bucle Principal del Juego (Game Loop)
running = True
while running:
    # Manejo de eventos (clicks, cerrar ventana, etc.)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            pygame.quit()
            sys.exit()

    # --- LÓGICA DE DIBUJO EN EL LIENZO INTERNO ---
    canvas.fill((30, 30, 46)) # Color de fondo retro (ej: un azul oscuro/grisáceo)

    # Dibujar la carta en el lienzo virtual
    canvas.blit(dorso_carta, (carta_x, carta_y))

    # --- ESCALADO FINAL PARA MANTENER EL PIXEL ART NÍDITO ---
    # Scalamos el canvas interno al tamaño de la ventana real usando transform.scale
    scaled_surface = pygame.transform.scale(canvas, (INTERNAL_WIDTH * WINDOW_SCALE, INTERNAL_HEIGHT * WINDOW_SCALE))
    screen.blit(scaled_surface, (0, 0))

    # Actualizar pantalla
    pygame.display.flip()
    clock.render_fps = 60
    clock.tick(60)