"""
logger.py - Sistema de registro de eventos y errores
======================================================
Gestiona la escritura de logs a archivo y consola para Software FJ.
Implementa el patrón Singleton para garantizar una única instancia del logger.
"""

import logging
import os
from datetime import datetime
from typing import Optional


class SistemaLog:
    """
    Gestor de logs del sistema Software FJ.

    Implementa el patrón Singleton para mantener una única instancia del logger
    durante toda la ejecución del programa. Escribe eventos en un archivo de log
    con formato estructurado y también muestra mensajes críticos en consola.
    """

    _instancia: Optional["SistemaLog"] = None
    _inicializado: bool = False

    def __new__(cls, directorio_logs: str = "logs"):
        if cls._instancia is None:
            cls._instancia = super().__new__(cls)
        return cls._instancia

    def __init__(self, directorio_logs: str = "logs"):
        # Evita re-inicialización en llamadas posteriores al Singleton
        if self._inicializado:
            return

        self.directorio_logs = directorio_logs
        self._crear_directorio()
        self._configurar_logger()
        SistemaLog._inicializado = True

    # ── Configuración interna ────────────────────────────────────────────────

    def _crear_directorio(self) -> None:
        """Crea el directorio de logs si no existe."""
        try:
            os.makedirs(self.directorio_logs, exist_ok=True)
        except OSError as e:
            print(f"[ADVERTENCIA] No se pudo crear el directorio de logs '{self.directorio_logs}': {e}")
            self.directorio_logs = "."

    def _configurar_logger(self) -> None:
        """Configura el logger de Python con handlers de archivo y consola."""
        nombre_archivo = os.path.join(
            self.directorio_logs,
            f"sistema_{datetime.now().strftime('%Y%m%d')}.log"
        )

        self._logger = logging.getLogger("SoftwareFJ")
        self._logger.setLevel(logging.DEBUG)

        # Evitar duplicar handlers si se reinicializa
        if self._logger.handlers:
            self._logger.handlers.clear()

        # Handler de archivo: guarda TODOS los niveles
        fmt_archivo = logging.Formatter(
            fmt="%(asctime)s | %(levelname)-8s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        handler_archivo = logging.FileHandler(nombre_archivo, encoding="utf-8")
        handler_archivo.setLevel(logging.DEBUG)
        handler_archivo.setFormatter(fmt_archivo)

        # Handler de consola: muestra solo WARNING y superior
        fmt_consola = logging.Formatter(
            fmt="  [%(levelname)s] %(message)s"
        )
        handler_consola = logging.StreamHandler()
        handler_consola.setLevel(logging.WARNING)
        handler_consola.setFormatter(fmt_consola)

        self._logger.addHandler(handler_archivo)
        self._logger.addHandler(handler_consola)

        self._logger.info("=" * 70)
        self._logger.info("Sistema Software FJ - Log de operaciones iniciado")
        self._logger.info("=" * 70)

    # ── API pública ──────────────────────────────────────────────────────────

    def info(self, mensaje: str) -> None:
        """Registra un evento informativo."""
        self._logger.info(mensaje)

    def advertencia(self, mensaje: str) -> None:
        """Registra una advertencia no crítica."""
        self._logger.warning(mensaje)

    def error(self, mensaje: str, exc: Exception = None) -> None:
        """Registra un error con trazabilidad opcional de la excepción."""
        if exc:
            self._logger.error(f"{mensaje} | Excepción: {type(exc).__name__}: {exc}")
        else:
            self._logger.error(mensaje)

    def critico(self, mensaje: str, exc: Exception = None) -> None:
        """Registra un error crítico del sistema."""
        if exc:
            self._logger.critical(f"{mensaje} | Excepción: {type(exc).__name__}: {exc}")
        else:
            self._logger.critical(mensaje)

    def debug(self, mensaje: str) -> None:
        """Registra información de depuración detallada."""
        self._logger.debug(mensaje)

    def separador(self, titulo: str = "") -> None:
        """Escribe un separador visual en el log para mejor legibilidad."""
        linea = "-" * 60
        if titulo:
            self._logger.info(f"{linea} {titulo} {linea}")
        else:
            self._logger.info(linea)
