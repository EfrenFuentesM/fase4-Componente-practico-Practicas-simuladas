"""
app.py - Orquestador principal de la interfaz gráfica de Software FJ.

Este archivo contiene la clase SoftwareFJApp, la cual gestiona la ventana principal,
la navegación entre diferentes vistas (Dashboard, Clientes, etc.) y la integración
con la lógica de negocio a través del objeto GestorSistema.
"""
import tkinter as tk
from tkinter import messagebox
from datetime import date

from software_fj.gestor import GestorSistema
from software_fj.gui.estilos import C, F, aplicar_estilos
from software_fj.gui.dashboard import Dashboard
from software_fj.gui.vista_clientes import VistaClientes
from software_fj.gui.vista_servicios import VistaServicios
from software_fj.gui.vista_reservas import VistaReservas
from software_fj.gui.vista_logs import VistaLogs


class SoftwareFJApp(tk.Tk):
    """
    Clase principal que hereda de tk.Tk para construir la ventana de la aplicación.
    Implementa un sistema de navegación por pestañas personalizadas y manejo de estados.
    """

    # Configuración de los botones de la barra lateral (ID, Texto)
    _NAV = [
        ("dashboard", "🏠  Dashboard"),
        ("clientes",  "👥  Clientes"),
        ("servicios", "🛠  Servicios"),
        ("reservas",  "📅  Reservas"),
        ("logs",      "📋  Registros"),
    ]

    def __init__(self):
        super().__init__()

        # ── Configuración General de la Ventana ──────────────────────────────
        self.title("Software FJ — Sistema de Gestión Integral")
        self.geometry("1280x780")
        self.minsize(1024, 680)
        self.configure(bg=C["bg"])
        self.protocol("WM_DELETE_WINDOW", self._salir)

        # Intento de cargar el ícono de la aplicación
        try:
            self.iconbitmap(default="")
        except Exception:
            pass

        # ── Inicialización del Motor del Sistema (Backend) ───────────────────
        # Se instancia el gestor que manejará la persistencia y lógica de datos.
        self.gestor = GestorSistema(directorio_logs="logs")
        self._cargar_datos_iniciales()

        # ── Aplicación del Sistema de Estilos ────────────────────────────────
        aplicar_estilos(self)

        # ── Estructura de la Interfaz de Usuario ──────────────────────────────
        self._nav_btns: dict[str, tk.Button] = {} # Registro de botones de navegación
        self._vistas:   dict[str, tk.Frame]  = {} # Diccionario de marcos de vista
        self._vista_actual = ""

        self._crear_sidebar()    # Panel lateral izquierdo
        self._crear_contenido()  # Área central para las vistas
        self._crear_status_bar() # Barra de estado inferior

        # Navegar automáticamente a la pantalla de inicio
        self._navegar("dashboard")

    # ── Gestión de Datos ─────────────────────────────────────────────────────

    def _cargar_datos_iniciales(self):
        """
        Carga una serie de servicios predefinidos para facilitar la demostración
        y pruebas del sistema.
        """
        from software_fj.servicios import (
            ReservaSala, AlquilerEquipo, AsesoriaEspecializada)

        servicios = [
            ReservaSala("SRV-S01", "Sala Ejecutiva A",
                        capacidad=10, precio_base=150.0,
                        tiene_proyector=True, tiene_videoconferencia=True),
            ReservaSala("SRV-S02", "Sala de Capacitación",
                        capacidad=30, precio_base=200.0,
                        tiene_proyector=True, tiene_videoconferencia=False),
            AlquilerEquipo("SRV-E01", "Laptop Dell XPS 15",
                           tipo_equipo="laptop", precio_base_dia=80.0,
                           unidades_disponibles=5, requiere_deposito=True,
                           monto_deposito=500.0, costo_seguro_dia=15.0),
            AlquilerEquipo("SRV-E02", "Servidor HP ProLiant",
                           tipo_equipo="servidor", precio_base_dia=250.0,
                           unidades_disponibles=2, requiere_deposito=True,
                           monto_deposito=2000.0),
            AsesoriaEspecializada("SRV-A01", "Asesoría en Ciberseguridad",
                                  especialidad="Ciberseguridad",
                                  precio_base=300.0, nivel_experto="experto",
                                  modalidad="remota"),
            AsesoriaEspecializada("SRV-A02", "Asesoría Legal Empresarial",
                                  especialidad="Derecho Corporativo",
                                  precio_base=250.0, nivel_experto="senior",
                                  modalidad="presencial"),
        ]
        for srv in servicios:
            try:
                self.gestor.agregar_servicio(srv)
            except Exception:
                # Si el servicio ya existe en el gestor, se ignora el error
                pass

    # ── Construcción de la Barra Lateral (Sidebar) ───────────────────────────

    def _crear_sidebar(self):
        """Construye el panel de navegación lateral."""
        sidebar = tk.Frame(self, bg=C["sidebar"], width=230)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        # Sección del Logotipo
        logo_frame = tk.Frame(sidebar, bg=C["sidebar"], height=80)
        logo_frame.pack(fill="x", padx=16)
        logo_frame.pack_propagate(False)
        
        logo_container = tk.Frame(logo_frame, bg=C["sidebar"])
        logo_container.place(relx=0, rely=0.5, anchor="w")
        
        tk.Label(logo_container, text="⚙", bg=C["sidebar"],
                 fg=C["accent"], font=("Segoe UI", 24)).pack(side="left")
        tk.Label(logo_container, text="Software FJ", bg=C["sidebar"],
                 fg=C["text"], font=F["logo"]).pack(side="left", padx=(10, 0), pady=(3, 0))
        tk.Frame(sidebar, bg=C["border"], height=1).pack(fill="x")

        # Espaciador
        tk.Frame(sidebar, bg=C["sidebar"], height=12).pack()

        # Generación dinámica de botones de menú
        for key, label in self._NAV:
            btn_frame = tk.Frame(sidebar, bg=C["sidebar"])
            btn_frame.pack(fill="x", padx=8, pady=2)

            btn = tk.Button(
                btn_frame,
                text=label,
                command=lambda k=key: self._navegar(k),
                bg=C["sidebar"],
                fg=C["text2"],
                activebackground=C["btn_primary"],
                activeforeground=C["text"],
                font=F["sidebar"],
                relief="flat", bd=0,
                anchor="w",
                padx=14, pady=10,
                cursor="hand2",
            )
            btn.pack(fill="x")
            # Enlazar eventos de mouse para efectos visuales
            btn.bind("<Enter>", lambda e, b=btn, k=key: self._hover_on(b, k))
            btn.bind("<Leave>", lambda e, b=btn, k=key: self._hover_off(b, k))
            self._nav_btns[key] = btn

        # Espacio flexible y pie de la barra lateral
        tk.Frame(sidebar, bg=C["sidebar"]).pack(fill="both", expand=True)
        tk.Frame(sidebar, bg=C["border"], height=1).pack(fill="x")
        tk.Label(sidebar, text="v1.0 • Software FJ",
                 bg=C["sidebar"], fg=C["text2"],
                 font=F["small"]).pack(pady=10)

    def _hover_on(self, btn: tk.Button, key: str):
        """Resalta el botón si no es el seleccionado actualmente."""
        if key != self._vista_actual:
            btn.config(bg=C["panel"], fg=C["text"])

    def _hover_off(self, btn: tk.Button, key: str):
        """Restaura el estilo original del botón."""
        if key != self._vista_actual:
            btn.config(bg=C["sidebar"], fg=C["text2"])

    # ── Gestión de Contenido y Vistas ────────────────────────────────────────

    def _crear_contenido(self):
        """Instancia y posiciona todas las vistas del sistema en el contenedor central."""
        contenedor = tk.Frame(self, bg=C["bg"])
        contenedor.pack(side="left", fill="both", expand=True)

        # Argumentos comunes para todas las vistas
        kwargs = dict(gestor=self.gestor,
                      actualizar_status=self.actualizar_status)

        # Mapeo de identificadores a clases de vista
        vistas_cls = {
            "dashboard": Dashboard,
            "clientes":  VistaClientes,
            "servicios": VistaServicios,
            "reservas":  VistaReservas,
            "logs":      VistaLogs,
        }
        for key, Cls in vistas_cls.items():
            vista = Cls(contenedor, **kwargs)
            # Todas las vistas ocupan el mismo espacio (sistema de capas)
            vista.place(relx=0, rely=0, relwidth=1, relheight=1)
            self._vistas[key] = vista

    # ── Barra de Estado (Status Bar) ─────────────────────────────────────────

    def _crear_status_bar(self):
        """Crea la barra inferior que muestra mensajes del sistema y la fecha."""
        bar = tk.Frame(self, bg=C["card"], height=28)
        bar.pack(side="bottom", fill="x")
        bar.pack_propagate(False)

        self._status_lbl = tk.Label(
            bar, text="Sistema listo.",
            bg=C["card"], fg=C["text2"],
            font=F["small"], anchor="w",
        )
        self._status_lbl.pack(side="left", padx=12, fill="y")

        tk.Label(bar,
                 text=f"📅 {date.today().strftime('%d/%m/%Y')}",
                 bg=C["card"], fg=C["text2"],
                 font=F["small"]).pack(side="right", padx=12)

    def actualizar_status(self, mensaje: str, tipo: str = "ok"):
        """
        Muestra un mensaje temporal en la barra de estado con un color indicativo.
        
        Args:
            mensaje: El texto a mostrar.
            tipo: 'ok', 'error', 'warn' o 'info'.
        """
        colores = {
            "ok":    C["text2"],
            "error": C["error"],
            "warn":  C["warning"],
            "info":  C["accent"],
        }
        color = colores.get(tipo, C["text2"])
        self._status_lbl.config(text=f"  {mensaje}", fg=color)
        
        # Restaurar mensaje neutral tras 5 segundos
        self.after(5000, lambda: self._status_lbl.config(
            text="  Sistema listo.", fg=C["text2"]))

    # ── Lógica de Navegación ─────────────────────────────────────────────────

    def _navegar(self, vista: str):
        """
        Cambia la vista visible y actualiza el resaltado en el sidebar.
        """
        # Actualizar el aspecto de los botones de navegación
        for key, btn in self._nav_btns.items():
            if key == vista:
                btn.config(bg=C["btn_primary"], fg=C["text"])
            else:
                btn.config(bg=C["sidebar"], fg=C["text2"])

        # Traer la vista al frente (sistema de capas de Tkinter)
        self._vistas[vista].tkraise()
        self._vista_actual = vista

        # Ejecutar refresco de datos si la vista lo soporta
        v = self._vistas[vista]
        if hasattr(v, "refrescar"):
            try:
                v.refrescar()
            except Exception:
                pass

    # ── Eventos de Salida ────────────────────────────────────────────────────

    def _salir(self):
        """Muestra una confirmación antes de cerrar la aplicación."""
        if messagebox.askokcancel("Salir",
                                  "¿Deseas cerrar Software FJ?",
                                  parent=self):
            self.destroy()
