class Dificultad:
    
    def __init__(self,id_dificultad,tipo,limite_errores,puntaje_base,tiempo):
        self.__id_dificultad = id_dificultad
        self.__tipo = tipo
        self.__limite_errores = limite_errores
        self.__puntaje_base = puntaje_base
        self.__tiempo = tiempo
        
    def getDificultad (self):
        return self.__id_dificultad
        
    def getTipo(self):
        return self.__tipo
    
    def getLimiteErrores(self):
        return self.__limite_errores
    
    def getTiempo(self):
        return self.__tiempo
    
    def getPuntajeBase(self):
        return self.__puntaje_base
    
    def setTiempo (self,nuevotiempo):
        self.__tiempo = nuevotiempo 