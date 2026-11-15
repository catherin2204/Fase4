import logging
from collections.abc import Callable

from software_fj.entities import Cliente
from software_fj.exceptions import SistemaError
from software_fj.logging_config import configurar_logging
from software_fj.reservations import EstadoReserva
from software_fj.services import (
    AlquilerEquipo,
    AsesoriaEspecializada,
    SalaReuniones,
    Servicio,
)
from software_fj.system import SistemaGestion


def ejecutar_demo() -> int:
    logger = configurar_logging()
    sistema = SistemaGestion()
    datos: dict[str, object] = {}
    completadas = 0

    def ejecutar(nombre: str, operacion: Callable[[], object]) -> object | None:
        nonlocal completadas
        logger.info("Inicia operación: %s.", nombre)
        try:
            resultado = operacion()
        except SistemaError as error:
            print(f"[ERROR] {nombre}: {error}")
            return None
        except Exception:
            logger.exception("Error inesperado durante la operación '%s'.", nombre)
            print(f"[ERROR] {nombre}: ocurrió un error inesperado; consulte el log.")
            return None
        else:
            completadas += 1
            print(f"[OK] {nombre}")
            return resultado
        finally:
            logger.info("Finaliza operación: %s.", nombre)

    def registrar_cliente() -> Cliente:
        cliente = Cliente("Ana Pérez", "ana@example.com", "+57 3001234567")
        sistema.registrar_cliente(cliente)
        datos["cliente"] = cliente
        return cliente

    def crear_reserva_sala(parametros: dict[str, object]) -> str:
        cliente = datos["cliente"]
        servicio = datos["sala"]
        if not isinstance(cliente, Cliente) or not isinstance(servicio, SalaReuniones):
            raise RuntimeError("No se registraron el cliente y la sala de la demostración.")
        reserva = sistema.crear_reserva(
            cliente.id, servicio.id, 2, parametros
        )
        return reserva.id

    def obtener_reserva(clave: str):
        identificador = datos.get(clave)
        if not isinstance(identificador, str):
            raise RuntimeError(f"No se creó la reserva de demostración '{clave}'.")
        return sistema.obtener_reserva(identificador)

    def crear_reserva_equipo() -> str:
        cliente = datos.get("cliente")
        servicio = datos.get("equipo")
        if not isinstance(cliente, Cliente) or not isinstance(servicio, Servicio):
            raise RuntimeError("No se registraron el cliente y el equipo de la demostración.")
        reserva = sistema.crear_reserva(
            cliente.id, servicio.id, 3, {"unidades": 2}
        )
        datos["reserva_equipo"] = reserva.id
        return reserva.id

    def confirmar_y_cancelar_equipo() -> EstadoReserva:
        reserva = obtener_reserva("reserva_equipo")
        reserva.confirmar()
        reserva.cancelar()
        return reserva.estado

    ejecutar("registrar cliente válido", registrar_cliente)
    ejecutar(
        "rechazar cliente inválido",
        lambda: Cliente("A", "correo-inválido", "123"),
    )
    ejecutar(
        "rechazar correo duplicado",
        lambda: sistema.registrar_cliente(
            Cliente("Ana Pérez", "ANA@example.com", "+57 3012223344")
        ),
    )
    ejecutar(
        "registrar sala de reuniones",
        lambda: datos.setdefault(
            "sala", sistema.registrar_servicio(SalaReuniones("Sala Norte", 50, 8))
        ),
    )
    ejecutar(
        "registrar alquiler de equipos",
        lambda: datos.setdefault(
            "equipo",
            sistema.registrar_servicio(AlquilerEquipo("Proyector", 30, "proyector", 4)),
        ),
    )
    ejecutar(
        "registrar asesoría especializada",
        lambda: sistema.registrar_servicio(
            AsesoriaEspecializada("Consultoría", 80, "seguridad informática")
        ),
    )
    ejecutar(
        "rechazar servicio con capacidad inválida",
        lambda: SalaReuniones("Sala pequeña", 20, 0),
    )

    ejecutar(
        "crear reserva de sala",
        lambda: datos.__setitem__(
            "reserva_valida", crear_reserva_sala({"personas": 4})
        ),
    )
    ejecutar(
        "confirmar reserva de sala",
        lambda: obtener_reserva("reserva_valida").confirmar(),
    )
    ejecutar(
        "procesar reserva con impuesto y descuento",
        lambda: obtener_reserva("reserva_valida").procesar(
            tasa_impuesto=0.1, descuento=0.05
        ),
    )
    ejecutar(
        "crear reserva sin parámetros requeridos",
        lambda: datos.__setitem__("reserva_invalida", crear_reserva_sala({})),
    )
    ejecutar(
        "detectar parámetros faltantes al confirmar",
        lambda: obtener_reserva("reserva_invalida").confirmar(),
    )
    ejecutar(
        "crear reserva de equipo válida",
        crear_reserva_equipo,
    )
    ejecutar(
        "confirmar y cancelar reserva de equipo",
        confirmar_y_cancelar_equipo,
    )
    ejecutar(
        "rechazar cancelación después del procesamiento",
        lambda: obtener_reserva("reserva_valida").cancelar(),
    )

    logger.info(
        "Demostración finalizada: %d operaciones exitosas; estado reserva principal: %s.",
        completadas,
        obtener_reserva("reserva_valida").estado.value
        if "reserva_valida" in datos
        else EstadoReserva.FALLIDA.value,
    )
    print(f"\nOperaciones exitosas: {completadas}. Revise logs/software_fj.log.")
    return completadas
