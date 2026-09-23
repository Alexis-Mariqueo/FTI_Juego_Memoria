class Partida:
    
    def __init__ (self,id_partida,id_jugador,id_dificultad,errores_cometidos,puntaje_total,resultado):
        self.__id_partida = id_partida
        self.__id_jugador = id_jugador
        self.__id_dificultad = id_dificultad
        self.__errores_cometidos = errores_cometidos
        self.__puntaje_total = puntaje_total
        self.__resultado = resultado
        
        
    def getIdPartida(self):
        return self.__id_partida
    
    def getIdJugador(self):
        return self.__id_jugador
    
    def getIdDificultad(self):
        return self.__id_dificultad
    
    def getErroresCometidos(self):
        return self.__errores_cometidos
    
    def getPuntajeTotal(self):
        return self.__puntaje_total
    
    def getResultado(self):
        return self.__resultado
    
    def setErroresCometidos(self,errores):
        self.__errores_cometidos = errores
    
    def setPuntajeTotal(self,puntaje):
        self.__puntaje_total = puntaje
        
    def setResultado(self,resultado):
        self.__resultado = resultado