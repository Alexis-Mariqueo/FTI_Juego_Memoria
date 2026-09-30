import pygame
from Vista.ConfiguracionPartidaView import ConfiguracionPartidaView

class ConfiguracionPartidaControlador:
    def __init__(self, pantalla, configuracion):
        self.vista = ConfiguracionPartidaView(pantalla, configuracion)
        
        # Variables de estado (Por defecto podemos preseleccionar Fácil y 5 mins, o dejarlos en None)
        self.dificultad_seleccionada = "FACIL" 
        self.tiempo_seleccionado = 5

    def actualizar(self, eventos):
        pos_mouse = pygame.mouse.get_pos()

        for event in eventos:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                
                # Clics en Dificultad
                if self.vista.btn_facil.collidepoint(pos_mouse):
                    self.vista.reproducir_click()
                    self.dificultad_seleccionada = "FACIL"
                elif self.vista.btn_dificil.collidepoint(pos_mouse):
                    self.vista.reproducir_click()
                    self.dificultad_seleccionada = "DIFICIL"
                
                # Clics en Tiempo
                elif self.vista.btn_tiempo_5.collidepoint(pos_mouse):
                    self.vista.reproducir_click()
                    self.tiempo_seleccionado = 5
                elif self.vista.btn_tiempo_10.collidepoint(pos_mouse):
                    self.vista.reproducir_click()
                    self.tiempo_seleccionado = 10
                
                # Clic en Comenzar (Solo funciona si ambas opciones están seleccionadas)
                elif self.vista.btn_comenzar.collidepoint(pos_mouse):
                    if self.dificultad_seleccionada and self.tiempo_seleccionado:
                        self.vista.reproducir_click()
                        
                        # AQUÍ GUARDAS LA CONFIGURACIÓN EN TU JUEGO O SE LA PASAS AL JUEGOCONTROLADOR
                        # ...
                        
                        return "JUEGO" # Transiciona a la pantalla del juego
                
                # Clic en Atrás
                elif self.vista.btn_volver.collidepoint(pos_mouse):
                    self.vista.reproducir_click()
                    return "MENU"

        self.vista.dibujar(self.dificultad_seleccionada, self.tiempo_seleccionado)
        
        return "CONFIG_PARTIDA"