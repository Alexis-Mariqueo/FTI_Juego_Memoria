import pygame
from Vista.MenuView import MenuView

class MenuControlador:
    def __init__(self, pantalla, configuracion):
        self.pantalla = pantalla
        self.configuracion = configuracion
        # 1. Pasamos la configuración a la vista
        self.vista = MenuView(pantalla, self.configuracion)
    
    def actualizar(self, eventos):
        pos_mouse = pygame.mouse.get_pos()
        
        # Ejecutar sonido hover 
        self.vista.verificar_hover(pos_mouse)

        for event in eventos:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # Ejecutar sonido click y retornar nuevo estado
                if self.vista.btn_jugar.collidepoint(pos_mouse):
                    self.vista.reproducir_click()
                    return "JUEGO"
                
                elif self.vista.btn_ajuste.collidepoint(pos_mouse):
                    self.vista.reproducir_click()
                    return "AJUSTE" 
                
                elif self.vista.btn_ranking.collidepoint(pos_mouse):
                    self.vista.reproducir_click()
                    return "RANKING"
                
                elif self.vista.btn_salir.collidepoint(pos_mouse):
                    self.vista.reproducir_click()
                    # 2. Delegar el cierre al main.py
                    return "SALIR"

        # 3. Dibujar al final del ciclo
        self.vista.dibujar()
        
        return "MENU"