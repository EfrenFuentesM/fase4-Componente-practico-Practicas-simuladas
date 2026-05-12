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
    Crea un botón personalizado con efectos de 'hover' (iluminación al pasar el mouse).
    """
    bg = C[color]
    b = tk.Button(
        parent, text=texto, command=comando,
        bg=bg, fg=C["text"],
        activebackground=C["accent"], activeforeground=C["text"],
        font=F["body_b"], relief="flat", bd=0,
        padx=12, pady=6, cursor="hand2",
        **kwargs
    )
    # Efectos visuales interactivos
    b.bind("<Enter>", lambda e: b.config(bg=_lighten(bg)))
    b.bind("<Leave>", lambda e: b.config(bg=bg))
    return b


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
