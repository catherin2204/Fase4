import math
from abc import abstractmethod
from typing import Mapping, overload

from software_fj.entities import Entidad
from software_fj.exceptions import (
    CalculoError,
    ParametroFaltanteError,
    ServicioNoDisponibleError,
    ValidacionError,
)


def _es_numero_finito(valor: object) -> bool:
    if not isinstance(valor, (int, float)) or isinstance(valor, bool):
        return False
    try:
        return math.isfinite(valor)
    except OverflowError:
        return False


def _es_numero_positivo(valor: object) -> bool:
    return _es_numero_finito(valor) and valor > 0


class Servicio(Entidad):
    def __init__(self, nombre: str, tarifa_base: float, disponible: bool = True) -> None:
        super().__init__()
        self._nombre = nombre.strip() if isinstance(nombre, str) else nombre
        self._tarifa_base = tarifa_base
        self._disponible = disponible
        self.validar()

    @property
    def nombre(self) -> str:
        return self._nombre

    @property
    def tarifa_base(self) -> float:
        return float(self._tarifa_base)

    @property
    def disponible(self) -> bool:
        return self._disponible

    def establecer_disponibilidad(self, disponible: bool) -> None:
        if not isinstance(disponible, bool):
            raise ValidacionError("La disponibilidad debe ser booleana.")
        self._disponible = disponible

    def validar(self) -> None:
        if not isinstance(self._nombre, str) or not self._nombre:
            raise ValidacionError("El servicio debe tener un nombre.")
        if not _es_numero_positivo(self._tarifa_base):
            raise ValidacionError("La tarifa base debe ser un número positivo y finito.")
        if not isinstance(self._disponible, bool):
            raise ValidacionError("La disponibilidad debe ser booleana.")

    def validar_parametros(self, **parametros: object) -> None:
        if not self._disponible:
            raise ServicioNoDisponibleError(
                f"El servicio '{self.nombre}' no está disponible."
            )
        self._validar_parametros(**parametros)

    @abstractmethod
    def _validar_parametros(self, **parametros: object) -> None:
        raise NotImplementedError

    @abstractmethod
    def _calcular_costo_base(
        self, duracion: float, parametros: Mapping[str, object]
    ) -> float:
        raise NotImplementedError

    @abstractmethod
    def describir(self) -> str:
        raise NotImplementedError

    @overload
    def calcular_costo(
        self, duracion: float, *, parametros: Mapping[str, object] | None = None
    ) -> float: ...

    @overload
    def calcular_costo(
        self,
        duracion: float,
        *,
        tasa_impuesto: float,
        parametros: Mapping[str, object] | None = None,
    ) -> float: ...

    @overload
    def calcular_costo(
        self,
        duracion: float,
        *,
        descuento: float,
        tasa_impuesto: float = 0.0,
        parametros: Mapping[str, object] | None = None,
    ) -> float: ...

    def calcular_costo(
        self,
        duracion: float,
        *,
        tasa_impuesto: float = 0.0,
        descuento: float = 0.0,
        parametros: Mapping[str, object] | None = None,
    ) -> float:
        opciones = dict(parametros or {})
        self.validar_parametros(**opciones)
        if not _es_numero_positivo(duracion):
            raise ValidacionError("La duración debe ser un número positivo y finito.")
        if (
            not _es_numero_finito(tasa_impuesto)
            or not 0 <= tasa_impuesto <= 1
        ):
            raise ValidacionError("La tasa de impuesto debe estar entre 0 y 1.")
        if (
            not _es_numero_finito(descuento)
            or not 0 <= descuento <= 1
        ):
            raise ValidacionError("El descuento debe estar entre 0 y 1.")

        try:
            costo_base = self._calcular_costo_base(float(duracion), opciones)
            total = costo_base * (1 - descuento) * (1 + tasa_impuesto)
            if not math.isfinite(total) or total < 0:
                raise CalculoError("El costo resultante no es finito ni válido.")
        except (OverflowError, TypeError, ValueError) as error:
            raise CalculoError("No fue posible calcular el costo del servicio.") from error
        return round(total, 2)


class SalaReuniones(Servicio):
    def __init__(
        self, nombre: str, tarifa_hora: float, capacidad_maxima: int, disponible: bool = True
    ) -> None:
        self._capacidad_maxima = capacidad_maxima
        super().__init__(nombre, tarifa_hora, disponible)
        if (
            not isinstance(capacidad_maxima, int)
            or isinstance(capacidad_maxima, bool)
            or capacidad_maxima <= 0
        ):
            raise ValidacionError("La capacidad máxima debe ser un entero positivo.")

    def _validar_parametros(self, **parametros: object) -> None:
        desconocidos = parametros.keys() - {"personas"}
        if desconocidos:
            raise ValidacionError(f"Parámetros no reconocidos: {sorted(desconocidos)}.")
        if "personas" not in parametros:
            raise ParametroFaltanteError("Debe indicar la cantidad de personas.")
        personas = parametros["personas"]
        if not isinstance(personas, int) or isinstance(personas, bool) or personas <= 0:
            raise ValidacionError("La cantidad de personas debe ser un entero positivo.")
        if personas > self._capacidad_maxima:
            raise ValidacionError(
                f"La sala admite como máximo {self._capacidad_maxima} personas."
            )

    def _calcular_costo_base(
        self, duracion: float, parametros: Mapping[str, object]
    ) -> float:
        return self.tarifa_base * duracion

    def describir(self) -> str:
        return (
            f"Sala de reuniones '{self.nombre}', capacidad "
            f"{self._capacidad_maxima} personas, tarifa por hora "
            f"{self.tarifa_base:.2f}."
        )


class AlquilerEquipo(Servicio):
    def __init__(
        self,
        nombre: str,
        tarifa_diaria: float,
        tipo_equipo: str,
        unidades_disponibles: int,
        disponible: bool = True,
    ) -> None:
        self._tipo_equipo = tipo_equipo.strip() if isinstance(tipo_equipo, str) else tipo_equipo
        self._unidades_disponibles = unidades_disponibles
        super().__init__(nombre, tarifa_diaria, disponible)
        if not isinstance(self._tipo_equipo, str) or not self._tipo_equipo:
            raise ValidacionError("Debe especificar el tipo de equipo.")
        if (
            not isinstance(unidades_disponibles, int)
            or isinstance(unidades_disponibles, bool)
            or unidades_disponibles <= 0
        ):
            raise ValidacionError("Las unidades disponibles deben ser un entero positivo.")

    def _validar_parametros(self, **parametros: object) -> None:
        desconocidos = parametros.keys() - {"unidades"}
        if desconocidos:
            raise ValidacionError(f"Parámetros no reconocidos: {sorted(desconocidos)}.")
        if "unidades" not in parametros:
            raise ParametroFaltanteError("Debe indicar la cantidad de equipos.")
        unidades = parametros["unidades"]
        if not isinstance(unidades, int) or isinstance(unidades, bool) or unidades <= 0:
            raise ValidacionError("La cantidad de equipos debe ser un entero positivo.")
        if unidades > self._unidades_disponibles:
            raise ServicioNoDisponibleError(
                f"Solo hay {self._unidades_disponibles} unidades disponibles."
            )

    def _calcular_costo_base(
        self, duracion: float, parametros: Mapping[str, object]
    ) -> float:
        return self.tarifa_base * duracion * int(parametros["unidades"])

    def describir(self) -> str:
        return (
            f"Alquiler de {self._tipo_equipo}: {self._unidades_disponibles} unidades "
            f"disponibles, tarifa diaria {self.tarifa_base:.2f}."
        )


class AsesoriaEspecializada(Servicio):
    def __init__(
        self, nombre: str, tarifa_hora: float, especialidad: str, disponible: bool = True
    ) -> None:
        self._especialidad = especialidad.strip() if isinstance(especialidad, str) else especialidad
        super().__init__(nombre, tarifa_hora, disponible)
        if not isinstance(self._especialidad, str) or not self._especialidad:
            raise ValidacionError("Debe especificar la especialidad de la asesoría.")

    def _validar_parametros(self, **parametros: object) -> None:
        desconocidos = parametros.keys() - {"sesiones"}
        if desconocidos:
            raise ValidacionError(f"Parámetros no reconocidos: {sorted(desconocidos)}.")
        if "sesiones" not in parametros:
            raise ParametroFaltanteError("Debe indicar la cantidad de sesiones.")
        sesiones = parametros["sesiones"]
        if not isinstance(sesiones, int) or isinstance(sesiones, bool) or sesiones <= 0:
            raise ValidacionError("La cantidad de sesiones debe ser un entero positivo.")

    def _calcular_costo_base(
        self, duracion: float, parametros: Mapping[str, object]
    ) -> float:
        return self.tarifa_base * duracion * int(parametros["sesiones"])

    def describir(self) -> str:
        return (
            f"Asesoría especializada en {self._especialidad}, "
            f"tarifa por hora {self.tarifa_base:.2f}."
        )
