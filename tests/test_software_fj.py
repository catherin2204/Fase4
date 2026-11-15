import unittest

from software_fj import (
    Cliente,
    EstadoReserva,
    OperacionNoPermitidaError,
    ParametroFaltanteError,
    ReservaError,
    SalaReuniones,
    SistemaGestion,
    ServicioNoDisponibleError,
    ValidacionError,
)


class SistemaFjTests(unittest.TestCase):
    def setUp(self) -> None:
        self.sistema = SistemaGestion()
        self.cliente = self.sistema.registrar_cliente(
            Cliente("Ana Pérez", "ana@example.com", "+57 3001234567")
        )
        self.sala = self.sistema.registrar_servicio(
            SalaReuniones("Sala Norte", 50, 8)
        )

    def test_cliente_normaliza_correo_y_rechaza_datos_invalidos(self) -> None:
        self.assertEqual(self.cliente.correo, "ana@example.com")
        self.assertEqual(self.cliente.telefono, "+57 3001234567")
        with self.assertRaises(ValidacionError):
            Cliente("A", "invalido", "123")

    def test_sala_requiere_personas_para_confirmar(self) -> None:
        reserva = self.sistema.crear_reserva(
            self.cliente.id, self.sala.id, 2, {}
        )
        with self.assertRaises(ReservaError) as contexto:
            reserva.confirmar()
        self.assertIsInstance(contexto.exception.__cause__, ParametroFaltanteError)
        self.assertEqual(reserva.estado, EstadoReserva.FALLIDA)

    def test_calculo_con_impuesto_y_descuento(self) -> None:
        costo = self.sala.calcular_costo(
            2,
            parametros={"personas": 4},
            tasa_impuesto=0.1,
            descuento=0.05,
        )
        self.assertEqual(costo, 104.5)

    def test_reserva_se_confirma_procesa_y_no_se_cancela_despues(self) -> None:
        reserva = self.sistema.crear_reserva(
            self.cliente.id, self.sala.id, 2, {"personas": 4}
        )
        reserva.confirmar()
        self.assertEqual(reserva.procesar(), 100.0)
        self.assertEqual(reserva.estado, EstadoReserva.PROCESADA)
        with self.assertRaises(OperacionNoPermitidaError):
            reserva.cancelar()

    def test_servicio_no_disponible_impide_confirmacion_con_causa(self) -> None:
        self.sala.establecer_disponibilidad(False)
        reserva = self.sistema.crear_reserva(
            self.cliente.id, self.sala.id, 2, {"personas": 4}
        )
        with self.assertRaises(ReservaError) as contexto:
            reserva.confirmar()
        self.assertIsInstance(contexto.exception.__cause__, ServicioNoDisponibleError)
        self.assertEqual(reserva.estado, EstadoReserva.FALLIDA)

    def test_rechaza_parametros_desconocidos(self) -> None:
        with self.assertRaises(ValidacionError):
            self.sala.validar_parametros(personas=4, sala_privada=True)


if __name__ == "__main__":
    unittest.main()
