"""
widgets.py — Componentes reutilizables para GSC.
"""

import customtkinter as ctk
from app.theme import COLORS, FONTS
from typing import Optional, Callable, List


class FormField(ctk.CTkFrame):
    """Label + Entry en una sola unidad."""

    def __init__(self, parent, label: str, placeholder: str = "",
                 required: bool = False, **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)
        self.required = required

        ctk.CTkLabel(
            self,
            text=f"{label} {'*' if required else ''}",
            font=FONTS["label"],
            text_color=COLORS["text_secondary"],
        ).pack(anchor="w")

        self.entry = ctk.CTkEntry(
            self,
            placeholder_text=placeholder,
            height=36,
            fg_color=COLORS["bg_input"],
            border_color=COLORS["border_primary"],
            text_color=COLORS["text_primary"],
            font=FONTS["body_medium"],
        )
        self.entry.pack(fill="x", pady=(3, 0))

    def get(self) -> str:
        return self.entry.get().strip()

    def set(self, value):
        self.entry.delete(0, "end")
        if value is not None:
            self.entry.insert(0, str(value))

    def clear(self):
        self.entry.delete(0, "end")

    def validate(self) -> bool:
        ok = not self.required or bool(self.get())
        self.entry.configure(
            border_color=COLORS["border_primary"] if ok else COLORS["danger"]
        )
        return ok


class ActionButton(ctk.CTkButton):
    """Botón de acción con variantes de color."""

    _VARIANTS = {
        "primary": (COLORS["accent_primary"], COLORS["accent_hover"], "#000000"),
        "danger":  (COLORS["danger"],         "#C0392B",              "#FFFFFF"),
        "ghost":   ("transparent",            COLORS["bg_hover"],     COLORS["text_primary"]),
        "info":    (COLORS["info"],           "#3A7BD5",              "#FFFFFF"),
        "warning": (COLORS["warning"],        "#B8860B",              "#000000"),
    }

    def __init__(self, parent, text: str, command=None,
                 variant: str = "primary", **kwargs):
        fg, hover, txt = self._VARIANTS.get(variant, self._VARIANTS["primary"])
        super().__init__(
            parent, text=text, command=command,
            height=36, corner_radius=8,
            fg_color=fg, hover_color=hover,
            text_color=txt, font=FONTS["body_medium"],
            **kwargs,
        )


class SectionTitle(ctk.CTkLabel):
    """Título de sección con acento verde."""

    def __init__(self, parent, text: str, **kwargs):
        super().__init__(
            parent, text=text,
            font=FONTS["title_small"],
            text_color=COLORS["accent_primary"],
            **kwargs,
        )


class KPICard(ctk.CTkFrame):
    """Tarjeta de indicador numérico para el Dashboard."""

    def __init__(self, parent, titulo: str, valor: str, subtexto: str = "",
                 color_acento: str = COLORS["accent_primary"], icono: str = "📊",
                 **kwargs):
        super().__init__(
            parent,
            fg_color=COLORS["bg_card"],
            corner_radius=12,
            border_width=1,
            border_color=COLORS["border_primary"],
            **kwargs,
        )
        inner = ctk.CTkFrame(self, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=20, pady=16)

        top = ctk.CTkFrame(inner, fg_color="transparent")
        top.pack(fill="x")
        ctk.CTkLabel(top, text=icono,
                     font=("Segoe UI Emoji", 18),
                     text_color=color_acento).pack(side="left", padx=(0, 8))
        ctk.CTkLabel(top, text=titulo.upper(),
                     font=FONTS["caption"],
                     text_color=COLORS["text_secondary"]).pack(side="left")

        self.value_label = ctk.CTkLabel(
            inner, text=valor,
            font=FONTS["kpi"],
            text_color=color_acento,
        )
        self.value_label.pack(anchor="w", pady=(5, 0))

        footer = ctk.CTkFrame(inner, fg_color="transparent")
        footer.pack(fill="x", pady=(5, 0))
        ctk.CTkFrame(footer, width=20, height=3, fg_color=color_acento).pack(
            side="left", padx=(0, 8)
        )
        ctk.CTkLabel(footer, text=subtexto,
                     font=FONTS["caption"],
                     text_color=COLORS["text_muted"]).pack(side="left")

    def update_value(self, v: str):
        self.value_label.configure(text=v)


class PageHeader(ctk.CTkFrame):
    """Encabezado estándar de página."""

    def __init__(self, parent, titulo: str, subtitulo: str = "", **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)
        ctk.CTkLabel(self, text=titulo,
                     font=FONTS["title_large"],
                     text_color=COLORS["text_primary"]).pack(side="left", padx=(0, 12))
        if subtitulo:
            ctk.CTkLabel(self, text=subtitulo,
                         font=FONTS["body_medium"],
                         text_color=COLORS["text_secondary"]).pack(side="left", pady=(6, 0))


class StatusBadge(ctk.CTkLabel):
    """Badge coloreado según estado."""

    _MAP = {
        "success": (COLORS["success"], "#0D2818"),
        "warning": (COLORS["warning"], "#2A1E00"),
        "danger":  (COLORS["danger"],  "#2A0000"),
        "info":    (COLORS["info"],    "#0D1B2A"),
    }

    def __init__(self, parent, text: str, estado: str = "info", **kwargs):
        fg, bg = self._MAP.get(estado, self._MAP["info"])
        super().__init__(
            parent, text=f"  {text}  ",
            font=FONTS["body_small"],
            text_color=fg, fg_color=bg,
            corner_radius=4, **kwargs,
        )