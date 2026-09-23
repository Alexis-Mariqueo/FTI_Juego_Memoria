import pygame

class AjusteView:
    def __init__(self, pantalla, configuracion):
        self.pantalla = pantalla
        self.configuracion = configuracion 
        self.fuente_titulo = pygame.font.Font(None, 48)
        self.fuente_normal = pygame.font.Font(None, 36)
        
        try:
            self.sonido_prueba = pygame.mixer.Sound("Efectos Sonido/boton_click.mp3")
            self.sonido_prueba.set_volume(self.configuracion.get_volumen_efectos())
        except:
            self.sonido_prueba = None 
        
        try:
            self.fondo = pygame.image.load("Imagenes/fondo_1.png").convert() 
            self.fondo = pygame.transform.scale(self.fondo, self.pantalla.get_size())
        except:
            self.fondo = None

        ancho = self.pantalla.get_width()
        
        self.barra_musica = pygame.Rect(ancho // 2 - 150, 200, 300, 20)
        self.barra_efectos = pygame.Rect(ancho // 2 - 150, 300, 300, 20)
        self.btn_volver = pygame.Rect(ancho // 2 - 100, 450, 200, 50)

    def dibujar(self):
        if self.fondo:
            self.pantalla.blit(self.fondo, (0, 0))
        else:
            self.pantalla.fill((30, 30, 30))

        txt_titulo = self.fuente_titulo.render("Ajustes de Sonido", True, (255, 255, 255))
        self.pantalla.blit(txt_titulo, (self.pantalla.get_width()//2 - txt_titulo.get_width()//2, 80))

        # Aseguramos que el valor extraído sea flotante y esté estrictamente entre 0.0 y 1.0
        vol_musica = max(0.0, min(1.0, float(self.configuracion.get_volumen_musica())))
        vol_efectos = max(0.0, min(1.0, float(self.configuracion.get_volumen_efectos())))

        # Dibujar UI Música
        txt_musica = self.fuente_normal.render(f"Música: {int(vol_musica * 100)}%", True, (255, 255, 255))
        self.pantalla.blit(txt_musica, (self.barra_musica.x, self.barra_musica.y - 35))
        
        pygame.draw.rect(self.pantalla, (100, 100, 100), self.barra_musica)
        ancho_musica = int(self.barra_musica.width * vol_musica)
        rect_llena_m = pygame.Rect(self.barra_musica.x, self.barra_musica.y, ancho_musica, 20)
        pygame.draw.rect(self.pantalla, (50, 200, 50), rect_llena_m)
        pygame.draw.circle(self.pantalla, (255, 255, 255), (self.barra_musica.x + ancho_musica, self.barra_musica.centery), 12)

        # Dibujar UI Efectos
        txt_efectos = self.fuente_normal.render(f"Efectos: {int(vol_efectos * 100)}%", True, (255, 255, 255))
        self.pantalla.blit(txt_efectos, (self.barra_efectos.x, self.barra_efectos.y - 35))
        
        pygame.draw.rect(self.pantalla, (100, 100, 100), self.barra_efectos)
        ancho_efectos = int(self.barra_efectos.width * vol_efectos)
        rect_llena_e = pygame.Rect(self.barra_efectos.x, self.barra_efectos.y, ancho_efectos, 20)
        pygame.draw.rect(self.pantalla, (50, 150, 255), rect_llena_e)
        pygame.draw.circle(self.pantalla, (255, 255, 255), (self.barra_efectos.x + ancho_efectos, self.barra_efectos.centery), 12)

        # Dibujar Botón Volver
        pygame.draw.rect(self.pantalla, (200, 50, 50), self.btn_volver)
        txt_volver = self.fuente_normal.render("Atrás", True, (255, 255, 255))
        self.pantalla.blit(txt_volver, (self.btn_volver.centerx - txt_volver.get_width()//2, self.btn_volver.centery - txt_volver.get_height()//2))

    def calcular_nuevo_volumen(self, barra, pos_mouse_x):
        pos_relativa = pos_mouse_x - barra.x
        pos_relativa = max(0, min(pos_relativa, barra.width))
        return pos_relativa / barra.width

    def probar_sonido_efectos(self, nuevo_volumen):
        if self.sonido_prueba:
            self.sonido_prueba.set_volume(nuevo_volumen)
            self.sonido_prueba.play()