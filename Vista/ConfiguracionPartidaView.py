import pygame

class ConfiguracionPartidaView:
    def __init__(self, pantalla, configuracion):
        self.pantalla = pantalla
        self.configuracion = configuracion
        
        # Fuentes
        self.fuente_titulo = pygame.font.Font(None, 54)
        self.fuente_subtitulo = pygame.font.Font(None, 40)
        self.fuente_boton = pygame.font.Font(None, 32)

        ancho = self.pantalla.get_width()
        alto = self.pantalla.get_height()

        # 1. Áreas de colisión (Botones)
        # Botón Volver (Esquina inferior izquierda)
        self.btn_volver = pygame.Rect(20, alto - 70, 120, 50)
        
        # Botones de Dificultad (Fila superior)
        self.btn_facil = pygame.Rect(ancho // 2 - 210, 150, 200, 50)
        self.btn_dificil = pygame.Rect(ancho // 2 + 10, 150, 200, 50)
        
        # Botones de Tiempo (Fila intermedia)
        self.btn_tiempo_5 = pygame.Rect(ancho // 2 - 210, 270, 200, 50)
        self.btn_tiempo_10 = pygame.Rect(ancho // 2 + 10, 270, 200, 50)
        
        # Botón Comenzar (Centrado abajo)
        self.btn_comenzar = pygame.Rect(ancho // 2 - 125, 370, 250, 60)

        # Sonido y Fondo
        try:
            self.sonido_click = pygame.mixer.Sound("Efectos Sonido/boton_click.mp3")
        except:
            self.sonido_click = None

        try:
            self.fondo = pygame.image.load("Imagenes/fondo_1.png").convert() 
            self.fondo = pygame.transform.scale(self.fondo, self.pantalla.get_size())
        except:
            self.fondo = None

    def dibujar(self, dif_seleccionada, tiempo_seleccionado):
        """
        dif_seleccionada: "FACIL" o "DIFICIL"
        tiempo_seleccionado: 5 o 10
        """
        # Fondo
        if self.fondo:
            self.pantalla.blit(self.fondo, (0, 0))
        else:
            self.pantalla.fill((30, 30, 30))

        # Textos de Encabezado
        txt_titulo = self.fuente_titulo.render("Configurar Partida", True, (255, 215, 0))
        self.pantalla.blit(txt_titulo, (self.pantalla.get_width()//2 - txt_titulo.get_width()//2, 30))

        txt_dif = self.fuente_subtitulo.render("Dificultad", True, (255, 255, 255))
        self.pantalla.blit(txt_dif, (self.pantalla.get_width()//2 - txt_dif.get_width()//2, 110))
        
        txt_tiempo = self.fuente_subtitulo.render("Tiempo", True, (255, 255, 255))
        self.pantalla.blit(txt_tiempo, (self.pantalla.get_width()//2 - txt_tiempo.get_width()//2, 230))

        # --- DIBUJAR BOTONES DE DIFICULTAD ---
        color_facil = (50, 200, 50) if dif_seleccionada == "FACIL" else (100, 100, 100)
        color_dificil = (50, 200, 50) if dif_seleccionada == "DIFICIL" else (100, 100, 100)
        
        self._dibujar_boton(self.btn_facil, color_facil, "Fácil (8 Cartas)")
        self._dibujar_boton(self.btn_dificil, color_dificil, "Difícil (16 Cartas)")

        # --- DIBUJAR BOTONES DE TIEMPO ---
        color_t5 = (50, 200, 50) if tiempo_seleccionado == 5 else (100, 100, 100)
        color_t10 = (50, 200, 50) if tiempo_seleccionado == 10 else (100, 100, 100)
        
        self._dibujar_boton(self.btn_tiempo_5, color_t5, "5 Minutos")
        self._dibujar_boton(self.btn_tiempo_10, color_t10, "10 Minutos")

        # --- DIBUJAR BOTÓN COMENZAR ---
        # Si todo está seleccionado, lo pintamos de azul vivo, si no, un azul oscuro apagado
        if dif_seleccionada and tiempo_seleccionado:
            color_comenzar = (50, 150, 255)
        else:
            color_comenzar = (60, 80, 120) 
            
        pygame.draw.rect(self.pantalla, color_comenzar, self.btn_comenzar, border_radius=10)
        pygame.draw.rect(self.pantalla, (255, 255, 255), self.btn_comenzar, width=2, border_radius=10)
        txt_comenzar = self.fuente_subtitulo.render("Comenzar Juego", True, (255, 255, 255))
        self.pantalla.blit(txt_comenzar, (self.btn_comenzar.centerx - txt_comenzar.get_width()//2, self.btn_comenzar.centery - txt_comenzar.get_height()//2))

        # --- DIBUJAR BOTÓN VOLVER ---
        pygame.draw.rect(self.pantalla, (200, 50, 50), self.btn_volver, border_radius=5)
        pygame.draw.rect(self.pantalla, (255, 150, 150), self.btn_volver, width=2, border_radius=5)
        txt_volver = self.fuente_boton.render("Atrás", True, (255, 255, 255))
        self.pantalla.blit(txt_volver, (self.btn_volver.centerx - txt_volver.get_width()//2, self.btn_volver.centery - txt_volver.get_height()//2))

    def _dibujar_boton(self, rectangulo, color_fondo, texto):
        """Método auxiliar para no repetir código al dibujar los 4 botones de opciones."""
        pygame.draw.rect(self.pantalla, color_fondo, rectangulo, border_radius=8)
        # Si el botón está seleccionado (verde), le ponemos borde blanco para que resalte
        ancho_borde = 3 if color_fondo == (50, 200, 50) else 1
        pygame.draw.rect(self.pantalla, (200, 200, 200), rectangulo, width=ancho_borde, border_radius=8)
        
        txt = self.fuente_boton.render(texto, True, (255, 255, 255))
        self.pantalla.blit(txt, (rectangulo.centerx - txt.get_width()//2, rectangulo.centery - txt.get_height()//2))

    def reproducir_click(self):
        if self.sonido_click:
            volumen = self.configuracion.get_volumen_efectos()
            self.sonido_click.set_volume(volumen)
            self.sonido_click.play()