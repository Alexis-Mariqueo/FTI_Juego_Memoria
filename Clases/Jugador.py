class Jugador:
    
    def __init__(self,id_jugador,nombre_jugador,fecha_registro):
        self.__id_jugador = id_jugador
        self.__nombre_jugador = nombre_jugador
        self.__fecha_registro = fecha_registro
        
    def getNombre(self):
        return self.__nombre_jugador
    
    def getFechaRegistro(self):
        return self.__fecha_registro
    
    def getIdJugador(self):
        return self.__id_jugador
    
    
    
    
         
    