"""
Módulo de Exportación — Excel y reportes de texto.
"""

import customtkinter as ctk
from tkinter import messagebox
from app.theme import COLORS, FONTS, TABLAS_EXPORTABLES
from app.ui.widgets import ActionButton, SectionTitle
from app.exportar import exportar_a_excel, abrir_archivo


class ExportarPage(ctk.CTkFrame):
    """Panel de exportación de datos a Excel y reportes."""

    def __init__(self, parent, db):
        super().__init__(parent, fg_color="transparent")
        self.db = db
        self._construir_ui()

    def _construir_ui(self):
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=24, pady=16)

        ctk.CTkLabel(container, text="📤  Exportación de Datos",
                     font=FONTS["title_large"], text_color=COLORS["text_primary"]
                     ).pack(anchor="w", pady=(0, 4))
        ctk.CTkLabel(container, text="Exporte cualquier tabla a Excel o genere informes de mantenimiento.",
                     font=FONTS["body_medium"], text_color=COLORS["text_secondary"]
                     ).pack(anchor="w", pady=(0, 24))

        # Grid de tarjetas de exportación
        cards_grid = ctk.CTkFrame(container, fg_color="transparent")
        cards_grid.pack(fill="x")
        cards_grid.columnconfigure((0, 1), weight=1)

        # Tarjetas para cada tabla
        tablas = [
            ("Clientes",               "📋", "Todos los clientes registrados en el sistema.",            COLORS["info"]),
            ("Proyectos_Instalacion",  "⚡", "Historial completo de instalaciones solares.",             COLORS["accent_primary"]),
            ("Historial_Consumo",      "📊", "Lecturas mensuales de generación y consumo.",              COLORS["solar_yellow"]),
            ("Mantenimientos",         "🛠", "Registro de todas las visitas técnicas realizadas.",       COLORS["warning"]),
        ]

        for i, (tabla, icono, desc, color) in enumerate(tablas):
            row, col = divmod(i, 2)
            card = ctk.CTkFrame(cards_grid, fg_color=COLORS["bg_card"],
                                corner_radius=12, border_width=1,
                                border_color=COLORS["border_primary"])
            card.grid(row=row, column=col, padx=8, pady=8, sticky="nsew")

            inner = ctk.CTkFrame(card, fg_color="transparent")
            inner.pack(fill="both", expand=True, padx=20, pady=16)

            # Encabezado de tarjeta
            header = ctk.CTkFrame(inner, fg_color="transparent")
            header.pack(fill="x", pady=(0, 8))
            ctk.CTkLabel(header, text=icono, font=("Segoe UI Emoji", 24),
                         text_color=color).pack(side="left", padx=(0, 10))
            ctk.CTkLabel(header, text=TABLAS_EXPORTABLES.get(tabla, tabla),
                         font=FONTS["title_small"], text_color=COLORS["text_primary"]
                         ).pack(side="left")

            ctk.CTkLabel(inner, text=desc, font=FONTS["body_small"],
                         text_color=COLORS["text_secondary"], wraplength=280
                         ).pack(anchor="w", pady=(0, 14))

            # Contador de registros
            try:
                _, datos = self.db.exportar_tabla_a_dict(tabla)
                n = len(datos)
            except Exception:
                n = 0

            ctk.CTkLabel(inner, text=f"{n} registros disponibles",
                         font=FONTS["caption"], text_color=color
                         ).pack(anchor="w", pady=(0, 10))

            ActionButton(
                inner,
                text="📥  Exportar a Excel",
                command=lambda t=tabla: self._exportar(t)
            ).pack(fill="x")

        # Sección de informe de mantenimiento por cliente
        sep = ctk.CTkFrame(container, height=1, fg_color=COLORS["border_primary"])
        sep.pack(fill="x", pady=24)

        SectionTitle(container, "▸ Informe de Mantenimiento Individual").pack(anchor="w", pady=(0, 8))

        informe_frame = ctk.CTkFrame(container, fg_color=COLORS["bg_card"],
                                      corner_radius=12, border_width=1,
                                      border_color=COLORS["border_primary"])
        informe_frame.pack(fill="x")

        inner_informe = ctk.CTkFrame(informe_frame, fg_color="transparent")
        inner_informe.pack(fill="x", padx=20, pady=16)
        inner_informe.columnconfigure((0, 1), weight=1)

        ctk.CTkLabel(inner_informe,
                     text="Seleccione un cliente y el mantenimiento para generar un informe técnico detallado en formato texto.",
                     font=FONTS["body_small"], text_color=COLORS["text_secondary"],
                     wraplength=500
                     ).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 12))

        # Selector de cliente
        clientes = self.db.obtener_clientes()
        self.clientes_map = {c["nombre_titular"]: c["id"] for c in clientes}
        opts_c = list(self.clientes_map.keys()) if self.clientes_map else ["Sin clientes"]

        ctk.CTkLabel(inner_informe, text="Cliente:", font=FONTS["label"],
                     text_color=COLORS["text_secondary"]).grid(row=1, column=0, sticky="w")
        self.combo_cliente = ctk.CTkComboBox(
            inner_informe, values=opts_c, height=34,
            fg_color=COLORS["bg_input"], border_color=COLORS["border_primary"],
            text_color=COLORS["text_primary"], font=FONTS["body_small"],
            command=lambda v: self._cargar_mantenimientos_cliente()
        )
        self.combo_cliente.grid(row=2, column=0, sticky="ew", padx=(0, 8), pady=(4, 0))

        # Selector de mantenimiento
        ctk.CTkLabel(inner_informe, text="Mantenimiento:", font=FONTS["label"],
                     text_color=COLORS["text_secondary"]).grid(row=1, column=1, sticky="w")
        self.combo_mant = ctk.CTkComboBox(
            inner_informe, values=["Seleccione un cliente primero"], height=34,
            fg_color=COLORS["bg_input"], border_color=COLORS["border_primary"],
            text_color=COLORS["text_primary"], font=FONTS["body_small"]
        )
        self.combo_mant.grid(row=2, column=1, sticky="ew", pady=(4, 0))
        self.mantenimientos_map = {}

        ActionButton(
            inner_informe,
            text="📄  Generar Informe de Mantenimiento",
            command=self._generar_informe_individual
        ).grid(row=3, column=0, columnspan=2, sticky="ew", pady=(16, 0))

    def _exportar(self, tabla: str):
        """Exporta la tabla seleccionada a Excel."""
        try:
            columnas, datos = self.db.exportar_tabla_a_dict(tabla)
            if not datos:
                messagebox.showinfo("Sin datos", f"La tabla '{tabla}' no tiene registros.")
                return

            ruta = exportar_a_excel(columnas, datos, TABLAS_EXPORTABLES.get(tabla, tabla))
            if ruta:
                if messagebox.askyesno("Exportación Exitosa",
                                        f"Archivo guardado en:\n{ruta}\n\n¿Abrir el archivo?"):
                    abrir_archivo(ruta)
            else:
                messagebox.showerror("Error",
                                     "No se pudo exportar. Asegúrese de tener instalado 'openpyxl':\n"
                                     "pip install openpyxl")
        except Exception as e:
            messagebox.showerror("Error", f"Error al exportar:\n{e}")

    def _cargar_mantenimientos_cliente(self):
        """Carga los mantenimientos del cliente seleccionado."""
        cliente_nombre = self.combo_cliente.get()
        cliente_id = self.clientes_map.get(cliente_nombre)
        if not cliente_id:
            return

        proyectos = self.db.obtener_proyectos(cliente_id)
        self.mantenimientos_map = {}
        opts = []

        for p in proyectos:
            mantenimientos = self.db.obtener_mantenimientos(p["id"])
            for m in mantenimientos:
                key = f"Visita {m['fecha_visita']} — Téc: {m['tecnico_encargado']}"
                self.mantenimientos_map[key] = (m, p)
                opts.append(key)

        if opts:
            self.combo_mant.configure(values=opts)
            self.combo_mant.set(opts[0])
        else:
            self.combo_mant.configure(values=["Sin mantenimientos registrados"])
            self.combo_mant.set("Sin mantenimientos registrados")

    def _generar_informe_individual(self):
        """Genera el informe de mantenimiento en texto."""
        mant_key = self.combo_mant.get()
        mant_data = self.mantenimientos_map.get(mant_key)

        if not mant_data:
            messagebox.showwarning("Sin selección",
                                   "Seleccione un cliente y un mantenimiento válido.")
            return

        mantenimiento, proyecto = mant_data
        cliente_id = proyecto.get("cliente_id")
        cliente = self.db.obtener_cliente_por_id(cliente_id)

        if not cliente:
            messagebox.showerror("Error", "No se pudo obtener los datos del cliente.")
            return

        from app.exportar import generar_informe_mantenimiento, abrir_archivo
        ruta = generar_informe_mantenimiento(mantenimiento, proyecto, cliente)

        if ruta:
            if messagebox.askyesno("Informe Generado",
                                    f"Informe guardado en:\n{ruta}\n\n¿Abrir el archivo?"):
                abrir_archivo(ruta)
        else:
            messagebox.showerror("Error", "No se pudo generar el informe.")
