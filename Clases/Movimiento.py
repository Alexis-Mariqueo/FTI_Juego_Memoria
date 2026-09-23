class Movimiento:
    
    def __init__ (self,id_movimiento,id_partida,nro_turno,es_acierto):
        self.__id_movimiento = id_movimiento
        self.__id_partida = id_partida
        self.__nro_turno = nro_turno
        self.__es_acierto = es_acierto
        
    def getIdMovimiento(self):
        return self.__id_movimiento
    
    def getIdPartida (self):
        return self.__id_partida
    
    def getNroTurno(self):
        return self.__nro_turno
    
    def getEsAcierto(self):
        return self.__es_acierto
    
    def setNroTurno(self,turno):
        self.__nro_turno = turno
    
    def setEsAcierto(self,acierto):
        self.__es_acierto = acierto