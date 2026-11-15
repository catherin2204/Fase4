import logging
from typing import TypeVar

from software_fj.entities import Cliente, Entidad
from software_fj.exceptions import (
    EntidadNoEncontradaError,
    ValidacionError,
)
from software_fj.reservations import Reserva
from software_fj.services import Servicio

TEntidad = TypeVar("TEntidad", bound=Entidad)


class SistemaGestion:
    def __init__(self) -> None:
        self._clientes: list[Cliente] = []
        self._servicios: list[Servicio] = []
        self._reservas: list[Reserva] = []
        self._logger = logging.getLogger("software_fj")

    @property
    def clientes(self) -> tuple[Cliente, ...]:
        return tuple(self._clientes)

    @property
    def servicios(self) -> tuple[Servicio, ...]:
        return tuple(self._servicios)

    @property
    def reservas(self) -> tuple[Reserva, ...]:
        return tuple(self._reservas)

    def registrar_cliente(self, cliente: Cliente) -> Cliente:
        if not isinstance(cliente, Cliente):
            raise ValidacionError("Solo se pueden registrar instancias de Cliente.")
        cliente.validar()
        if any(actual.correo == cliente.correo for actual in self._clientes):
            raise ValidacionError(f"Ya existe un cliente con correo {cliente.correo}.")
        self._clientes.append(cliente)
        self._logger.info("Cliente registrado: %s (%s).", cliente.nombre, cliente.id)
        return cliente

    def registrar_servicio(self, servicio: Servicio) -> Servicio:
        if not isinstance(servicio, Servicio):
            raise ValidacionError("Solo se pueden registrar instancias de Servicio.")
        servicio.validar()
        if any(actual.id == servicio.id for actual in self._servicios):
            raise ValidacionError("El servicio ya está registrado.")
        self._servicios.append(servicio)
        self._logger.info("Servicio registrado: %s (%s).", servicio.nombre, servicio.id)
        return servicio

    def crear_reserva(
        self,
        cliente_id: str,
        servicio_id: str,
        duracion: float,
        parametros: dict[str, object] | None = None,
    ) -> Reserva:
        cliente = self._buscar_por_id(self._clientes, cliente_id, "cliente")
        servicio = self._buscar_por_id(self._servicios, servicio_id, "servicio")
        reserva = Reserva(cliente, servicio, duracion, parametros)
        self._reservas.append(reserva)
        self._logger.info("Reserva creada: %s.", reserva.id)
        return reserva

    def obtener_cliente(self, cliente_id: str) -> Cliente:
        return self._buscar_por_id(self._clientes, cliente_id, "cliente")

    def obtener_servicio(self, servicio_id: str) -> Servicio:
        return self._buscar_por_id(self._servicios, servicio_id, "servicio")

    def obtener_reserva(self, reserva_id: str) -> Reserva:
        return self._buscar_por_id(self._reservas, reserva_id, "reserva")

    def _buscar_por_id(
        self, elementos: list[TEntidad], identificador: str, tipo: str
    ) -> TEntidad:
        if not isinstance(identificador, str) or not identificador:
            raise ValidacionError(f"El identificador de {tipo} debe ser un texto válido.")
        for elemento in elementos:
            if elemento.id == identificador:
                return elemento
        raise EntidadNoEncontradaError(
            f"No se encontró {tipo} con identificador {identificador}."
        )
