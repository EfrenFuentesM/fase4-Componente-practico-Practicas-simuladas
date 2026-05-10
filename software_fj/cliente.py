"""
cliente.py - Clase Cliente con encapsulación y validaciones robustas
=====================================================================
Gestiona los datos personales de los clientes de Software FJ con
encapsulación estricta, validaciones exhaustivas y manejo de excepciones.
"""

import re
from typing import List, Optional
from software_fj.entidad import Entidad
from software_fj.excepciones import ClienteInvalidoError, ParametroFaltanteError


class Cliente(Entidad):
    """
    Representa a un cliente de Software FJ.

    Encapsula los datos personales del cliente con acceso controlado
    a través de propiedades y validaciones en cada setter.

    Atributos privados:
        _nombre (str): Nombre completo del cliente.
        _email (str): Correo electrónico válido.
        _telefono (str): Número telefónico en formato válido.
        _tipo (str): Categoría del cliente: 'regular', 'premium' o 'corporativo'.
        _historial_reservas (List[str]): IDs de reservas realizadas por el cliente.
    """

    TIPOS_VALIDOS = ("regular", "premium", "corporativo")
    _PATRON_EMAIL = re.compile(r"^[\w.\-+]+@[\w\-]+\.[a-zA-Z]{2,}$")
    _PATRON_TELEFONO = re.compile(r"^\+?[\d\s\-]{7,15}$")

    def __init__(
        self,
        id_cliente: str,
        nombre: str,
        email: str,
        telefono: str,
        tipo: str = "regular",
    ):
        """
        Inicializa un cliente con validación de todos sus atributos.

        Args:
            id_cliente: Identificador único del cliente.
            nombre: Nombre completo (mínimo 3 caracteres).
            email: Correo electrónico con formato válido.
            telefono: Número de teléfono de contacto.
            tipo: Categoría del cliente ('regular', 'premium', 'corporativo').

        Raises:
            ParametroFaltanteError: Si algún campo obligatorio está ausente.
            ClienteInvalidoError: Si algún campo no pasa las validaciones.
        """
        # Validar parámetros antes de llamar al super().__init__
        self._validar_parametros_constructor(id_cliente, nombre, email, telefono, tipo)

        super().__init__(id_cliente)

        # Asignación usando setters para reutilizar validaciones
        self._nombre: str = ""
        self._email: str = ""
        self._telefono: str = ""
        self._tipo: str = ""
        self._historial_reservas: List[str] = []

        self.nombre = nombre
        self.email = email
        self.telefono = telefono
        self.tipo = tipo

    # ── Validación del constructor ───────────────────────────────────────────

    @staticmethod
    def _validar_parametros_constructor(id_c, nombre, email, telefono, tipo) -> None:
        """Verifica que ningún parámetro obligatorio sea None o vacío."""
        campos = {
            "id_cliente": id_c,
            "nombre": nombre,
            "email": email,
            "telefono": telefono,
        }
        for campo, valor in campos.items():
            if valor is None:
                raise ParametroFaltanteError(campo, "constructor de Cliente")
            if isinstance(valor, str) and not valor.strip():
                raise ParametroFaltanteError(campo, "constructor de Cliente")

    # ── Propiedades con validación ───────────────────────────────────────────

    @property
    def nombre(self) -> str:
        return self._nombre

    @nombre.setter
    def nombre(self, valor: str) -> None:
        if not valor or not valor.strip():
            raise ClienteInvalidoError("El nombre no puede estar vacío.", "nombre")
        valor = valor.strip()
        if len(valor) < 3:
            raise ClienteInvalidoError(
                f"El nombre '{valor}' es demasiado corto (mínimo 3 caracteres).", "nombre"
            )
        if len(valor) > 100:
            raise ClienteInvalidoError(
                "El nombre no puede exceder los 100 caracteres.", "nombre"
            )
        if not re.match(r"^[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ\s\-']+$", valor):
            raise ClienteInvalidoError(
                f"El nombre '{valor}' contiene caracteres no permitidos.", "nombre"
            )
        self._nombre = valor

    @property
    def email(self) -> str:
        return self._email

    @email.setter
    def email(self, valor: str) -> None:
        if not valor or not valor.strip():
            raise ClienteInvalidoError("El email no puede estar vacío.", "email")
        valor = valor.strip().lower()
        if not self._PATRON_EMAIL.match(valor):
            raise ClienteInvalidoError(
                f"El email '{valor}' no tiene un formato válido.", "email"
            )
        self._email = valor

    @property
    def telefono(self) -> str:
        return self._telefono

    @telefono.setter
    def telefono(self, valor: str) -> None:
        if not valor or not valor.strip():
            raise ClienteInvalidoError("El teléfono no puede estar vacío.", "telefono")
        valor = valor.strip()
        if not self._PATRON_TELEFONO.match(valor):
            raise ClienteInvalidoError(
                f"El teléfono '{valor}' no tiene un formato válido.", "telefono"
            )
        self._telefono = valor

    @property
    def tipo(self) -> str:
        return self._tipo

    @tipo.setter
    def tipo(self, valor: str) -> None:
        if not valor or not str(valor).strip():
            raise ClienteInvalidoError("El tipo de cliente no puede estar vacío.", "tipo")
        valor = str(valor).strip().lower()
        if valor not in self.TIPOS_VALIDOS:
            raise ClienteInvalidoError(
                f"El tipo '{valor}' no es válido. Opciones: {self.TIPOS_VALIDOS}.", "tipo"
            )
        self._tipo = valor

    @property
    def historial_reservas(self) -> List[str]:
        """Retorna una copia del historial para preservar encapsulación."""
        return list(self._historial_reservas)

    # ── Métodos de negocio ───────────────────────────────────────────────────

    def agregar_reserva(self, id_reserva: str) -> None:
        """
        Agrega el ID de una reserva al historial del cliente.

        Args:
            id_reserva: Identificador de la reserva a registrar.

        Raises:
            ParametroFaltanteError: Si el ID de reserva es None o vacío.
        """
        if not id_reserva or not str(id_reserva).strip():
            raise ParametroFaltanteError("id_reserva", "agregar_reserva")
        self._historial_reservas.append(str(id_reserva).strip())

    def obtener_descuento_tipo(self) -> float:
        """
        Calcula el porcentaje de descuento según el tipo de cliente.

        Returns:
            Factor de descuento entre 0.0 y 1.0.
        """
        descuentos = {
            "regular": 0.0,
            "premium": 0.10,
            "corporativo": 0.20,
        }
        return descuentos.get(self._tipo, 0.0)

    def total_reservas(self) -> int:
        """Retorna el número total de reservas realizadas."""
        return len(self._historial_reservas)

    # ── Métodos abstractos implementados ─────────────────────────────────────

    def describir(self) -> str:
        return (
            f"Cliente [{self._id}] | {self._nombre} | {self._email} | "
            f"Tel: {self._telefono} | Tipo: {self._tipo.upper()} | "
            f"Reservas: {self.total_reservas()}"
        )

    def validar(self) -> bool:
        """Verifica que todos los campos obligatorios estén correctamente establecidos."""
        return bool(
            self._id
            and self._nombre
            and self._email
            and self._telefono
            and self._tipo in self.TIPOS_VALIDOS
        )

    # ── Representación ───────────────────────────────────────────────────────

    def __str__(self) -> str:
        return self.describir()
