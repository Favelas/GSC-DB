"""
dashboard.py — Panel principal con KPIs reales y alertas de mantenimiento.
"""

import customtkinter as ctk
from app.theme import COLORS, FONTS
from app.ui.widgets import KPICard


class DashboardPage(ctk.CTkFrame):
    def __init__(self, parent, db):
        super().__init__(parent, fg_color="transparent")
        self.db = db
        self._construir_ui()
        self._cargar()

    def _construir_ui(self):
        cont = ctk.CTkFrame(self, fg_color="transparent")
        cont.pack(fill="both", expand=True, padx=28, pady=20)

        # ── Encabezado ────────────────────────────────────────────
        hdr = ctk.CTkFrame(cont, fg_color="transparent")
        hdr.pack(fill="x", pady=(0, 20))

        ctk.CTkLabel(hdr, text="⚡  Dashboard",
                     font=FONTS["title_large"],
                     text_color=COLORS["text_primary"]).pack(side="left")
        ctk.CTkButton(
            hdr, text="↻  Refrescar", width=110, height=32,
            fg_color=COLORS["bg_card"], hover_color=COLORS["bg_hover"],
            text_color=COLORS["text_secondary"], font=FONTS["body_small"],
            command=self._cargar,
        ).pack(side="right")

        # ── KPIs ──────────────────────────────────────────────────
        kpi_row = ctk.CTkFrame(cont, fg_color="transparent")
        kpi_row.pack(fill="x", pady=(0, 20))
        kpi_row.columnconfigure((0, 1, 2, 3), weight=1)

        self.kpi_clientes = KPICard(kpi_row, "Clientes", "—",
                                     "Registros activos", icono="👤")
        self.kpi_clientes.grid(row=0, column=0, padx=6, sticky="nsew")

        self.kpi_kwp = KPICard(kpi_row, "kWp Instalados", "—",
                                "Capacidad total", icono="⚡",
                                color_acento=COLORS["solar_yellow"])
        self.kpi_kwp.grid(row=0, column=1, padx=6, sticky="nsew")

        self.kpi_proyectos = KPICard(kpi_row, "Proyectos", "—",
                                      "Instalaciones", icono="🔧",
                                      color_acento=COLORS["info"])
        self.kpi_proyectos.grid(row=0, column=2, padx=6, sticky="nsew")

        self.kpi_retie = KPICard(kpi_row, "RETIE Pendiente", "—",
                                  "Certificaciones", icono="⚠",
                                  color_acento=COLORS["warning"])
        self.kpi_retie.grid(row=0, column=3, padx=6, sticky="nsew")

        # ── Fila inferior ─────────────────────────────────────────
        bot = ctk.CTkFrame(cont, fg_color="transparent")
        bot.pack(fill="both", expand=True)
        bot.columnconfigure(0, weight=3)
        bot.columnconfigure(1, weight=1)

        # Panel alertas
        alertas_card = ctk.CTkFrame(bot, fg_color=COLORS["bg_card"],
                                     corner_radius=12, border_width=1,
                                     border_color=COLORS["border_primary"])
        alertas_card.grid(row=0, column=0, sticky="nsew", padx=(0, 8))

        ah = ctk.CTkFrame(alertas_card, fg_color="transparent")
        ah.pack(fill="x", padx=20, pady=(16, 4))
        ctk.CTkLabel(ah, text="⚠  Mantenimientos Vencidos (+6 meses)",
                     font=FONTS["title_small"],
                     text_color=COLORS["warning"]).pack(side="left")
        self.badge = ctk.CTkLabel(ah, text="0", font=FONTS["body_small"],
                                   text_color=COLORS["warning"],
                                   fg_color="#2A1E00", corner_radius=10, width=26)
        self.badge.pack(side="left", padx=8)

        self.scroll_alertas = ctk.CTkScrollableFrame(
            alertas_card, fg_color="transparent", height=240)
        self.scroll_alertas.pack(fill="both", expand=True, padx=12, pady=(0, 12))

        # Panel accesos rápidos
        acc_card = ctk.CTkFrame(bot, fg_color=COLORS["bg_card"],
                                 corner_radius=12, border_width=1,
                                 border_color=COLORS["border_primary"])
        acc_card.grid(row=0, column=1, sticky="nsew", padx=(8, 0))
        ctk.CTkLabel(acc_card, text="🚀  Accesos Rápidos",
                     font=FONTS["title_small"],
                     text_color=COLORS["accent_primary"]).pack(anchor="w", padx=20, pady=(16, 10))

        self._acc_parent = acc_card  # guardamos para luego inyectar navegación

    def _cargar(self):
        try:
            kpis = self.db.obtener_kpis()
            self.kpi_clientes.update_value(str(kpis["clientes"]))
            self.kpi_kwp.update_value(f"{kpis['kwp']} kWp")
            self.kpi_proyectos.update_value(str(kpis["proyectos"]))
            self.kpi_retie.update_value(str(kpis["retie_pend"]))

            alertas = kpis.get("alertas", [])
            self.badge.configure(text=str(len(alertas)))

            for w in self.scroll_alertas.winfo_children():
                w.destroy()

            if not alertas:
                ctk.CTkLabel(self.scroll_alertas,
                             text="✓  Todos los sistemas al día",
                             font=FONTS["body_medium"],
                             text_color=COLORS["success"]).pack(pady=20)
            else:
                for a in alertas:
                    self._fila_alerta(a)
        except Exception as e:
            print(f"[Dashboard] Error: {e}")

    def _fila_alerta(self, a: dict):
        f = ctk.CTkFrame(self.scroll_alertas, fg_color=COLORS["bg_secondary"],
                          corner_radius=6)
        f.pack(fill="x", pady=2, padx=4)

        ctk.CTkLabel(f, text="⚠", font=("Segoe UI Emoji", 14),
                     text_color=COLORS["warning"], width=28).pack(side="left", padx=(10, 4), pady=8)

        info = ctk.CTkFrame(f, fg_color="transparent")
        info.pack(side="left", fill="x", expand=True, pady=6)

        ctk.CTkLabel(info, text=a.get("nombre_titular", "N/A"),
                     font=FONTS["label"],
                     text_color=COLORS["text_primary"]).pack(anchor="w")
        ultimo = a.get("ultimo_mant", "Nunca")
        ctk.CTkLabel(info,
                     text=f"Último mant: {ultimo or 'Sin registro'}  |  Tel: {a.get('telefono','N/A')}",
                     font=FONTS["caption"],
                     text_color=COLORS["text_muted"]).pack(anchor="w")
