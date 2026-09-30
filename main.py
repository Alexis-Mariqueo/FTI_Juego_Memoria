import pygame
import sys
from Clases.Configuracion import Configuracion
from Controlador.MenuControlador import MenuControlador
from Controlador.RankingControlador import RankingControlador
from Controlador.AjusteControlador import AjusteControlador
from Controlador.ConfiguracionPartida import ConfiguracionPartidaControlador
from Controlador.JuegoControlador import JuegoControlador

def main():
    pygame.init()
    pygame.mixer.init() 
    pantalla = pygame.display.set_mode((640, 480))
    pygame.display.set_caption("Memotest Pixel Art")

    # 1. Ocultar el cursor de Windows
    pygame.mouse.set_visible(False)
    
    # 2. Cargar el cursor personalizado
    cursor_img = pygame.image.load("Imagenes/cursor_mouse.png").convert_alpha()

    reloj = pygame.time.Clock()

    # 3. Inicializar la configuración global
    configuracion = Configuracion()
    
    #Aplicar el volumen de la musica del juego Antes de Arrancar
    pygame.mixer.music.set_volume(configuracion.get_volumen_musica())

    

    # 4. Instanciar los controladores inyectando la configuración
    controlador_menu = MenuControlador(pantalla, configuracion)
    controlador_ajuste = AjusteControlador(pantalla, configuracion)
    controlador_ranking = RankingControlador(pantalla,configuracion)
    controlador_config_partida = ConfiguracionPartidaControlador(pantalla, configuracion)
    
    controlador_actual = controlador_menu
    estado_actual = "MENU"

    while True:
        eventos = pygame.event.get()
        for event in eventos:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        # El controlador actual procesa la lógica y devuelve qué estado sigue
        nuevo_estado = controlador_actual.actualizar(eventos)

        # 5. Máquina de estados bidireccional
        if nuevo_estado != estado_actual:
            if nuevo_estado == "MENU":
                controlador_actual = controlador_menu
            elif nuevo_estado == "CONFIG_PARTIDA":
                controlador_actual = controlador_config_partida
                if nuevo_estado == "JUEGO":
                    dificultad = controlador_config_partida.dificultad_seleccionada
                    tiempo = controlador_config_partida.tiempo_seleccionado
                    # Creamos el juego con esas opciones
                    controlador_juego = JuegoControlador(pantalla, configuracion, dificultad, tiempo)
                    controlador_actual = controlador_juego
            elif nuevo_estado == "AJUSTE":
                controlador_actual = controlador_ajuste
            elif nuevo_estado == "RANKING":
                controlador_actual = controlador_ranking
            elif nuevo_estado == "SALIR":
                pygame.quit()
                sys.exit()
            
            estado_actual = nuevo_estado

        # Dibujar cursor
        pos_mouse = pygame.mouse.get_pos()
        pantalla.blit(cursor_img, pos_mouse)

        pygame.display.flip()
        reloj.tick(60)

if __name__ == "__main__":
    main()