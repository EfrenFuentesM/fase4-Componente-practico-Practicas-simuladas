"""
servicios/alquiler_equipo.py - Servicio de Alquiler de Equipos
===============================================================
Implementa el servicio de alquiler de equipos tecnológicos para Software FJ.
"""

from software_fj.servicio import Servicio
from software_fj.excepciones import (
    ParametroFaltanteError,
    ReservaInvalidaError,
    ServicioNoDisponibleError,
    CalculoCostoError,
)


class AlquilerEquipo(Servicio):
    """
    Servicio de alquiler de equipos tecnológicos.

    Extiende Servicio con gestión de stock, tipo de equipo y
    cargo por seguro opcional.

    Atributos específicos:
        _tipo_equipo (str): Categoría del equipo (laptop, proyector, servidor, etc.).
        _unidades_disponibles (int): Cantidad de unidades en stock.
        _requiere_deposito (bool): Indica si se cobra depósito de garantía.
        _monto_deposito (float): Monto del depósito reembolsable.
        _costo_seguro_dia (float): Cargo diario por seguro opcional.
    """

    TIPOS_EQUIPO_VALIDOS = ("laptop", "proyector", "servidor", "impresora", "tablet", "otro")
    DURACION_MINIMA_DIAS: float = 0.5   # medio día
    DURACION_MAXIMA_DIAS: float = 30.0  # un mes

    def __init__(
        self,
        id_servicio: str,
        nombre: str,
        tipo_equipo: str,
        precio_base_dia: float,
        unidades_disponibles: int = 1,
        requiere_deposito: bool = False,
        monto_deposito: float = 0.0,
        costo_seguro_dia: float = 0.0,
        disponible: bool = True,
    ):
        """
        Inicializa el servicio de alquiler de equipo.

        Args:
            id_servicio: ID único del servicio.
            nombre: Nombre descriptivo del equipo.
            tipo_equipo: Categoría del equipo (ver TIPOS_EQUIPO_VALIDOS).
            precio_base_dia: Costo de alquiler por día.
            unidades_disponibles: Cantidad de unidades en stock.
            requiere_deposito: True si el alquiler exige depósito.
            monto_deposito: Valor del depósito de garantía.
            costo_seguro_dia: Costo adicional por seguro diario.
            disponible: Disponibilidad inicial.

        Raises:
            ValueError: Si el tipo de equipo no es válido o las unidades son negativas.
        """
        tipo_equipo = str(tipo_equipo).strip().lower()
        if tipo_equipo not in self.TIPOS_EQUIPO_VALIDOS:
            raise ValueError(
                f"Tipo de equipo '{tipo_equipo}' no válido. "
                f"Opciones: {self.TIPOS_EQUIPO_VALIDOS}"
            )

        descripcion = (
            f"Alquiler de {nombre} ({tipo_equipo}). "
            f"Stock disponible: {unidades_disponibles} unidad(es). "
            f"{'Requiere depósito de garantía. ' if requiere_deposito else ''}"
        )
        super().__init__(id_servicio, nombre, descripcion, precio_base_dia, disponible)

        if not isinstance(unidades_disponibles, int) or unidades_disponibles < 0:
            raise ValueError(
                f"Las unidades disponibles deben ser un entero >= 0. "
                f"Se recibió: {unidades_disponibles}"
            )

        self._tipo_equipo: str = tipo_equipo
        self._unidades_disponibles: int = unidades_disponibles
        self._requiere_deposito: bool = bool(requiere_deposito)
        self._monto_deposito: float = max(0.0, float(monto_deposito))
        self._costo_seguro_dia: float = max(0.0, float(costo_seguro_dia))

    # ── Propiedades ──────────────────────────────────────────────────────────

    @property
    def tipo_equipo(self) -> str:
        return self._tipo_equipo

    @property
    def unidades_disponibles(self) -> int:
        return self._unidades_disponibles

    @property
    def requiere_deposito(self) -> bool:
        return self._requiere_deposito

    @property
    def monto_deposito(self) -> float:
        return self._monto_deposito

    @property
    def costo_seguro_dia(self) -> float:
        return self._costo_seguro_dia

    # ── Gestión de stock ─────────────────────────────────────────────────────

    def reducir_stock(self, cantidad: int = 1) -> None:
        """
        Reduce el stock disponible cuando se confirma un alquiler.

        Raises:
            ServicioNoDisponibleError: Si no hay suficiente stock.
        """
        if cantidad > self._unidades_disponibles:
            raise ServicioNoDisponibleError(
                self._nombre,
                f"se solicitaron {cantidad} unidad(es) pero solo hay "
                f"{self._unidades_disponibles} disponible(s)"
            )
        self._unidades_disponibles -= cantidad

    def reponer_stock(self, cantidad: int = 1) -> None:
        """Incrementa el stock disponible (ej.: al cancelar una reserva)."""
        if cantidad < 0:
            raise ValueError("No se puede reponer una cantidad negativa.")
        self._unidades_disponibles += cantidad

    # ── Métodos abstractos implementados ─────────────────────────────────────

    def calcular_costo(self, duracion_dias: float, **kwargs) -> float:
        """
        Calcula el costo de alquiler por días.

        Parámetros kwargs:
            incluir_seguro (bool): Si True, suma el cargo por seguro diario.
            cantidad_unidades (int): Número de unidades a alquilar.

        Returns:
            Costo total del alquiler (sin depósito; el depósito es reembolsable).

        Raises:
            ReservaInvalidaError: Si la duración está fuera de rango.
            ServicioNoDisponibleError: Si no hay stock suficiente.
        """
        try:
            duracion_dias = float(duracion_dias)
        except (TypeError, ValueError) as e:
            raise CalculoCostoError(
                f"La duración '{duracion_dias}' no es válida para alquiler.", e
            ) from e

        if duracion_dias < self.DURACION_MINIMA_DIAS:
            raise ReservaInvalidaError(
                f"La duración mínima de alquiler es {self.DURACION_MINIMA_DIAS} día(s). "
                f"Se solicitó {duracion_dias}."
            )
        if duracion_dias > self.DURACION_MAXIMA_DIAS:
            raise ReservaInvalidaError(
                f"La duración máxima de alquiler es {self.DURACION_MAXIMA_DIAS} día(s). "
                f"Se solicitó {duracion_dias}."
            )

        incluir_seguro = kwargs.get("incluir_seguro", False)
        cantidad = kwargs.get("cantidad_unidades", 1)

        if not isinstance(cantidad, int) or cantidad < 1:
            raise ReservaInvalidaError(
                f"La cantidad de unidades debe ser un entero >= 1. Se recibió: {cantidad}"
            )
        if cantidad > self._unidades_disponibles:
            raise ServicioNoDisponibleError(
                self._nombre,
                f"no hay suficiente stock: se solicitan {cantidad} unidades "
                f"pero solo hay {self._unidades_disponibles}."
            )

        try:
            costo = self._precio_base * duracion_dias * cantidad

            if incluir_seguro and self._costo_seguro_dia > 0:
                costo += self._costo_seguro_dia * duracion_dias * cantidad

            return round(costo, 2)

        except Exception as e:
            raise CalculoCostoError(
                f"Error calculando costo de alquiler para '{self._nombre}'.", e
            ) from e

    def validar_parametros(self, **kwargs) -> bool:
        """Valida que la duración y la cantidad de unidades sean correctas."""
        duracion = kwargs.get("duracion_dias")
        cantidad = kwargs.get("cantidad_unidades", 1)

        if duracion is None:
            raise ParametroFaltanteError("duracion_dias", "AlquilerEquipo.validar_parametros")

        try:
            duracion = float(duracion)
        except (TypeError, ValueError):
            return False

        if not (self.DURACION_MINIMA_DIAS <= duracion <= self.DURACION_MAXIMA_DIAS):
            return False
        if not isinstance(cantidad, int) or cantidad < 1:
            return False
        if cantidad > self._unidades_disponibles:
            return False

        return True

    def describir(self) -> str:
        estado = "✓ Disponible" if self._disponible else "✗ No disponible"
        return (
            f"[EQUIPO] [{self._id}] '{self._nombre}' | "
            f"Tipo: {self._tipo_equipo} | "
            f"Stock: {self._unidades_disponibles} unidades | "
            f"Precio: ${self._precio_base:.2f}/día | {estado}"
        )
