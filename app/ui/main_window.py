"""
main_window.py — Ventana principal con sidebar, header y panel de ajustes.
Versión 3.0 — Soporte para cambio de contraseña segura.
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

        self._construir_layout()
        self._navegar("dashboard")

    def _centrar(self, w, h):
        self.update_idletasks()
        x = (self.winfo_screenwidth() - w) // 2
        y = (self.winfo_screenheight() - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")

    # ─── LAYOUT PRINCIPAL ─────────────────────────────────────────────────────

    def _construir_layout(self):
        """Estructura: Sidebar (izq) + Header + Contenedor de páginas (dcha)"""
        # SIDEBAR
        self.sidebar = ctk.CTkFrame(
            self, width=240,
            fg_color=COLORS["sidebar_bg"],
            corner_radius=0,
            border_width=1,
            border_color=COLORS["border_primary"],
        )
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)
        self._construir_sidebar()

        # PANEL DERECHO (header + contenedor)
        right_panel = ctk.CTkFrame(self, fg_color="transparent")
        right_panel.pack(side="right", fill="both", expand=True)
        right_panel.columnconfigure(0, weight=1)
        right_panel.rowconfigure(0, weight=0)  # header fijo
        right_panel.rowconfigure(1, weight=1)  # contenido expandible

        # HEADER
        self._construir_header(right_panel)

        # CONTENEDOR DE PÁGINAS
        self.container = ctk.CTkFrame(right_panel, fg_color="transparent")
        self.container.grid(row=1, column=0, sticky="nsew", padx=0, pady=0)
        self.container.columnconfigure(0, weight=1)
        self.container.rowconfigure(0, weight=1)

    def _construir_sidebar(self):
        """Logo, nav items, footer con usuario."""
        # Logo
        ctk.CTkLabel(self.sidebar, text="☀", font=("Segoe UI Emoji", 40),
                     text_color=COLORS["solar_yellow"]).pack(pady=(28, 0))
        ctk.CTkLabel(self.sidebar, text="SOLAR CARIBE",
                     font=FONTS["title_medium"],
                     text_color=COLORS["accent_primary"]).pack(pady=(2, 28))

        # Separador
        ctk.CTkFrame(self.sidebar, height=1,
                     fg_color=COLORS["border_primary"]).pack(fill="x", padx=16, pady=(0, 14))

        # Botones de navegación
        for item in NAV_ITEMS:
            btn = ctk.CTkButton(
                self.sidebar,
                text=f"  {item['icon']}   {item['label']}",
                font=FONTS["body_large"],
                height=44,
                fg_color="transparent",
                text_color=COLORS["text_secondary"],
                hover_color=COLORS["bg_hover"],
                anchor="w",
                corner_radius=8,
                command=lambda k=item["id"]: self._navegar(k),
            )
            btn.pack(fill="x", padx=12, pady=4)
            self.nav_buttons[item["id"]] = btn

        # FOOTER usuario
        footer = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        footer.pack(side="bottom", fill="x", pady=16, padx=12)

        ctk.CTkFrame(footer, height=1,
                     fg_color=COLORS["border_primary"]).pack(fill="x", pady=(0, 12))

        ctk.CTkLabel(footer,
                     text=self.user.get("nombre_completo", "Usuario"),
                     font=FONTS["body_medium"],
                     text_color=COLORS["text_primary"]).pack(anchor="w")

        ctk.CTkLabel(footer, text="● Sesión activa",
                     font=FONTS["caption"],
                     text_color=COLORS["success"]).pack(anchor="w")

        # Botones footer
        btn_ajustes = ctk.CTkButton(
            footer, text="⚙  Ajustes",
            height=32, fg_color="transparent",
            hover_color=COLORS["bg_hover"],
            text_color=COLORS["text_secondary"],
            font=FONTS["body_small"],
            command=self._abrir_ajustes,
        )
        btn_ajustes.pack(fill="x", pady=(8, 4))

        btn_logout = ctk.CTkButton(
            footer, text="⏻  Cerrar sesión",
            height=32, fg_color="transparent",
            hover_color=COLORS["danger"],
            text_color=COLORS["text_secondary"],
            font=FONTS["body_small"],
            command=self._cerrar_sesion,
        )
        btn_logout.pack(fill="x")

    def _construir_header(self, parent):
        """Header con título dinámico de página actual."""
        header = ctk.CTkFrame(parent, fg_color=COLORS["bg_card"],
                               corner_radius=0, border_width=1,
                               border_color=COLORS["border_primary"],
                               height=60)
        header.grid(row=0, column=0, sticky="ew", padx=0, pady=0)
        header.pack_propagate(False)

        inner = ctk.CTkFrame(header, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=24, pady=12)
        inner.columnconfigure(0, weight=1)

        self.lbl_titulo = ctk.CTkLabel(
            inner, text="Dashboard",
            font=FONTS["title_medium"],
            text_color=COLORS["text_primary"])
        self.lbl_titulo.pack(side="left", anchor="w")

    # ─── NAVEGACIÓN ───────────────────────────────────────────────────────────

    def _navegar(self, key: str):
        # Actualizar estilos de botones
        for k, b in self.nav_buttons.items():
            if k == key:
                b.configure(fg_color=COLORS["bg_hover"],
                            text_color=COLORS["accent_primary"])
            else:
                b.configure(fg_color="transparent",
                            text_color=COLORS["text_secondary"])

        # Limpiar contenedor
        for child in self.container.winfo_children():
            child.destroy()

        # Actualizar título en header
        titulo_map = {
            "dashboard": "⚡ Dashboard",
            "clientes": "👤 Clientes",
            "proyectos": "🔧 Proyectos",
            "consumos": "📊 Consumo y Generación",
            "mantenimientos": "🛠 Mantenimientos",
            "expediente": "📁 Expedientes",
            "exportar": "📤 Exportar / Facturación",
        }
        self.lbl_titulo.configure(text=titulo_map.get(key, "Gestión Solar"))

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

    # ─── PANEL DE AJUSTES ──────────────────────────────────────────────────────

    def _abrir_ajustes(self):
        """Abre ventana modal de ajustes."""
        ventana = ctk.CTkToplevel(self)
        ventana.title("Ajustes de Seguridad")
        ventana.geometry("480x520")
        ventana.resizable(False, False)
        ventana.configure(fg_color=COLORS["bg_primary"])

        # Centrar ventana de ajustes respecto a main
        ventana.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() - 480) // 2
        y = self.winfo_y() + (self.winfo_height() - 520) // 2
        ventana.geometry(f"480x520+{x}+{y}")
        ventana.grab_set()

        # Contenido
        cont = ctk.CTkFrame(ventana, fg_color="transparent")
        cont.pack(fill="both", expand=True, padx=24, pady=20)

        # Título
        ctk.CTkLabel(cont, text="⚙  Ajustes de Seguridad",
                     font=FONTS["title_medium"],
                     text_color=COLORS["accent_primary"]).pack(anchor="w", pady=(0, 20))

        # Sección contraseña
        ctk.CTkLabel(cont, text="Cambiar Contraseña",
                     font=FONTS["title_small"],
                     text_color=COLORS["text_primary"]).pack(anchor="w", pady=(0, 12))

        frame_pwd = ctk.CTkFrame(cont, fg_color=COLORS["bg_card"],
                                  corner_radius=10, border_width=1,
                                  border_color=COLORS["border_primary"])
        frame_pwd.pack(fill="x", pady=(0, 20))

        inner_pwd = ctk.CTkFrame(frame_pwd, fg_color="transparent")
        inner_pwd.pack(fill="x", padx=16, pady=16)

        # Campo contraseña actual
        ctk.CTkLabel(inner_pwd, text="Contraseña Actual *",
                     font=FONTS["label"],
                     text_color=COLORS["text_secondary"]).pack(anchor="w")
        entry_actual = ctk.CTkEntry(
            inner_pwd, placeholder_text="Ingrese su contraseña actual",
            height=36, show="•",
            fg_color=COLORS["bg_input"],
            border_color=COLORS["border_primary"],
            text_color=COLORS["text_primary"],
            font=FONTS["body_medium"])
        entry_actual.pack(fill="x", pady=(3, 12))

        # Campo contraseña nueva
        ctk.CTkLabel(inner_pwd, text="Contraseña Nueva *",
                     font=FONTS["label"],
                     text_color=COLORS["text_secondary"]).pack(anchor="w")
        entry_nueva = ctk.CTkEntry(
            inner_pwd, placeholder_text="Mínimo 8 caracteres",
            height=36, show="•",
            fg_color=COLORS["bg_input"],
            border_color=COLORS["border_primary"],
            text_color=COLORS["text_primary"],
            font=FONTS["body_medium"])
        entry_nueva.pack(fill="x", pady=(3, 12))

        # Campo confirmar
        ctk.CTkLabel(inner_pwd, text="Confirmar Nueva Contraseña *",
                     font=FONTS["label"],
                     text_color=COLORS["text_secondary"]).pack(anchor="w")
        entry_confirma = ctk.CTkEntry(
            inner_pwd, placeholder_text="Repita la nueva contraseña",
            height=36, show="•",
            fg_color=COLORS["bg_input"],
            border_color=COLORS["border_primary"],
            text_color=COLORS["text_primary"],
            font=FONTS["body_medium"])
        entry_confirma.pack(fill="x", pady=(3, 0))

        # Mensaje info
        ctk.CTkLabel(inner_pwd, text="📝  Usa mayúsculas, números y símbolos para mayor seguridad.",
                     font=FONTS["caption"],
                     text_color=COLORS["info"],
                     wraplength=400).pack(anchor="w", pady=(12, 0))

        # Botones
        btn_frame = ctk.CTkFrame(cont, fg_color="transparent")
        btn_frame.pack(fill="x")

        def cambiar_pwd():
            actual = entry_actual.get()
            nueva = entry_nueva.get()
            confirma = entry_confirma.get()

            if not actual or not nueva or not confirma:
                messagebox.showwarning("Validación",
                                       "Complete todos los campos.")
                return

            if len(nueva) < 8:
                messagebox.showwarning("Seguridad",
                                       "La contraseña debe tener al menos 8 caracteres.")
                return

            if nueva != confirma:
                messagebox.showerror("Error",
                                     "Las contraseñas nuevas no coinciden.")
                return

            # Cambiar en BD
            exito, msg = self.db.cambiar_contrasena(
                self.user["id"], actual, nueva)

            if exito:
                messagebox.showinfo("Éxito",
                                    "Contraseña actualizada correctamente.")
                ventana.destroy()
            else:
                messagebox.showerror("Error", msg)

        ctk.CTkButton(btn_frame, text="💾  Guardar Cambios",
                      height=38,
                      fg_color=COLORS["accent_primary"],
                      hover_color=COLORS["accent_hover"],
                      text_color="#000000",
                      font=FONTS["body_medium"],
                      command=cambiar_pwd).pack(side="left", padx=(0, 8))

        ctk.CTkButton(btn_frame, text="✗  Cancelar",
                      height=38,
                      fg_color="transparent",
                      hover_color=COLORS["bg_hover"],
                      text_color=COLORS["text_secondary"],
                      font=FONTS["body_medium"],
                      command=ventana.destroy).pack(side="left")

    # ─── CERRAR SESIÓN ────────────────────────────────────────────────────────

    def _cerrar_sesion(self):
        if messagebox.askyesno("Cerrar sesión", "¿Desea cerrar la sesión?"):
            self.destroy()
            from app.ui.login_window import LoginWindow
            LoginWindow(self.db).mainloop()