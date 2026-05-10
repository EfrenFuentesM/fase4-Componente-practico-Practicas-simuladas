"""
servicio.py - Clase abstracta Servicio
========================================
Define el contrato base para todos los servicios ofrecidos por Software FJ.
"""

from abc import abstractmethod
from typing import Optional
from software_fj.entidad import Entidad
from software_fj.excepciones import (
    ParametroFaltanteError,
    ServicioNoDisponibleError,
    DescuentoInvalidoError,
    CalculoCostoError,
)


class Servicio(Entidad):
    """
    Clase abstracta que representa un servicio de Software FJ.

    Proporciona estructura común: nombre, descripción, precio base,
    disponibilidad y métodos de cálculo de costo polimórficos.

    Subclases concretas:
        - ReservaSala
        - AlquilerEquipo
        - AsesoriaEspecializada
    """

    IMPUESTO_DEFAULT: float = 0.16  # 16% IVA por defecto

    def __init__(
        self,
        id_servicio: str,
        nombre: str,
        descripcion: str,
        precio_base: float,
        disponible: bool = True,
    ):
        """
        Inicializa un servicio con sus atributos fundamentales.

        Args:
            id_servicio: Identificador único del servicio.
            nombre: Nombre descriptivo del servicio.
            descripcion: Descripción detallada del servicio.
            precio_base: Precio unitario base (debe ser > 0).
            disponible: Indica si el servicio está activo.

        Raises:
            ParametroFaltanteError: Si nombre o descripción están vacíos.
            ValueError: Si el precio_base no es positivo.
        """
        if not nombre or not str(nombre).strip():
            raise ParametroFaltanteError("nombre", f"Servicio(id={id_servicio})")
        if not descripcion or not str(descripcion).strip():
            raise ParametroFaltanteError("descripcion", f"Servicio(id={id_servicio})")

        super().__init__(id_servicio)

        self._nombre: str = str(nombre).strip()
        self._descripcion: str = str(descripcion).strip()
        self._disponible: bool = bool(disponible)

        # El setter valida el rango
        self._precio_base: float = 0.0
        self.precio_base = precio_base

    # ── Propiedades ──────────────────────────────────────────────────────────

    @property
    def nombre(self) -> str:
        return self._nombre

    @property
    def descripcion(self) -> str:
        return self._descripcion

    @property
    def precio_base(self) -> float:
        return self._precio_base

    @precio_base.setter
    def precio_base(self, valor: float) -> None:
        try:
            valor = float(valor)
        except (TypeError, ValueError) as e:
            raise CalculoCostoError(
                f"El precio base debe ser numérico, se recibió: {valor!r}", e
            ) from e
        if valor <= 0:
            raise ValueError(
                f"El precio base debe ser mayor a 0. Se recibió: {valor}"
            )
        self._precio_base = valor

    @property
    def disponible(self) -> bool:
        return self._disponible

    @disponible.setter
    def disponible(self, valor: bool) -> None:
        self._disponible = bool(valor)

    # ── Métodos abstractos ───────────────────────────────────────────────────

    @abstractmethod
    def calcular_costo(self, duracion_horas: float, **kwargs) -> float:
        """
        Calcula el costo total del servicio para la duración dada.

        Args:
            duracion_horas: Duración en horas de la reserva.
            **kwargs: Parámetros opcionales (descuento, impuesto, etc.).

        Returns:
            Costo total como número positivo.
        """
        ...

    @abstractmethod
    def validar_parametros(self, **kwargs) -> bool:
        """
        Valida que los parámetros específicos del servicio sean correctos.

        Returns:
            True si todos los parámetros son válidos.
        """
        ...

    # ── Métodos concretos sobrecargados ──────────────────────────────────────

    def calcular_costo_con_impuesto(
        self,
        duracion_horas: float,
        tasa_impuesto: Optional[float] = None,
    ) -> float:
        """
        Calcula el costo total incluyendo impuesto.

        Sobrecarga conceptual: si no se proporciona tasa, usa el impuesto default.

        Args:
            duracion_horas: Duración en horas.
            tasa_impuesto: Tasa de impuesto (0.0–1.0). Usa IMPUESTO_DEFAULT si es None.

        Returns:
            Costo con impuesto aplicado.
        """
        tasa = tasa_impuesto if tasa_impuesto is not None else self.IMPUESTO_DEFAULT
        try:
            costo_base = self.calcular_costo(duracion_horas)
            return round(costo_base * (1 + tasa), 2)
        except Exception as e:
            raise CalculoCostoError(
                f"Error calculando costo con impuesto para '{self._nombre}'", e
            ) from e

    def calcular_costo_con_descuento(
        self,
        duracion_horas: float,
        descuento: float = 0.0,
        aplicar_impuesto: bool = False,
    ) -> float:
        """
        Calcula el costo aplicando un descuento y opcionalmente el impuesto.

        Sobrecarga conceptual: descuento es opcional y el impuesto se activa con flag.

        Args:
            duracion_horas: Duración en horas.
            descuento: Porcentaje de descuento (0.0–1.0).
            aplicar_impuesto: Si True, suma el IVA después del descuento.

        Returns:
            Costo final ajustado.

        Raises:
            DescuentoInvalidoError: Si el descuento está fuera de rango.
        """
        if not (0.0 <= descuento <= 1.0):
            raise DescuentoInvalidoError(descuento)
        try:
            costo_base = self.calcular_costo(duracion_horas)
            costo_descontado = round(costo_base * (1 - descuento), 2)
            if aplicar_impuesto:
                costo_descontado = round(costo_descontado * (1 + self.IMPUESTO_DEFAULT), 2)
            return costo_descontado
        except DescuentoInvalidoError:
            raise
        except Exception as e:
            raise CalculoCostoError(
                f"Error aplicando descuento al servicio '{self._nombre}'", e
            ) from e

    def verificar_disponibilidad(self) -> None:
        """
        Lanza una excepción si el servicio no está disponible.

        Raises:
            ServicioNoDisponibleError: Si el servicio está desactivado.
        """
        if not self._disponible:
            raise ServicioNoDisponibleError(
                self._nombre, "el servicio ha sido desactivado en el sistema"
            )

    def validar(self) -> bool:
        return bool(self._id and self._nombre and self._precio_base > 0)

    def describir(self) -> str:
        estado = "✓ Disponible" if self._disponible else "✗ No disponible"
        return (
            f"Servicio [{self._id}] '{self._nombre}' | "
            f"Precio base: ${self._precio_base:.2f}/h | {estado}"
        )

    def __str__(self) -> str:
        return self.describir()
