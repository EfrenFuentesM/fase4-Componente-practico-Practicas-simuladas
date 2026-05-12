"""vista_clientes.py - Gestión de Clientes"""
import tkinter as tk
from tkinter import ttk, messagebox
from software_fj.gui.estilos import C, F, btn, entry
from software_fj.cliente import Cliente
from software_fj.excepciones import (
    ClienteInvalidoError, ClienteYaRegistradoError,
    ParametroFaltanteError, SoftwareFJError,
)


class VistaClientes(tk.Frame):
    def __init__(self, parent, gestor, actualizar_status, **kwargs):
        super().__init__(parent, bg=C["bg"], **kwargs)
        self.gestor = gestor
        self.actualizar_status = actualizar_status
        self._construir()

    # ── UI principal ─────────────────────────────────────────────────────────

    def _construir(self):
        # Encabezado
        hdr = tk.Frame(self, bg=C["bg"])
        hdr.pack(fill="x", padx=24, pady=(24, 0))
        tk.Label(hdr, text="Gestión de Clientes", bg=C["bg"],
                 fg=C["text"], font=F["title"]).pack(side="left")
        btn(hdr, "+ Nuevo Cliente", self._abrir_form_nuevo,
            "btn_success").pack(side="right")

        # Barra de búsqueda
        search_frame = tk.Frame(self, bg=C["bg"])
        search_frame.pack(fill="x", padx=24, pady=12)
        tk.Label(search_frame, text="🔍", bg=C["bg"],
                 fg=C["text2"], font=F["body"]).pack(side="left")
        self._buscar_var = tk.StringVar()
        self._buscar_var.trace_add("write", lambda *_: self._filtrar())
        e = entry(search_frame, textvariable=self._buscar_var, width=35)
        e.pack(side="left", padx=6)
        tk.Label(search_frame, text="Buscar por nombre o email",
                 bg=C["bg"], fg=C["text2"], font=F["small"]).pack(side="left")

        # Tabla
        tabla_frame = tk.Frame(self, bg=C["card"])
        tabla_frame.pack(fill="both", expand=True, padx=24, pady=(0, 16))

        cols = ("id", "nombre", "email", "telefono", "tipo", "reservas")
        self._tree = ttk.Treeview(tabla_frame, columns=cols,
                                   show="headings", style="Dark.Treeview",
                                   selectmode="browse")
        cfg = {
            "id":       ("ID",          90,  "w"),
            "nombre":   ("Nombre",      200, "w"),
            "email":    ("Email",       210, "w"),
            "telefono": ("Teléfono",    130, "w"),
            "tipo":     ("Tipo",        100, "center"),
            "reservas": ("Reservas",    80,  "center"),
        }
        for col, (txt, w, anchor) in cfg.items():
            self._tree.heading(col, text=txt,
                               command=lambda c=col: self._ordenar(c))
            self._tree.column(col, width=w, anchor=anchor)

        sb = ttk.Scrollbar(tabla_frame, orient="vertical",
                           command=self._tree.yview,
                           style="Dark.Vertical.TScrollbar")
        self._tree.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        self._tree.pack(fill="both", expand=True)

        self._tree.tag_configure("premium",      foreground="#c084fc")
        self._tree.tag_configure("corporativo",  foreground=C["warning"])
        self._tree.tag_configure("regular",      foreground=C["text"])
        self._tree.tag_configure("even",         background=C["row_even"])
        self._tree.tag_configure("odd",          background=C["row_odd"])

        self._tree.bind("<Double-1>", self._ver_detalle)

        # Botones de acción
        acciones = tk.Frame(self, bg=C["bg"])
        acciones.pack(fill="x", padx=24, pady=(0, 20))
        btn(acciones, "Ver detalle", self._ver_detalle_btn,
            "btn_neutral").pack(side="left", padx=(0, 8))

        self._sort_col = None
        self._sort_asc = True
        self._todos = []

    # ── Poblar tabla ─────────────────────────────────────────────────────────

    def refrescar(self):
        self._todos = self.gestor.listar_clientes()
        self._filtrar()
        self.actualizar_status(
            f"{len(self._todos)} cliente(s) registrado(s).", "ok")

    def _filtrar(self):
        texto = self._buscar_var.get().lower().strip()
        filtrados = [
            c for c in self._todos
            if texto in c.nombre.lower() or texto in c.email.lower()
        ] if texto else list(self._todos)
        self._poblar_tabla(filtrados)

    def _poblar_tabla(self, clientes):
        for row in self._tree.get_children():
            self._tree.delete(row)
        for i, c in enumerate(clientes):
            tag_tipo = c.tipo
            tag_par  = "even" if i % 2 == 0 else "odd"
            self._tree.insert("", "end", iid=c.id, values=(
                c.id, c.nombre, c.email, c.telefono,
                c.tipo.capitalize(), c.total_reservas(),
            ), tags=(tag_tipo, tag_par))

    def _ordenar(self, columna):
        clientes = self.gestor.listar_clientes()
        campos = {
            "id": lambda c: c.id,
            "nombre": lambda c: c.nombre,
            "email": lambda c: c.email,
            "tipo": lambda c: c.tipo,
            "reservas": lambda c: c.total_reservas(),
        }
        if columna in campos:
            if self._sort_col == columna:
                self._sort_asc = not self._sort_asc
            else:
                self._sort_asc = True
                self._sort_col = columna
            clientes.sort(key=campos[columna], reverse=not self._sort_asc)
            self._poblar_tabla(clientes)

    # ── Formulario nuevo cliente ──────────────────────────────────────────────

    def _abrir_form_nuevo(self):
        _DialogCliente(self, self.gestor, self._on_guardado)

    def _on_guardado(self, mensaje):
        self.refrescar()
        self.actualizar_status(mensaje, "ok")

    # ── Ver detalle ───────────────────────────────────────────────────────────

    def _ver_detalle_btn(self):
        sel = self._tree.selection()
        if not sel:
            messagebox.showinfo("Sin selección",
                                "Selecciona un cliente de la tabla.",
                                parent=self)
            return
        self._mostrar_detalle(sel[0])

    def _ver_detalle(self, event=None):
        sel = self._tree.selection()
        if sel:
            self._mostrar_detalle(sel[0])

    def _mostrar_detalle(self, id_cliente):
        try:
            c = self.gestor.obtener_cliente(id_cliente)
        except SoftwareFJError as e:
            messagebox.showerror("Error", str(e), parent=self)
            return

        win = tk.Toplevel(self)
        win.title(f"Detalle — {c.nombre}")
        win.configure(bg=C["card"])
        # Incrementado de 300 a 340 para asegurar visibilidad de campos
        win.geometry("420x340")
        win.resizable(False, False)
        win.grab_set()

        tk.Label(win, text=c.nombre, bg=C["card"],
                 fg=C["accent"], font=F["section"]).pack(pady=(20, 4))

        info = [
            ("ID",        c.id),
            ("Email",     c.email),
            ("Teléfono",  c.telefono),
            ("Tipo",      c.tipo.capitalize()),
            ("Reservas",  str(c.total_reservas())),
            ("Creado",    c.fecha_creacion.strftime("%Y-%m-%d %H:%M")),
        ]
        for campo, valor in info:
            row = tk.Frame(win, bg=C["card"])
            row.pack(fill="x", padx=24, pady=3)
            tk.Label(row, text=campo + ":", bg=C["card"],
                     fg=C["text2"], font=F["small"], width=10,
                     anchor="w").pack(side="left")
            tk.Label(row, text=valor, bg=C["card"],
                     fg=C["text"], font=F["body_b"]).pack(side="left")

        btn(win, "Cerrar", win.destroy, "btn_neutral").pack(pady=16)


# ── Diálogo de registro de cliente ───────────────────────────────────────────

class _DialogCliente(tk.Toplevel):
    TIPOS = ["regular", "premium", "corporativo"]

    def __init__(self, parent, gestor, callback):
        super().__init__(parent)
        self.gestor   = gestor
        self.callback = callback
        self.title("Registrar Nuevo Cliente")
        self.configure(bg=C["card"])
        # Ajuste: Incrementado de 420 a 480 para evitar que los botones se corten en la parte inferior
        self.geometry("440x480")
        self.resizable(False, False)
        self.grab_set()
        self._construir()

    def _construir(self):
        tk.Label(self, text="Nuevo Cliente", bg=C["card"],
                 fg=C["accent"], font=F["section"]).pack(pady=(20, 4))
        tk.Frame(self, bg=C["border"], height=1).pack(fill="x",
                                                       padx=20, pady=8)

        form = tk.Frame(self, bg=C["card"])
        form.pack(fill="x", padx=24)

        self._vars = {}
        campos = [
            ("ID Cliente",  "id",       False),
            ("Nombre",      "nombre",   False),
            ("Email",       "email",    False),
            ("Teléfono",    "telefono", False),
        ]
        for texto, key, _ in campos:
            tk.Label(form, text=texto, bg=C["card"],
                     fg=C["text2"], font=F["small"]).pack(anchor="w",
                                                          pady=(8, 2))
            var = tk.StringVar()
            self._vars[key] = var
            e = entry(form, textvariable=var)
            e.pack(fill="x", ipady=5)

        # Tipo
        tk.Label(form, text="Tipo de cliente", bg=C["card"],
                 fg=C["text2"], font=F["small"]).pack(anchor="w", pady=(8, 2))
        self._tipo_var = tk.StringVar(value="regular")
        cb = ttk.Combobox(form, textvariable=self._tipo_var,
                          values=self.TIPOS, state="readonly",
                          style="Dark.TCombobox", font=F["body"])
        cb.pack(fill="x", ipady=4)

        tk.Frame(self, bg=C["border"], height=1).pack(fill="x",
                                                       padx=20, pady=12)

        btn_row = tk.Frame(self, bg=C["card"])
        btn_row.pack()
        btn(btn_row, "Cancelar", self.destroy,
            "btn_neutral").pack(side="left", padx=6)
        btn(btn_row, "Registrar", self._guardar,
            "btn_success").pack(side="left", padx=6)

    def _guardar(self):
        id_c    = self._vars["id"].get().strip()
        nombre  = self._vars["nombre"].get().strip()
        email   = self._vars["email"].get().strip()
        tel     = self._vars["telefono"].get().strip()
        tipo    = self._tipo_var.get()

        try:
            cliente = Cliente(id_c, nombre, email, tel, tipo)
            self.gestor.registrar_cliente(cliente)
            messagebox.showinfo("Éxito",
                f"Cliente '{nombre}' registrado correctamente.", parent=self)
            self.callback(f"Cliente [{id_c}] {nombre} registrado.")
            self.destroy()
        except (ClienteInvalidoError, ClienteYaRegistradoError,
                ParametroFaltanteError) as e:
            messagebox.showerror("Error de validación", str(e), parent=self)
        except Exception as e:
            messagebox.showerror("Error inesperado", str(e), parent=self)
