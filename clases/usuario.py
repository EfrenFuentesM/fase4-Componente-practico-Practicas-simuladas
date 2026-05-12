class Usuario:


    def __init__(self, nombre, edad):
        self.nombre = nombre
        self.edad = edad

    def mostrar_datos(self):
        return f"Nombre: {self.nombre} | Edad: {self.edad}"