import pygame

class JuegoView:
    def __init__(self, pantalla, configuracion):
        self.pantalla = pantalla
        self.configuracion = configuracion
        
        # Fuentes para HUD y Overlays
        self.fuente_hud = pygame.font.Font(None, 36)
        self.fuente_titulo_fin = pygame.font.Font(None, 72)
        self.fuente_texto = pygame.font.Font(None, 40)
        
        ancho = self.pantalla.get_width()
        alto = self.pantalla.get_height()
        
        # Botones rectangulares (para que el controlador detecte clics)
        self.btn_continuar = pygame.Rect(ancho // 2 - 100, alto // 2 + 80, 200, 50)
        
        # Caja de texto para el nombre
        self.caja_nombre = pygame.Rect(ancho // 2 - 150, alto // 2, 300, 50)
        
        # Capa semitransparente para oscurecer el fondo al ganar/perder
        self.overlay = pygame.Surface((ancho, alto))
        self.overlay.set_alpha(200) # Nivel de transparencia (0-255)
        self.overlay.fill((0, 0, 0)) # Negro
        
        try:
            self.sonido_click = pygame.mixer.Sound("Efectos Sonido/boton_click.mp3")
        except:
            self.sonido_click = None

        try:
            self.fondo = pygame.image.load("Imagenes/fondo_juego.png").convert()
            self.fondo = pygame.transform.scale(self.fondo, self.pantalla.get_size())
        except:
            self.fondo = None

    def dibujar(self, estado_juego, cartas, tiempo, aciertos, puntos, vidas, nombre_actual=""):
        """
        estado_juego: "JUGANDO", "GANO", "PERDIO", "INGRESO_NOMBRE"
        """
        # 1. Dibujar fondo siempre
        if self.fondo:
            self.pantalla.blit(self.fondo, (0, 0))
        else:
            self.pantalla.fill((40, 50, 60))

        # 2. Dibujar HUD principal (Tiempo, Vidas, Aciertos, Puntos)
        self._dibujar_hud(tiempo, vidas, aciertos, puntos)
        
        # 3. Dibujar Cartas (El tablero)
        self._dibujar_cartas(cartas)
        
        # 4. Superponer pantallas emergentes según el estado
        if estado_juego == "PERDIO":
            self._dibujar_pantalla_fin("Has perdido", (255, 100, 100), None)
            
        elif estado_juego == "GANO":
            self._dibujar_pantalla_fin("¡Has ganado!", (100, 255, 100), puntos)
            
        elif estado_juego == "INGRESO_NOMBRE":
            self._dibujar_ingreso_nombre(nombre_actual)

    def _dibujar_hud(self, tiempo, vidas, aciertos, puntos):
        # Esquina superior izquierda: Tiempo
        txt_tiempo = self.fuente_hud.render(f"Tiempo: {tiempo}", True, (255, 255, 255))
        self.pantalla.blit(txt_tiempo, (20, 20))
        
        # Arriba al centro: Vidas
        txt_vidas = self.fuente_hud.render(f"Vidas: {vidas}", True, (255, 50, 50))
        self.pantalla.blit(txt_vidas, (self.pantalla.get_width()//2 - txt_vidas.get_width()//2, 20))
        
        # Abajo a la izquierda: Aciertos
        txt_aciertos = self.fuente_hud.render(f"Aciertos: {aciertos}", True, (255, 255, 255))
        self.pantalla.blit(txt_aciertos, (20, self.pantalla.get_height() - 40))
        
        # Abajo a la derecha: Puntos
        txt_puntos = self.fuente_hud.render(f"Puntos: {puntos}", True, (255, 215, 0))
        self.pantalla.blit(txt_puntos, (self.pantalla.get_width() - 150, self.pantalla.get_height() - 40))

    def _dibujar_cartas(self, cartas):
        # Iterar sobre los objetos carta que envíe el controlador
        for carta in cartas:
            pygame.draw.rect(self.pantalla, carta.color_actual, carta.rect, border_radius=5)
            pygame.draw.rect(self.pantalla, (255, 255, 255), carta.rect, width=2, border_radius=5)
            # Si la carta tiene imagen o texto, se dibujaría aquí comprobando si está volteada

    def _dibujar_pantalla_fin(self, titulo, color_titulo, puntos):
        self.pantalla.blit(self.overlay, (0, 0)) # Oscurece el juego de fondo
        
        # Título
        txt_t = self.fuente_titulo_fin.render(titulo, True, color_titulo)
        self.pantalla.blit(txt_t, (self.pantalla.get_width()//2 - txt_t.get_width()//2, 120))
        
        # Puntaje (Solo si ganó)
        if puntos is not None:
            txt_p = self.fuente_texto.render(f"Puntaje Final: {puntos}", True, (255, 215, 0))
            self.pantalla.blit(txt_p, (self.pantalla.get_width()//2 - txt_p.get_width()//2, 220))
            
        # Botón Continuar
        self._dibujar_boton_continuar()

    def _dibujar_ingreso_nombre(self, nombre_actual):
        self.pantalla.blit(self.overlay, (0, 0))
        
        # Texto instructivo
        txt_inst = self.fuente_texto.render("Ingresa tu nombre para el ranking:", True, (255, 255, 255))
        self.pantalla.blit(txt_inst, (self.pantalla.get_width()//2 - txt_inst.get_width()//2, 150))
        
        # Caja de texto
        pygame.draw.rect(self.pantalla, (255, 255, 255), self.caja_nombre, border_radius=5)
        pygame.draw.rect(self.pantalla, (50, 150, 255), self.caja_nombre, width=3, border_radius=5)
        
        # Texto tipeado
        txt_nombre = self.fuente_texto.render(nombre_actual, True, (0, 0, 0))
        self.pantalla.blit(txt_nombre, (self.caja_nombre.x + 10, self.caja_nombre.y + 12))
        
        # Botón Continuar
        self._dibujar_boton_continuar()

    def _dibujar_boton_continuar(self):
        pygame.draw.rect(self.pantalla, (50, 200, 50), self.btn_continuar, border_radius=8)
        pygame.draw.rect(self.pantalla, (255, 255, 255), self.btn_continuar, width=2, border_radius=8)
        txt_btn = self.fuente_hud.render("Continuar", True, (255, 255, 255))
        self.pantalla.blit(txt_btn, (self.btn_continuar.centerx - txt_btn.get_width()//2, self.btn_continuar.centery - txt_btn.get_height()//2))

    def reproducir_click(self):
        if self.sonido_click:
            self.sonido_click.set_volume(self.configuracion.get_volumen_efectos())
            self.sonido_click.play()