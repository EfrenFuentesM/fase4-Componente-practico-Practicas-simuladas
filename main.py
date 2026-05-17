"""
main.py - Interfaz de línea de comandos (CLI) para Software FJ.

Este script permite interactuar con el sistema básico a través de la terminal.
Proporciona funciones para gestionar usuarios de manera simplificada.
"""
from clases.sistema import Sistema
from utilidades.validaciones import validar_entero

# Inicialización del sistema core
sistema = Sistema()

def mostrar_menu():
    """Muestra las opciones disponibles en la consola."""
    print("\n" + "="*15 + " MENÚ DE USUARIOS " + "="*15)
    print("1. Agregar usuario")
    print("2. Mostrar usuarios")
    print("3. Eliminar usuario")
    print("4. Salir")
    print("="*48)

while True:
    mostrar_menu()
    opcion = input("Seleccione una opción: ")

    try:
        # Convertir entrada a entero para procesar la lógica
        opcion = int(opcion)

        if opcion == 1:
            # Flujo para agregar un nuevo usuario
            nombre = input("Ingrese nombre: ")
            edad = validar_entero("Ingrese edad: ")
            sistema.agregar_usuario(nombre, edad)

        elif opcion == 2:
            # Mostrar listado de usuarios registrados
            sistema.mostrar_usuarios()

        elif opcion == 3:
            # Proceso de eliminación por nombre
            nombre = input("Ingrese nombre del usuario a eliminar: ")
            sistema.eliminar_usuario(nombre)

        elif opcion == 4:
            # Cierre controlado del programa
            print("Saliendo del programa CLI...")
            break

        else:
            print("⚠️ Opción inválida. Intente de nuevo.")

    except ValueError:
        # Manejo de error si la entrada no es un número
        print("❌ Error: Debe ingresar un valor numérico.")
