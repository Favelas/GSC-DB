"""
GESTIÓN SOLAR DEL CARIBE S.A.S.
Widgets reutilizables y estilizados para la interfaz de usuario.
"""

import customtkinter as ctk
from app.theme import COLORS, FONTS
from typing import Optional, Callable, List


class PageHeader(ctk.CTkFrame):
    """Encabezado estándar de página con título y subtítulo."""
    def __init__(self, parent, titulo: str, subtitulo: str = "", **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)

        ctk.CTkLabel(
            self, text=titulo.upper(),
            font=FONTS["title_large"],
            text_color=COLORS["text_primary"]
        ).pack(side="left", padx=(0, 12))

        if subtitulo:
            ctk.CTkLabel(
                self, text=subtitulo,
                font=FONTS["body_medium"],
                text_color=COLORS["text_secondary"]
            ).pack(side="left", pady=(6, 0))


class KPICard(ctk.CTkFrame):
    """Tarjeta de indicador KPI con diseño de acento GSC."""
    def __init__(self, parent, titulo: str, valor: str, subtexto: str = "",
                 color_acento: str = COLORS["accent_primary"], icono: str = "📊", **kwargs):
        super().__init__(
            parent,
            fg_color=COLORS["bg_card"],
            corner_radius=12,
            border_width=1,
            border_color=COLORS["border_primary"],
            **kwargs
        )

        inner = ctk.CTkFrame(self, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=20, pady=16)

        # Fila superior: ícono + título
        top_row = ctk.CTkFrame(inner, fg_color="transparent")
        top_row.pack(fill="x")

        ctk.CTkLabel(
            top_row, text=icono,
            font=("Segoe UI Emoji", 18),
            text_color=color_acento
        ).pack(side="left", padx=(0, 8))

        ctk.CTkLabel(
            top_row, text=titulo.upper(),
            font=FONTS["caption"],
            text_color=COLORS["text_secondary"]
        ).pack(side="left")

        # Valor principal
        self.value_label = ctk.CTkLabel(
            inner, text=valor,
            font=FONTS["kpi"],
            text_color=COLORS["text_primary"]
        )
        self.value_label.pack(anchor="w", pady=(5, 0))

        # Fila inferior: Barra de acento + subtexto
        footer = ctk.CTkFrame(inner, fg_color="transparent")
        footer.pack(fill="x", pady=(5, 0))

        ctk.CTkFrame(footer, width=20, height=3, fg_color=color_acento).pack(side="left", padx=(0, 8))

        self.sub_label = ctk.CTkLabel(
            footer, text=subtexto,
            font=FONTS["caption"],
            text_color=COLORS["text_muted"]
        )
        self.sub_label.pack(side="left")

    def update_value(self, nuevo_valor):
        """Permite actualizar el KPI dinámicamente."""
        self.value_label.configure(text=nuevo_valor)


class DataTable(ctk.CTkFrame):
    """Tabla de datos optimizada para registros de clientes y proyectos."""
    def __init__(self, parent, columnas: List[str], anchos: Optional[List[int]] = None, **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)
        self.columnas = columnas
        self.anchos = anchos or [150] * len(columnas)
        self.on_select: Optional[Callable] = None
        self._construir()

    def _construir(self):
        header_frame = ctk.CTkFrame(self, fg_color=COLORS["bg_secondary"], corner_radius=6)
        header_frame.pack(fill="x", pady=(0, 4))

        for col, ancho in zip(self.columnas, self.anchos):
            ctk.CTkLabel(
                header_frame, text=col.upper(),
                font=FONTS["label"],
                text_color=COLORS["text_secondary"],
                width=ancho, anchor="w"
            ).pack(side="left", padx=12, pady=10)

        self.scroll_frame = ctk.CTkScroll