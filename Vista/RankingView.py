import pygame

class RankingView:
    def __init__(self, pantalla, configuracion):
        self.pantalla = pantalla
        self.configuracion = configuracion
        
        # Fuentes para los distintos textos
        self.fuente_titulo = pygame.font.Font(None, 64)
        self.fuente_cabecera = pygame.font.Font(None, 40)
        self.fuente_fila = pygame.font.Font(None, 36)

        # 1. Botón "Atrás" en la esquina inferior izquierda
        # Tomamos el alto de la pantalla (ej. 480) y le restamos 70 para dejar 20px de margen
        alto_pantalla = self.pantalla.get_height()
        self.btn_volver = pygame.Rect(20, alto_pantalla - 70, 150, 50)

        # Sonido de clic (igual que en tus otras vistas)
        try:
            self.sonido_click = pygame.mixer.Sound("Efectos Sonido/boton_click.mp3")
        except:
            self.sonido_click = None

        # Cargar Fondo
        try:
            # Puedes cambiar el nombre del archivo al fondo que prefieras
            self.fondo = pygame.image.load("Imagenes/fondo_1.jpg").convert()
            self.fondo = pygame.transform.scale(self.fondo, self.pantalla.get_size())
        except:
            self.fondo = None

    def dibujar(self, datos_ranking):
        """
        datos_ranking: Debe ser una lista de tuplas o listas. 
        Ejemplo: [("Alexis", 5000), ("María", 4200), ("Juan", 3100)]
        """
        # 1. Fondo
        if self.fondo:
            self.pantalla.blit(self.fondo, (0, 0))
        else:
            self.pantalla.fill((30, 30, 30))

        # 2. Título Principal
        txt_titulo = self.fuente_titulo.render("RANKING", True, (255, 215, 0)) # Color dorado
        self.pantalla.blit(txt_titulo, (self.pantalla.get_width()//2 - txt_titulo.get_width()//2, 40))

        # 3. Caja de la Tabla (Fondo oscuro para que resalten las letras)
        ancho_pantalla = self.pantalla.get_width()
        caja_tabla = pygame.Rect(ancho_pantalla // 2 - 200, 120, 400, 260)
        
        pygame.draw.rect(self.pantalla, (50, 50, 50), caja_tabla, border_radius=10)
        pygame.draw.rect(self.pantalla, (200, 200, 200), caja_tabla, width=3, border_radius=10) # Borde

        # 4. Cabeceras de la tabla (Nombre y Puntaje)
        col_nombre_x = caja_tabla.x + 40
        col_puntaje_x = caja_tabla.right - 140

        txt_nombre = self.fuente_cabecera.render("Nombre", True, (150, 200, 255))
        txt_puntaje = self.fuente_cabecera.render("Puntaje", True, (150, 200, 255))
        
        self.pantalla.blit(txt_nombre, (col_nombre_x, caja_tabla.y + 20))
        self.pantalla.blit(txt_puntaje, (col_puntaje_x, caja_tabla.y + 20))

        # Línea separadora debajo de las cabeceras
        y_linea = caja_tabla.y + 60
        pygame.draw.line(self.pantalla, (200, 200, 200), (caja_tabla.x + 20, y_linea), (caja_tabla.right - 20, y_linea), 2)

        # 5. Imprimir los jugadores en la tabla
        y_inicial_filas = y_linea + 15
        
        # Limitamos a los 5 mejores para que no se salga de la caja
        for i, jugador in enumerate(datos_ranking[:5]): 
            nombre_jugador = str(jugador[0])
            puntaje_jugador = str(jugador[1])

            # Agregamos el número de posición (1., 2., 3...)
            txt_n = self.fuente_fila.render(f"{i+1}. {nombre_jugador}", True, (255, 255, 255))
            txt_p = self.fuente_fila.render(puntaje_jugador, True, (255, 215, 0)) # Puntaje en dorado

            self.pantalla.blit(txt_n, (col_nombre_x, y_inicial_filas + (i * 35)))
            self.pantalla.blit(txt_p, (col_puntaje_x, y_inicial_filas + (i * 35)))

        # 6. Dibujar botón "Atrás" (Esquina inferior izquierda)
        pygame.draw.rect(self.pantalla, (200, 50, 50), self.btn_volver, border_radius=5)
        pygame.draw.rect(self.pantalla, (255, 150, 150), self.btn_volver, width=2, border_radius=5) # Borde del botón
        
        txt_volver = self.fuente_cabecera.render("Atrás", True, (255, 255, 255))
        self.pantalla.blit(txt_volver, (self.btn_volver.centerx - txt_volver.get_width()//2, self.btn_volver.centery - txt_volver.get_height()//2))

    def reproducir_click(self):
        if self.sonido_click:
            # Obtiene el volumen fresco de la RAM justo antes de sonar
            volumen = self.configuracion.get_volumen_efectos()
            self.sonido_click.set_volume(volumen)
            self.sonido_click.play()