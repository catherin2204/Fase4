import re
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from uuid import uuid4

from software_fj.exceptions import ValidacionError


class Entidad(ABC):
    def __init__(self) -> None:
        self._id = str(uuid4())
        self._creado_en = datetime.now(timezone.utc)

    @property
    def id(self) -> str:
        return self._id

    @property
    def creado_en(self) -> datetime:
        return self._creado_en

    @abstractmethod
    def validar(self) -> None:
        raise NotImplementedError


class Cliente(Entidad):
    def __init__(self, nombre: str, correo: str, telefono: str) -> None:
        super().__init__()
        self._nombre = nombre.strip() if isinstance(nombre, str) else nombre
        self._correo = correo.strip().lower() if isinstance(correo, str) else correo
        self._telefono = telefono.strip() if isinstance(telefono, str) else telefono
        self.validar()

    @property
    def nombre(self) -> str:
        return self._nombre

    @property
    def correo(self) -> str:
        return self._correo

    @property
    def telefono(self) -> str:
        return self._telefono

    def validar(self) -> None:
        if not isinstance(self._nombre, str) or len(self._nombre) < 2:
            raise ValidacionError("El nombre debe contener al menos 2 caracteres.")
        if not isinstance(self._correo, str) or not re.fullmatch(
            r"[^@\s]+@[^@\s]+\.[^@\s]+", self._correo
        ):
            raise ValidacionError("El correo electrónico no tiene un formato válido.")
        if not isinstance(self._telefono, str) or not re.fullmatch(
            r"\+?[0-9][0-9\s()-]{6,19}", self._telefono
        ):
            raise ValidacionError("El teléfono no tiene un formato válido.")
