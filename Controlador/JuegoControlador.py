import pygame
from Vista.JuegoView import JuegoView
# from Modelo.ControladorLogica import Autómata (Tu clase que maneja la lógica de pares y vidas)

class JuegoControlador:
    def __init__(self, pantalla, configuracion, dificultad, tiempo_limite):
        self.pantalla = pantalla
        self.configuracion = configuracion
        self.vista = JuegoView(pantalla, configuracion)
        
        # Variables lógicas del juego
        self.estado_juego = "JUGANDO" # Posibles: "JUGANDO", "GANO", "PERDIO", "INGRESO_NOMBRE"
        self.tiempo_restante = f"{tiempo_limite}:00" # Aquí conectarías tu cronómetro
        self.vidas = 5
        self.aciertos = 0
        self.puntos = 0
        self.cartas = [] # Aquí cargarías tus objetos Carta
        
        # Variables para el ingreso de texto
        self.nombre_ingresado = ""

    def actualizar(self, eventos):
        pos_mouse = pygame.mouse.get_pos()

        for event in eventos:
            # 1. EVENTOS DURANTE EL JUEGO ACTIVO
            if self.estado_juego == "JUGANDO":
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    # Aquí va la lógica de colisión con las cartas y el Autómata
                    # Ejemplo:
                    # if logica_automata.evaluar() == "VICTORIA":
                    #     self.estado_juego = "GANO"
                    # elif self.vidas == 0:
                    #     self.estado_juego = "PERDIO"
                    pass

            # 2. EVENTOS EN PANTALLAS DE FIN (PERDIÓ / GANÓ)
            elif self.estado_juego in ["GANO", "PERDIO"]:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self.vista.btn_continuar.collidepoint(pos_mouse):
                        self.vista.reproducir_click()
                        # Si ganó o perdió, lo mandamos a poner su nombre
                        self.estado_juego = "INGRESO_NOMBRE"

            # 3. EVENTOS EN INGRESO DE NOMBRE
            elif self.estado_juego == "INGRESO_NOMBRE":
                # Detectar clics en el botón de guardar
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self.vista.btn_continuar.collidepoint(pos_mouse):
                        self.vista.reproducir_click()
                        # Aquí llamas a tu BD para guardar el nombre y puntaje
                        # gestor_bd.guardar(self.nombre_ingresado, self.puntos)
                        
                        return "RANKING" # Termina el juego y lo manda al Ranking

                # Detectar pulsaciones del teclado para escribir el nombre
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_BACKSPACE:
                        # Borrar última letra
                        self.nombre_ingresado = self.nombre_ingresado[:-1]
                    elif event.key == pygame.K_RETURN:
                        # Apretar ENTER equivale a hacer clic en Continuar
                        # gestor_bd.guardar(...)
                        return "RANKING"
                    else:
                        # Limitar la longitud a 12 caracteres y agregar la letra tecleada
                        if len(self.nombre_ingresado) < 12:
                            self.nombre_ingresado += event.unicode

        # Dibujar la pantalla según el estado actual
        self.vista.dibujar(
            self.estado_juego, 
            self.cartas, 
            self.tiempo_restante, 
            self.aciertos, 
            self.puntos, 
            self.vidas, 
            self.nombre_ingresado
        )
        
        return "JUEGO"