import json
import os

class Configuracion:
    def __init__(self, ruta="config.json"):
        self.ruta = ruta
        # Valores por defecto
        self.datos = {"volumen_efectos": 0.3, "volumen_musica": 0.5}
        self.cargar()

    def cargar(self):
        if os.path.exists(self.ruta):
            with open(self.ruta, "r") as archivo:
                self.datos = json.load(archivo)
        else:
            self.guardar() # Lo crea si no existe

    def guardar(self):
        with open(self.ruta, "w") as archivo:
            json.dump(self.datos, archivo, indent=4)

    def get_volumen_efectos(self):
        return self.datos.get("volumen_efectos", 1.0)
    
    def get_volumen_musica(self):
        return self.datos.get("volumen_musica", 1.0)
    
    def set_volumen_efectos(self, valor):
        # Actualiza el diccionario SOLO en memoria RAM
        self.datos["volumen_efectos"] = valor

    def set_volumen_musica(self, valor):
        # Actualiza el diccionario SOLO en memoria RAM
        self.datos["volumen_musica"] = valor