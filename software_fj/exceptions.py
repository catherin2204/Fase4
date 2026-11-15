import logging


class SistemaError(Exception):
    """Error base del dominio; todo error del sistema queda registrado."""

    def __init__(self, mensaje: str) -> None:
        super().__init__(mensaje)
        logging.getLogger("software_fj").error(
            "%s: %s", self.__class__.__name__, mensaje
        )


class ValidacionError(SistemaError):
    """Los datos recibidos no cumplen las reglas del sistema."""


class ParametroFaltanteError(ValidacionError):
    """Falta un parámetro requerido por un servicio."""


class OperacionNoPermitidaError(SistemaError):
    """La operación no está permitida para el estado actual."""


class ServicioNoDisponibleError(SistemaError):
    """El servicio solicitado no está disponible."""


class ReservaError(SistemaError):
    """No se pudo completar una operación de reserva."""


class CalculoError(SistemaError):
    """El importe calculado no es válido."""


class EntidadNoEncontradaError(SistemaError):
    """No se encontró la entidad solicitada."""
