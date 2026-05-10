"""
software_fj/__init__.py - Paquete principal de Software FJ
"""
from software_fj.excepciones import *
from software_fj.logger import SistemaLog
from software_fj.entidad import Entidad
from software_fj.cliente import Cliente
from software_fj.servicio import Servicio
from software_fj.reserva import Reserva, EstadoReserva
from software_fj.gestor import GestorSistema
from software_fj.servicios import ReservaSala, AlquilerEquipo, AsesoriaEspecializada

__version__ = "1.0.0"
__author__ = "Software FJ"
