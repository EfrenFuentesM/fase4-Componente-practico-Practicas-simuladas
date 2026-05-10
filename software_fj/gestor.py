"""
gestor.py - Clase GestorSistema
================================
Controlador principal del sistema Software FJ.
Gestiona listas internas de clientes, servicios y reservas
con manejo completo de excepciones y registro de operaciones.
"""

from typing import Dict, List, Optional
from software_fj.cliente import Cliente
from software_fj.servicio import Servicio
from software_fj.reserva import Reserva, EstadoReserva
from software_fj.logger import SistemaLog
from software_fj.excepciones import (
    ClienteYaRegistradoError,
    ClienteNoEncontradoError,
    ServicioNoEncontradoError,
    ReservaNoEncontradaError,
    OperacionNoPermitidaError,
    SoftwareFJError,
)


class GestorSistema:
    """
    Controlador central del sistema Software FJ.

    Gestiona las listas internas de clientes, servicios y reservas,
    orquestando todas las operaciones del negocio con manejo de errores
    centralizado y registro en el sistema de logs.

    Atributos:
        _clientes (Dict[str, Cliente]): Mapa ID→Cliente.
        _servicios (Dict[str, Servicio]): Mapa ID→Servicio.
        _reservas (Dict[str, Reserva]): Mapa ID→Reserva.
        _log (SistemaLog): Logger del sistema.
        _contador_reservas (int): Auto-incremental para generar IDs de reserva.
    """

    def __init__(self, directorio_logs: str = "logs"):
        self._clientes: Dict[str, Cliente] = {}
        self._servicios: Dict[str, Servicio] = {}
        self._reservas: Dict[str, Reserva] = {}
        self._contador_reservas: int = 0
        self._log = SistemaLog(directorio_logs)
        self._log.info("GestorSistema inicializado correctamente.")

    # ── Generador de IDs ─────────────────────────────────────────────────────

    def _generar_id_reserva(self) -> str:
        self._contador_reservas += 1
        return f"RSV-{self._contador_reservas:04d}"

    # ════════════════════════════════════════════════════════════════════════
    # Gestión de Clientes
    # ════════════════════════════════════════════════════════════════════════

    def registrar_cliente(self, cliente: Cliente) -> None:
        """
        Registra un nuevo cliente en el sistema.

        Args:
            cliente: Instancia de Cliente válida.

        Raises:
            ClienteYaRegistradoError: Si el ID ya existe en el sistema.
            SoftwareFJError: Ante cualquier otro error del dominio.
        """
        try:
            if cliente.id in self._clientes:
                raise ClienteYaRegistradoError(cliente.id)

            if not cliente.validar():
                raise ValueError(f"El cliente '{cliente.id}' no pasó la validación interna.")

            self._clientes[cliente.id] = cliente
            self._log.info(f"Cliente registrado exitosamente: {cliente.describir()}")

        except ClienteYaRegistradoError:
            self._log.advertencia(
                f"Intento de registrar cliente duplicado: ID='{cliente.id}'"
            )
            raise
        except Exception as e:
            self._log.error(f"Error al registrar cliente ID='{cliente.id}'", e)
            raise

    def obtener_cliente(self, id_cliente: str) -> Cliente:
        """
        Busca y retorna un cliente por su ID.

        Raises:
            ClienteNoEncontradoError: Si el ID no existe.
        """
        try:
            if id_cliente not in self._clientes:
                raise ClienteNoEncontradoError(id_cliente)
            return self._clientes[id_cliente]
        except ClienteNoEncontradoError:
            self._log.error(f"Cliente no encontrado: ID='{id_cliente}'")
            raise

    def listar_clientes(self) -> List[Cliente]:
        """Retorna la lista de todos los clientes registrados."""
        return list(self._clientes.values())

    # ════════════════════════════════════════════════════════════════════════
    # Gestión de Servicios
    # ════════════════════════════════════════════════════════════════════════

    def agregar_servicio(self, servicio: Servicio) -> None:
        """
        Agrega un servicio al catálogo del sistema.

        Raises:
            ValueError: Si el ID del servicio ya está registrado.
        """
        try:
            if servicio.id in self._servicios:
                raise ValueError(
                    f"Ya existe un servicio con ID '{servicio.id}' en el catálogo."
                )
            if not servicio.validar():
                raise ValueError(
                    f"El servicio '{servicio.id}' no pasó la validación interna."
                )
            self._servicios[servicio.id] = servicio
            self._log.info(f"Servicio agregado al catálogo: {servicio.describir()}")

        except Exception as e:
            self._log.error(f"Error al agregar servicio ID='{servicio.id}'", e)
            raise

    def obtener_servicio(self, id_servicio: str) -> Servicio:
        """
        Busca y retorna un servicio por su ID.

        Raises:
            ServicioNoEncontradoError: Si el ID no existe.
        """
        try:
            if id_servicio not in self._servicios:
                raise ServicioNoEncontradoError(id_servicio)
            return self._servicios[id_servicio]
        except ServicioNoEncontradoError:
            self._log.error(f"Servicio no encontrado: ID='{id_servicio}'")
            raise

    def listar_servicios(self) -> List[Servicio]:
        """Retorna la lista de todos los servicios en catálogo."""
        return list(self._servicios.values())

    def listar_servicios_disponibles(self) -> List[Servicio]:
        """Retorna solo los servicios actualmente disponibles."""
        return [s for s in self._servicios.values() if s.disponible]

    # ════════════════════════════════════════════════════════════════════════
    # Gestión de Reservas
    # ════════════════════════════════════════════════════════════════════════

    def crear_reserva(
        self,
        id_cliente: str,
        id_servicio: str,
        duracion: float,
        fecha_reserva,
        notas: str = "",
        **parametros_extra,
    ) -> Reserva:
        """
        Crea una nueva reserva en estado PENDIENTE.

        Args:
            id_cliente: ID del cliente que hace la reserva.
            id_servicio: ID del servicio a reservar.
            duracion: Duración (horas o días según el servicio).
            fecha_reserva: Fecha programada para el servicio.
            notas: Observaciones opcionales.
            **parametros_extra: Parámetros adicionales del servicio.

        Returns:
            La reserva creada en estado PENDIENTE.

        Raises:
            ClienteNoEncontradoError: Si el cliente no existe.
            ServicioNoEncontradoError: Si el servicio no existe.
            SoftwareFJError: Ante cualquier error del dominio.
        """
        id_reserva = self._generar_id_reserva()
        self._log.info(
            f"Iniciando creación de reserva {id_reserva} | "
            f"Cliente='{id_cliente}' | Servicio='{id_servicio}' | Duración={duracion}"
        )
        try:
            cliente = self.obtener_cliente(id_cliente)
            servicio = self.obtener_servicio(id_servicio)

            reserva = Reserva(
                id_reserva=id_reserva,
                cliente=cliente,
                servicio=servicio,
                duracion=duracion,
                fecha_reserva=fecha_reserva,
                notas=notas,
                **parametros_extra,
            )

            self._reservas[id_reserva] = reserva
            self._log.info(f"Reserva creada: {reserva.describir()}")
            return reserva

        except SoftwareFJError as e:
            self._log.error(f"Error de dominio al crear reserva {id_reserva}", e)
            raise
        except Exception as e:
            self._log.critico(f"Error inesperado al crear reserva {id_reserva}", e)
            raise

    def confirmar_reserva(self, id_reserva: str) -> float:
        """
        Confirma una reserva existente y calcula su costo.

        Args:
            id_reserva: ID de la reserva a confirmar.

        Returns:
            El costo total de la reserva confirmada.

        Raises:
            ReservaNoEncontradaError: Si no existe la reserva.
            OperacionNoPermitidaError: Si la reserva no puede confirmarse.
        """
        try:
            reserva = self._obtener_reserva(id_reserva)
            costo = reserva.confirmar()
            self._log.info(
                f"Reserva {id_reserva} CONFIRMADA | "
                f"Costo total: ${costo:.2f} | "
                f"Cliente: {reserva.cliente.nombre}"
            )
            return costo

        except OperacionNoPermitidaError as e:
            self._log.advertencia(f"Operación no permitida sobre reserva {id_reserva}: {e}")
            raise
        except SoftwareFJError as e:
            self._log.error(f"Error al confirmar reserva {id_reserva}", e)
            raise
        except Exception as e:
            self._log.critico(f"Error inesperado al confirmar reserva {id_reserva}", e)
            raise

    def cancelar_reserva(self, id_reserva: str, motivo: str = "") -> None:
        """
        Cancela una reserva existente.

        Args:
            id_reserva: ID de la reserva a cancelar.
            motivo: Razón de la cancelación.

        Raises:
            ReservaNoEncontradaError: Si no existe la reserva.
            OperacionNoPermitidaError: Si el estado no permite cancelación.
        """
        try:
            reserva = self._obtener_reserva(id_reserva)
            reserva.cancelar(motivo or "Cancelación solicitada")
            self._log.advertencia(
                f"Reserva {id_reserva} CANCELADA | "
                f"Motivo: {motivo or 'No especificado'}"
            )

        except OperacionNoPermitidaError as e:
            self._log.advertencia(f"No se puede cancelar la reserva {id_reserva}: {e}")
            raise
        except SoftwareFJError as e:
            self._log.error(f"Error al cancelar reserva {id_reserva}", e)
            raise

    def completar_reserva(self, id_reserva: str) -> None:
        """Marca una reserva confirmada como completada."""
        try:
            reserva = self._obtener_reserva(id_reserva)
            reserva.completar()
            self._log.info(f"Reserva {id_reserva} marcada como COMPLETADA.")
        except SoftwareFJError as e:
            self._log.error(f"Error al completar reserva {id_reserva}", e)
            raise

    def obtener_reserva(self, id_reserva: str) -> Reserva:
        """Retorna una reserva por su ID (API pública)."""
        return self._obtener_reserva(id_reserva)

    def _obtener_reserva(self, id_reserva: str) -> Reserva:
        """Método interno para obtener una reserva o lanzar excepción."""
        from software_fj.excepciones import ReservaNoEncontradaError
        if id_reserva not in self._reservas:
            raise ReservaNoEncontradaError(id_reserva)
        return self._reservas[id_reserva]

    def listar_reservas(self) -> List[Reserva]:
        """Retorna todas las reservas registradas."""
        return list(self._reservas.values())

    def listar_reservas_por_estado(self, estado: EstadoReserva) -> List[Reserva]:
        """Filtra y retorna reservas según su estado."""
        return [r for r in self._reservas.values() if r.estado == estado]

    # ── Reporte de resumen ───────────────────────────────────────────────────

    def generar_resumen(self) -> str:
        """
        Genera un resumen del estado actual del sistema.

        Returns:
            Cadena formateada con métricas del sistema.
        """
        total = len(self._reservas)
        confirmadas = len(self.listar_reservas_por_estado(EstadoReserva.CONFIRMADA))
        canceladas = len(self.listar_reservas_por_estado(EstadoReserva.CANCELADA))
        completadas = len(self.listar_reservas_por_estado(EstadoReserva.COMPLETADA))
        rechazadas = len(self.listar_reservas_por_estado(EstadoReserva.RECHAZADA))

        ingresos = sum(
            r.costo_total
            for r in self._reservas.values()
            if r.estado in {EstadoReserva.CONFIRMADA, EstadoReserva.COMPLETADA}
        )

        resumen = (
            f"\n{'═'*60}\n"
            f"  RESUMEN DEL SISTEMA - Software FJ\n"
            f"{'═'*60}\n"
            f"  Clientes registrados  : {len(self._clientes)}\n"
            f"  Servicios en catálogo : {len(self._servicios)}\n"
            f"  Total de reservas     : {total}\n"
            f"    ✓ Confirmadas       : {confirmadas}\n"
            f"    ✔ Completadas       : {completadas}\n"
            f"    ✗ Canceladas        : {canceladas}\n"
            f"    ✘ Rechazadas        : {rechazadas}\n"
            f"  Ingresos generados    : ${ingresos:,.2f}\n"
            f"{'═'*60}"
        )
        self._log.info(resumen)
        return resumen
