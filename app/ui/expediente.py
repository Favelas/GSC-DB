"""
expediente.py — Expediente completo del cliente v3.0
Optimización: layouts expandibles, mejor rendimiento visual.
"""

import customtkinter as ctk
from tkinter import messagebox
from app.theme import COLORS, FONTS
from app.ui.widgets import ActionButton


class ExpedientePage(ctk.CTkFrame):
    def __init__(self, parent, db):
        super().__init__(parent, fg_color="transparent")
        self.db = db
        self.cliente_sel = None
        self._construir_ui()

    def _construir_ui(self):
        cont = ctk.CTkFrame(self, fg_color="transparent")
        cont.pack(fill="both", expand=True, padx=24, pady=16)

        ctk.CTkLabel(cont, text="Expediente del Cliente",
                     font=FONTS["title_large"],
                     text_color=COLORS["text_primary"]).pack(anchor="w", pady=(0, 14))

        main = ctk.CTkFrame(cont, fg_color="transparent")
        main.pack(fill="both", expand=True)
        main.columnconfigure(0, weight=1)
        main.columnconfigure(1, weight=3)
        main.rowconfigure(0, weight=1)

        # Selector
        sel = ctk.CTkFrame(main, fg_color=COLORS["bg_card"],
                            corner_radius=12, border_width=1,
                            border_color=COLORS["border_primary"])
        sel.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        sel.rowconfigure(2, weight=1)

        ctk.CTkLabel(sel, text="Seleccionar Cliente",
                     font=FONTS["title_small"],
                     text_color=COLORS["text_secondary"]).pack(
                         anchor="w", padx=16, pady=(14, 6))

        self.entry_busq = ctk.CTkEntry(
            sel, placeholder_text="🔍  Buscar…",
            height=32, fg_color=COLORS["bg_input"],
            border_color=COLORS["border_primary"],
            text_color=COLORS["text_primary"], font=FONTS["body_small"])
        self.entry_busq.pack(fill="x", padx=12, pady=(0, 8))
        self.entry_busq.bind("<KeyRelease>",
                              lambda e: self._cargar_lista())

        self.lista = ctk.CTkScrollableFrame(sel, fg_color="transparent")
        self.lista.pack(fill="both", expand=True, padx=8, pady=(0, 12))
        self._cargar_lista()

        # Expediente
        self.exp_panel = ctk.CTkScrollableFrame(
            main, fg_color=COLORS["bg_card"], corner_radius=12)
        self.exp_panel.grid(row=0, column=1, sticky="nsew", padx=(8, 0))
        self._placeholder()

    def _cargar_lista(self):
        busq = self.entry_busq.get()
        clientes = self.db.obtener_clientes(busq)
        for w in self.lista.winfo_children():
            w.destroy()
        for c in clientes:
            item = ctk.CTkFrame(self.lista, fg_color=COLORS["bg_secondary"],
                                corner_radius=6, cursor="hand2")
            item.pack(fill="x", pady=2, padx=2)
            ctk.CTkLabel(item, text=c["nombre_titular"],
                         font=FONTS["label"],
                         text_color=COLORS["text_primary"]).pack(
                             anchor="w", padx=10, pady=(6, 0))
            ctk.CTkLabel(item, text=f"CC: {c['cedula_nit']}",
                         font=FONTS["caption"],
                         text_color=COLORS["text_muted"]).pack(
                             anchor="w", padx=10, pady=(0, 6))
            for w in [item] + item.winfo_children():
                w.bind("<Button-1>",
                        lambda e, obj=c: self._cargar_exp(obj))

    def _placeholder(self):
        for w in self.exp_panel.winfo_children():
            w.destroy()
        ctk.CTkLabel(
            self.exp_panel,
            text="☀  Seleccione un cliente",
            font=FONTS["title_small"],
            text_color=COLORS["text_muted"]).pack(expand=True, pady=100)

    def _cargar_exp(self, cliente: dict):
        self.cliente_sel = cliente
        for w in self.exp_panel.winfo_children():
            w.destroy()

        inner = ctk.CTkFrame(self.exp_panel, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=20, pady=16)

        # Datos cliente
        ctk.CTkLabel(inner, text=cliente["nombre_titular"],
                     font=FONTS["title_large"],
                     text_color=COLORS["text_primary"]).pack(anchor="w")
        ctk.CTkLabel(inner,
                     text=(f"CC/NIT: {cliente['cedula_nit']}  |  "
                           f"Tel: {cliente.get('telefono','N/A')}"),
                     font=FONTS["body_small"],
                     text_color=COLORS["text_muted"]).pack(anchor="w", pady=(2, 0))
        ctk.CTkLabel(inner,
                     text=(f"📍 {cliente.get('direccion_completa','N/A')} — "
                           f"{cliente.get('barrio_sector','')}  |  "
                           f"Estrato {cliente.get('estrato','?')}"),
                     font=FONTS["body_small"],
                     text_color=COLORS["text_secondary"]).pack(anchor="w", pady=(0, 12))
        ctk.CTkLabel(inner,
                     text=(f"Tarifa Air-e: ${cliente.get('tarifa_aire_actual',0):,.0f}/kWh  |  "
                           f"Tarifa GSC: ${cliente.get('tarifa_gsc',0):,.0f}/kWh"),
                     font=FONTS["body_small"],
                     text_color=COLORS["accent_primary"]).pack(anchor="w", pady=(0, 12))

        ctk.CTkFrame(inner, height=1,
                      fg_color=COLORS["border_primary"]).pack(fill="x", pady=(0, 14))

        # Proyecto
        proyectos = self.db.obtener_proyectos(cliente["id"])
        if proyectos:
            p = proyectos[0]
            self._seccion_proyecto(inner, p)

        # Gráfico
        historial = self.db.obtener_datos_grafico_cliente(cliente["id"])
        if historial:
            self._seccion_grafico(inner, historial)

        # Mantenimientos
        if proyectos:
            mants = self.db.obtener_mantenimientos(proyectos[0]["id"])
            if mants:
                self._seccion_mantenimientos(inner, mants)

    def _seccion_proyecto(self, parent, p: dict):
        card = ctk.CTkFrame(parent, fg_color=COLORS["bg_secondary"],
                             corner_radius=10)
        card.pack(fill="x", pady=(0, 14))

        hdr = ctk.CTkFrame(card, fg_color="transparent")
        hdr.pack(fill="x", padx=16, pady=(12, 6))
        ctk.CTkLabel(hdr, text="⚡  Sistema Solar Instalado",
                     font=FONTS["title_small"],
                     text_color=COLORS["accent_primary"]).pack(side="left")
        color_r = COLORS["success"] if p.get("estatus_retie") == "Certificado" \
            else COLORS["warning"]
        ctk.CTkLabel(hdr, text=f"RETIE: {p.get('estatus_retie','?')}",
                     font=FONTS["body_small"],
                     text_color=color_r).pack(side="right")

        g = ctk.CTkFrame(card, fg_color="transparent")
        g.pack(fill="x", padx=16)
        g.columnconfigure((0, 1, 2, 3), weight=1)

        kpis = [
            ("Capacidad",  f"{p.get('kwp_instalados','?')} kWp"),
            ("Inversor",   f"{p.get('marca_inversor','?')} {p.get('capacidad_inversor_kw','?')}kW"),
            ("Paneles",    p.get("marca_paneles", "N/A")),
            ("Instalado",  p.get("fecha_instalacion", "N/A")),
        ]
        for i, (t, v) in enumerate(kpis):
            f = ctk.CTkFrame(g, fg_color="transparent")
            f.grid(row=0, column=i, padx=8, pady=10, sticky="ew")
            ctk.CTkLabel(f, text=t, font=FONTS["caption"],
                         text_color=COLORS["text_muted"]).pack(anchor="w")
            ctk.CTkLabel(f, text=v, font=FONTS["label"],
                         text_color=COLORS["text_primary"]).pack(anchor="w")

        # Seriales
        if p.get("seriales_paneles"):
            ctk.CTkLabel(card,
                         text=f"Seriales paneles: {p['seriales_paneles']}",
                         font=FONTS["caption"],
                         text_color=COLORS["text_muted"],
                         wraplength=500).pack(anchor="w", padx=16, pady=(0, 4))
        if p.get("serial_inversor"):
            ctk.CTkLabel(card,
                         text=f"S/N inversor: {p['serial_inversor']}",
                         font=FONTS["caption"],
                         text_color=COLORS["text_muted"]).pack(anchor="w", padx=16)

        if p.get("ruta_fotos_entrega"):
            ActionButton(card, text="📂  Abrir Carpeta",
                         command=lambda: self._abrir(p["ruta_fotos_entrega"]),
                         variant="ghost").pack(anchor="w", padx=16, pady=(6, 12))
        else:
            ctk.CTkFrame(card, height=8,
                          fg_color="transparent").pack()

    def _seccion_grafico(self, parent, historial: list):
        gframe = ctk.CTkFrame(parent, fg_color=COLORS["bg_secondary"],
                               corner_radius=10)
        gframe.pack(fill="x", pady=(0, 14))

        ctk.CTkLabel(gframe,
                     text="📊  Generación Solar — Últimos 12 meses",
                     font=FONTS["title_small"],
                     text_color=COLORS["text_primary"]).pack(
                         anchor="w", padx=16, pady=(12, 8))

        try:
            import matplotlib
            matplotlib.use("TkAgg")
            import matplotlib.pyplot as plt
            from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

            labels = [f"{str(r['mes']).zfill(2)}/{r['anio']}"
                      for r in historial]
            valores = [r.get("kwh_consumidos", 0) or 0 for r in historial]

            fig, ax = plt.subplots(figsize=(8, 3))
            fig.patch.set_facecolor("#1C2333")
            ax.set_facecolor("#21262D")
            x = range(len(labels))
            ax.bar(x, valores, color="#00C896", alpha=0.85, width=0.6)
            ax.set_xticks(list(x))
            ax.set_xticklabels(labels, color="#8B949E", fontsize=8)
            ax.tick_params(colors="#8B949E", labelsize=8)
            for spine in ["top", "right"]:
                ax.spines[spine].set_visible(False)
            for spine in ["bottom", "left"]:
                ax.spines[spine].set_color("#30363D")
            ax.set_ylabel("kWh", color="#8B949E", fontsize=9)
            fig.tight_layout(pad=1.0)

            canvas = FigureCanvasTkAgg(fig, master=gframe)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="x", padx=12, pady=(0, 12))

        except ImportError:
            # Fallback sin matplotlib
            for r in historial[-8:]:
                kwh = r.get("kwh_consumidos", 0) or 0
                pct = min(kwh / 300, 1.0)
                color = (COLORS["success"] if kwh >= 200
                         else COLORS["warning"] if kwh >= 100
                         else COLORS["danger"])
                fila = ctk.CTkFrame(gframe, fg_color="transparent")
                fila.pack(fill="x", padx=16, pady=2)
                ctk.CTkLabel(fila,
                             text=f"{str(r['mes']).zfill(2)}/{r['anio']}",
                             width=55, font=FONTS["caption"],
                             text_color=COLORS["text_muted"]).pack(side="left")
                bar = ctk.CTkProgressBar(fila, height=12, corner_radius=3,
                                          fg_color=COLORS["bg_input"],
                                          progress_color=color)
                bar.pack(side="left", fill="x", expand=True, padx=8)
                bar.set(pct)
                ctk.CTkLabel(fila, text=f"{kwh:.0f}",
                             width=40, font=FONTS["caption"],
                             text_color=color).pack(side="right")
            ctk.CTkFrame(gframe, height=8,
                          fg_color="transparent").pack()

    def _seccion_mantenimientos(self, parent, mants):
        card = ctk.CTkFrame(parent, fg_color=COLORS["bg_secondary"],
                             corner_radius=10)
        card.pack(fill="x", pady=(0, 14))

        ctk.CTkLabel(card, text="🛠  Mantenimientos",
                     font=FONTS["title_small"],
                     text_color=COLORS["text_primary"]).pack(
                         anchor="w", padx=16, pady=(12, 8))

        labels_e = {1: "Crítico", 2: "Deficiente", 3: "Regular",
                    4: "Bueno", 5: "Excelente"}

        for m in mants[:5]:
            item = ctk.CTkFrame(card, fg_color=COLORS["bg_card"],
                                corner_radius=6)
            item.pack(fill="x", padx=12, pady=2)

            top = ctk.CTkFrame(item, fg_color="transparent")
            top.pack(fill="x", padx=12, pady=(6, 2))
            ctk.CTkLabel(top,
                         text=f"📅 {m.get('fecha_visita','N/A')}  |  "
                              f"👷 {m.get('tecnico_encargado','N/A')}",
                         font=FONTS["body_small"],
                         text_color=COLORS["text_primary"]).pack(side="left")

            bot = ctk.CTkFrame(item, fg_color="transparent")
            bot.pack(fill="x", padx=12, pady=(0, 6))
            txt = (f"Estr: {labels_e.get(m.get('estado_estructura',3),'?')}  |  "
                   f"Cab: {labels_e.get(m.get('estado_cableado',3),'?')}  |  "
                   f"Limpieza: {'✓' if m.get('limpieza_paneles') else '✗'}")
            ctk.CTkLabel(bot, text=txt, font=FONTS["caption"],
                         text_color=COLORS["text_muted"]).pack(side="left")

        ctk.CTkFrame(card, height=8,
                      fg_color="transparent").pack()

    def _abrir(self, ruta: str):
        import os, platform, subprocess
        if not ruta or not os.path.exists(ruta):
            messagebox.showwarning("GSC",
                                   f"Carpeta no encontrada:\n{ruta}")
            return
        try:
            if platform.system() == "Windows":
                os.startfile(ruta)
            elif platform.system() == "Darwin":
                subprocess.Popen(["open", ruta])
            else:
                subprocess.Popen(["xdg-open", ruta])
        except Exception:
            pass