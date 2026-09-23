import pygame
from Vista.AjusteView import AjusteView 

class AjusteControlador:
    def __init__(self, pantalla, configuracion):
        self.pantalla = pantalla
        self.configuracion = configuracion
        self.vista = AjusteView(pantalla, self.configuracion)
        
        self.arrastrando_efectos = False
        self.arrastrando_musica = False
        
    def actualizar(self, eventos):
        pos_mouse = pygame.mouse.get_pos()
        clic_mantenido = pygame.mouse.get_pressed()[0]

        if clic_mantenido:
            # --- BARRA DE MÚSICA ---
            if self.vista.barra_musica.inflate(0, 20).collidepoint(pos_mouse):
                nuevo_volumen = self.vista.calcular_nuevo_volumen(self.vista.barra_musica, pos_mouse[0])
                
                # Forzar silencio total si está muy cerca de 0
                if nuevo_volumen < 0.03: 
                    nuevo_volumen = 0.0
                
                # Usar tu método original para actualizar RAM
                self.configuracion.set_volumen_musica(nuevo_volumen)
                pygame.mixer.music.set_volume(nuevo_volumen)
                self.arrastrando_musica = True
            
            # --- BARRA DE EFECTOS ---
            elif self.vista.barra_efectos.inflate(0, 20).collidepoint(pos_mouse):
                nuevo_volumen = self.vista.calcular_nuevo_volumen(self.vista.barra_efectos, pos_mouse[0])
                
                if nuevo_volumen < 0.03:
                    nuevo_volumen = 0.0
                    
                self.configuracion.set_volumen_efectos(nuevo_volumen)
                self.arrastrando_efectos = True

        for event in eventos:
            # Clic para salir
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.vista.btn_volver.collidepoint(pos_mouse):
                    # Forzamos un guardado de seguridad al apretar "Atrás"
                    self.configuracion.guardar()
                    return "MENU"
            
            # Soltar el clic
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                
                if self.arrastrando_efectos or self.arrastrando_musica:
                    self.configuracion.guardar()
                
                if self.arrastrando_efectos:
                    self.vista.probar_sonido_efectos(self.configuracion.get_volumen_efectos())
                
                self.arrastrando_efectos = False
                self.arrastrando_musica = False

        self.vista.dibujar()
        
        return "AJUSTE"