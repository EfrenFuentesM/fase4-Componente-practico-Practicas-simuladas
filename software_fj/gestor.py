"""
gestor.py - Núcleo Lógico de Software FJ.
========================================
Este módulo implementa el GestorSistema, que actúa como el "Cerebro" de la aplicación.
Se encarga de coordinar la interacción entre Clientes, Servicios y Reservas,
asegurando que todas las reglas de negocio se cumplan y registrando cada
evento importante en el sistema de logs.
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
    Controlador central que orquestra la lógica de negocio de Software FJ.

    Mantiene en memoria los diccionarios de datos y proporciona métodos
    para realizar operaciones seguras (CRUD y procesos complejos) sobre el sistema.
    Todo error es capturado y registrado para facilitar el mantenimiento.

    Atributos:
        _clientes (Dict[str, Cliente]): Colección de clientes indexada por su ID único.
        _servicios (Dict[str, Servicio]): Catálogo de servicios disponibles por ID.
        _reservas (Dict[str, Reserva]): Historial de todas las reservas realizadas.
        _log (SistemaLog): Componente encargado de la escritura de archivos de registro.
        _contador_reservas (int): Secuencial utilizado para generar folios de reserva únicos.
    """

    def __init__(self, directorio_logs: str = "logs"):
        """Inicializa las estructuras de datos y el motor de logging."""
        self._clientes: Dict[str, Cliente] = {}
        self._servicios: Dict[str, Servicio] = {}
        self._reservas: Dict[str, Reserva] = {}
        self._contador_reservas: int = 0
        self._log = SistemaLog(directorio_logs)
        self._log.info("Motor GestorSistema iniciado con éxito.")

    # ── Utilidades Internas ──────────────────────────────────────────────────

    def _generar_id_reserva(self) -> str:
        """Genera un nuevo ID de reserva con formato RSV-0001."""
        self._contador_reservas += 1
        return f"RSV-{self._contador_reservas:04d}"

    # ════════════════════════════════════════════════════════════════════════
    # Sección: Gestión de Clientes
    # ════════════════════════════════════════════════════════════════════════

    def registrar_cliente(self, cliente: Cliente) -> None:
        """
        Incorpora un nuevo cliente a la base de datos del sistema.

        Args:
            cliente: Objeto Cliente ya instanciado.

        Raises:
            ClienteYaRegistradoError: Si el identificador ya existe en el mapa.
            SoftwareFJError: Si el objeto cliente no es válido según sus propias reglas.
        """
        try:
            if cliente.id in self._clientes:
                raise ClienteYaRegistradoError(cliente.id)

            if not cliente.validar():
                raise ValueError(f"Validación fallida para el cliente '{cliente.id}'.")

            self._clientes[cliente.id] = cliente
            self._log.info(f"Nuevo cliente registrado: {cliente.describir()}")

        except ClienteYaRegistradoError:
            self._log.advertencia(f"Intento de registro duplicado para ID: '{cliente.id}'")
            raise
        except Exception as e:
            self._log.error(f"Fallo crítico al registrar cliente '{cliente.id}'", e)
            raise

    def obtener_cliente(self, id_cliente: str) -> Cliente:
        """
        Busca un cliente específico por su ID.
        
        Returns:
            Instancia de Cliente si se encuentra.
        """
        try:
            if id_cliente not in self._clientes:
                raise ClienteNoEncontradoError(id_cliente)
            return self._clientes[id_cliente]
        except ClienteNoEncontradoError:
            self._log.error(f"Búsqueda fallida: Cliente '{id_cliente}' no existe.")
            raise

    def listar_clientes(self) -> List[Cliente]:
        """Devuelve una lista con todos los objetos cliente registrados."""
        return list(self._clientes.values())

    # ════════════════════════════════════════════════════════════════════════
    # Sección: Gestión del Catálogo de Servicios
    # ════════════════════════════════════════════════════════════════════════

    def agregar_servicio(self, servicio: Servicio) -> None:
        """
        Añade un servicio (Sala, Equipo o Asesoría) al catálogo oficial.

        Args:
            servicio: Instancia que hereda de la clase base Servicio.
        """
        try:
            if servicio.id in self._servicios:
                raise ValueError(f"ID de servicio duplicado en catálogo: '{servicio.id}'")
            
            if not servicio.validar():
                raise ValueError(f"Estructura de servicio inválida: '{servicio.id}'")
            
            self._servicios[servicio.id] = servicio
            self._log.info(f"Catálogo actualizado: {servicio.describir()}")

        except Exception as e:
            self._log.error(f"No se pudo añadir el servicio '{servicio.id}'", e)
            raise

    def obtener_servicio(self, id_servicio: str) -> Servicio:
        """Recupera un servicio por su código único."""
        try:
            if id_servicio not in self._servicios:
                raise ServicioNoEncontradoError(id_servicio)
            return self._servicios[id_servicio]
        except ServicioNoEncontradoError:
            self._log.error(f"Catálogo: Servicio '{id_servicio}' no encontrado.")
            raise

    def listar_servicios(self) -> List[Servicio]:
        """Obtiene la lista completa de servicios (disponibles o no)."""
        return list(self._servicios.values())

    def listar_servicios_disponibles(self) -> List[Servicio]:
        """Filtra el catálogo para mostrar solo los que pueden reservarse ahora."""
        return [s for s in self._servicios.values() if s.disponible]

    # ════════════════════════════════════════════════════════════════════════
    # Sección: Ciclo de Vida de Reservas
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
        Inicia el proceso de una nueva reserva.
        
        Crea el objeto Reserva vinculando al cliente y servicio, lo guarda como
        PENDIENTE y lo registra en el historial.
        """
        id_reserva = self._generar_id_reserva()
        self._log.info(f"Creando reserva {id_reserva} para Cliente:{id_cliente}")
        
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
            self._log.info(f"Reserva {id_reserva} guardada como PENDIENTE.")
            return reserva

        except SoftwareFJError as e:
            self._log.error(f"Error lógico al crear reserva {id_reserva}", e)
            raise
        except Exception as e:
            self._log.critico(f"Fallo de sistema inesperado en reserva {id_reserva}", e)
            raise

    def confirmar_reserva(self, id_reserva: str) -> float:
        """
        Valida y confirma una reserva pendiente, calculando el costo final.
        
        Returns:
            Importe total a pagar calculado por el servicio.
        """
        try:
            reserva = self._obtener_reserva(id_reserva)
            costo = reserva.confirmar()
            self._log.info(f"Reserva {id_reserva} CONFIRMADA. Total: ${costo:.2f}")
            return costo

        except OperacionNoPermitidaError as e:
            self._log.advertencia(f"Estado inválido para confirmación en {id_reserva}: {e}")
            raise
        except Exception as e:
            self._log.error(f"Fallo al confirmar la reserva {id_reserva}", e)
            raise

    def cancelar_reserva(self, id_reserva: str, motivo: str = "") -> None:
        """
        Cancela una reserva y libera los recursos asociados (si aplica).
        """
        try:
            reserva = self._obtener_reserva(id_reserva)
            reserva.cancelar(motivo or "Cancelación por el usuario")
            self._log.advertencia(f"Reserva {id_reserva} CANCELADA. Motivo: {motivo}")

        except Exception as e:
            self._log.error(f"No se pudo cancelar la reserva {id_reserva}", e)
            raise

    def completar_reserva(self, id_reserva: str) -> None:
        """Finaliza el ciclo de vida de una reserva confirmada."""
        try:
            reserva = self._obtener_reserva(id_reserva)
            reserva.completar()
            self._log.info(f"Reserva {id_reserva} finalizada satisfactoriamente.")
        except Exception as e:
            self._log.error(f"Error al marcar como completada la reserva {id_reserva}", e)
            raise

    def obtener_reserva(self, id_reserva: str) -> Reserva:
        """Acceso público para consultar datos de una reserva."""
        return self._obtener_reserva(id_reserva)

    def _obtener_reserva(self, id_reserva: str) -> Reserva:
        """Buscador interno de reservas con validación de existencia."""
        if id_reserva not in self._reservas:
            raise ReservaNoEncontradaError(id_reserva)
        return self._reservas[id_reserva]

    def listar_reservas(self) -> List[Reserva]:
        """Obtiene el historial completo de reservas."""
        return list(self._reservas.values())

    def listar_reservas_por_estado(self, estado: EstadoReserva) -> List[Reserva]:
        """Obtiene reservas filtradas (ej. solo 'CANCELADA' o 'CONFIRMADA')."""
        return [r for r in self._reservas.values() if r.estado == estado]

    # ── Generación de Informes ───────────────────────────────────────────────

    def generar_resumen(self) -> str:
        """
        Calcula estadísticas globales del sistema y las formatea como texto.
        
        Muestra conteo por estados e ingresos totales de reservas confirmadas/completas.
        """
        total = len(self._reservas)
        confirmadas = len(self.listar_reservas_por_estado(EstadoReserva.CONFIRMADA))
        canceladas = len(self.listar_reservas_por_estado(EstadoReserva.CANCELADA))
        completadas = len(self.listar_reservas_por_estado(EstadoReserva.COMPLETADA))
        rechazadas = len(self.listar_reservas_por_estado(EstadoReserva.RECHAZADA))

        # Sumatoria de ingresos basada en reservas válidas
        ingresos = sum(
            r.costo_total
            for r in self._reservas.values()
            if r.estado in {EstadoReserva.CONFIRMADA, EstadoReserva.COMPLETADA}
        )

        resumen = (
            f"\n{'═'*60}\n"
            f"  RESUMEN EJECUTIVO - Software FJ\n"
            f"{'═'*60}\n"
            f"  Clientes registrados  : {len(self._clientes)}\n"
            f"  Servicios en catálogo : {len(self._servicios)}\n"
            f"  Histórico de reservas : {total}\n"
            f"    ✓ Confirmadas       : {confirmadas}\n"
            f"    ✔ Completadas       : {completadas}\n"
            f"    ✗ Canceladas        : {canceladas}\n"
            f"    ✘ Rechazadas        : {rechazadas}\n"
            f"  Ingresos proyectados  : ${ingresos:,.2f}\n"
            f"{'═'*60}"
        )
        self._log.info("Resumen de sistema generado.")
        return resumen
