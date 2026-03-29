"""
main_window.py — Ventana principal con sidebar y enrutador de páginas.
"""

import customtkinter as ctk
from tkinter import messagebox
from app.theme import COLORS, FONTS, NAV_ITEMS


class MainWindow(ctk.CTk):
    def __init__(self, db, user: dict):
        super().__init__()
        self.db = db
        self.user = user
        self.nav_buttons = {}

        self.title("GSC S.A.S. — Gestión Solar del Caribe")
        self.geometry("1280x720")
        self.configure(fg_color=COLORS["bg_primary"])
        self._centrar(1280, 720)

        self._construir_sidebar()

        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.pack(side="right", fill="both", expand=True)

        self._navegar("dashboard")

    def _centrar(self, w, h):
        self.update_idletasks()
        x = (self.winfo_screenwidth() - w) // 2
        y = (self.winfo_screenheight() - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")

    # ─── SIDEBAR ──────────────────────────────────────────────────────────────

    def _construir_sidebar(self):
        sb = ctk.CTkFrame(
            self, width=240,
            fg_color=COLORS["sidebar_bg"],
            corner_radius=0,
            border_width=1,
            border_color=COLORS["border_primary"],
        )
        sb.pack(side="left", fill="y")
        sb.pack_propagate(False)

        # Logo
        ctk.CTkLabel(sb, text="☀", font=("Segoe UI Emoji", 40),
                     text_color=COLORS["solar_yellow"]).pack(pady=(28, 0))
        ctk.CTkLabel(sb, text="SOLAR CARIBE",
                     font=FONTS["title_medium"],
                     text_color=COLORS["accent_primary"]).pack(pady=(2, 28))

        # Botones nav
        for item in NAV_ITEMS:
            btn = ctk.CTkButton(
                sb,
                text=f"  {item['icon']}   {item['label']}",
                font=FONTS["body_large"],
                height=46,
                fg_color="transparent",
                text_color=COLORS["text_secondary"],
                hover_color=COLORS["bg_hover"],
                anchor="w",
                corner_radius=8,
                command=lambda k=item["id"]: self._navegar(k),
            )
            btn.pack(fill="x", padx=12, pady=3)
            self.nav_buttons[item["id"]] = btn

        # Footer usuario
        footer = ctk.CTkFrame(sb, fg_color="transparent")
        footer.pack(side="bottom", fill="x", pady=20, padx=12)
        ctk.CTkFrame(footer, height=1,
                     fg_color=COLORS["border_primary"]).pack(fill="x", pady=(0, 12))
        ctk.CTkLabel(footer,
                     text=self.user.get("nombre_completo", "Usuario"),
                     font=FONTS["body_medium"],
                     text_color=COLORS["text_primary"]).pack(anchor="w")
        ctk.CTkLabel(footer, text="● Sesión activa",
                     font=FONTS["caption"],
                     text_color=COLORS["success"]).pack(anchor="w")
        ctk.CTkButton(
            footer, text="⏻  Cerrar sesión",
            height=32, fg_color="transparent",
            hover_color=COLORS["danger"],
            text_color=COLORS["text_secondary"],
            font=FONTS["body_small"],
            command=self._cerrar_sesion,
        ).pack(fill="x", pady=(10, 0))

    # ─── NAVEGACIÓN ───────────────────────────────────────────────────────────

    def _navegar(self, key: str):
        for k, b in self.nav_buttons.items():
            if k == key:
                b.configure(fg_color=COLORS["bg_hover"],
                            text_color=COLORS["accent_primary"])
            else:
                b.configure(fg_color="transparent",
                            text_color=COLORS["text_secondary"])

        for child in self.container.winfo_children():
            child.destroy()

        try:
            page = self._crear_pagina(key)
            if page:
                page.pack(fill="both", expand=True)
        except Exception as e:
            messagebox.showerror("Error de navegación",
                                 f"No se pudo cargar '{key}':\n{e}")

    def _crear_pagina(self, key: str):
        if key == "dashboard":
            from app.ui.dashboard import DashboardPage
            return DashboardPage(self.container, self.db)
        if key == "clientes":
            from app.ui.clientes import ClientesPage
            return ClientesPage(self.container, self.db)
        if key == "proyectos":
            from app.ui.proyectos import ProyectosPage
            return ProyectosPage(self.container, self.db)
        if key == "consumos":
            from app.ui.consumos import ConsumosPage
            return ConsumosPage(self.container, self.db)
        if key == "mantenimientos":
            from app.ui.mantenimientos import MantenimientosPage
            return MantenimientosPage(self.container, self.db)
        if key == "expediente":
            from app.ui.expediente import ExpedientePage
            return ExpedientePage(self.container, self.db)
        if key == "exportar":
            from app.ui.exportar_page import ExportarPage
            return ExportarPage(self.container, self.db)
        # fallback
        lbl = ctk.CTkLabel(self.container,
                            text=f"Módulo '{key}' próximamente…",
                            font=FONTS["title_medium"])
        lbl.pack(expand=True)
        return lbl

    def _cerrar_sesion(self):
        if messagebox.askyesno("Cerrar sesión", "¿Desea cerrar la sesión?"):
            self.destroy()
            from app.ui.login_window import LoginWindow
            LoginWindow(self.db).mainloop()
