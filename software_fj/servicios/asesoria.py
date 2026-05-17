"""
servicios/asesoria.py - Servicio de Asesorías Especializadas
=============================================================
Implementa el servicio de asesorías técnicas y estratégicas para Software FJ.
"""

from software_fj.servicio import Servicio
from software_fj.excepciones import (
    ParametroFaltanteError,
    ReservaInvalidaError,
    CalculoCostoError,
)


class AsesoriaEspecializada(Servicio):
    """
    Servicio de asesoría especializada (técnica, legal, estratégica, etc.).

    Extiende Servicio con manejo de especialidades, nivel de experto
    y tarifa diferencial según urgencia.

    Atributos específicos:
        _especialidad (str): Área de conocimiento del asesor.
        _nivel_experto (str): Nivel del asesor ('junior', 'senior', 'experto').
        _factor_nivel (float): Multiplicador de precio según nivel.
        _modalidad (str): Forma de prestación ('presencial', 'remota', 'hibrida').
        _duracion_minima_horas (float): Tiempo mínimo de contratación.
    """

    NIVELES_VALIDOS = ("junior", "senior", "experto")
    MODALIDADES_VALIDAS = ("presencial", "remota", "hibrida")
    FACTOR_URGENCIA: float = 1.5  # Recargo del 50% por solicitud urgente
    DURACION_MINIMA_HORAS: float = 1.0
    DURACION_MAXIMA_HORAS: float = 40.0  # Hasta una semana de trabajo

    FACTORES_NIVEL = {
        "junior": 1.0,
        "senior": 1.5,
        "experto": 2.0,
    }

    RECARGO_PRESENCIAL: float = 0.10  # 10% adicional por desplazamiento

    def __init__(
        self,
        id_servicio: str,
        nombre: str,
        especialidad: str,
        precio_base: float,
        nivel_experto: str = "senior",
        modalidad: str = "remota",
        disponible: bool = True,
    ):
        """
        Inicializa el servicio de asesoría.

        Args:
            id_servicio: ID único del servicio.
            nombre: Nombre del servicio de asesoría.
            especialidad: Área de conocimiento (ej.: 'Ciberseguridad').
            precio_base: Precio base por hora del asesor junior.
            nivel_experto: Nivel del asesor ('junior', 'senior', 'experto').
            modalidad: Modalidad de prestación del servicio.
            disponible: Disponibilidad inicial.

        Raises:
            ValueError: Si el nivel o la modalidad no son válidos.
        """
        nivel_experto = str(nivel_experto).strip().lower()
        modalidad = str(modalidad).strip().lower()

        if nivel_experto not in self.NIVELES_VALIDOS:
            raise ValueError(
                f"Nivel de experto '{nivel_experto}' no válido. "
                f"Opciones: {self.NIVELES_VALIDOS}"
            )
        if modalidad not in self.MODALIDADES_VALIDAS:
            raise ValueError(
                f"Modalidad '{modalidad}' no válida. "
                f"Opciones: {self.MODALIDADES_VALIDAS}"
            )

        descripcion = (
            f"Asesoría especializada en {especialidad}. "
            f"Nivel: {nivel_experto.capitalize()}. "
            f"Modalidad: {modalidad.capitalize()}."
        )
        super().__init__(id_servicio, nombre, descripcion, precio_base, disponible)

        self._especialidad: str = str(especialidad).strip()
        self._nivel_experto: str = nivel_experto
        self._modalidad: str = modalidad
        self._factor_nivel: float = self.FACTORES_NIVEL[nivel_experto]

    # ── Propiedades ──────────────────────────────────────────────────────────

    @property
    def especialidad(self) -> str:
        return self._especialidad

    @property
    def nivel_experto(self) -> str:
        return self._nivel_experto

    @property
    def modalidad(self) -> str:
        return self._modalidad

    @property
    def tarifa_efectiva(self) -> float:
        """Retorna la tarifa real por hora según el nivel del experto."""
        return round(self._precio_base * self._factor_nivel, 2)

    # ── Métodos abstractos implementados ─────────────────────────────────────

    def calcular_costo(self, duracion_horas: float, **kwargs) -> float:
        """
        Calcula el costo de la asesoría.

        Parámetros kwargs:
            urgente (bool): Si True, aplica recargo por urgencia (50%).
            presencial_forzado (bool): Si True, aplica recargo de 10% por modalidad presencial.

        Returns:
            Costo total calculado.

        Raises:
            ReservaInvalidaError: Si la duración está fuera del rango permitido.
            CalculoCostoError: Si ocurre un error en el cálculo.
        """
        try:
            duracion_horas = float(duracion_horas)
        except (TypeError, ValueError) as e:
            raise CalculoCostoError(
                f"La duración '{duracion_horas}' no es un número válido.", e
            ) from e

        if duracion_horas < self.DURACION_MINIMA_HORAS:
            raise ReservaInvalidaError(
                f"La duración mínima de asesoría es {self.DURACION_MINIMA_HORAS} hora(s). "
                f"Se solicitó {duracion_horas}h."
            )
        if duracion_horas > self.DURACION_MAXIMA_HORAS:
            raise ReservaInvalidaError(
                f"La duración máxima de asesoría es {self.DURACION_MAXIMA_HORAS} hora(s). "
                f"Se solicitó {duracion_horas}h."
            )

        urgente = kwargs.get("urgente", False)
        presencial_forzado = kwargs.get("presencial_forzado", False)

        try:
            # Precio ajustado por nivel del experto
            costo = self._precio_base * self._factor_nivel * duracion_horas

            # Recargo por urgencia
            if urgente:
                costo *= self.FACTOR_URGENCIA

            # Recargo por modalidad presencial
            if presencial_forzado or self._modalidad == "presencial":
                costo *= (1 + self.RECARGO_PRESENCIAL)

            return round(costo, 2)

        except Exception as e:
            raise CalculoCostoError(
                f"Error calculando el costo de la asesoría '{self._nombre}'.", e
            ) from e

    def validar_parametros(self, **kwargs) -> bool:
        """Valida que la duración de la asesoría sea correcta."""
        duracion = kwargs.get("duracion_horas")

        if duracion is None:
            raise ParametroFaltanteError("duracion_horas", "AsesoriaEspecializada.validar_parametros")

        try:
            duracion = float(duracion)
        except (TypeError, ValueError):
            return False

        return self.DURACION_MINIMA_HORAS <= duracion <= self.DURACION_MAXIMA_HORAS

    def describir(self) -> str:
        estado = "✓ Disponible" if self._disponible else "✗ No disponible"
        return (
            f"[ASESORÍA] [{self._id}] '{self._nombre}' | "
            f"Especialidad: {self._especialidad} | "
            f"Nivel: {self._nivel_experto.capitalize()} | "
            f"Modalidad: {self._modalidad.capitalize()} | "
            f"Tarifa efectiva: ${self.tarifa_efectiva:.2f}/h | {estado}"
        )
