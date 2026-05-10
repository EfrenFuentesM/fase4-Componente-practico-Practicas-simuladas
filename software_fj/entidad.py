"""
entidad.py - Clase abstracta base del sistema Software FJ
==========================================================
Define el contrato mínimo que deben cumplir todas las entidades del sistema.
"""

from abc import ABC, abstractmethod
from datetime import datetime


class Entidad(ABC):
    """
    Clase abstracta base para todas las entidades del sistema Software FJ.

    Proporciona identidad única, marca temporal de creación y obliga
    a todas las subclases a implementar representación descriptiva
    y validación propia de sus datos.

    Atributos:
        _id (str): Identificador único de la entidad.
        _fecha_creacion (datetime): Fecha y hora de creación del objeto.
    """

    def __init__(self, id_entidad: str):
        """
        Inicializa la entidad con un ID único y timestamp de creación.

        Args:
            id_entidad: Identificador único de la entidad.

        Raises:
            ValueError: Si el ID proporcionado es None o vacío.
        """
        if not id_entidad or not str(id_entidad).strip():
            raise ValueError("El identificador de la entidad no puede ser vacío o None.")
        self._id: str = str(id_entidad).strip()
        self._fecha_creacion: datetime = datetime.now()

    # ── Propiedades ──────────────────────────────────────────────────────────

    @property
    def id(self) -> str:
        """Retorna el identificador único de la entidad (solo lectura)."""
        return self._id

    @property
    def fecha_creacion(self) -> datetime:
        """Retorna la fecha y hora de creación (solo lectura)."""
        return self._fecha_creacion

    # ── Métodos abstractos ───────────────────────────────────────────────────

    @abstractmethod
    def describir(self) -> str:
        """
        Retorna una descripción legible de la entidad.

        Returns:
            Cadena con la descripción detallada del objeto.
        """
        ...

    @abstractmethod
    def validar(self) -> bool:
        """
        Verifica que los datos internos de la entidad son consistentes.

        Returns:
            True si la entidad es válida; False en caso contrario.
        """
        ...

    # ── Métodos concretos ────────────────────────────────────────────────────

    def obtener_info_base(self) -> dict:
        """
        Retorna un diccionario con los atributos base de la entidad.

        Returns:
            Diccionario con 'id' y 'fecha_creacion'.
        """
        return {
            "id": self._id,
            "fecha_creacion": self._fecha_creacion.strftime("%Y-%m-%d %H:%M:%S"),
        }

    def __eq__(self, other: object) -> bool:
        """Dos entidades son iguales si comparten el mismo ID."""
        if not isinstance(other, Entidad):
            return NotImplemented
        return self._id == other._id

    def __hash__(self) -> int:
        return hash(self._id)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(id='{self._id}')"
