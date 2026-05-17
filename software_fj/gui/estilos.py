"""
estilos.py - Definición de la identidad visual y componentes estilizados de Software FJ.

Este módulo centraliza la paleta de colores, tipografías y estilos de los widgets
de la interfaz gráfica, permitiendo una personalización coherente y profesional.
"""
import tkinter as tk
from tkinter import ttk

# ── Paleta de Colores "Innovative Orange" ────────────────────────────────────
# Se utiliza una base oscura (GitHub-like) con acentos en naranja vibrante.
C = {
    "bg":           "#0d1117", # Fondo principal de la aplicación
    "sidebar":      "#161b22", # Fondo de la barra lateral de navegación
    "card":         "#21262d", # Fondo de tarjetas y contenedores internos
    "panel":        "#2d333b", # Fondo de paneles y entradas de texto
    "accent":       "#ff9500", # Naranja vibrante para elementos destacados
    "success":      "#3fb950", # Verde para mensajes de éxito
    "warning":      "#d29922", # Amarillo/Ocre para advertencias
    "error":        "#f85149", # Rojo para errores críticos
    "text":         "#e6edf3", # Texto principal de alto contraste
    "text2":        "#8b949e", # Texto secundario de menor contraste
    "border":       "#30363d", # Color de bordes y separadores
    "btn_primary":  "#e67e22", # Botón principal (Naranja corporativo)
    "btn_success":  "#238636", # Botón de confirmación o guardado
    "btn_danger":   "#da3633", # Botón de eliminación o peligro
    "btn_warning":  "#9e6a03", # Botón de advertencia
    "btn_neutral":  "#30363d", # Botón neutral o de cancelación
    "row_even":     "#21262d", # Color de fila par en tablas
    "row_odd":      "#1c2128", # Color de fila impar en tablas
    "row_sel":      "#4a3a1a", # Fondo de selección (Ámbar oscuro)
}

# ── Configuración de Tipografías ─────────────────────────────────────────────
# Se utiliza 'Segoe UI' por su legibilidad en Windows, con Consolas para datos técnicos.
F = {
    "title":   ("Segoe UI", 16, "bold"),
    "section": ("Segoe UI", 13, "bold"),
    "heading": ("Segoe UI", 11, "bold"),
    "body":    ("Segoe UI", 10),
    "body_b":  ("Segoe UI", 10, "bold"),
    "small":   ("Segoe UI", 9),
    "sidebar": ("Segoe UI", 11),
    "logo":    ("Segoe UI", 14, "bold"),
    "stat":    ("Segoe UI", 26, "bold"),
    "mono":    ("Consolas", 9),
}


def aplicar_estilos(root: tk.Tk) -> None:
    """
    Configura y aplica los estilos de la biblioteca ttk de Tkinter.
    Define el aspecto visual de tablas, barras de desplazamiento y selectores.
    """
    s = ttk.Style(root)
    s.theme_use("clam") # Base clam para máxima personalización

    # ── Configuración de Treeview (Tablas) ───────────────────────────────────
    s.configure("Dark.Treeview",
        background=C["card"], foreground=C["text"],
        fieldbackground=C["card"], rowheight=28,
        font=F["body"], borderwidth=0, relief="flat",
    )
    s.configure("Dark.Treeview.Heading",
        background=C["panel"], foreground=C["accent"],
        font=F["body_b"], relief="flat", borderwidth=0, padding=(8, 6),
    )
    # Estados de selección y hover en tablas
    s.map("Dark.Treeview",
        background=[("selected", C["row_sel"])],
        foreground=[("selected", C["text"])],
    )
    s.map("Dark.Treeview.Heading",
        background=[("active", C["border"])],
    )

    # ── Configuración de Scrollbar ───────────────────────────────────────────
    s.configure("Dark.Vertical.TScrollbar",
        background=C["panel"], troughcolor=C["card"],
        arrowcolor=C["text2"], borderwidth=0, width=10,
    )
    s.configure("Dark.Horizontal.TScrollbar",
        background=C["panel"], troughcolor=C["card"],
        arrowcolor=C["text2"], borderwidth=0, width=10,
    )

    # ── Configuración de Combobox ────────────────────────────────────────────
    s.configure("Dark.TCombobox",
        fieldbackground=C["panel"], background=C["panel"],
        foreground=C["text"], arrowcolor=C["accent"],
        bordercolor=C["border"], selectbackground=C["row_sel"],
    )
    s.map("Dark.TCombobox",
        fieldbackground=[("readonly", C["panel"])],
        foreground=[("readonly", C["text"])],
        selectbackground=[("readonly", C["row_sel"])],
    )


def btn(parent, texto, comando, color="btn_primary", **kwargs):
    """
    Crea un botón con esquinas redondeadas y efecto hover.
    Devuelve un RoundedBtn basado en Canvas.
    """
    return RoundedBtn(parent, texto, comando, color)


def btn_refresh(parent, comando, **kwargs):
    """
    Botón 'Actualizar' animado con esquinas redondeadas:
    - Giro del símbolo ↻ en 8 pasos al hacer clic
    - Pulso de color naranja mientras gira
    - Hover con fondo naranja
    """
    _SPIN_FRAMES = ["↻", "↺", "↻", "↺", "↻", "↺", "↻", "↺"]
    _SPIN_COLORS = [
        C["accent"], _lighten(C["accent"]), C["accent"], _lighten(C["accent"]),
        C["accent"], _lighten(C["accent"]), C["accent"], C["btn_neutral"],
    ]
    texto_base = "↻  Actualizar"

    b = RoundedBtn(parent, texto_base, None, "btn_neutral")
    _state = {"animating": False}

    def _spin(step=0):
        if step < len(_SPIN_FRAMES):
            b.set_text(f"{_SPIN_FRAMES[step]}  Actualizar")
            b.set_bg(_SPIN_COLORS[step])
            b.after(80, lambda: _spin(step + 1))
        else:
            b.set_text(texto_base)
            b.set_bg(C["btn_neutral"])
            b.set_enabled(True)
            _state["animating"] = False

    def _on_click():
        if _state["animating"]:
            return
        _state["animating"] = True
        b.set_enabled(False)
        _spin(0)
        b.after(50, comando)

    b._command = _on_click
    return b


class RoundedBtn(tk.Canvas):
    """
    Botón de acción con esquinas redondeadas, implementado sobre Canvas.
    Soporta estados: normal, hover y deshabilitado.
    Métodos públicos: set_text(), set_bg(), set_enabled().
    """

    _HEIGHT = 34
    _RADIUS = 12

    def __init__(self, parent, text: str, command, color: str = "btn_primary"):
        import tkinter.font as tkf
        _f = tkf.Font(family="Segoe UI", size=10, weight="bold")
        init_w = _f.measure(text) + 32   # padding horizontal

        try:
            parent_bg = parent.cget("bg")
        except Exception:
            parent_bg = C["bg"]

        super().__init__(
            parent,
            bg=parent_bg,
            highlightthickness=0,
            height=self._HEIGHT,
            width=init_w,
            cursor="hand2",
        )
        self._text_str = text
        self._command  = command
        self._bg       = C[color]
        self._bg_hover = _lighten(C[color])
        self._hovering = False
        self._enabled  = True

        self.bind("<Configure>", lambda e: self._redraw())
        self.bind("<Button-1>",  lambda e: self._on_click())
        self.bind("<Enter>",     lambda e: self._set_hover(True))
        self.bind("<Leave>",     lambda e: self._set_hover(False))

    def _draw_bg(self, w, h, fill):
        r = self._RADIUS
        x1, y1, x2, y2 = 0, 0, w, h
        pts = [
            x1+r, y1,   x2-r, y1,
            x2,   y1,   x2,   y1+r,
            x2,   y2-r, x2,   y2,
            x2-r, y2,   x1+r, y2,
            x1,   y2,   x1,   y2-r,
            x1,   y1+r, x1,   y1,
        ]
        self.create_polygon(pts, smooth=True, fill=fill, outline="")

    def _redraw(self):
        self.delete("all")
        w = self.winfo_width()  or int(self["width"])
        h = self.winfo_height() or self._HEIGHT
        if w < 4 or h < 4:
            return
        fill = self._bg_hover if (self._hovering and self._enabled) else self._bg
        self._draw_bg(w, h, fill)
        fg = C["text"] if self._enabled else C["text2"]
        self.create_text(w // 2, h // 2, text=self._text_str,
                         fill=fg, font=F["body_b"], anchor="center")

    def _set_hover(self, h: bool):
        if self._enabled:
            self._hovering = h
            self._redraw()

    def _on_click(self):
        if self._enabled and self._command:
            self._command()

    # ── API pública ──────────────────────────────────────────────────────────

    def set_text(self, text: str):
        """Actualiza el texto del botón y lo redibuja."""
        self._text_str = text
        self._redraw()

    def set_bg(self, color_hex: str):
        """Cambia el color de fondo directo (hex) y lo redibuja."""
        self._bg = color_hex
        self._bg_hover = _lighten(color_hex)
        self._redraw()

    def set_enabled(self, enabled: bool):
        """Habilita o deshabilita el botón."""
        self._enabled  = enabled
        self._hovering = False
        self._redraw()


class SidebarNavBtn(tk.Canvas):
    """
    Botón de navegación lateral con esquinas muy redondeadas.

    Implementado sobre un Canvas para poder dibujar un rectángulo
    redondeado propio, ya que tk.Button no soporta border-radius nativo.
    Gestiona internamente los estados: normal, hover y activo.
    """

    _HEIGHT = 42        # Altura fija del botón en píxeles
    _RADIUS = 16        # Radio del redondeo de las esquinas (más redondeado)
    _PAD_X  = 14        # Margen izquierdo del texto

    def __init__(self, parent, text: str, command, **kwargs):
        super().__init__(
            parent,
            bg=C["sidebar"],
            highlightthickness=0,
            height=self._HEIGHT,
            cursor="hand2",
            **kwargs,
        )
        self._text_str = text
        self._command  = command
        self._is_active  = False
        self._is_hovering = False

        # Eventos
        self.bind("<Configure>",  lambda e: self._redraw())
        self.bind("<Button-1>",   lambda e: self._command())
        self.bind("<Enter>",      lambda e: self._set_hover(True))
        self.bind("<Leave>",      lambda e: self._set_hover(False))

    # ── Dibujo ───────────────────────────────────────────────────────────────

    def _colors(self):
        """Devuelve (fondo, texto) según el estado actual."""
        if self._is_active:
            return C["btn_primary"], C["text"]
        if self._is_hovering:
            return C["accent"], C["text"]
        return C["sidebar"], C["text2"]

    def _redraw(self):
        """Redibujar el botón completo sobre el canvas."""
        self.delete("all")
        w = self.winfo_width()
        h = self.winfo_height()
        if w < 4 or h < 4:
            return

        bg, fg = self._colors()
        r = self._RADIUS

        # Dibujar fondo redondeado solo cuando hay color visible
        if self._is_active or self._is_hovering:
            x1, y1, x2, y2 = 4, 2, w - 4, h - 2
            # Polígono con smooth=True produce curvas de Bézier → esquinas redondas
            pts = [
                x1 + r, y1,   x2 - r, y1,   # borde superior
                x2,     y1,   x2,     y1 + r,  # esquina sup-der
                x2,     y2 - r, x2,   y2,    # borde derecho
                x2 - r, y2,   x1 + r, y2,   # borde inferior
                x1,     y2,   x1,     y2 - r,  # esquina inf-izq
                x1,     y1 + r, x1,   y1,    # borde izquierdo
            ]
            self.create_polygon(pts, smooth=True, fill=bg, outline="")

        # Texto del botón
        self.create_text(
            self._PAD_X, h // 2,
            text=self._text_str,
            fill=fg,
            font=F["sidebar"],
            anchor="w",
        )

    # ── Estado ───────────────────────────────────────────────────────────────

    def _set_hover(self, entering: bool):
        if not self._is_active:
            self._is_hovering = entering
            self._redraw()

    def set_active(self, active: bool):
        """Marca el botón como seleccionado (activo) o no."""
        self._is_active   = active
        self._is_hovering = False
        self._redraw()


def entry(parent, **kwargs):
    """
    Crea un campo de entrada de texto estilizado con borde resaltado al ganar el foco.
    """
    e = tk.Entry(
        parent,
        bg=C["panel"], fg=C["text"],
        insertbackground=C["text"],
        relief="flat", bd=0,
        font=F["body"],
        highlightthickness=1,
        highlightcolor=C["accent"],
        highlightbackground=C["border"],
        **kwargs
    )
    return e


def label(parent, texto="", size="body", color="text", **kwargs):
    """
    Crea una etiqueta de texto (Label) con opciones de tamaño y color predefinidos.
    """
    return tk.Label(
        parent, text=texto,
        bg=kwargs.pop("bg", C["card"]),
        fg=C[color],
        font=F[size],
        **kwargs
    )


def card(parent, **kwargs):
    """
    Crea un contenedor (Frame) con el estilo de 'tarjeta' para organizar secciones.
    """
    return tk.Frame(parent, bg=C["card"], padx=16, pady=12, **kwargs)


def separador_h(parent, pady=8):
    """
    Genera una línea horizontal discreta para separar elementos visuales.
    """
    f = tk.Frame(parent, bg=C["border"], height=1)
    f.pack(fill="x", pady=pady)
    return f


def _lighten(hex_color: str) -> str:
    """
    Aclara un color hexadecimal para simular un efecto de iluminación.
    """
    try:
        r = int(hex_color[1:3], 16)
        g = int(hex_color[3:5], 16)
        b = int(hex_color[5:7], 16)
        r = min(255, r + 25)
        g = min(255, g + 25)
        b = min(255, b + 25)
        return f"#{r:02x}{g:02x}{b:02x}"
    except Exception:
        return hex_color
