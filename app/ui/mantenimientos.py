"""
Módulo de Mantenimientos — Registro y seguimiento de visitas técnicas.
"""

import customtkinter as ctk
from tkinter import messagebox, filedialog
from app.theme import COLORS, FONTS
from app.ui.widgets import ActionButton, FormField, SectionTitle


class MantenimientosPage(ctk.CTkFrame):
    """Registro de mantenimientos técnicos."""

    def __init__(self, parent, db):
        super().__init__(parent, fg_color="transparent")
        self.db = db
        self.mantenimiento_seleccionado = None

        self._construir_ui()
        self._cargar_mantenimientos()

    def _construir_ui(self):
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=24, pady=16)

        header = ctk.CTkFrame(container, fg_color="transparent")
        header.pack(fill="x", pady=(0, 16))
        ctk.CTkLabel(header, text="🛠  Mantenimientos Técnicos",
                     font=FONTS["title_large"], text_color=COLORS["text_primary"]).pack(side="left")

        panels = ctk.CTkFrame(container, fg_color="transparent")
        panels.pack(fill="both", expand=True)
        panels.columnconfigure(0, weight=2)
        panels.columnconfigure(1, weight=3)

        # Lista
        left = ctk.CTkFrame(panels, fg_color=COLORS["bg_card"], corner_radius=12,
                             border_width=1, border_color=COLORS["border_primary"])
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 8))

        ctk.CTkLabel(left, text="Visitas Registradas",
                     font=FONTS["title_small"], text_color=COLORS["text_secondary"]
                     ).pack(anchor="w", padx=16, pady=(14, 8))

        self.lista_frame = ctk.CTkScrollableFrame(left, fg_color="transparent", height=480)
        self.lista_frame.pack(fill="both", expand=True, padx=8, pady=(0, 12))

        # Formulario
        form_scroll = ctk.CTkScrollableFrame(panels, fg_color=COLORS["bg_card"], corner_radius=12)
        form_scroll.grid(row=0, column=1, sticky="nsew", padx=(8, 0))

        inner = ctk.CTkFrame(form_scroll, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=20, pady=16)

        ctk.CTkLabel(inner, text="Registrar Mantenimiento",
                     font=FONTS["title_medium"], text_color=COLORS["text_primary"]
                     ).pack(anchor="w", pady=(0, 16))

        SectionTitle(inner, "▸ Proyecto Asociado").pack(anchor="w", pady=(0, 6))

        proyectos = self.db.obtener_proyectos()
        self.proyectos_map = {
            f"{p['nombre_titular']} — {p['kwp_instalados']} kWp ({p['fecha_instalacion']})": p["id"]
            for p in proyectos
        }
        opts = list(self.proyectos_map.keys()) if self.proyectos_map else ["Sin proyectos"]

        ctk.CTkLabel(inner, text="Proyecto *", font=FONTS["label"],
                     text_color=COLORS["text_secondary"]).pack(anchor="w")
        self.combo_proyecto = ctk.CTkComboBox(
            inner, values=opts, height=36,
            fg_color=COLORS["bg_input"], border_color=COLORS["border_primary"],
            text_color=COLORS["text_primary"], font=FONTS["body_small"]
        )
        self.combo_proyecto.pack(fill="x", pady=(3, 12))

        SectionTitle(inner, "▸ Datos de Visita").pack(anchor="w", pady=(8, 6))

        grid = ctk.CTkFrame(inner, fg_color="transparent")
        grid.pack(fill="x")
        grid.columnconfigure((0, 1), weight=1)

        self.f_fecha = FormField(grid, "Fecha Visita *", "YYYY-MM-DD", required=True)
        self.f_fecha.grid(row=0, column=0, sticky="ew", padx=(0, 6), pady=4)

        self.f_tecnico = FormField(grid, "Técnico Encargado *", "Nombre del técnico", required=True)
        self.f_tecnico.grid(row=0, column=1, sticky="ew", padx=(6, 0), pady=4)

        SectionTitle(inner, "▸ Inspección Técnica").pack(anchor="w", pady=(14, 6))

        estados_frame = ctk.CTkFrame(inner, fg_color="transparent")
        estados_frame.pack(fill="x")
        estados_frame.columnconfigure((0, 1), weight=1)

        # Estado Estructura
        est_frame = ctk.CTkFrame(estados_frame, fg_color="transparent")
        est_frame.grid(row=0, column=0, sticky="ew", padx=(0, 6))
        ctk.CTkLabel(est_frame, text="Estado Estructura (1-5):", font=FONTS["label"],
                     text_color=COLORS["text_secondary"]).pack(anchor="w")
        self.slider_estructura = ctk.CTkSlider(
            est_frame, from_=1, to=5, number_of_steps=4,
            fg_color=COLORS["bg_input"], progress_color=COLORS["accent_primary"],
            button_color=COLORS["accent_primary"]
        )
        self.slider_estructura.pack(fill="x", pady=4)
        self.slider_estructura.set(3)
        self.lbl_estructura = ctk.CTkLabel(est_frame, text="3 — Regular",
                                            font=FONTS["body_small"],
                                            text_color=COLORS["text_muted"])
        self.lbl_estructura.pack(anchor="w")
        self.slider_estructura.configure(command=lambda v: self._actualizar_label_slider(
            v, self.lbl_estructura))

        # Estado Cableado
        cab_frame = ctk.CTkFrame(estados_frame, fg_color="transparent")
        cab_frame.grid(row=0, column=1, sticky="ew", padx=(6, 0))
        ctk.CTkLabel(cab_frame, text="Estado Cableado (1-5):", font=FONTS["label"],
                     text_color=COLORS["text_secondary"]).pack(anchor="w")
        self.slider_cableado = ctk.CTkSlider(
            cab_frame, from_=1, to=5, number_of_steps=4,
            fg_color=COLORS["bg_input"], progress_color=COLORS["accent_primary"],
            button_color=COLORS["accent_primary"]
        )
        self.slider_cableado.pack(fill="x", pady=4)
        self.slider_cableado.set(3)
        self.lbl_cableado = ctk.CTkLabel(cab_frame, text="3 — Regular",
                                          font=FONTS["body_small"],
                                          text_color=COLORS["text_muted"])
        self.lbl_cableado.pack(anchor="w")
        self.slider_cableado.configure(command=lambda v: self._actualizar_label_slider(
            v, self.lbl_cableado))

        # Limpieza y tierra
        extra_frame = ctk.CTkFrame(inner, fg_color="transparent")
        extra_frame.pack(fill="x", pady=8)
        extra_frame.columnconfigure((0, 1), weight=1)

        limpieza_frame = ctk.CTkFrame(extra_frame, fg_color="transparent")
        limpieza_frame.grid(row=0, column=0, sticky="ew", padx=(0, 6))
        ctk.CTkLabel(limpieza_frame, text="Limpieza de Paneles:", font=FONTS["label"],
                     text_color=COLORS["text_secondary"]).pack(anchor="w")
        self.var_limpieza = ctk.BooleanVar(value=False)
        ctk.CTkSwitch(
            limpieza_frame, text="Realizada",
            variable=self.var_limpieza,
            fg_color=COLORS["bg_input"],
            progress_color=COLORS["accent_primary"],
            text_color=COLORS["text_primary"],
            font=FONTS["body_medium"]
        ).pack(anchor="w", pady=6)

        self.f_tierra = FormField(extra_frame, "Continuidad Tierra (Ω)", "Ej: 0.85")
        self.f_tierra.grid(row=0, column=1, sticky="ew", padx=(6, 0))

        # Fotos
        fotos_row = ctk.CTkFrame(inner, fg_color="transparent")
        fotos_row.pack(fill="x", pady=4)
        ctk.CTkLabel(fotos_row, text="Fotos de Evidencia:", font=FONTS["label"],
                     text_color=COLORS["text_secondary"]).pack(anchor="w")
        fotos_input = ctk.CTkFrame(fotos_row, fg_color="transparent")
        fotos_input.pack(fill="x")
        self.f_fotos = ctk.CTkEntry(fotos_input, placeholder_text="Ruta de carpeta de evidencia...",
                                     height=34, fg_color=COLORS["bg_input"],
                                     border_color=COLORS["border_primary"],
                                     text_color=COLORS["text_primary"], font=FONTS["body_small"])
        self.f_fotos.pack(side="left", fill="x", expand=True, padx=(0, 6))
        ctk.CTkButton(fotos_input, text="📂", width=40, height=34,
                      fg_color=COLORS["bg_secondary"], hover_color=COLORS["bg_hover"],
                      text_color=COLORS["text_primary"],
                      command=self._seleccionar_carpeta_fotos).pack(side="right")

        # Observaciones
        SectionTitle(inner, "▸ Observaciones Críticas").pack(anchor="w", pady=(14, 6))
        self.txt_obs = ctk.CTkTextbox(inner, height=80,
                                       fg_color=COLORS["bg_input"],
                                       border_color=COLORS["border_primary"],
                                       text_color=COLORS["text_primary"],
                                       font=FONTS["body_small"])
        self.txt_obs.pack(fill="x")

        btn_frame = ctk.CTkFrame(inner, fg_color="transparent")
        btn_frame.pack(fill="x", pady=(16, 0))
        ActionButton(btn_frame, text="💾  Guardar Mantenimiento", command=self._guardar).pack(side="left", padx=(0, 8))
        ActionButton(btn_frame, text="✗  Limpiar", command=self._limpiar, variant="ghost").pack(side="left")

    def _actualizar_label_slider(self, valor, label):
        estados = {1: "Crítico", 2: "Deficiente", 3: "Regular", 4: "Bueno", 5: "Excelente"}
        v = round(float(valor))
        label.configure(text=f"{v} — {estados.get(v, '')}")

    def _seleccionar_carpeta_fotos(self):
        ruta = filedialog.askdirectory(title="Carpeta de fotos de evidencia")
        if ruta:
            self.f_fotos.delete(0, "end")
            self.f_fotos.insert(0, ruta)

    def _cargar_mantenimientos(self):
        mantenimientos = self.db.obtener_mantenimientos()
        for w in self.lista_frame.winfo_children():
            w.destroy()

        if not mantenimientos:
            ctk.CTkLabel(self.lista_frame, text="Sin mantenimientos registrados",
                         font=FONTS["body_medium"], text_color=COLORS["text_muted"]).pack(pady=20)
            return

        for m in mantenimientos:
            self._crear_item(m)

    def _crear_item(self, m: dict):
        item = ctk.CTkFrame(self.lista_frame, fg_color=COLORS["bg_secondary"], corner_radius=8)
        item.pack(fill="x", pady=2, padx=2)

        top = ctk.CTkFrame(item, fg_color="transparent")
        top.pack(fill="x", padx=12, pady=(8, 2))

        ctk.CTkLabel(top, text=m.get("nombre_titular", "N/A"),
                     font=FONTS["label"], text_color=COLORS["text_primary"]).pack(side="left")
        ctk.CTkLabel(top, text=m.get("fecha_visita", ""),
                     font=FONTS["body_small"], text_color=COLORS["text_muted"]).pack(side="right")

        bot = ctk.CTkFrame(item, fg_color="transparent")
        bot.pack(fill="x", padx=12, pady=(0, 8))
        ctk.CTkLabel(bot,
                     text=f"Técnico: {m.get('tecnico_encargado', 'N/A')}  |  "
                          f"Estr: {m.get('estado_estructura', '-')}/5  |  "
                          f"Cab: {m.get('estado_cableado', '-')}/5  |  "
                          f"Tierra: {m.get('continuidad_tierra_ohm', '-')}Ω",
                     font=FONTS["caption"], text_color=COLORS["text_muted"]).pack(anchor="w")

    def _guardar(self):
        if not self.f_fecha.validate() or not self.f_tecnico.validate():
            messagebox.showwarning("Validación", "Complete los campos requeridos.")
            return

        proyecto_key = self.combo_proyecto.get()
        proyecto_id = self.proyectos_map.get(proyecto_key)
        if not proyecto_id:
            messagebox.showwarning("Validación", "Seleccione un proyecto válido.")
            return

        try:
            tierra = float(self.f_tierra.get()) if self.f_tierra.get() else 0.0
        except ValueError:
            messagebox.showerror("Error", "La continuidad de tierra debe ser un número decimal.")
            return

        datos = {
            "proyecto_id": proyecto_id,
            "fecha_visita": self.f_fecha.get(),
            "tecnico_encargado": self.f_tecnico.get(),
            "estado_estructura": round(self.slider_estructura.get()),
            "estado_cableado": round(self.slider_cableado.get()),
            "limpieza_paneles": self.var_limpieza.get(),
            "continuidad_tierra_ohm": tierra,
            "fotos_evidencia_path": self.f_fotos.get(),
            "observaciones_criticas": self.txt_obs.get("1.0", "end").strip(),
        }

        try:
            self.db.crear_mantenimiento(datos)
            messagebox.showinfo("Éxito", "Mantenimiento registrado correctamente.")
            self._limpiar()
            self._cargar_mantenimientos()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar:\n{e}")

    def _limpiar(self):
        for f in [self.f_fecha, self.f_tecnico, self.f_tierra]:
            f.clear()
        self.slider_estructura.set(3)
        self.slider_cableado.set(3)
        self.var_limpieza.set(False)
        self.f_fotos.delete(0, "end")
        self.txt_obs.delete("1.0", "end")
