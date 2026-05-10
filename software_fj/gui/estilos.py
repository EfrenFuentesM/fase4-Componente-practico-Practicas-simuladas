"""estilos.py - Paleta de colores, fuentes y estilos ttk para Software FJ GUI"""
import tkinter as tk
from tkinter import ttk

# ── Paleta de colores ────────────────────────────────────────────────────────
C = {
    "bg":           "#0d1117",
    "sidebar":      "#161b22",
    "card":         "#21262d",
    "panel":        "#2d333b",
    "accent":       "#58a6ff",
    "success":      "#3fb950",
    "warning":      "#d29922",
    "error":        "#f85149",
    "text":         "#e6edf3",
    "text2":        "#8b949e",
    "border":       "#30363d",
    "btn_primary":  "#1f6feb",
    "btn_success":  "#238636",
    "btn_danger":   "#da3633",
    "btn_warning":  "#9e6a03",
    "btn_neutral":  "#30363d",
    "row_even":     "#21262d",
    "row_odd":      "#1c2128",
    "row_sel":      "#1f4f8f",
}

# ── Fuentes ──────────────────────────────────────────────────────────────────
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
    """Configura los estilos ttk globales."""
    s = ttk.Style(root)
    s.theme_use("clam")

    # ── Treeview ─────────────────────────────────────────────────────────────
    s.configure("Dark.Treeview",
        background=C["card"], foreground=C["text"],
        fieldbackground=C["card"], rowheight=28,
        font=F["body"], borderwidth=0, relief="flat",
    )
    s.configure("Dark.Treeview.Heading",
        background=C["panel"], foreground=C["accent"],
        font=F["body_b"], relief="flat", borderwidth=0, padding=(8, 6),
    )
    s.map("Dark.Treeview",
        background=[("selected", C["row_sel"])],
        foreground=[("selected", C["text"])],
    )
    s.map("Dark.Treeview.Heading",
        background=[("active", C["border"])],
    )

    # ── Scrollbar ─────────────────────────────────────────────────────────────
    s.configure("Dark.Vertical.TScrollbar",
        background=C["panel"], troughcolor=C["card"],
        arrowcolor=C["text2"], borderwidth=0, width=10,
    )
    s.configure("Dark.Horizontal.TScrollbar",
        background=C["panel"], troughcolor=C["card"],
        arrowcolor=C["text2"], borderwidth=0, width=10,
    )

    # ── Combobox ──────────────────────────────────────────────────────────────
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
    """Crea un botón estilizado con el tema oscuro."""
    bg = C[color]
    b = tk.Button(
        parent, text=texto, command=comando,
        bg=bg, fg=C["text"],
        activebackground=C["accent"], activeforeground=C["text"],
        font=F["body_b"], relief="flat", bd=0,
        padx=12, pady=6, cursor="hand2",
        **kwargs
    )
    b.bind("<Enter>", lambda e: b.config(bg=_lighten(bg)))
    b.bind("<Leave>", lambda e: b.config(bg=bg))
    return b


def entry(parent, **kwargs):
    """Crea un Entry estilizado."""
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
    """Crea un Label estilizado."""
    return tk.Label(
        parent, text=texto,
        bg=kwargs.pop("bg", C["card"]),
        fg=C[color],
        font=F[size],
        **kwargs
    )


def card(parent, **kwargs):
    """Crea un Frame con apariencia de tarjeta."""
    return tk.Frame(parent, bg=C["card"], padx=16, pady=12, **kwargs)


def separador_h(parent, pady=8):
    """Línea separadora horizontal."""
    f = tk.Frame(parent, bg=C["border"], height=1)
    f.pack(fill="x", pady=pady)
    return f


def _lighten(hex_color: str) -> str:
    """Aclara ligeramente un color hexadecimal."""
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
