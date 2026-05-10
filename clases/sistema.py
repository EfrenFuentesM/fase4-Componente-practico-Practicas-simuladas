from clases.usuario import Usuario

class Sistema:

    def __init__(self):
        self.usuarios = []

    def agregar_usuario(self, nombre, edad):

        usuario = Usuario(nombre, edad)

        self.usuarios.append(usuario)

        print("Usuario agregado correctamente.")

    def mostrar_usuarios(self):

        if len(self.usuarios) == 0:
            print("No hay usuarios registrados.")

        else:

            print("\n===== LISTA DE USUARIOS =====\n")

            for usuario in self.usuarios:
                print(usuario.mostrar_datos())

    def eliminar_usuario(self, nombre):

        for usuario in self.usuarios:
            if usuario.nombre == nombre:
                self.usuarios.remove(usuario)
                print("Usuario eliminado correctamente.")
                return

        print("No se encontró un usuario con ese nombre.")
