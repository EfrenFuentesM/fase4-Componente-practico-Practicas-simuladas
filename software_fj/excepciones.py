"""
excepciones.py - Excepciones personalizadas para el sistema Software FJ
========================================================================
Define la jerarquía de excepciones propias del dominio del negocio.
"""


class SoftwareFJError(Exception):
    """Excepción base del sistema Software FJ. Todas las excepciones del sistema heredan de esta."""

    def __init__(self, mensaje: str, codigo: str = "SFJ-000"):
        self.mensaje = mensaje
        self.codigo = codigo
        super().__init__(f"[{codigo}] {mensaje}")

    def __str__(self):
        return f"[{self.codigo}] {self.mensaje}"


# ── Excepciones de Cliente ──────────────────────────────────────────────────

class ClienteInvalidoError(SoftwareFJError):
    """Se lanza cuando los datos de un cliente no cumplen las validaciones requeridas."""

    def __init__(self, mensaje: str, campo: str = ""):
        self.campo = campo
        codigo = "SFJ-101"
        detalle = f"Campo '{campo}': {mensaje}" if campo else mensaje
        super().__init__(detalle, codigo)


class ClienteYaRegistradoError(SoftwareFJError):
    """Se lanza cuando se intenta registrar un cliente con un ID ya existente."""

    def __init__(self, id_cliente: str):
        self.id_cliente = id_cliente
        super().__init__(f"El cliente con ID '{id_cliente}' ya se encuentra registrado.", "SFJ-102")


class ClienteNoEncontradoError(SoftwareFJError):
    """Se lanza cuando no se encuentra un cliente en el sistema."""

    def __init__(self, id_cliente: str):
        self.id_cliente = id_cliente
        super().__init__(f"No se encontró ningún cliente con ID '{id_cliente}'.", "SFJ-103")


# ── Excepciones de Servicio ─────────────────────────────────────────────────

class ServicioNoDisponibleError(SoftwareFJError):
    """Se lanza cuando un servicio no está disponible para reservar."""

    def __init__(self, nombre_servicio: str, razon: str = ""):
        self.nombre_servicio = nombre_servicio
        detalle = f"El servicio '{nombre_servicio}' no está disponible"
        if razon:
            detalle += f": {razon}"
        super().__init__(detalle, "SFJ-201")


class ServicioNoEncontradoError(SoftwareFJError):
    """Se lanza cuando no se localiza un servicio por su ID."""

    def __init__(self, id_servicio: str):
        self.id_servicio = id_servicio
        super().__init__(f"No se encontró ningún servicio con ID '{id_servicio}'.", "SFJ-202")


class ParametroFaltanteError(SoftwareFJError):
    """Se lanza cuando un parámetro obligatorio está ausente o es None."""

    def __init__(self, parametro: str, contexto: str = ""):
        self.parametro = parametro
        self.contexto = contexto
        detalle = f"Parámetro obligatorio ausente: '{parametro}'"
        if contexto:
            detalle += f" en {contexto}"
        super().__init__(detalle, "SFJ-203")


# ── Excepciones de Reserva ──────────────────────────────────────────────────

class ReservaInvalidaError(SoftwareFJError):
    """Se lanza cuando los datos de una reserva son inválidos."""

    def __init__(self, mensaje: str):
        super().__init__(mensaje, "SFJ-301")


class ReservaNoEncontradaError(SoftwareFJError):
    """Se lanza cuando no se encuentra una reserva por su ID."""

    def __init__(self, id_reserva: str):
        self.id_reserva = id_reserva
        super().__init__(f"No se encontró ninguna reserva con ID '{id_reserva}'.", "SFJ-302")


class OperacionNoPermitidaError(SoftwareFJError):
    """Se lanza cuando se intenta una operación inválida sobre el estado actual de una reserva."""

    def __init__(self, operacion: str, estado_actual: str):
        self.operacion = operacion
        self.estado_actual = estado_actual
        super().__init__(
            f"La operación '{operacion}' no está permitida para una reserva en estado '{estado_actual}'.",
            "SFJ-303"
        )


# ── Excepciones de Cálculo ──────────────────────────────────────────────────

class CalculoCostoError(SoftwareFJError):
    """Se lanza cuando ocurre un error en el cálculo de costos."""

    def __init__(self, mensaje: str, causa: Exception = None):
        self.causa = causa
        super().__init__(mensaje, "SFJ-401")
        if causa:
            self.__cause__ = causa


class DescuentoInvalidoError(SoftwareFJError):
    """Se lanza cuando el descuento aplicado está fuera del rango permitido."""

    def __init__(self, descuento: float):
        self.descuento = descuento
        super().__init__(
            f"El descuento '{descuento}' es inválido. Debe estar entre 0.0 y 1.0 (0% y 100%).",
            "SFJ-402"
        )
