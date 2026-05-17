"""vista_logs.py - Visor de Registros del Sistema"""
import tkinter as tk
from tkinter import filedialog, messagebox
import os
from datetime import date
from software_fj.gui.estilos import C, F, btn, btn_refresh


class VistaLogs(tk.Frame):
    def __init__(self, parent, gestor, actualizar_status, **kwargs):
        super().__init__(parent, bg=C["bg"], **kwargs)
        self.gestor = gestor
        self.actualizar_status = actualizar_status
        self._ruta_log = self._detectar_log()
        self._auto_refresh = tk.BooleanVar(value=True)
        self._job_refresh = None
        self._construir()

    # ── UI ───────────────────────────────────────────────────────────────────

    def _construir(self):
        # Encabezado
        hdr = tk.Frame(self, bg=C["bg"])
        hdr.pack(fill="x", padx=24, pady=(24, 0))
        tk.Label(hdr, text="Registros del Sistema", bg=C["bg"],
                 fg=C["text"], font=F["title"]).pack(side="left")

        ctrl = tk.Frame(hdr, bg=C["bg"])
        ctrl.pack(side="right")
        tk.Checkbutton(
            ctrl, text="Auto-actualizar", variable=self._auto_refresh,
            bg=C["bg"], fg=C["text2"], selectcolor=C["panel"],
            activebackground=C["bg"], activeforeground=C["text"],
            font=F["small"], command=self._toggle_auto,
        ).pack(side="left", padx=8)
        btn_refresh(ctrl, self.refrescar).pack(side="left", padx=4)

        btn(ctrl, "Limpiar vista", self._limpiar, "btn_warning").pack(side="left", padx=4)
        btn(ctrl, "Guardar copia", self._guardar_copia, "btn_primary").pack(side="left", padx=4)

        # Ruta del log
        ruta_frame = tk.Frame(self, bg=C["bg"])
        ruta_frame.pack(fill="x", padx=24, pady=(8, 4))
        self._lbl_ruta = tk.Label(
            ruta_frame,
            text=f"Archivo: {self._ruta_log or 'No encontrado'}",
            bg=C["bg"], fg=C["text2"], font=F["small"],
        )
        self._lbl_ruta.pack(side="left")
        self._lbl_lineas = tk.Label(ruta_frame, text="",
                                     bg=C["bg"], fg=C["text2"],
                                     font=F["small"])
        self._lbl_lineas.pack(side="right")

        # Leyenda
        ley = tk.Frame(self, bg=C["bg"])
        ley.pack(fill="x", padx=24, pady=(0, 6))
        for txt, color in [
            ("■ INFO",     C["text2"]),
            ("■ WARNING",  C["warning"]),
            ("■ ERROR",    C["error"]),
            ("■ CRITICAL", "#ff6b6b"),
            ("■ DEBUG",    "#4a9eff"),
        ]:
            tk.Label(ley, text=txt, bg=C["bg"],
                     fg=color, font=F["small"]).pack(side="left", padx=8)

        # Área de texto con scroll
        txt_frame = tk.Frame(self, bg=C["card"])
        txt_frame.pack(fill="both", expand=True,
                       padx=24, pady=(0, 20))

        self._txt = tk.Text(
            txt_frame,
            bg=C["bg"], fg=C["text"],
            font=F["mono"],
            relief="flat", bd=0,
            state="disabled",
            wrap="none",
            selectbackground=C["row_sel"],
            insertbackground=C["text"],
        )
        vsb = tk.Scrollbar(txt_frame, orient="vertical",
                           command=self._txt.yview,
                           bg=C["panel"], troughcolor=C["card"])
        hsb = tk.Scrollbar(txt_frame, orient="horizontal",
                           command=self._txt.xview,
                           bg=C["panel"], troughcolor=C["card"])
        self._txt.configure(yscrollcommand=vsb.set,
                            xscrollcommand=hsb.set)

        vsb.pack(side="right", fill="y")
        hsb.pack(side="bottom", fill="x")
        self._txt.pack(fill="both", expand=True)

        # Tags de color por nivel
        self._txt.tag_configure("INFO",     foreground=C["text2"])
        self._txt.tag_configure("WARNING",  foreground=C["warning"])
        self._txt.tag_configure("ERROR",    foreground=C["error"])
        self._txt.tag_configure("CRITICAL", foreground="#ff6b6b")
        self._txt.tag_configure("DEBUG",    foreground="#4a9eff")
        self._txt.tag_configure("SEPARADOR", foreground=C["border"])
        self._txt.tag_configure("TIMESTAMP", foreground="#555e6b")

    # ── Lógica ───────────────────────────────────────────────────────────────

    def _detectar_log(self):
        """Busca el archivo de log del día actual."""
        nombre = f"logs/sistema_{date.today().strftime('%Y%m%d')}.log"
        return nombre if os.path.exists(nombre) else None

    def refrescar(self):
        self._ruta_log = self._detectar_log()
        self._lbl_ruta.config(
            text=f"Archivo: {self._ruta_log or 'No encontrado'}")

        self._txt.configure(state="normal")
        self._txt.delete("1.0", "end")

        if not self._ruta_log:
            self._txt.insert("end",
                "No se encontró archivo de log para hoy.\n"
                "Ejecuta al menos una operación para generarlo.\n",
                "WARNING")
            self._txt.configure(state="disabled")
            self._lbl_lineas.config(text="0 líneas")
            return

        try:
            with open(self._ruta_log, "r", encoding="utf-8",
                      errors="replace") as f:
                lineas = f.readlines()

            for linea in lineas:
                tag = self._tag_para_linea(linea)
                self._txt.insert("end", linea, tag)

            self._txt.see("end")  # scroll al final
            self._txt.configure(state="disabled")
            self._lbl_lineas.config(text=f"{len(lineas)} líneas")
            self.actualizar_status(
                f"Log actualizado — {len(lineas)} líneas.", "ok")

        except OSError as e:
            self._txt.insert("end", f"Error al leer el log: {e}\n", "ERROR")
            self._txt.configure(state="disabled")

    def _tag_para_linea(self, linea: str) -> str:
        """Determina el tag de color según el nivel de log."""
        if "| CRITICAL" in linea:
            return "CRITICAL"
        if "| ERROR   " in linea or "| ERROR" in linea:
            return "ERROR"
        if "| WARNING " in linea or "| WARNING" in linea:
            return "WARNING"
        if "| DEBUG   " in linea or "| DEBUG" in linea:
            return "DEBUG"
        if "---" in linea or "===" in linea:
            return "SEPARADOR"
        return "INFO"

    def _limpiar(self):
        """Limpia la vista (no borra el archivo)."""
        self._txt.configure(state="normal")
        self._txt.delete("1.0", "end")
        self._txt.configure(state="disabled")
        self._lbl_lineas.config(text="0 líneas (vista limpiada)")
        self.actualizar_status("Vista de logs limpiada.", "warn")

    def _guardar_copia(self):
        """Copia el contenido del log a un archivo elegido por el usuario."""
        if not self._ruta_log:
            messagebox.showwarning("Sin log", "No hay archivo de log activo.",
                                   parent=self)
            return
        ruta_destino = filedialog.asksaveasfilename(
            parent=self,
            defaultextension=".log",
            filetypes=[("Log files", "*.log"), ("Texto", "*.txt")],
            initialfile=f"copia_log_{date.today()}.log",
        )
        if not ruta_destino:
            return
        try:
            with open(self._ruta_log, "r", encoding="utf-8") as f:
                contenido = f.read()
            with open(ruta_destino, "w", encoding="utf-8") as f:
                f.write(contenido)
            messagebox.showinfo("Guardado",
                f"Copia guardada en:\n{ruta_destino}", parent=self)
        except OSError as e:
            messagebox.showerror("Error", str(e), parent=self)

    def _toggle_auto(self):
        if self._auto_refresh.get():
            self._programar_refresh()
        else:
            if self._job_refresh:
                self.after_cancel(self._job_refresh)
                self._job_refresh = None

    def _programar_refresh(self):
        """Recarga el log cada 5 segundos si auto-refresh está activo."""
        if self._auto_refresh.get():
            self.refrescar()
            self._job_refresh = self.after(5000, self._programar_refresh)

    def refrescar(self):  # noqa: F811 — sobreescribe el anterior para compatibilidad
        self._ruta_log = self._detectar_log()
        self._lbl_ruta.config(
            text=f"Archivo: {self._ruta_log or 'No encontrado'}")

        self._txt.configure(state="normal")
        self._txt.delete("1.0", "end")

        if not self._ruta_log:
            self._txt.insert("end",
                "No se encontró archivo de log para hoy.\n", "WARNING")
            self._txt.configure(state="disabled")
            self._lbl_lineas.config(text="0 líneas")
            return

        try:
            with open(self._ruta_log, "r", encoding="utf-8",
                      errors="replace") as f:
                lineas = f.readlines()

            for linea in lineas:
                tag = self._tag_para_linea(linea)
                self._txt.insert("end", linea, tag)

            self._txt.see("end")
            self._txt.configure(state="disabled")
            self._lbl_lineas.config(text=f"{len(lineas)} líneas")
            self.actualizar_status(
                f"Log actualizado — {len(lineas)} líneas.", "ok")

        except OSError as e:
            self._txt.insert("end", f"Error al leer log: {e}\n", "ERROR")
            self._txt.configure(state="disabled")
