# -*- coding: utf-8 -*-
"""
gui_main.py - Punto de entrada principal para la interfaz gráfica (GUI).

Este script inicializa el entorno necesario y lanza la aplicación Software FJ.
Para ejecutar la aplicación, utilice el comando: python gui_main.py
"""
import sys
import os

# ── Configuración del Entorno ────────────────────────────────────────────────
# Se asegura de que la raíz del proyecto esté en el sys.path para permitir
# importaciones absolutas del paquete 'software_fj'.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from software_fj.gui.app import SoftwareFJApp


def main():
    """
    Función de arranque que instancia la aplicación y comienza el bucle de eventos.
    """
    app = SoftwareFJApp()
    app.mainloop()


if __name__ == "__main__":
    # Punto de ejecución si el script se llama directamente.
    main()
