"""
Módulo Expediente del Cliente — Vista completa con gráfico de generación.
"""

import customtkinter as ctk
from tkinter import messagebox
from app.theme import COLORS, FONTS
from app.ui.widgets import ActionButton, StatusBadge
from app.exportar import abrir_carpeta_windows, generar_informe_mantenimiento


class ExpedientePage(ctk.CTkFrame):
    """Visualizador de expediente completo del cliente con gráficos."""

    def __init__(self, parent, db):
        super().__init__(parent, fg_color="transparent")
        self.db = db
        self.cliente_seleccionado = None

        self._construir_ui()

    def _construir_ui(self):
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=24, pady=16)

        header = ctk.CTkFrame(container, fg_color="transparent")
        header.pack(fill="x", pady=(0, 16))
        ctk.CTkLabel(header, text="📁  Expediente del Cliente",
                     font=FONTS["title_large"], text_color=COLORS["text_primary"]).pack(side="left")

        main_layout = ctk.CTkFrame(container, fg_color="transparent")
        main_layout.pack(fill="both", expand=True)
        main_layout.columnconfigure(0, weight=1)
        main_layout.columnconfigure(1, weight=3)

        # === SELECTOR DE CLIENTE ===
        selector_panel = ctk.CTkFrame(main_layout, fg_color=COLORS["bg_card"],
                                       corner_radius=12, border_width=1,
                                       border_color=COLORS["border_primary"])
        selector_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 8))

        ctk.CTkLabel(selector_panel, text="Seleccionar Cliente",
                     font=FONTS["title_small"], text_color=COLORS["text_secondary"]
                     ).pack(anchor="w", padx=16, pady=(14, 8))

        busqueda = ctk.CTkEntry(selector_panel,
                                placeholder_text="🔍  Buscar cliente...",
                                height=32, fg_color=COLORS["bg_input"],
                                border_color=COLORS["border_primary"],
                                text_color=COLORS["text_primary"],
                                font=FONTS["body_small"])
        busqueda.pack(fill="x", padx=12, pady=(0, 8))

        self.lista_clientes = ctk.CTkScrollableFrame(selector_panel, fg_color="transparent")
        self.lista_clientes.pack(fill="both", expand=True, padx=8, pady=(0, 12))

        busqueda.bind("<KeyRelease>", lambda e: self._cargar_lista_clientes(busqueda.get()))
        self._cargar_lista_clientes()

        # === EXPEDIENTE ===
        self.expediente_panel = ctk.CTkScrollableFrame(
            main_layout, fg_color=COLORS["bg_card"], corner_radius=12
        )
        self.expediente_panel.grid(row=0, column=1, sticky="nsew", padx=(8, 0))

        self._mostrar_placeholder()

    def _cargar_lista_clientes(self, busqueda: str = ""):
        clientes = self.db.obtener_clientes(busqueda)
        for w in self.lista_clientes.winfo_children():
            w.destroy()

        for c in clientes:
            item = ctk.CTkFrame(self.lista_clientes, fg_color=COLORS["bg_secondary"],
                                corner_radius=6, cursor="hand2")
            item.pack(fill="x", pady=2, padx=2)
            ctk.CTkLabel(item, text=c["nombre_titular"],
                         font=FONTS["label"], text_color=COLORS["text_primary"]
                         ).pack(anchor="w", padx=10, pady=(6, 0))
            ctk.CTkLabel(item, text=f"CC: {c['cedula_nit']}",
                         font=FONTS["caption"], text_color=COLORS["text_muted"]
                         ).pack(anchor="w", padx=10, pady=(0, 6))

            item.bind("<Button-1>", lambda e, c=c: self._cargar_expediente(c))
            for child in item.winfo_children():
                child.bind("<Button-1>", lambda e, c=c: self._cargar_expediente(c))

    def _mostrar_placeholder(self):
        for w in self.expediente_panel.winfo_children():
            w.destroy()
        ctk.CTkLabel(
            self.expediente_panel,
            text="☀  Seleccione un cliente para ver su expediente completo",
            font=FONTS["title_small"],
            text_color=COLORS["text_muted"]
        ).pack(expand=True, pady=100)

    def _cargar_expediente(self, cliente: dict):
        self.cliente_seleccionado = cliente
        for w in self.expediente_panel.winfo_children():
            w.destroy()

        inner = ctk.CTkFrame(self.expediente_panel, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=20, pady=16)

        # === DATOS DEL CLIENTE ===
        ctk.CTkLabel(inner, text=cliente["nombre_titular"],
                     font=FONTS["title_large"], text_color=COLORS["text_primary"]
                     ).pack(anchor="w")
        ctk.CTkLabel(inner, text=f"CC/NIT: {cliente['cedula_nit']}  |  Tel: {cliente.get('telefono', 'N/A')}  |  Email: {cliente.get('email', 'N/A')}",
                     font=FONTS["body_small"], text_color=COLORS["text_muted"]
                     ).pack(anchor="w", pady=(2, 4))
        ctk.CTkLabel(inner, text=f"📍 {cliente.get('direccion_completa', 'N/A')} — {cliente.get('barrio_sector', '')}  |  Estrato {cliente.get('estrato', 'N/A')}",
                     font=FONTS["body_small"], text_color=COLORS["text_secondary"]
                     ).pack(anchor="w", pady=(0, 14))

        separador = ctk.CTkFrame(inner, height=1, fg_color=COLORS["border_primary"])
        separador.pack(fill="x", pady=(0, 16))

        # === PROYECTO ===
        proyectos = self.db.obtener_proyectos(cliente["id"])
        if proyectos:
            p = proyectos[0]
            proy_frame = ctk.CTkFrame(inner, fg_color=COLORS["bg_secondary"], corner_radius=10)
            proy_frame.pack(fill="x", pady=(0, 16))

            proy_header = ctk.CTkFrame(proy_frame, fg_color="transparent")
            proy_header.pack(fill="x", padx=16, pady=(12, 6))
            ctk.CTkLabel(proy_header, text="⚡  Sistema Solar Instalado",
                         font=FONTS["title_small"], text_color=COLORS["accent_primary"]
                         ).pack(side="left")

            color_retie = COLORS["success"] if p["estatus_retie"] == "Certificado" else COLORS["warning"]
            ctk.CTkLabel(proy_header, text=f"RETIE: {p['estatus_retie']}",
                         font=FONTS["body_small"], text_color=color_retie
                         ).pack(side="right")

            datos_proy = ctk.CTkFrame(proy_frame, fg_color="transparent")
            datos_proy.pack(fill="x", padx=16)
            datos_proy.columnconfigure((0, 1, 2, 3), weight=1)

            kpis_proy = [
                ("Capacidad", f"{p['kwp_instalados']} kWp"),
                ("Inversor", f"{p.get('marca_inversor', 'N/A')} {p.get('capacidad_inversor_kw', '')}kW"),
                ("Paneles", p.get("marca_paneles", "N/A")),
                ("Instalado", p.get("fecha_instalacion", "N/A")),
            ]
            for i, (titulo, valor) in enumerate(kpis_proy):
                f = ctk.CTkFrame(datos_proy, fg_color="transparent")
                f.grid(row=0, column=i, padx=8, pady=10, sticky="ew")
                ctk.CTkLabel(f, text=titulo, font=FONTS["caption"],
                             text_color=COLORS["text_muted"]).pack(anchor="w")
                ctk.CTkLabel(f, text=valor, font=FONTS["label"],
                             text_color=COLORS["text_primary"]).pack(anchor="w")

            # Botón abrir carpeta
            if p.get("ruta_carpeta_fotos_entrega"):
                btn_row = ctk.CTkFrame(proy_frame, fg_color="transparent")
                btn_row.pack(fill="x", padx=16, pady=(0, 12))
                ActionButton(
                    btn_row,
                    text=f"📂  Abrir Carpeta de Fotos",
                    command=lambda: self._abrir_carpeta(p["ruta_carpeta_fotos_entrega"]),
                    variant="ghost"
                ).pack(side="left")

        # === GRÁFICO DE GENERACIÓN ===
        historial = self.db.obtener_datos_grafico_cliente(cliente["id"])
        if historial:
            self._construir_grafico(inner, historial)

        # === MANTENIMIENTOS ===
        if proyectos:
            mantenimientos = self.db.obtener_mantenimientos(proyectos[0]["id"])
            if mantenimientos:
                self._construir_seccion_mantenimientos(inner, mantenimientos, proyectos[0], cliente)

    def _construir_grafico(self, parent, historial: list):
        """Construye un gráfico de barras de generación kWh vs 240 kWh promesa."""
        grafico_frame = ctk.CTkFrame(parent, fg_color=COLORS["bg_secondary"],
                                      corner_radius=10)
        grafico_frame.pack(fill="x", pady=(0, 16))

        header = ctk.CTkFrame(grafico_frame, fg_color="transparent")
        header.pack(fill="x", padx=16, pady=(12, 4))
        ctk.CTkLabel(header, text="📊  Generación Solar — kWh Real vs Promesa (240 kWh)",
                     font=FONTS["title_small"], text_color=COLORS["text_primary"]
                     ).pack(side="left")

        try:
            import matplotlib
            matplotlib.use("TkAgg")
            import matplotlib.pyplot as plt
            from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
            import matplotlib.patches as mpatches

            meses = [r["mes_ano"][-5:] for r in historial]  # MM-YY
            valores = [r["lectura_inversor_gsc"] for r in historial]
            promesa = [240] * len(meses)

            fig, ax = plt.subplots(figsize=(7, 2.8))
            fig.patch.set_facecolor("#1C2333")
            ax.set_facecolor("#21262D")

            x = range(len(meses))
            bars = ax.bar(x, valores, color="#00C896", alpha=0.9, width=0.5, label="Generado")
            ax.plot(x, promesa, color="#FFD700", linewidth=1.5, linestyle="--", label="Promesa 240 kWh")

            ax.set_xticks(list(x))
            ax.set_xticklabels(meses, color="#8B949E", fontsize=8)
            ax.tick_params(colors="#8B949E", labelsize=8)
            ax.spines["bottom"].set_color("#30363D")
            ax.spines["left"].set_color("#30363D")
            ax.spines["top"].set_visible(False)
            ax.spines["right"].set_visible(False)
            ax.yaxis.label.set_color("#8B949E")
            ax.set_ylabel("kWh", color="#8B949E", fontsize=9)
            ax.legend(facecolor="#1C2333", edgecolor="#30363D",
                      labelcolor="#8B949E", fontsize=8)

            fig.tight_layout(pad=1.0)

            canvas = FigureCanvasTkAgg(fig, master=grafico_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="x", padx=12, pady=(0, 12))

        except ImportError:
            # Fallback sin matplotlib
            ctk.CTkLabel(
                grafico_frame,
                text="Instale matplotlib para ver el gráfico: pip install matplotlib",
                font=FONTS["body_small"], text_color=COLORS["warning"]
            ).pack(padx=16, pady=12)

            # Gráfico de barras simple con CTk
            barra_container = ctk.CTkFrame(grafico_frame, fg_color="transparent")
            barra_container.pack(fill="x", padx=16, pady=(0, 12))

            for r in historial[-6:]:
                kwh = r.get("lectura_inversor_gsc", 0)
                pct = min(kwh / 240, 1.0)
                color = COLORS["success"] if pct >= 0.9 else (
                    COLORS["warning"] if pct >= 0.6 else COLORS["danger"])

                fila = ctk.CTkFrame(barra_container, fg_color="transparent")
                fila.pack(fill="x", pady=2)
                ctk.CTkLabel(fila, text=r["mes_ano"][-5:], width=50,
                             font=FONTS["caption"], text_color=COLORS["text_muted"]).pack(side="left")
                bar = ctk.CTkProgressBar(fila, height=14, corner_radius=3,
                                          fg_color=COLORS["bg_input"],
                                          progress_color=color)
                bar.pack(side="left", fill="x", expand=True, padx=8)
                bar.set(pct)
                ctk.CTkLabel(fila, text=f"{kwh:.0f}", width=40,
                             font=FONTS["caption"], text_color=color).pack(side="right")

    def _construir_seccion_mantenimientos(self, parent, mantenimientos, proyecto, cliente):
        """Sección de historial de mantenimientos con botón de informe."""
        mant_frame = ctk.CTkFrame(parent, fg_color=COLORS["bg_secondary"], corner_radius=10)
        mant_frame.pack(fill="x", pady=(0, 16))

        mant_header = ctk.CTkFrame(mant_frame, fg_color="transparent")
        mant_header.pack(fill="x", padx=16, pady=(12, 8))
        ctk.CTkLabel(mant_header, text="🛠  Historial de Mantenimientos",
                     font=FONTS["title_small"], text_color=COLORS["text_primary"]
                     ).pack(side="left")

        for m in mantenimientos[:5]:
            item = ctk.CTkFrame(mant_frame, fg_color=COLORS["bg_card"], corner_radius=6)
            item.pack(fill="x", padx=12, pady=2)

            top = ctk.CTkFrame(item, fg_color="transparent")
            top.pack(fill="x", padx=12, pady=(6, 2))
            ctk.CTkLabel(top, text=f"📅 {m.get('fecha_visita', 'N/A')}  |  👷 {m.get('tecnico_encargado', 'N/A')}",
                         font=FONTS["body_small"], text_color=COLORS["text_primary"]
                         ).pack(side="left")

            estados = {1: "Crítico", 2: "Deficiente", 3: "Regular", 4: "Bueno", 5: "Excelente"}
            bot = ctk.CTkFrame(item, fg_color="transparent")
            bot.pack(fill="x", padx=12, pady=(0, 6))
            ctk.CTkLabel(bot,
                         text=f"Estr: {estados.get(m.get('estado_estructura', 3), 'N/A')}  |  "
                              f"Cable: {estados.get(m.get('estado_cableado', 3), 'N/A')}  |  "
                              f"Limpieza: {'✓' if m.get('limpieza_paneles') else '✗'}  |  "
                              f"Tierra: {m.get('continuidad_tierra_ohm', 'N/A')}Ω",
                         font=FONTS["caption"], text_color=COLORS["text_muted"]
                         ).pack(side="left")

            # Botón generar informe
            ActionButton(
                bot, text="📄 Informe",
                command=lambda m=m: self._generar_informe(m, proyecto, cliente),
                variant="ghost"
            ).pack(side="right")

        ctk.CTkFrame(mant_frame, height=1, fg_color="transparent").pack(pady=4)

    def _abrir_carpeta(self, ruta: str):
        if not abrir_carpeta_windows(ruta):
            messagebox.showwarning("No encontrada",
                                   f"La carpeta no existe:\n{ruta}\nVerifique la ruta configurada.")

    def _generar_informe(self, mantenimiento: dict, proyecto: dict, cliente: dict):
        from app.exportar import generar_informe_mantenimiento, abrir_archivo
        ruta = generar_informe_mantenimiento(mantenimiento, proyecto, cliente)
        if ruta:
            if messagebox.askyesno("Informe Generado",
                                    f"Informe guardado en:\n{ruta}\n\n¿Desea abrir el archivo?"):
                abrir_archivo(ruta)
        else:
            messagebox.showerror("Error", "No se pudo generar el informe.")
