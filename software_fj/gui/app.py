"""app.py - Ventana principal de la aplicación Software FJ"""
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
    """Ventana principal del sistema Software FJ."""

    _NAV = [
        ("dashboard", "🏠  Dashboard"),
        ("clientes",  "👥  Clientes"),
        ("servicios", "🛠  Servicios"),
        ("reservas",  "📅  Reservas"),
        ("logs",      "📋  Registros"),
    ]

    def __init__(self):
        super().__init__()

        # ── Configuración de ventana ─────────────────────────────────────────
        self.title("Software FJ — Sistema de Gestión Integral")
        self.geometry("1280x780")
        self.minsize(1024, 680)
        self.configure(bg=C["bg"])
        self.protocol("WM_DELETE_WINDOW", self._salir)

        # Ícono (usa el ícono por defecto si no hay archivo)
        try:
            self.iconbitmap(default="")
        except Exception:
            pass

        # ── Backend ──────────────────────────────────────────────────────────
        self.gestor = GestorSistema(directorio_logs="logs")
        self._cargar_datos_iniciales()

        # ── Estilos ──────────────────────────────────────────────────────────
        aplicar_estilos(self)

        # ── Construir UI ─────────────────────────────────────────────────────
        self._nav_btns: dict[str, tk.Button] = {}
        self._vistas:   dict[str, tk.Frame]  = {}
        self._vista_actual = ""

        self._crear_sidebar()
        self._crear_contenido()
        self._crear_status_bar()

        # Arrancar en Dashboard
        self._navegar("dashboard")

    # ── Datos iniciales ───────────────────────────────────────────────────────

    def _cargar_datos_iniciales(self):
        """Pre-carga los 6 servicios de demostración."""
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
                pass  # Ya existe (re-ejecución)

    # ── Sidebar ───────────────────────────────────────────────────────────────

    def _crear_sidebar(self):
        sidebar = tk.Frame(self, bg=C["sidebar"], width=230)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        # Logo
        logo_frame = tk.Frame(sidebar, bg=C["sidebar"], height=80) # Altura ajustada
        logo_frame.pack(fill="x", padx=16)
        logo_frame.pack_propagate(False)
        
        # Ajuste: Contenedor para alinear icono y texto perfectamente
        logo_container = tk.Frame(logo_frame, bg=C["sidebar"])
        logo_container.place(relx=0, rely=0.5, anchor="w") # Centrado vertical relativo
        
        tk.Label(logo_container, text="⚙", bg=C["sidebar"],
                 fg=C["accent"], font=("Segoe UI", 24)).pack(side="left") # Icono ligeramente más grande
        tk.Label(logo_container, text="Software FJ", bg=C["sidebar"],
                 fg=C["text"], font=F["logo"]).pack(side="left", padx=(10, 0), pady=(3, 0)) # Ajuste fino vertical del texto
        tk.Frame(sidebar, bg=C["border"], height=1).pack(fill="x")

        # Espaciado
        tk.Frame(sidebar, bg=C["sidebar"], height=12).pack()

        # Botones de navegación
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
            btn.bind("<Enter>", lambda e, b=btn, k=key: self._hover_on(b, k))
            btn.bind("<Leave>", lambda e, b=btn, k=key: self._hover_off(b, k))
            self._nav_btns[key] = btn

        # Separador y versión en la parte inferior
        tk.Frame(sidebar, bg=C["sidebar"]).pack(fill="both", expand=True)
        tk.Frame(sidebar, bg=C["border"], height=1).pack(fill="x")
        tk.Label(sidebar, text="v1.0 • Software FJ",
                 bg=C["sidebar"], fg=C["text2"],
                 font=F["small"]).pack(pady=10)

    def _hover_on(self, btn: tk.Button, key: str):
        if key != self._vista_actual:
            btn.config(bg=C["panel"], fg=C["text"])

    def _hover_off(self, btn: tk.Button, key: str):
        if key != self._vista_actual:
            btn.config(bg=C["sidebar"], fg=C["text2"])

    # ── Área de contenido ─────────────────────────────────────────────────────

    def _crear_contenido(self):
        contenedor = tk.Frame(self, bg=C["bg"])
        contenedor.pack(side="left", fill="both", expand=True)

        kwargs = dict(gestor=self.gestor,
                      actualizar_status=self.actualizar_status)

        vistas_cls = {
            "dashboard": Dashboard,
            "clientes":  VistaClientes,
            "servicios": VistaServicios,
            "reservas":  VistaReservas,
            "logs":      VistaLogs,
        }
        for key, Cls in vistas_cls.items():
            vista = Cls(contenedor, **kwargs)
            vista.place(relx=0, rely=0, relwidth=1, relheight=1)
            self._vistas[key] = vista

    # ── Barra de estado ───────────────────────────────────────────────────────

    def _crear_status_bar(self):
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
        colores = {
            "ok":    C["text2"],
            "error": C["error"],
            "warn":  C["warning"],
            "info":  C["accent"],
        }
        color = colores.get(tipo, C["text2"])
        self._status_lbl.config(text=f"  {mensaje}", fg=color)
        # Resetea al color neutral después de 5 segundos
        self.after(5000, lambda: self._status_lbl.config(
            text="  Sistema listo.", fg=C["text2"]))

    # ── Navegación ────────────────────────────────────────────────────────────

    def _navegar(self, vista: str):
        # Actualizar botones del sidebar
        for key, btn in self._nav_btns.items():
            if key == vista:
                btn.config(bg=C["btn_primary"], fg=C["text"])
            else:
                btn.config(bg=C["sidebar"], fg=C["text2"])

        # Mostrar la vista seleccionada
        self._vistas[vista].tkraise()
        self._vista_actual = vista

        # Refrescar datos de la vista
        v = self._vistas[vista]
        if hasattr(v, "refrescar"):
            try:
                v.refrescar()
            except Exception:
                pass

    # ── Cierre ────────────────────────────────────────────────────────────────

    def _salir(self):
        if messagebox.askokcancel("Salir",
                                  "¿Deseas cerrar Software FJ?",
                                  parent=self):
            self.destroy()
