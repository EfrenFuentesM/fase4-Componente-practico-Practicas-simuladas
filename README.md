# Software FJ - Sistema de Gestión Integral

Este proyecto es un sistema integral de gestión orientado a objetos para la empresa **Software FJ**, desarrollado completamente en Python puro. El sistema permite gestionar **clientes, servicios y reservas** de forma estable, modular y extensible. 

Destaca por no utilizar bases de datos, manteniendo la información en memoria mediante listas y objetos, y enfocándose en una implementación rigurosa de los principios de Programación Orientada a Objetos (POO) y el manejo avanzado de excepciones.

## Características Principales

*   **Arquitectura Orientada a Objetos:** Implementación completa de abstracción, herencia, polimorfismo, encapsulación y sobrecarga.
*   **Gestión de Clientes:** Registro de clientes con validaciones robustas (nombres, correos, teléfonos) y clasificación (regular, premium, corporativo).
*   **Catálogo de Servicios:** Soporte para múltiples tipos de servicios heredados de una clase base abstracta:
    *   🏢 *Reserva de Salas:* Control de aforo, proyector y videoconferencia.
    *   💻 *Alquiler de Equipos:* Gestión de stock, depósitos y seguros.
    *   🎓 *Asesorías Especializadas:* Especialidades, niveles de experto (junior, senior, experto) y modalidades.
*   **Gestor de Reservas:** Ciclo de vida completo de las reservas (Pendiente, Confirmada, Cancelada, Completada, Rechazada) con cálculo dinámico de costos, aplicación de impuestos, descuentos por tipo de cliente y validación de disponibilidad.
*   **Manejo Avanzado de Excepciones:** Jerarquía de excepciones personalizadas (`SoftwareFJError`) para capturar y gestionar errores sin que el sistema colapse (ej. `ClienteInvalidoError`, `ReservaInvalidaError`, `ServicioNoDisponibleError`).
*   **Sistema de Logging (Registro):** Registro automático de todas las operaciones, eventos y errores en un archivo de log diario, implementado con el patrón Singleton.
*   **Interfaz Gráfica Moderna (GUI):** Interfaz construida con Tkinter, con un diseño oscuro profesional tipo panel de control (Dashboard), navegación lateral y vistas completas para cada módulo.

## Estructura del Proyecto

```text
Proyecto/
├── main.py                          # Script principal de simulación (CLI)
├── gui_main.py                      # Script de arranque de la Interfaz Gráfica (GUI)
├── logs/
│   └── sistema_YYYYMMDD.log         # Archivos de registro generados automáticamente
└── software_fj/
    ├── __init__.py
    ├── excepciones.py               # Definición de excepciones personalizadas
    ├── logger.py                    # Sistema de logging a archivo (Singleton)
    ├── entidad.py                   # Clase abstracta base
    ├── cliente.py                   # Clase Cliente con validaciones
    ├── servicio.py                  # Clase abstracta Servicio
    ├── reserva.py                   # Clase Reserva integradora
    ├── gestor.py                    # Controlador principal del sistema
    ├── servicios/                   # Subpaquete de servicios específicos
    │   ├── reserva_sala.py
    │   ├── alquiler_equipo.py
    │   └── asesoria.py
    └── gui/                         # Subpaquete de la Interfaz Gráfica
        ├── app.py                   # Ventana principal
        ├── estilos.py               # Configuración de temas y estilos visuales
        ├── dashboard.py             # Vista de resumen
        ├── vista_clientes.py        # Módulo visual de clientes
        ├── vista_servicios.py       # Módulo visual de servicios
        ├── vista_reservas.py        # Módulo visual de reservas
        └── vista_logs.py            # Visor integrado de logs
```

## Requisitos

*   Python 3.8 o superior.
*   Librerías estándar de Python (no requiere instalaciones externas como `pip install`).

## Cómo Ejecutar

El proyecto cuenta con dos modos de ejecución:

### 1. Interfaz Gráfica de Usuario (GUI)

Para interactuar visualmente con el sistema, gestionar entidades de forma gráfica y ver los registros en tiempo real:

```bash
python gui_main.py
```
*(Nota: Para evitar problemas de codificación de caracteres en consolas Windows antiguas, se recomienda usar `python -X utf8 gui_main.py`)*

### 2. Simulación en Consola (CLI)

Para ejecutar una demostración automatizada que simula más de 10 escenarios (incluyendo casos válidos e inválidos para demostrar el manejo de excepciones):

```bash
python main.py
```
*(Igualmente, se recomienda `python -X utf8 main.py` en Windows)*

## Principios POO Aplicados

*   **Abstracción:** Uso del módulo `abc` para definir contratos base en las clases `Entidad` y `Servicio`.
*   **Herencia:** Jerarquía clara donde componentes específicos extienden funcionalidades de clases base.
*   **Polimorfismo:** Métodos como `calcular_costo()` se comportan de manera distinta dependiendo si es una Sala, un Equipo o una Asesoría.
*   **Encapsulación:** Atributos privados (prefijo `_`) con propiedades (`@property` y setters) para validar cada cambio de estado.
*   **Sobrecarga (simulada en Python):** Múltiples variantes funcionales (ej. `calcular_costo_con_impuesto()`, `calcular_costo_con_descuento()`) manejando argumentos opcionales y `**kwargs`.

## Autor

Desarrollado para el componente práctico de Arquitectura de Software / POO.
