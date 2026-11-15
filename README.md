# Sistema de gestión Software FJ

Aplicación de consola orientada a objetos para gestionar clientes, servicios y
reservas en memoria. No utiliza bases de datos ni dependencias externas. Los
eventos y errores se registran en `logs/software_fj.log`.

## Requisitos

- Python 3.10 o posterior

## Ejecutar la demostración

Desde la raíz del proyecto:

```powershell
python main.py
```

La demostración ejecuta operaciones válidas e inválidas y continúa después de
los errores controlados. Los errores inesperados también se registran con su
traza antes de continuar con la siguiente operación.

## Ejecutar pruebas

```powershell
python -m unittest discover -s tests -v
```

## Diseño

- `Entidad` define la abstracción común para clientes, servicios y reservas.
- `Servicio` es abstracta; sus implementaciones incluyen salas, alquiler de
  equipos y asesorías.
- `Cliente` encapsula y valida sus datos personales.
- `Reserva` controla transiciones de estado, confirmación, cancelación y
  procesamiento.
- `SistemaGestion` mantiene las colecciones en memoria y ofrece operaciones de
  registro y búsqueda.
- Las excepciones del dominio se registran en el log. La confirmación y el
  procesamiento demuestran bloques `try/except/else/finally` y encadenamiento
  de excepciones.
- `Servicio.calcular_costo` admite variantes de cálculo con impuesto,
  descuento y parámetros opcionales; las declaraciones `@overload` documentan
  las firmas para herramientas de tipos.