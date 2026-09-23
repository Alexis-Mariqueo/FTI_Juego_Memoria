import pygame

class MenuView:
    
    def __init__(self, pantalla, configuracion):
        self.pantalla = pantalla
        self.fuente = pygame.font.Font(None, 36)
        
        self.configuracion = configuracion 
        
        # 1. Cargamos los efectos (PERO NO les seteamos el volumen todavía)
        self.sonido_hover = pygame.mixer.Sound("Efectos Sonido/boton_sonido.mp3")
        self.sonido_click = pygame.mixer.Sound("Efectos Sonido/boton_click.mp3")
        
        # 2. La música usa el motor GLOBAL de Pygame, no la clase Sound.
        # Verificamos si ya hay música sonando para no reiniciarla si volvemos desde Ajustes
        if not pygame.mixer.music.get_busy():
            pygame.mixer.music.load("Musica/Save Room.mp3")
            pygame.mixer.music.set_volume(self.configuracion.get_volumen_musica())
            pygame.mixer.music.play(-1) # -1 para que se repita en bucle
        
        self.boton_hover_actual = None
        
        # Cargar el fondo
        self.fondo = pygame.image.load("Imagenes/fondo_1.jpg").convert()
        tamaño_pantalla = self.pantalla.get_size()
        self.fondo = pygame.transform.scale(self.fondo, tamaño_pantalla)
        
        # Definir los rectángulos de los 4 botones
        self.btn_jugar = pygame.Rect(220, 120, 200, 50)
        self.btn_ajuste = pygame.Rect(220, 190, 200, 50) 
        self.btn_ranking = pygame.Rect(220, 260, 200, 50)
        self.btn_salir = pygame.Rect(220, 330, 200, 50)

    def dibujar(self):
        self.pantalla.blit(self.fondo, (0, 0))

        pygame.draw.rect(self.pantalla, (200, 50, 50), self.btn_jugar)
        pygame.draw.rect(self.pantalla, (200, 150, 50), self.btn_ajuste) 
        pygame.draw.rect(self.pantalla, (50, 200, 50), self.btn_ranking)
        pygame.draw.rect(self.pantalla, (50, 50, 200), self.btn_salir)

        texto_jugar = self.fuente.render("Jugar", True, (255, 255, 255))
        texto_ajuste = self.fuente.render("Ajuste", True, (255, 255, 255)) 
        texto_ranking = self.fuente.render("Ranking", True, (255, 255, 255))
        texto_salir = self.fuente.render("Salir", True, (255, 255, 255))

        self.pantalla.blit(texto_jugar, (self.btn_jugar.x + 65, self.btn_jugar.y + 15))
        self.pantalla.blit(texto_ajuste, (self.btn_ajuste.x + 65, self.btn_ajuste.y + 15))
        self.pantalla.blit(texto_ranking, (self.btn_ranking.x + 45, self.btn_ranking.y + 15))
        self.pantalla.blit(texto_salir, (self.btn_salir.x + 70, self.btn_salir.y + 15))

    def verificar_hover(self, pos_mouse):
        botones = [self.btn_jugar, self.btn_ajuste, self.btn_ranking, self.btn_salir]
        boton_tocado = next((btn for btn in botones if btn.collidepoint(pos_mouse)), None)

        if boton_tocado != self.boton_hover_actual:
            if boton_tocado is not None:
                # 3. Leemos la RAM y seteamos el volumen UN MILISEGUNDO antes de reproducir
                volumen_actual = self.configuracion.get_volumen_efectos()
                self.sonido_hover.set_volume(volumen_actual)
                self.sonido_hover.play()
            self.boton_hover_actual = boton_tocado
    
    def reproducir_click(self):
        # 4. Hacemos lo mismo para el click
        volumen_actual = self.configuracion.get_volumen_efectos()
        self.sonido_click.set_volume(volumen_actual)
        self.sonido_click.play()
        
        
       