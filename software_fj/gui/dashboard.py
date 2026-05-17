"""dashboard.py - Vista principal con estadísticas del sistema"""
import tkinter as tk
from software_fj.gui.estilos import C, F, card, label, btn_refresh
from software_fj.reserva import EstadoReserva


class Dashboard(tk.Frame):
    def __init__(self, parent, gestor, actualizar_status, **kwargs):
        super().__init__(parent, bg=C["bg"], **kwargs)
        self.gestor = gestor
        self.actualizar_status = actualizar_status
        self._construir()

    def _construir(self):
        # ── Encabezado ────────────────────────────────────────────────────────
        hdr = tk.Frame(self, bg=C["bg"])
        hdr.pack(fill="x", padx=24, pady=(24, 0))
        tk.Label(hdr, text="Dashboard", bg=C["bg"], fg=C["text"],
                 font=F["title"]).pack(side="left")
        btn_refresh(hdr, self.refrescar).pack(side="right")


        # ── Tarjetas de estadísticas ──────────────────────────────────────────
        self._stats_frame = tk.Frame(self, bg=C["bg"])
        self._stats_frame.pack(fill="x", padx=24, pady=16)

        self._stat_cards = {}
        stats_config = [
            ("clientes",  "Clientes",  C["accent"],   "👥"),
            ("servicios", "Servicios", C["warning"],  "🛠"),
            ("reservas",  "Reservas",  C["success"],  "📅"),
            ("ingresos",  "Ingresos",  "#c084fc",     "💰"),
        ]
        for i, (key, titulo, color, icono) in enumerate(stats_config):
            c_frame = tk.Frame(self._stats_frame, bg=C["card"],
                               width=220, height=110)
            c_frame.grid(row=0, column=i, padx=8, pady=4, sticky="nsew")
            c_frame.grid_propagate(False)
            self._stats_frame.columnconfigure(i, weight=1)

            tk.Label(c_frame, text=icono + "  " + titulo,
                     bg=C["card"], fg=C["text2"], font=F["small"]
                     ).place(x=12, y=12)
            val_lbl = tk.Label(c_frame, text="0",
                               bg=C["card"], fg=color, font=F["stat"])
            val_lbl.place(x=12, y=38)
            sub_lbl = tk.Label(c_frame, text="",
                               bg=C["card"], fg=C["text2"], font=F["small"])
            sub_lbl.place(x=12, y=82)
            # Barra de color inferior
            tk.Frame(c_frame, bg=color, height=3).place(
                x=0, rely=1.0, anchor="sw", relwidth=1.0)

            self._stat_cards[key] = (val_lbl, sub_lbl)

        # ── Reservas recientes ────────────────────────────────────────────────
        sec = tk.Frame(self, bg=C["bg"])
        sec.pack(fill="both", expand=True, padx=24, pady=(0, 24))

        tk.Label(sec, text="Reservas recientes", bg=C["bg"],
                 fg=C["text"], font=F["section"]).pack(anchor="w", pady=(0, 8))

        tabla_frame = tk.Frame(sec, bg=C["card"])
        tabla_frame.pack(fill="both", expand=True)

        from tkinter import ttk
        cols = ("id", "cliente", "servicio", "estado", "costo")
        self._tree = ttk.Treeview(tabla_frame, columns=cols,
                                   show="headings", style="Dark.Treeview",
                                   selectmode="browse")
        encabezados = {
            "id": ("ID Reserva", 110),
            "cliente": ("Cliente", 200),
            "servicio": ("Servicio", 220),
            "estado": ("Estado", 110),
            "costo": ("Costo", 100),
        }
        for col, (txt, w) in encabezados.items():
            self._tree.heading(col, text=txt)
            self._tree.column(col, width=w, anchor="w")

        sb = ttk.Scrollbar(tabla_frame, orient="vertical",
                           command=self._tree.yview,
                           style="Dark.Vertical.TScrollbar")
        self._tree.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        self._tree.pack(fill="both", expand=True)

        self._tree.tag_configure("CONFIRMADA",  foreground=C["success"])
        self._tree.tag_configure("COMPLETADA",  foreground=C["accent"])
        self._tree.tag_configure("CANCELADA",   foreground=C["error"])
        self._tree.tag_configure("RECHAZADA",   foreground=C["warning"])
        self._tree.tag_configure("PENDIENTE",   foreground=C["text2"])

    def refrescar(self):
        """Actualiza todas las estadísticas y la tabla."""
        clientes  = self.gestor.listar_clientes()
        servicios = self.gestor.listar_servicios()
        reservas  = self.gestor.listar_reservas()

        confirmadas = [r for r in reservas
                       if r.estado == EstadoReserva.CONFIRMADA]
        completadas = [r for r in reservas
                       if r.estado == EstadoReserva.COMPLETADA]
        ingresos = sum(r.costo_total for r in confirmadas + completadas)

        # Actualizar tarjetas
        self._stat_cards["clientes"][0].config(text=str(len(clientes)))
        self._stat_cards["clientes"][1].config(text="registrados")
        self._stat_cards["servicios"][0].config(text=str(len(servicios)))
        disp = sum(1 for s in servicios if s.disponible)
        self._stat_cards["servicios"][1].config(text=f"{disp} disponibles")
        self._stat_cards["reservas"][0].config(text=str(len(reservas)))
        self._stat_cards["reservas"][1].config(
            text=f"{len(confirmadas)} confirmadas")
        self._stat_cards["ingresos"][0].config(
            text=f"${ingresos:,.0f}")
        self._stat_cards["ingresos"][1].config(text="total generado")

        # Actualizar tabla
        for row in self._tree.get_children():
            self._tree.delete(row)

        for r in sorted(reservas,
                        key=lambda x: x.id, reverse=True)[:20]:
            estado = r.estado.value.upper()
            self._tree.insert("", "end", values=(
                r.id,
                r.cliente.nombre,
                r.servicio.nombre,
                estado,
                f"${r.costo_total:,.2f}",
            ), tags=(estado,))

        self.actualizar_status("Dashboard actualizado.", "ok")
