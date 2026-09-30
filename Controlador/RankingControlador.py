import pygame
from Vista.RankingView import RankingView
# from Modelo.GestorBaseDatos import GestorBaseDatos # <-- Importa tu clase de BD aquí

class RankingControlador:
    def __init__(self, pantalla, configuracion):
        self.pantalla = pantalla
        self.configuracion = configuracion
        self.vista = RankingView(self.pantalla, self.configuracion)
        
        # Cargamos los datos de la BD al instanciar la pantalla
        self.datos_jugadores = self.obtener_ranking_bd()

    def obtener_ranking_bd(self):
        """
        Realiza el SELECT a la base de datos para obtener los mejores puntajes.
        Debe retornar una lista de tuplas, ej: [("Alexis", 8500), ("María", 7200)]
        """
        # --- ACÁ VA TU CONEXIÓN REAL ---
        # gestor_bd = GestorBaseDatos()
        # ranking = gestor_bd.obtener_top_5_jugadores()
        # return ranking
        
        # Mock temporal para que la vista no crashee mientras conectas tu clase:
        return [("Jugador1", 1000), ("Jugador2", 500)] 

    def actualizar(self, eventos):
        pos_mouse = pygame.mouse.get_pos()

        for event in eventos:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.vista.btn_volver.collidepoint(pos_mouse):
                    self.vista.reproducir_click()
                    
                    # Volvemos a consultar a la BD al salir, por si los puntajes
                    # cambiaron mientras navegábamos por los menús.
                    self.datos_jugadores = self.obtener_ranking_bd() 
                    
                    return "MENU"

        # La vista solo se encarga de dibujar lo que el controlador le pasa
        self.vista.dibujar(self.datos_jugadores)
        
        return "RANKING"
