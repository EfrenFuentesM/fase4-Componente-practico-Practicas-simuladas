def validar_entero(mensaje):

    while True:

        try:
            numero = int(input(mensaje))
            return numero

        except ValueError:
            print("Error: debe ingresar un número válido.")