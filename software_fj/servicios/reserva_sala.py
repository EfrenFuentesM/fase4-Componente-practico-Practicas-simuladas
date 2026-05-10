"""
servicios/reserva_sala.py - Servicio de Reserva de Salas
=========================================================
Implementa el servicio de reserva de salas de reunión para Software FJ.
"""

from software_fj.servicio import Servicio
from software_fj.excepciones import (
    ParametroFaltanteError,
    ReservaInvalidaError,
    CalculoCostoError,
)


class ReservaSala(Servicio):
    """
    Servicio de reserva de salas de reunión.

    Extiende Servicio con atributos específicos de sala: capacidad,
    tipo de equipamiento y costo adicional por proyector/videoconferencia.

    Atributos específicos:
        _capacidad (int): Número máximo de personas.
        _tiene_proyector (bool): Indica si la sala cuenta con proyector.
        _tiene_videoconferencia (bool): Indica si tiene sistema de videoconferencia.
        _costo_proyector_hora (float): Cargo adicional por uso de proyector.
        _costo_vc_hora (float): Cargo adicional por videoconferencia.
    """

    COSTO_PROYECTOR_HORA: float = 25.0
    COSTO_VIDEOCONFERENCIA_HORA: float = 50.0
    DURACION_MAXIMA_HORAS: float = 12.0
    DURACION_MINIMA_HORAS: float = 0.5

    def __init__(
        self,
        id_servicio: str,
        nombre: str,
        capacidad: int,
        precio_base: float,
        tiene_proyector: bool = False,
        tiene_videoconferencia: bool = False,
        disponible: bool = True,
    ):
        """
        Inicializa la sala con sus características físicas.

        Args:
            id_servicio: ID único de la sala.
            nombre: Nombre de la sala (ej: "Sala Ejecutiva A").
            capacidad: Aforo máximo de personas (debe ser >= 1).
            precio_base: Precio base por hora.
            tiene_proyector: True si incluye proyector.
            tiene_videoconferencia: True si incluye sistema de VC.
            disponible: Disponibilidad inicial.

        Raises:
            ValueError: Si la capacidad no es válida.
        """
        descripcion = (
            f"Sala de reunión con capacidad para {capacidad} personas. "
            f"{'Proyector incluido. ' if tiene_proyector else ''}"
            f"{'Videoconferencia disponible.' if tiene_videoconferencia else ''}"
        )
        super().__init__(id_servicio, nombre, descripcion, precio_base, disponible)

        if not isinstance(capacidad, int) or capacidad < 1:
            raise ValueError(
                f"La capacidad debe ser un entero positivo. Se recibió: {capacidad}"
            )
        self._capacidad: int = capacidad
        self._tiene_proyector: bool = bool(tiene_proyector)
        self._tiene_videoconferencia: bool = bool(tiene_videoconferencia)

    # ── Propiedades ──────────────────────────────────────────────────────────

    @property
    def capacidad(self) -> int:
        return self._capacidad

    @property
    def tiene_proyector(self) -> bool:
        return self._tiene_proyector

    @property
    def tiene_videoconferencia(self) -> bool:
        return self._tiene_videoconferencia

    # ── Métodos abstractos implementados ─────────────────────────────────────

    def calcular_costo(self, duracion_horas: float, **kwargs) -> float:
        """
        Calcula el costo de reserva de la sala.

        Parámetros kwargs:
            usar_proyector (bool): Añade cargo por proyector si la sala lo tiene.
            usar_videoconferencia (bool): Añade cargo por VC si la sala lo tiene.
            num_personas (int): Validación de aforo (no altera el costo).

        Returns:
            Costo total calculado.

        Raises:
            ReservaInvalidaError: Si la duración está fuera del rango permitido.
            CalculoCostoError: Si ocurre un error aritmético.
        """
        try:
            duracion_horas = float(duracion_horas)
        except (TypeError, ValueError) as e:
            raise CalculoCostoError(
                f"La duración '{duracion_horas}' no es un número válido.", e
            ) from e

        if duracion_horas < self.DURACION_MINIMA_HORAS:
            raise ReservaInvalidaError(
                f"La duración mínima para '{self._nombre}' es "
                f"{self.DURACION_MINIMA_HORAS} hora(s). "
                f"Se solicitó {duracion_horas}h."
            )
        if duracion_horas > self.DURACION_MAXIMA_HORAS:
            raise ReservaInvalidaError(
                f"La duración máxima para '{self._nombre}' es "
                f"{self.DURACION_MAXIMA_HORAS} hora(s). "
                f"Se solicitó {duracion_horas}h."
            )

        usar_proyector = kwargs.get("usar_proyector", False)
        usar_vc = kwargs.get("usar_videoconferencia", False)
        num_personas = kwargs.get("num_personas", 1)

        # Validar aforo si se especifica
        if isinstance(num_personas, int) and num_personas > self._capacidad:
            raise ReservaInvalidaError(
                f"La sala '{self._nombre}' tiene capacidad para {self._capacidad} personas. "
                f"Se solicitaron {num_personas} personas."
            )

        try:
            costo = self._precio_base * duracion_horas

            if usar_proyector and self._tiene_proyector:
                costo += self.COSTO_PROYECTOR_HORA * duracion_horas

            if usar_vc and self._tiene_videoconferencia:
                costo += self.COSTO_VIDEOCONFERENCIA_HORA * duracion_horas

            return round(costo, 2)

        except Exception as e:
            raise CalculoCostoError(
                f"Error al calcular el costo de la sala '{self._nombre}'.", e
            ) from e

    def validar_parametros(self, **kwargs) -> bool:
        """
        Valida parámetros de la reserva de sala.

        Verifica que la duración sea válida y que el aforo sea respetado.
        """
        duracion = kwargs.get("duracion_horas")
        num_personas = kwargs.get("num_personas", 1)

        if duracion is None:
            raise ParametroFaltanteError("duracion_horas", "ReservaSala.validar_parametros")

        try:
            duracion = float(duracion)
        except (TypeError, ValueError):
            return False

        if not (self.DURACION_MINIMA_HORAS <= duracion <= self.DURACION_MAXIMA_HORAS):
            return False
        if isinstance(num_personas, int) and num_personas > self._capacidad:
            return False

        return True

    def describir(self) -> str:
        equipamiento = []
        if self._tiene_proyector:
            equipamiento.append("Proyector")
        if self._tiene_videoconferencia:
            equipamiento.append("Videoconferencia")
        eq_str = ", ".join(equipamiento) if equipamiento else "Básica"
        estado = "✓ Disponible" if self._disponible else "✗ No disponible"
        return (
            f"[SALA] [{self._id}] '{self._nombre}' | "
            f"Capacidad: {self._capacidad} personas | "
            f"Equipamiento: {eq_str} | "
            f"Precio: ${self._precio_base:.2f}/h | {estado}"
        )
