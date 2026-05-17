"""vista_reservas.py - Gestión de Reservas"""
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date, timedelta
from software_fj.gui.estilos import C, F, btn, entry
from software_fj.reserva import EstadoReserva
from software_fj.excepciones import SoftwareFJError
from software_fj.servicios import ReservaSala, AlquilerEquipo, AsesoriaEspecializada


class VistaReservas(tk.Frame):
    def __init__(self, parent, gestor, actualizar_status, **kwargs):
        super().__init__(parent, bg=C["bg"], **kwargs)
        self.gestor = gestor
        self.actualizar_status = actualizar_status
        self._construir()

    # ── Construcción UI ───────────────────────────────────────────────────────

    def _construir(self):
        # Encabezado
        hdr = tk.Frame(self, bg=C["bg"])
        hdr.pack(fill="x", padx=24, pady=(24, 0))
        tk.Label(hdr, text="Gestión de Reservas", bg=C["bg"],
                 fg=C["text"], font=F["title"]).pack(side="left")
        btn(hdr, "+ Nueva Reserva", self._abrir_form_reserva,
            "btn_success").pack(side="right")

        # Filtros de estado
        filtros_frame = tk.Frame(self, bg=C["bg"])
        filtros_frame.pack(fill="x", padx=24, pady=10)
        tk.Label(filtros_frame, text="Filtrar:", bg=C["bg"],
                 fg=C["text2"], font=F["small"]).pack(side="left")

        self._filtro_var = tk.StringVar(value="TODOS")
        opciones = ["TODOS"] + [e.value.upper()
                                for e in EstadoReserva]
        for op in opciones:
            color = self._color_estado(op)
            rb = tk.Radiobutton(
                filtros_frame, text=op, variable=self._filtro_var,
                value=op, command=self._filtrar,
                bg=C["bg"], fg=color, selectcolor=C["panel"],
                activebackground=C["bg"], activeforeground=color,
                font=F["small"], cursor="hand2",
            )
            rb.pack(side="left", padx=6)

        # Tabla
        tabla_frame = tk.Frame(self, bg=C["card"])
        tabla_frame.pack(fill="both", expand=True, padx=24, pady=(0, 8))

        cols = ("id", "cliente", "servicio", "duracion",
                "fecha", "estado", "costo")
        self._tree = ttk.Treeview(tabla_frame, columns=cols,
                                   show="headings", style="Dark.Treeview",
                                   selectmode="browse")
        cfg = {
            "id":       ("ID",          100, "w"),
            "cliente":  ("Cliente",     180, "w"),
            "servicio": ("Servicio",    200, "w"),
            "duracion": ("Duración",     80, "center"),
            "fecha":    ("Fecha",       100, "center"),
            "estado":   ("Estado",      100, "center"),
            "costo":    ("Costo",        90, "e"),
        }
        for col, (txt, w, anchor) in cfg.items():
            self._tree.heading(col, text=txt)
            self._tree.column(col, width=w, anchor=anchor)

        sb = ttk.Scrollbar(tabla_frame, orient="vertical",
                           command=self._tree.yview,
                           style="Dark.Vertical.TScrollbar")
        self._tree.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        self._tree.pack(fill="both", expand=True)

        # Tags de color por estado
        for estado, color in [
            ("CONFIRMADA", C["success"]),
            ("COMPLETADA", C["accent"]),
            ("CANCELADA",  C["error"]),
            ("RECHAZADA",  C["warning"]),
            ("PENDIENTE",  C["text2"]),
        ]:
            self._tree.tag_configure(estado, foreground=color)

        # Botones de acción sobre selección
        acc = tk.Frame(self, bg=C["bg"])
        acc.pack(fill="x", padx=24, pady=(0, 20))
        btn(acc, "✔ Confirmar",  self._confirmar,  "btn_success").pack(side="left", padx=(0, 6))
        btn(acc, "✘ Cancelar",   self._cancelar,   "btn_danger").pack(side="left", padx=(0, 6))
        btn(acc, "⬛ Completar",  self._completar,  "btn_primary").pack(side="left", padx=(0, 6))
        btn(acc, "👁 Detalle",    self._ver_detalle, "btn_neutral").pack(side="left", padx=(0, 6))

    # ── Poblar tabla ──────────────────────────────────────────────────────────

    def refrescar(self):
        self._filtrar()
        total = len(self.gestor.listar_reservas())
        self.actualizar_status(f"{total} reserva(s) en total.", "ok")

    def _filtrar(self):
        filtro = self._filtro_var.get()
        reservas = self.gestor.listar_reservas()
        if filtro != "TODOS":
            reservas = [r for r in reservas
                        if r.estado.value.upper() == filtro]
        for row in self._tree.get_children():
            self._tree.delete(row)
        for r in sorted(reservas, key=lambda x: x.id, reverse=True):
            estado = r.estado.value.upper()
            self._tree.insert("", "end", iid=r.id, values=(
                r.id,
                r.cliente.nombre,
                r.servicio.nombre,
                f"{r.duracion}u",
                str(r.fecha_reserva),
                estado,
                f"${r.costo_total:,.2f}",
            ), tags=(estado,))

    # ── Acciones sobre reservas ───────────────────────────────────────────────

    def _seleccionada(self):
        sel = self._tree.selection()
        if not sel:
            messagebox.showinfo("Sin selección",
                                "Selecciona una reserva.", parent=self)
            return None
        return sel[0]

    def _confirmar(self):
        id_r = self._seleccionada()
        if not id_r:
            return
        try:
            costo = self.gestor.confirmar_reserva(id_r)
            messagebox.showinfo("Confirmada",
                f"Reserva {id_r} confirmada.\nCosto total: ${costo:,.2f}",
                parent=self)
            self.refrescar()
            self.actualizar_status(
                f"Reserva {id_r} confirmada. Costo: ${costo:,.2f}", "ok")
        except SoftwareFJError as e:
            messagebox.showerror("Error", str(e), parent=self)
            self.actualizar_status(str(e), "error")

    def _cancelar(self):
        id_r = self._seleccionada()
        if not id_r:
            return
        motivo = _pedir_texto(self, "Cancelar reserva",
                              "Motivo de cancelación (opcional):")
        if motivo is None:
            return
        try:
            self.gestor.cancelar_reserva(id_r, motivo or "Cancelada desde GUI")
            messagebox.showinfo("Cancelada",
                f"Reserva {id_r} cancelada.", parent=self)
            self.refrescar()
            self.actualizar_status(f"Reserva {id_r} cancelada.", "warn")
        except SoftwareFJError as e:
            messagebox.showerror("Error", str(e), parent=self)

    def _completar(self):
        id_r = self._seleccionada()
        if not id_r:
            return
        if not messagebox.askyesno("Confirmar",
                                   f"¿Marcar {id_r} como COMPLETADA?",
                                   parent=self):
            return
        try:
            self.gestor.completar_reserva(id_r)
            messagebox.showinfo("Completada",
                f"Reserva {id_r} completada.", parent=self)
            self.refrescar()
            self.actualizar_status(f"Reserva {id_r} completada.", "ok")
        except SoftwareFJError as e:
            messagebox.showerror("Error", str(e), parent=self)

    def _ver_detalle(self):
        id_r = self._seleccionada()
        if not id_r:
            return
        try:
            r = self.gestor.obtener_reserva(id_r)
        except SoftwareFJError as e:
            messagebox.showerror("Error", str(e), parent=self)
            return

        win = tk.Toplevel(self)
        win.title(f"Detalle — {r.id}")
        win.configure(bg=C["card"])
        win.geometry("460x360")
        win.resizable(False, False)
        win.grab_set()

        estado_color = self._color_estado(r.estado.value.upper())
        tk.Label(win, text=r.id, bg=C["card"],
                 fg=C["accent"], font=F["section"]).pack(pady=(20, 4))
        tk.Label(win, text=r.estado.value.upper(), bg=C["card"],
                 fg=estado_color, font=F["body_b"]).pack()

        tk.Frame(win, bg=C["border"], height=1).pack(
            fill="x", padx=20, pady=10)

        info = [
            ("Cliente",   r.cliente.nombre + f" ({r.cliente.tipo})"),
            ("Email",     r.cliente.email),
            ("Servicio",  r.servicio.nombre),
            ("Tipo serv.",r.servicio.__class__.__name__),
            ("Duración",  f"{r.duracion} unidades"),
            ("Fecha",     str(r.fecha_reserva)),
            ("Costo",     f"${r.costo_total:,.2f}"),
            ("Creada",    r.fecha_creacion.strftime("%Y-%m-%d %H:%M")),
        ]
        if r.notas:
            info.append(("Notas", r.notas))

        for campo, valor in info:
            row = tk.Frame(win, bg=C["card"])
            row.pack(fill="x", padx=24, pady=3)
            tk.Label(row, text=campo + ":", bg=C["card"],
                     fg=C["text2"], font=F["small"],
                     width=12, anchor="w").pack(side="left")
            tk.Label(row, text=valor, bg=C["card"],
                     fg=C["text"], font=F["body_b"]).pack(side="left")

        btn(win, "Cerrar", win.destroy, "btn_neutral").pack(pady=16)

    # ── Formulario nueva reserva ──────────────────────────────────────────────

    def _abrir_form_reserva(self):
        clientes  = self.gestor.listar_clientes()
        servicios = self.gestor.listar_servicios_disponibles()
        if not clientes:
            messagebox.showwarning("Sin clientes",
                "Registra al menos un cliente antes de crear una reserva.",
                parent=self)
            return
        if not servicios:
            messagebox.showwarning("Sin servicios",
                "No hay servicios disponibles.", parent=self)
            return
        _DialogReserva(self, self.gestor, clientes, servicios,
                       self._on_reserva_creada)

    def _on_reserva_creada(self, id_reserva):
        self.refrescar()
        self.actualizar_status(
            f"Reserva {id_reserva} creada en estado PENDIENTE.", "ok")

    @staticmethod
    def _color_estado(estado):
        return {
            "CONFIRMADA": C["success"],
            "COMPLETADA": C["accent"],
            "CANCELADA":  C["error"],
            "RECHAZADA":  C["warning"],
            "PENDIENTE":  C["text2"],
            "TODOS":      C["text"],
        }.get(estado, C["text"])


# ── Diálogo nueva reserva ─────────────────────────────────────────────────────

class _DialogReserva(tk.Toplevel):
    def __init__(self, parent, gestor, clientes, servicios, callback):
        super().__init__(parent)
        self.gestor    = gestor
        self.clientes  = clientes
        self.servicios = servicios
        self.callback  = callback
        self.title("Nueva Reserva")
        self.configure(bg=C["card"])
        # Ajuste: Incrementado de 560 a 620 para asegurar espacio para opciones dinámicas
        self.geometry("500x620")
        self.resizable(False, False)
        self.grab_set()
        self._construir()

    def _construir(self):
        tk.Label(self, text="Nueva Reserva", bg=C["card"],
                 fg=C["accent"], font=F["section"]).pack(pady=(18, 4))
        tk.Frame(self, bg=C["border"], height=1).pack(
            fill="x", padx=20, pady=6)

        form = tk.Frame(self, bg=C["card"])
        form.pack(fill="x", padx=24)

        # Cliente
        tk.Label(form, text="Cliente", bg=C["card"],
                 fg=C["text2"], font=F["small"]).pack(anchor="w", pady=(8, 2))
        self._cli_var = tk.StringVar()
        cli_opciones  = [f"{c.id} — {c.nombre}" for c in self.clientes]
        self._cli_cb  = ttk.Combobox(form, textvariable=self._cli_var,
                                      values=cli_opciones, state="readonly",
                                      style="Dark.TCombobox", font=F["body"])
        self._cli_cb.pack(fill="x", ipady=4)
        if cli_opciones:
            self._cli_cb.current(0)

        # Servicio
        tk.Label(form, text="Servicio", bg=C["card"],
                 fg=C["text2"], font=F["small"]).pack(anchor="w", pady=(10, 2))
        self._srv_var = tk.StringVar()
        srv_opciones  = [f"{s.id} — {s.nombre}" for s in self.servicios]
        self._srv_cb  = ttk.Combobox(form, textvariable=self._srv_var,
                                      values=srv_opciones, state="readonly",
                                      style="Dark.TCombobox", font=F["body"])
        self._srv_cb.pack(fill="x", ipady=4)
        if srv_opciones:
            self._srv_cb.current(0)
        self._srv_cb.bind("<<ComboboxSelected>>",
                          lambda _: self._actualizar_opciones())

        # Duración
        dur_row = tk.Frame(form, bg=C["card"])
        dur_row.pack(fill="x", pady=(10, 0))
        tk.Label(dur_row, text="Duración", bg=C["card"],
                 fg=C["text2"], font=F["small"]).pack(anchor="w")
        self._dur_lbl = tk.Label(dur_row, text="(horas/días)",
                                  bg=C["card"], fg=C["text2"],
                                  font=("Segoe UI", 8))
        self._dur_lbl.pack(anchor="w")
        self._dur_var = tk.StringVar(value="2")
        entry(form, textvariable=self._dur_var, width=12
              ).pack(anchor="w", ipady=4)

        # Fecha
        tk.Label(form, text="Fecha (YYYY-MM-DD)", bg=C["card"],
                 fg=C["text2"], font=F["small"]).pack(anchor="w", pady=(10, 2))
        self._fecha_var = tk.StringVar(
            value=str(date.today() + timedelta(days=1)))
        entry(form, textvariable=self._fecha_var, width=14
              ).pack(anchor="w", ipady=4)

        # Notas
        tk.Label(form, text="Notas (opcional)", bg=C["card"],
                 fg=C["text2"], font=F["small"]).pack(anchor="w", pady=(10, 2))
        self._notas_var = tk.StringVar()
        entry(form, textvariable=self._notas_var).pack(fill="x", ipady=4)

        # Opciones adicionales dinámicas
        tk.Frame(self, bg=C["border"], height=1).pack(
            fill="x", padx=20, pady=10)
        self._extras_frame = tk.Frame(self, bg=C["card"])
        self._extras_frame.pack(fill="x", padx=24)
        self._extras = {}
        self._actualizar_opciones()

        tk.Frame(self, bg=C["border"], height=1).pack(
            fill="x", padx=20, pady=10)

        btn_row = tk.Frame(self, bg=C["card"])
        btn_row.pack()
        btn(btn_row, "Cancelar", self.destroy, "btn_neutral"
            ).pack(side="left", padx=6)
        btn(btn_row, "Crear Reserva", self._crear, "btn_success"
            ).pack(side="left", padx=6)
        btn(btn_row, "Crear y Confirmar", self._crear_y_confirmar,
            "btn_primary").pack(side="left", padx=6)

    def _servicio_seleccionado(self):
        idx = self._srv_cb.current()
        if idx < 0:
            return None
        return self.servicios[idx]

    def _actualizar_opciones(self):
        for w in self._extras_frame.winfo_children():
            w.destroy()
        self._extras = {}
        srv = self._servicio_seleccionado()
        if srv is None:
            return

        if isinstance(srv, ReservaSala):
            self._dur_lbl.config(text="(horas — máx. 12h)")
            opciones = [
                ("usar_proyector",         "Usar proyector",         srv.tiene_proyector),
                ("usar_videoconferencia",  "Usar videoconferencia",  srv.tiene_videoconferencia),
            ]
            tk.Label(self._extras_frame, text="Num. personas:",
                     bg=C["card"], fg=C["text2"], font=F["small"]
                     ).grid(row=0, column=0, sticky="w", pady=4)
            v = tk.StringVar(value="1")
            entry(self._extras_frame, textvariable=v, width=6
                  ).grid(row=0, column=1, sticky="w", padx=8)
            self._extras["num_personas"] = (v, "int")
            for i, (key, lbl, activo) in enumerate(opciones, start=1):
                var = tk.BooleanVar(value=False)
                cb  = tk.Checkbutton(
                    self._extras_frame, text=lbl,
                    variable=var, bg=C["card"], fg=C["text"],
                    selectcolor=C["panel"], activebackground=C["card"],
                    font=F["small"], state="normal" if activo else "disabled",
                )
                cb.grid(row=i, column=0, columnspan=2, sticky="w", pady=2)
                self._extras[key] = (var, "bool")

        elif isinstance(srv, AlquilerEquipo):
            self._dur_lbl.config(text="(días — máx. 30 días)")
            tk.Label(self._extras_frame, text="Unidades a alquilar:",
                     bg=C["card"], fg=C["text2"], font=F["small"]
                     ).grid(row=0, column=0, sticky="w", pady=4)
            v = tk.StringVar(value="1")
            entry(self._extras_frame, textvariable=v, width=6
                  ).grid(row=0, column=1, sticky="w", padx=8)
            self._extras["cantidad_unidades"] = (v, "int")

            var_seg = tk.BooleanVar(value=False)
            tk.Checkbutton(
                self._extras_frame, text="Incluir seguro",
                variable=var_seg, bg=C["card"], fg=C["text"],
                selectcolor=C["panel"], activebackground=C["card"],
                font=F["small"],
            ).grid(row=1, column=0, columnspan=2, sticky="w", pady=2)
            self._extras["incluir_seguro"] = (var_seg, "bool")

        else:  # Asesoría
            self._dur_lbl.config(text="(horas — máx. 40h)")
            var_urg = tk.BooleanVar(value=False)
            tk.Checkbutton(
                self._extras_frame, text="Solicitud urgente (+50%)",
                variable=var_urg, bg=C["card"], fg=C["text"],
                selectcolor=C["panel"], activebackground=C["card"],
                font=F["small"],
            ).grid(row=0, column=0, columnspan=2, sticky="w", pady=2)
            self._extras["urgente"] = (var_urg, "bool")

    def _recopilar_datos(self):
        idx_cli = self._cli_cb.current()
        idx_srv = self._srv_cb.current()
        if idx_cli < 0 or idx_srv < 0:
            raise ValueError("Selecciona un cliente y un servicio.")

        id_cliente  = self.clientes[idx_cli].id
        id_servicio = self.servicios[idx_srv].id

        try:
            duracion = float(self._dur_var.get())
        except ValueError:
            raise ValueError("La duración debe ser un número.")

        try:
            partes = self._fecha_var.get().split("-")
            fecha  = date(int(partes[0]), int(partes[1]), int(partes[2]))
        except Exception:
            raise ValueError("Fecha inválida. Usa formato YYYY-MM-DD.")

        notas  = self._notas_var.get().strip()
        kwargs = {}
        for key, (var, tipo) in self._extras.items():
            val = var.get()
            if tipo == "int":
                try:
                    val = int(val)
                except ValueError:
                    raise ValueError(f"'{key}' debe ser un entero.")
            kwargs[key] = val

        return id_cliente, id_servicio, duracion, fecha, notas, kwargs

    def _crear(self):
        try:
            id_c, id_s, dur, fecha, notas, kwargs = self._recopilar_datos()
            r = self.gestor.crear_reserva(id_c, id_s, dur, fecha,
                                          notas, **kwargs)
            messagebox.showinfo("Reserva creada",
                f"Reserva {r.id} creada en estado PENDIENTE.",
                parent=self)
            self.callback(r.id)
            self.destroy()
        except (ValueError, SoftwareFJError) as e:
            messagebox.showerror("Error", str(e), parent=self)

    def _crear_y_confirmar(self):
        try:
            id_c, id_s, dur, fecha, notas, kwargs = self._recopilar_datos()
            r = self.gestor.crear_reserva(id_c, id_s, dur, fecha,
                                          notas, **kwargs)
            costo = self.gestor.confirmar_reserva(r.id)
            messagebox.showinfo("Reserva confirmada",
                f"Reserva {r.id} creada y confirmada.\n"
                f"Costo total: ${costo:,.2f}",
                parent=self)
            self.callback(r.id)
            self.destroy()
        except (ValueError, SoftwareFJError) as e:
            messagebox.showerror("Error", str(e), parent=self)


# ── Helper ────────────────────────────────────────────────────────────────────

def _pedir_texto(parent, titulo, prompt):
    """Diálogo simple para pedir una cadena de texto."""
    win = tk.Toplevel(parent)
    win.title(titulo)
    win.configure(bg=C["card"])
    win.geometry("380x160")
    win.resizable(False, False)
    win.grab_set()

    tk.Label(win, text=prompt, bg=C["card"],
             fg=C["text"], font=F["body"]).pack(pady=(20, 8), padx=20)
    var = tk.StringVar()
    from software_fj.gui.estilos import entry as mk_entry
    mk_entry(win, textvariable=var).pack(fill="x", padx=20, ipady=5)

    resultado = [None]

    def aceptar():
        resultado[0] = var.get().strip()
        win.destroy()

    def cancelar():
        win.destroy()

    row = tk.Frame(win, bg=C["card"])
    row.pack(pady=16)
    btn(row, "Cancelar", cancelar, "btn_neutral").pack(side="left", padx=6)
    btn(row, "Aceptar",  aceptar,  "btn_primary").pack(side="left", padx=6)
    win.wait_window()
    return resultado[0]
