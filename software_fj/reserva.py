"""
reserva.py - Clase Reserva
============================
Integra cliente, servicio, duración y estado con manejo completo de excepciones.
Implementa confirmación, cancelación y procesamiento de reservas.
"""

from datetime import datetime, date
from enum import Enum
from typing import Optional

from software_fj.entidad import Entidad
from software_fj.cliente import Cliente
from software_fj.servicio import Servicio
from software_fj.excepciones import (
    ParametroFaltanteError,
    ReservaInvalidaError,
    OperacionNoPermitidaError,
    CalculoCostoError,
    ServicioNoDisponibleError,
)


class EstadoReserva(Enum):
    """Enumeración de los posibles estados de una reserva."""
    PENDIENTE = "pendiente"
    CONFIRMADA = "confirmada"
    CANCELADA = "cancelada"
    COMPLETADA = "completada"
    RECHAZADA = "rechazada"


class Reserva(Entidad):
    """
    Representa una reserva que integra un cliente y un servicio.

    Gestiona el ciclo de vida completo: PENDIENTE → CONFIRMADA → COMPLETADA,
    o bien PENDIENTE → CANCELADA / RECHAZADA.

    Implementa confirmación, cancelación y cálculo de costo con
    manejo robusto de excepciones en cada operación.

    Atributos:
        _cliente (Cliente): Cliente que realiza la reserva.
        _servicio (Servicio): Servicio reservado.
        _duracion (float): Duración de la reserva (horas o días según servicio).
        _fecha_reserva (date): Fecha programada para la reserva.
        _estado (EstadoReserva): Estado actual de la reserva.
        _costo_total (float): Costo calculado tras la confirmación.
        _notas (str): Observaciones adicionales.
        _parametros_extra (dict): Parámetros específicos del servicio.
    """

    def __init__(
        self,
        id_reserva: str,
        cliente: Cliente,
        servicio: Servicio,
        duracion: float,
        fecha_reserva: date,
        notas: str = "",
        **parametros_extra,
    ):
        """
        Inicializa una reserva en estado PENDIENTE.

        Args:
            id_reserva: Identificador único de la reserva.
            cliente: Objeto Cliente válido.
            servicio: Objeto Servicio válido y disponible.
            duracion: Duración del servicio (unidad depende del servicio).
            fecha_reserva: Fecha programada.
            notas: Observaciones opcionales.
            **parametros_extra: Parámetros adicionales para el servicio.

        Raises:
            ParametroFaltanteError: Si cliente, servicio, duración o fecha son None.
            ReservaInvalidaError: Si algún parámetro no es válido.
            ServicioNoDisponibleError: Si el servicio no está disponible.
        """
        # Validaciones previas al super().__init__
        self._validar_args_constructor(cliente, servicio, duracion, fecha_reserva)

        super().__init__(id_reserva)

        # Verificar disponibilidad del servicio (puede lanzar ServicioNoDisponibleError)
        servicio.verificar_disponibilidad()

        # Validar los parámetros del servicio con la duración dada
        params_validacion = dict(parametros_extra)
        params_validacion["duracion_horas"] = duracion
        params_validacion["duracion_dias"] = duracion

        try:
            servicio.validar_parametros(**params_validacion)
        except ParametroFaltanteError:
            pass  # Ya se proporcionó duracion arriba

        self._cliente: Cliente = cliente
        self._servicio: Servicio = servicio
        self._duracion: float = float(duracion)
        self._fecha_reserva: date = fecha_reserva
        self._notas: str = str(notas).strip()
        self._parametros_extra: dict = dict(parametros_extra)
        self._estado: EstadoReserva = EstadoReserva.PENDIENTE
        self._costo_total: float = 0.0
        self._fecha_confirmacion: Optional[datetime] = None
        self._fecha_cancelacion: Optional[datetime] = None
        self._motivo_cancelacion: str = ""

    # ── Validación del constructor ───────────────────────────────────────────

    @staticmethod
    def _validar_args_constructor(cliente, servicio, duracion, fecha_reserva) -> None:
        if cliente is None:
            raise ParametroFaltanteError("cliente", "constructor de Reserva")
        if servicio is None:
            raise ParametroFaltanteError("servicio", "constructor de Reserva")
        if duracion is None:
            raise ParametroFaltanteError("duracion", "constructor de Reserva")
        if fecha_reserva is None:
            raise ParametroFaltanteError("fecha_reserva", "constructor de Reserva")

        if not isinstance(cliente, Cliente):
            raise ReservaInvalidaError(
                f"El parámetro 'cliente' debe ser una instancia de Cliente, "
                f"se recibió: {type(cliente).__name__}"
            )
        if not isinstance(servicio, Servicio):
            raise ReservaInvalidaError(
                f"El parámetro 'servicio' debe ser una instancia de Servicio, "
                f"se recibió: {type(servicio).__name__}"
            )

        try:
            duracion_num = float(duracion)
        except (TypeError, ValueError) as e:
            raise ReservaInvalidaError(
                f"La duración '{duracion}' no es un valor numérico válido."
            ) from e

        if duracion_num <= 0:
            raise ReservaInvalidaError(
                f"La duración debe ser mayor a 0. Se recibió: {duracion_num}"
            )

    # ── Propiedades ──────────────────────────────────────────────────────────

    @property
    def cliente(self) -> Cliente:
        return self._cliente

    @property
    def servicio(self) -> Servicio:
        return self._servicio

    @property
    def duracion(self) -> float:
        return self._duracion

    @property
    def fecha_reserva(self) -> date:
        return self._fecha_reserva

    @property
    def estado(self) -> EstadoReserva:
        return self._estado

    @property
    def costo_total(self) -> float:
        return self._costo_total

    @property
    def notas(self) -> str:
        return self._notas

    @property
    def esta_confirmada(self) -> bool:
        return self._estado == EstadoReserva.CONFIRMADA

    @property
    def esta_cancelada(self) -> bool:
        return self._estado == EstadoReserva.CANCELADA

    # ── Operaciones del ciclo de vida ────────────────────────────────────────

    def confirmar(self, descuento: float = 0.0, aplicar_impuesto: bool = True) -> float:
        """
        Confirma la reserva calculando el costo total.

        Solo puede confirmarse una reserva en estado PENDIENTE.

        Args:
            descuento: Porcentaje de descuento a aplicar (0.0–1.0).
            aplicar_impuesto: Si True, suma el IVA al costo.

        Returns:
            El costo total de la reserva confirmada.

        Raises:
            OperacionNoPermitidaError: Si la reserva no está en estado PENDIENTE.
            ServicioNoDisponibleError: Si el servicio dejó de estar disponible.
            CalculoCostoError: Si el cálculo del costo falla.
        """
        if self._estado != EstadoReserva.PENDIENTE:
            raise OperacionNoPermitidaError("confirmar", self._estado.value)

        # Re-verificar disponibilidad en el momento de confirmación
        self._servicio.verificar_disponibilidad()

        try:
            # Obtener descuento del tipo de cliente si no se especifica
            if descuento == 0.0:
                descuento = self._cliente.obtener_descuento_tipo()

            # Calcular costo pasando los parametros especificos del servicio
            from software_fj.excepciones import DescuentoInvalidoError
            if not (0.0 <= descuento <= 1.0):
                raise DescuentoInvalidoError(descuento)

            costo_base = self._servicio.calcular_costo(
                self._duracion,
                **self._parametros_extra
            )
            costo_descontado = round(costo_base * (1 - descuento), 2)
            if aplicar_impuesto:
                costo_descontado = round(
                    costo_descontado * (1 + self._servicio.IMPUESTO_DEFAULT), 2
                )
            self._costo_total = costo_descontado
            self._estado = EstadoReserva.CONFIRMADA
            self._fecha_confirmacion = datetime.now()
            self._cliente.agregar_reserva(self._id)
            return self._costo_total

        except (CalculoCostoError, ServicioNoDisponibleError,
                OperacionNoPermitidaError, ReservaInvalidaError):
            self._estado = EstadoReserva.RECHAZADA
            raise
        except Exception as e:
            self._estado = EstadoReserva.RECHAZADA
            raise CalculoCostoError(
                f"Error inesperado al confirmar la reserva '{self._id}'.", e
            ) from e

    def cancelar(self, motivo: str = "Cancelación solicitada por el cliente") -> None:
        """
        Cancela la reserva si su estado lo permite.

        Solo puede cancelarse si está PENDIENTE o CONFIRMADA.

        Args:
            motivo: Razón de la cancelación.

        Raises:
            OperacionNoPermitidaError: Si la reserva ya está cancelada o completada.
        """
        estados_cancelables = {EstadoReserva.PENDIENTE, EstadoReserva.CONFIRMADA}
        if self._estado not in estados_cancelables:
            raise OperacionNoPermitidaError("cancelar", self._estado.value)

        self._estado = EstadoReserva.CANCELADA
        self._fecha_cancelacion = datetime.now()
        self._motivo_cancelacion = str(motivo).strip()

    def completar(self) -> None:
        """
        Marca la reserva como completada.

        Solo puede completarse si está CONFIRMADA.

        Raises:
            OperacionNoPermitidaError: Si la reserva no está confirmada.
        """
        if self._estado != EstadoReserva.CONFIRMADA:
            raise OperacionNoPermitidaError("completar", self._estado.value)
        self._estado = EstadoReserva.COMPLETADA

    def calcular_costo_estimado(self, descuento: float = 0.0) -> float:
        """
        Calcula una estimación del costo sin confirmar la reserva.

        Método sobrecargado: si no se pasa descuento, usa el del tipo de cliente.

        Args:
            descuento: Descuento explícito a aplicar (0.0–1.0).

        Returns:
            Costo estimado sin IVA.
        """
        if descuento == 0.0:
            descuento = self._cliente.obtener_descuento_tipo()
        return self._servicio.calcular_costo_con_descuento(
            self._duracion, descuento=descuento, aplicar_impuesto=False
        )

    def calcular_costo_con_iva(self) -> float:
        """
        Calcula la estimación del costo incluyendo IVA.

        Método sobrecargado: variante de calcular_costo_estimado con impuesto.

        Returns:
            Costo estimado con IVA.
        """
        descuento = self._cliente.obtener_descuento_tipo()
        return self._servicio.calcular_costo_con_descuento(
            self._duracion, descuento=descuento, aplicar_impuesto=True
        )

    # ── Métodos abstractos implementados ─────────────────────────────────────

    def describir(self) -> str:
        return (
            f"Reserva [{self._id}] | "
            f"Cliente: {self._cliente.nombre} | "
            f"Servicio: {self._servicio.nombre} | "
            f"Duración: {self._duracion}u | "
            f"Fecha: {self._fecha_reserva} | "
            f"Estado: {self._estado.value.upper()} | "
            f"Costo: ${self._costo_total:.2f}"
        )

    def validar(self) -> bool:
        return bool(
            self._id
            and self._cliente
            and self._cliente.validar()
            and self._servicio
            and self._servicio.validar()
            and self._duracion > 0
            and self._fecha_reserva is not None
        )

    def __str__(self) -> str:
        return self.describir()
