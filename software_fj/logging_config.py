import logging
from pathlib import Path


def configurar_logging(archivo: str | Path | None = None) -> logging.Logger:
    logger = logging.getLogger("software_fj")
    logger.setLevel(logging.INFO)
    logger.propagate = False

    if not logger.handlers:
        ruta = Path(archivo) if archivo is not None else (
            Path(__file__).resolve().parent.parent / "logs" / "software_fj.log"
        )
        ruta.parent.mkdir(parents=True, exist_ok=True)
        manejador = logging.FileHandler(ruta, encoding="utf-8")
        manejador.setFormatter(
            logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
        )
        logger.addHandler(manejador)

    return logger
