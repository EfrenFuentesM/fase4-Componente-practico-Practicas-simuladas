# -*- coding: utf-8 -*-
"""
gui_main.py - Punto de entrada de la interfaz gráfica de Software FJ
Ejecutar con:  python gui_main.py
"""
import sys
import os

# Asegurar que el paquete se encuentre en el path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from software_fj.gui.app import SoftwareFJApp


def main():
    app = SoftwareFJApp()
    app.mainloop()


if __name__ == "__main__":
    main()
