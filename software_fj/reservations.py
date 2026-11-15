import logging
from enum import Enum
from typing import Mapping

from software_fj.entities import Cliente, Entidad
from software_fj.exceptions import (
    OperacionNoPermitidaError,
    ReservaError,
    SistemaError,
    ValidacionError,
)
from software_fj.services import Servicio, _es_numero_finito


class EstadoReserva(Enum):
    PENDIENTE = "pendiente"
    CONFIRMADA = "confirmada"
    PROCESADA = "procesada"
    CANCELADA = "cancelada"
    FALLIDA = "fallida"


class Reserva(Entidad):
    def __init__(
        self,
        cliente: Cliente,
        servicio: Servicio,
        duracion: float,
        parametros: Mapping[str, object] | None = None,
    ) -> None:
        super().__init__()
        if not isinstance(cliente, Cliente):
            raise ValidacionError("La reserva requiere un cliente válido.")
        if not isinstance(servicio, Servicio):
            raise ValidacionError("La reserva requiere un servicio válido.")
        if (
            not _es_numero_finito(duracion) or duracion <= 0
        ):
            raise ValidacionError("La duración debe ser un número positivo y finito.")
        if parametros is not None and not isinstance(parametros, Mapping):
            raise ValidacionError("Los parámetros de la reserva deben ser un mapa.")

        self._cliente = cliente
        self._servicio = servicio
        self._duracion = float(duracion)
        self._parametros = dict(parametros or {})
        self._estado = EstadoReserva.PENDIENTE
        self._total: float | None = None
        self._logger = logging.getLogger("software_fj")

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
    def estado(self) -> EstadoReserva:
        return self._estado

    @property
    def total(self) -> float | None:
        return self._total

    def validar(self) -> None:
        self._cliente.validar()
        self._servicio.validar()

    def confirmar(self) -> None:
        if self._estado is not EstadoReserva.PENDIENTE:
            raise OperacionNoPermitidaError(
                f"No se puede confirmar una reserva en estado '{self._estado.value}'."
            )
        try:
            self._servicio.validar_parametros(**self._parametros)
        except SistemaError as error:
            self._estado = EstadoReserva.FALLIDA
            raise ReservaError("La reserva no pudo ser confirmada.") from error
        else:
            self._estado = EstadoReserva.CONFIRMADA
            self._logger.info("Reserva %s confirmada.", self.id)
        finally:
            self._logger.info("Validación de confirmación finalizada para %s.", self.id)

    def cancelar(self) -> None:
        if self._estado not in (EstadoReserva.PENDIENTE, EstadoReserva.CONFIRMADA):
            raise OperacionNoPermitidaError(
                f"No se puede cancelar una reserva en estado '{self._estado.value}'."
            )
        self._estado = EstadoReserva.CANCELADA
        self._logger.info("Reserva %s cancelada.", self.id)

    def procesar(
        self, *, tasa_impuesto: float = 0.0, descuento: float = 0.0
    ) -> float:
        if self._estado is not EstadoReserva.CONFIRMADA:
            raise OperacionNoPermitidaError(
                "Solo se pueden procesar reservas confirmadas."
            )
        try:
            total = self._servicio.calcular_costo(
                self._duracion,
                tasa_impuesto=tasa_impuesto,
                descuento=descuento,
                parametros=self._parametros,
            )
        except SistemaError as error:
            self._estado = EstadoReserva.FALLIDA
            raise ReservaError("No se pudo procesar el costo de la reserva.") from error
        else:
            self._total = total
            self._estado = EstadoReserva.PROCESADA
            self._logger.info("Reserva %s procesada por %.2f.", self.id, total)
            return total
        finally:
            self._logger.info("Procesamiento finalizado para la reserva %s.", self.id)
