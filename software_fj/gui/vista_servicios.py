"""vista_servicios.py - Catálogo de Servicios"""
import tkinter as tk
from tkinter import messagebox
from software_fj.gui.estilos import C, F, btn, btn_refresh
from software_fj.servicios import ReservaSala, AlquilerEquipo, AsesoriaEspecializada


class VistaServicios(tk.Frame):
    def __init__(self, parent, gestor, actualizar_status, **kwargs):
        super().__init__(parent, bg=C["bg"], **kwargs)
        self.gestor = gestor
        self.actualizar_status = actualizar_status
        self._construir()

    def _construir(self):
        # Encabezado
        hdr = tk.Frame(self, bg=C["bg"])
        hdr.pack(fill="x", padx=24, pady=(24, 0))
        tk.Label(hdr, text="Catálogo de Servicios", bg=C["bg"],
                 fg=C["text"], font=F["title"]).pack(side="left")
        btn_refresh(hdr, self.refrescar).pack(side="right")


        # Leyenda tipos
        ley = tk.Frame(self, bg=C["bg"])
        ley.pack(fill="x", padx=24, pady=(8, 4))
        leyenda = [
            ("🏢 Sala",     C["accent"]),
            ("💻 Equipo",   C["warning"]),
            ("🎓 Asesoría", "#c084fc"),
        ]
        for txt, color in leyenda:
            tk.Label(ley, text=txt, bg=C["bg"], fg=color,
                     font=F["small"]).pack(side="left", padx=8)

        # Contenedor scrollable
        canvas = tk.Canvas(self, bg=C["bg"], highlightthickness=0)
        sb = tk.Scrollbar(self, orient="vertical",
                          command=canvas.yview)
        canvas.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        canvas.pack(fill="both", expand=True, padx=(24, 0), pady=(8, 16))

        self._scroll_frame = tk.Frame(canvas, bg=C["bg"])
        self._scroll_win = canvas.create_window(
            (0, 0), window=self._scroll_frame, anchor="nw")

        self._scroll_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>",
                    lambda e: canvas.itemconfig(
                        self._scroll_win, width=e.width))
        canvas.bind_all("<MouseWheel>",
                        lambda e: canvas.yview_scroll(
                            int(-1 * (e.delta / 120)), "units"))
        self._canvas = canvas

    def refrescar(self):
        for w in self._scroll_frame.winfo_children():
            w.destroy()

        servicios = self.gestor.listar_servicios()
        if not servicios:
            tk.Label(self._scroll_frame,
                     text="No hay servicios en el catálogo.",
                     bg=C["bg"], fg=C["text2"],
                     font=F["body"]).pack(pady=40)
            return

        # Grid de tarjetas: 2 columnas
        grid = tk.Frame(self._scroll_frame, bg=C["bg"])
        grid.pack(fill="both", padx=4)
        grid.columnconfigure(0, weight=1)
        grid.columnconfigure(1, weight=1)

        for idx, srv in enumerate(servicios):
            row, col = divmod(idx, 2)
            self._crear_tarjeta(grid, srv, row, col)

        self.actualizar_status(
            f"{len(servicios)} servicio(s) en catálogo.", "ok")

    def _crear_tarjeta(self, parent, srv, row, col):
        # Color del tipo
        if isinstance(srv, ReservaSala):
            color = C["accent"]
            tipo  = "🏢 Sala de Reunión"
        elif isinstance(srv, AlquilerEquipo):
            color = C["warning"]
            tipo  = "💻 Alquiler de Equipo"
        else:
            color = "#c084fc"
            tipo  = "🎓 Asesoría Especializada"

        estado_color = C["success"] if srv.disponible else C["error"]
        estado_txt   = "● Disponible" if srv.disponible else "● No disponible"

        # Marco de tarjeta
        card = tk.Frame(parent, bg=C["card"],
                        padx=16, pady=14, relief="flat")
        card.grid(row=row, column=col, padx=8, pady=8, sticky="nsew")

        # Barra superior de color
        tk.Frame(card, bg=color, height=3).pack(fill="x", pady=(0, 10))

        # Tipo y estado en la misma fila
        top_row = tk.Frame(card, bg=C["card"])
        top_row.pack(fill="x")
        tk.Label(top_row, text=tipo, bg=C["card"],
                 fg=color, font=F["small"]).pack(side="left")
        tk.Label(top_row, text=estado_txt, bg=C["card"],
                 fg=estado_color, font=F["small"]).pack(side="right")

        # Nombre del servicio
        tk.Label(card, text=srv.nombre, bg=C["card"],
                 fg=C["text"], font=F["heading"],
                 wraplength=300, justify="left").pack(anchor="w", pady=(4, 8))

        # Descripción
        desc = srv.descripcion[:120] + "..." \
            if len(srv.descripcion) > 120 else srv.descripcion
        tk.Label(card, text=desc, bg=C["card"],
                 fg=C["text2"], font=F["small"],
                 wraplength=300, justify="left").pack(anchor="w")

        tk.Frame(card, bg=C["border"], height=1).pack(fill="x", pady=10)

        # Info específica por tipo
        info_frame = tk.Frame(card, bg=C["card"])
        info_frame.pack(fill="x")

        detalles = self._obtener_detalles(srv)
        for i, (campo, valor) in enumerate(detalles):
            col_f = tk.Frame(info_frame, bg=C["card"])
            col_f.grid(row=0, column=i, padx=(0, 16), sticky="w")
            tk.Label(col_f, text=campo, bg=C["card"],
                     fg=C["text2"], font=("Segoe UI", 8)).pack(anchor="w")
            tk.Label(col_f, text=valor, bg=C["card"],
                     fg=C["text"], font=F["body_b"]).pack(anchor="w")

        # Botón toggle disponibilidad
        accion_txt = "Desactivar" if srv.disponible else "Activar"
        accion_col = "btn_danger"  if srv.disponible else "btn_success"
        btn_toggle = btn(card, accion_txt,
                         lambda s=srv: self._toggle_disponible(s),
                         accion_col)
        btn_toggle.pack(anchor="e", pady=(10, 0))

    def _obtener_detalles(self, srv):
        if isinstance(srv, ReservaSala):
            eq = []
            if srv.tiene_proyector:        eq.append("Proyector")
            if srv.tiene_videoconferencia: eq.append("VC")
            return [
                ("Precio/hora",  f"${srv.precio_base:.2f}"),
                ("Capacidad",    f"{srv.capacidad} personas"),
                ("Equipamiento", ", ".join(eq) if eq else "Básica"),
            ]
        elif isinstance(srv, AlquilerEquipo):
            return [
                ("Precio/día",  f"${srv.precio_base:.2f}"),
                ("Tipo",         srv.tipo_equipo.capitalize()),
                ("Stock",        f"{srv.unidades_disponibles} uds."),
            ]
        else:  # Asesoría
            return [
                ("Tarifa/hora",  f"${srv.tarifa_efectiva:.2f}"),
                ("Nivel",        srv.nivel_experto.capitalize()),
                ("Modalidad",    srv.modalidad.capitalize()),
            ]

    def _toggle_disponible(self, srv):
        nombre   = srv.nombre
        accion   = "desactivar" if srv.disponible else "activar"
        if messagebox.askyesno("Confirmar",
                               f"¿{accion.capitalize()} '{nombre}'?",
                               parent=self):
            srv.disponible = not srv.disponible
            estado = "activado" if srv.disponible else "desactivado"
            self.actualizar_status(
                f"Servicio '{nombre}' {estado}.", "ok")
            self.refrescar()
