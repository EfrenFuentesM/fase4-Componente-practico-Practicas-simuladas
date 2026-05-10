from clases.sistema import Sistema
from utilidades.validaciones import validar_entero

sistema = Sistema()

while True:

    print("\n===== MENÚ =====")
    print("1. Agregar usuario")
    print("2. Mostrar usuarios")
    print("3. Salir")

    opcion = input("Seleccione una opción: ")

    try:

        opcion = int(opcion)

        if opcion == 1:

            nombre = input("Ingrese nombre: ")

            edad = validar_entero("Ingrese edad: ")

            sistema.agregar_usuario(nombre, edad)

        elif opcion == 2:

            sistema.mostrar_usuarios()

        elif opcion == 3:

            print("Programa finalizado.")
            break

        else:
            print("Opción inválida.")

    except ValueError:
        print("Debe ingresar un número.")