from datetime import date
import psycopg2
from .bd import Database
from Clases.Jugador import Jugador 
#################### ESTRUCTURA ####################
# jugador = id_jugador(pk) + nombre_jugador + fecha_registro
#####################################################

class JugadorDAO:
    def __init__(self):
        self.__bd = Database()
    
    ######################################## LECTURA ########################################

    def insertar_jugador (self, jugador : Jugador):
        """
        Inserta un nuevo jugador de forma permanente en la BD.
        Previene Inyecciones SQL y maneja errores de conexión.
        """
        query = 'INSERT INTO "public"."JUGADOR" (nombre_jugador,fecha_registro)'
        
        try:
            with self.__bd.cursor() as cursor:
                
                cursor.execute(query,(jugador.getNombre(),date.today()))
                
                id_generado = cursor.fetchone()[0] # Tomamos el primer elemento de la tupla
                jugador.id_jugador = id_generado
                
            if hasattr(self.__bd, 'connection') and self.__bd.connection:
                self.__bd.connection.commit()
            elif hasattr(self.__bd, 'commit'):
                self.__bd.commit() # Si tu clase expone el método commit directamente
                
            print(f"[ÉXITO] Jugador '{jugador.getNombre()}' guardado permanentemente con ID: {jugador.getIdJugador()}")
            return True

        except (Exception, psycopg2.Error) as error:
            # 6. Si algo falla (ej. se cae el servidor), hacemos Rollback para no dejar datos corruptos
            print(f"[ERROR] Error al insertar el jugador en la base de datos: {error}")
            if hasattr(self.__bd, 'connection') and self.__bd.connection:
                self.__bd.connection.rollback()
            elif hasattr(self.__bd, 'rollback'):
                self.__bd.rollback()
                
            return False

    def get_jugador_por_id(self,id_jugador):
        """Busca un jugador por ID y devuelve un objeto Jugador con sus datos de la BD."""
        with self.__bd.cursor() as cursor:
            cursor.execute ('SELECT id_jugador,nombre_jugador,fecha_registro FROM "public"."JUGADOR" WHERE id_jugador = %s',(id_jugador,))
            resultado = cursor.fetchone()
        
        if not resultado:
            return None
            
        jugador = Jugador(id_jugador = resultado[0],nombre_jugador=resultado[1],fecha_registro=resultado[2])
            
        return jugador
    
   def obtener_ranking_10_mejores_jugadores(self):
     """Busca un jugador por ID y devuelve una lista de objetos"""
        with self.__bd.cursor() as cursor:
            cursor.execute ('SELECT ')
            resultado = cursor.fetchone()
        
        if not resultado:
            return None
        
            
        jugador = Jugador(id_jugador = resultado[0],nombre_jugador=resultado[1],fecha_registro=resultado[2])
            
        return jugador
