"""
mantenimientos.py — Gestión documental de visitas técnicas v3.0
Optimización: layouts expandibles, espaciado mejorado.
"""

import customtkinter as ctk
from tkinter import messagebox, filedialog
from app.theme import COLORS, FONTS
from app.ui.widgets import FormField, ActionButton, SectionTitle


class MantenimientosPage(ctk.CTkFrame):
    def __init__(self, parent, db):
        super().__init__(parent, fg_color="transparent")
        self.db = db
        self._construir_ui()
        self._cargar_lista()

    def _construir_ui(self):
        cont = ctk.CTkFrame(self, fg_color="transparent")
        cont.pack(fill="both", expand=True, padx=24, pady=16)

        hdr = ctk.CTkFrame(cont, fg_color="transparent")
        hdr.pack(fill="x", pady=(0, 14))
        ctk.CTkLabel(hdr, text="Mantenimientos Técnicos",
                     font=FONTS["title_large"],
                     text_color=COLORS["text_primary"]).pack(side="left")

        panels = ctk.CTkFrame(cont, fg_color="transparent")
        panels.pack(fill="both", expand=True)
        panels.columnconfigure(0, weight=2)
        panels.columnconfigure(1, weight=3)

        # ── LISTA (expandible) ────────────────────────────────────
        left = ctk.CTkFrame(panels, fg_color=COLORS["bg_card"],
                             corner_radius=12, border_width=1,
                             border_color=COLORS["border_primary"])
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        left.rowconfigure(1, weight=1)

        ctk.CTkLabel(left, text="Historial de Visitas",
                     font=FONTS["title_small"],
                     text_color=COLORS["text_secondary"]).pack(
                         anchor="w", padx=16, pady=(14, 6))

        self.lista_scroll = ctk.CTkScrollableFrame(
            left, fg_color="transparent")
        self.lista_scroll.pack(fill="both", expand=True, padx=8, pady=(0, 12))

        # ── FORMULARIO (expandible) ───────────────────────────────
        right = ctk.CTkScrollableFrame(
            panels, fg_color=COLORS["bg_card"], corner_radius=12)
        right.grid(row=0, column=1, sticky="nsew", padx=(8, 0))
        self._construir_formulario(right)

    def _construir_formulario(self, parent):
        inner = ctk.CTkFrame(parent, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=20, pady=16)

        ctk.CTkLabel(inner, text="Registrar Visita Técnica",
                     font=FONTS["title_medium"],
                     text_color=COLORS["text_primary"]).pack(anchor="w", pady=(0, 14))

        SectionTitle(inner, "▸ Proyecto Asociado").pack(anchor="w", pady=(0, 8))

        proyectos = self.db.obtener_proyectos()
        self.proy_map = {}
        for p in proyectos:
            key = f"{p['cliente_nombre']} — {p.get('kwp_instalados','?')} kWp"
            self.proy_map[key] = p["id"]

        ctk.CTkLabel(inner, text="Proyecto *", font=FONTS["label"],
                     text_color=COLORS["text_secondary"]).pack(anchor="w", pady=(0, 2))
        self.cb_proy = ctk.CTkComboBox(
            inner,
            values=list(self.proy_map.keys()) if self.proy_map else ["Sin proyectos"],
            height=36, fg_color=COLORS["bg_input"],
            border_color=COLORS["border_primary"],
            text_color=COLORS["text_primary"], font=FONTS["body_small"])
        self.cb_proy.pack(fill="x", pady=(0, 14))

        SectionTitle(inner, "▸ Datos de Visita").pack(anchor="w", pady=(0, 8))

        g = ctk.CTkFrame(inner, fg_color="transparent")
        g.pack(fill="x", pady=(0, 14))
        g.columnconfigure((0, 1), weight=1)

        self.f_fecha = FormField(g, "Fecha Visita *", "YYYY-MM-DD", required=True)
        self.f_fecha.grid(row=0, column=0, sticky="ew", padx=(0, 6), pady=0)

        self.f_tecnico = FormField(g, "Técnico Encargado *",
                                    "Nombre del técnico", required=True)
        self.f_tecnico.grid(row=0, column=1, sticky="ew", padx=6, pady=0)

        SectionTitle(inner, "▸ Inspección Técnica").pack(anchor="w", pady=(14, 8))

        estados_frame = ctk.CTkFrame(inner, fg_color="transparent")
        estados_frame.pack(fill="x", pady=(0, 14))
        estados_frame.columnconfigure((0, 1), weight=1)

        # Slider estructura
        ef = ctk.CTkFrame(estados_frame, fg_color="transparent")
        ef.grid(row=0, column=0, sticky="ew", padx=(0, 6))
        ctk.CTkLabel(ef, text="Estado Estructura (1–5):", font=FONTS["label"],
                     text_color=COLORS["text_secondary"]).pack(anchor="w", pady=(0, 4))
        self.sl_estr = ctk.CTkSlider(ef, from_=1, to=5, number_of_steps=4,
                                      fg_color=COLORS["bg_input"],
                                      progress_color=COLORS["accent_primary"],
                                      button_color=COLORS["accent_primary"])
        self.sl_estr.pack(fill="x", pady=4)
        self.sl_estr.set(3)
        self.lbl_estr = ctk.CTkLabel(ef, text="3 — Regular",
                                      font=FONTS["body_small"],
                                      text_color=COLORS["text_muted"])
        self.lbl_estr.pack(anchor="w")
        self.sl_estr.configure(
            command=lambda v: self._upd_slider(v, self.lbl_estr))

        # Slider cableado
        cf = ctk.CTkFrame(estados_frame, fg_color="transparent")
        cf.grid(row=0, column=1, sticky="ew", padx=6)
        ctk.CTkLabel(cf, text="Estado Cableado (1–5):", font=FONTS["label"],
                     text_color=COLORS["text_secondary"]).pack(anchor="w", pady=(0, 4))
        self.sl_cab = ctk.CTkSlider(cf, from_=1, to=5, number_of_steps=4,
                                     fg_color=COLORS["bg_input"],
                                     progress_color=COLORS["accent_primary"],
                                     button_color=COLORS["accent_primary"])
        self.sl_cab.pack(fill="x", pady=4)
        self.sl_cab.set(3)
        self.lbl_cab = ctk.CTkLabel(cf, text="3 — Regular",
                                     font=FONTS["body_small"],
                                     text_color=COLORS["text_muted"])
        self.lbl_cab.pack(anchor="w")
        self.sl_cab.configure(
            command=lambda v: self._upd_slider(v, self.lbl_cab))

        # Limpieza + Tierra
        extra = ctk.CTkFrame(inner, fg_color="transparent")
        extra.pack(fill="x", pady=(0, 14))
        extra.columnconfigure((0, 1), weight=1)

        lf = ctk.CTkFrame(extra, fg_color="transparent")
        lf.grid(row=0, column=0, sticky="ew", padx=(0, 6))
        ctk.CTkLabel(lf, text="Limpieza de Paneles:", font=FONTS["label"],
                     text_color=COLORS["text_secondary"]).pack(anchor="w", pady=(0, 4))
        self.var_limpieza = ctk.BooleanVar(value=False)
        ctk.CTkSwitch(lf, text="Realizada", variable=self.var_limpieza,
                       fg_color=COLORS["bg_input"],
                       progress_color=COLORS["accent_primary"],
                       text_color=COLORS["text_primary"],
                       font=FONTS["body_medium"]).pack(anchor="w")

        self.f_tierra = FormField(extra, "Continuidad Tierra (Ω)", "Ej: 0.85")
        self.f_tierra.grid(row=0, column=1, sticky="ew", padx=6, pady=0)

        # ── GESTIÓN DOCUMENTAL ────────────────────────────────────
        SectionTitle(inner, "▸ Gestión Documental").pack(anchor="w", pady=(14, 8))

        doc_card = ctk.CTkFrame(inner, fg_color=COLORS["bg_secondary"],
                                 corner_radius=8)
        doc_card.pack(fill="x", pady=(0, 14))
        doc_inner = ctk.CTkFrame(doc_card, fg_color="transparent")
        doc_inner.pack(fill="x", padx=12, pady=12)

        ctk.CTkLabel(doc_inner, text="📸  Carpeta de Fotos:",
                     font=FONTS["label"],
                     text_color=COLORS["text_secondary"]).pack(anchor="w", pady=(0, 4))
        ri1 = ctk.CTkFrame(doc_inner, fg_color="transparent")
        ri1.pack(fill="x", pady=(0, 12))
        self.entry_fotos = ctk.CTkEntry(
            ri1, placeholder_text="Ruta de la carpeta…",
            height=32, fg_color=COLORS["bg_input"],
            border_color=COLORS["border_primary"],
            text_color=COLORS["text_primary"], font=FONTS["body_small"])
        self.entry_fotos.pack(side="left", fill="x", expand=True, padx=(0, 6))
        ctk.CTkButton(ri1, text="📂", width=38, height=32,
                      fg_color=COLORS["bg_card"],
                      hover_color=COLORS["bg_hover"],
                      text_color=COLORS["text_primary"],
                      command=self._sel_carpeta_fotos).pack(side="right")

        ctk.CTkLabel(doc_inner, text="📄  Acta / PDF:",
                     font=FONTS["label"],
                     text_color=COLORS["text_secondary"]).pack(anchor="w", pady=(0, 4))
        ri2 = ctk.CTkFrame(doc_inner, fg_color="transparent")
        ri2.pack(fill="x")
        self.entry_pdf = ctk.CTkEntry(
            ri2, placeholder_text="Ruta del archivo PDF…",
            height=32, fg_color=COLORS["bg_input"],
            border_color=COLORS["border_primary"],
            text_color=COLORS["text_primary"], font=FONTS["body_small"])
        self.entry_pdf.pack(side="left", fill="x", expand=True, padx=(0, 6))
        ctk.CTkButton(ri2, text="🗂", width=38, height=32,
                      fg_color=COLORS["bg_card"],
                      hover_color=COLORS["bg_hover"],
                      text_color=COLORS["text_primary"],
                      command=self._sel_pdf).pack(side="right")

        # Observaciones
        SectionTitle(inner, "▸ Observaciones Críticas").pack(
            anchor="w", pady=(14, 8))
        self.txt_obs = ctk.CTkTextbox(
            inner, height=80,
            fg_color=COLORS["bg_input"],
            border_color=COLORS["border_primary"],
            text_color=COLORS["text_primary"], font=FONTS["body_small"])
        self.txt_obs.pack(fill="x", pady=(0, 14))

        btn_row = ctk.CTkFrame(inner, fg_color="transparent")
        btn_row.pack(fill="x")
        ActionButton(btn_row, text="💾  Guardar Mantenimiento",
                     command=self._guardar).pack(side="left", padx=(0, 8))
        ActionButton(btn_row, text="✗  Limpiar",
                     command=self._limpiar, variant="ghost").pack(side="left")

    # ─────────────────────────────────────────────────────────────────────────
    # LISTA
    # ─────────────────────────────────────────────────────────────────────────

    def _cargar_lista(self):
        for w in self.lista_scroll.winfo_children():
            w.destroy()

        mants = self.db.obtener_mantenimientos()
        if not mants:
            ctk.CTkLabel(self.lista_scroll, text="Sin visitas registradas.",
                         font=FONTS["body_medium"],
                         text_color=COLORS["text_muted"]).pack(pady=20)
            return

        for m in mants:
            self._item_mant(m)

    def _item_mant(self, m: dict):
        estados = {1: "Crítico", 2: "Deficiente", 3: "Regular",
                   4: "Bueno", 5: "Excelente"}

        item = ctk.CTkFrame(self.lista_scroll, fg_color=COLORS["bg_secondary"],
                             corner_radius=8)
        item.pack(fill="x", pady=3, padx=2)

        top = ctk.CTkFrame(item, fg_color="transparent")
        top.pack(fill="x", padx=12, pady=(8, 2))
        ctk.CTkLabel(top, text=m.get("nombre_titular", "N/A"),
                     font=FONTS["label"],
                     text_color=COLORS["text_primary"]).pack(side="left")
        ctk.CTkLabel(top, text=m.get("fecha_visita", ""),
                     font=FONTS["body_small"],
                     text_color=COLORS["text_muted"]).pack(side="right")

        bot = ctk.CTkFrame(item, fg_color="transparent")
        bot.pack(fill="x", padx=12, pady=(0, 4))
        txt = (f"👷 {m.get('tecnico_encargado','N/A')}  |  "
               f"Estr: {estados.get(m.get('estado_estructura',3),'?')}  |  "
               f"Cab: {estados.get(m.get('estado_cableado',3),'?')}")
        ctk.CTkLabel(bot, text=txt, font=FONTS["caption"],
                     text_color=COLORS["text_muted"]).pack(anchor="w")

        # Iconos documentos
        docs_row = ctk.CTkFrame(item, fg_color="transparent")
        docs_row.pack(fill="x", padx=12, pady=(0, 8))
        if m.get("ruta_fotos"):
            ctk.CTkLabel(docs_row, text="📸 Fotos",
                         font=FONTS["caption"],
                         text_color=COLORS["info"]).pack(side="left", padx=(0, 8))
        if m.get("ruta_acta_pdf"):
            ctk.CTkLabel(docs_row, text="📄 PDF",
                         font=FONTS["caption"],
                         text_color=COLORS["info"]).pack(side="left")

    # ─────────────────────────────────────────────────────────────────────────
    # HELPERS
    # ─────────────────────────────────────────────────────────────────────────

    def _upd_slider(self, valor, lbl):
        labels = {1: "Crítico", 2: "Deficiente", 3: "Regular",
                  4: "Bueno", 5: "Excelente"}
        v = round(float(valor))
        lbl.configure(text=f"{v} — {labels.get(v,'')}")

    def _sel_carpeta_fotos(self):
        r = filedialog.askdirectory(title="Carpeta de fotos")
        if r:
            self.entry_fotos.delete(0, "end")
            self.entry_fotos.insert(0, r)

    def _sel_pdf(self):
        r = filedialog.askopenfilename(
            title="Seleccionar PDF",
            filetypes=[("PDF", "*.pdf"), ("Todos", "*.*")])
        if r:
            self.entry_pdf.delete(0, "end")
            self.entry_pdf.insert(0, r)

    def _guardar(self):
        if not self.f_fecha.validate() or not self.f_tecnico.validate():
            messagebox.showwarning("GSC", "Complete los campos requeridos.")
            return

        proy_key = self.cb_proy.get()
        proy_id = self.proy_map.get(proy_key)
        if not proy_id:
            messagebox.showwarning("GSC", "Seleccione un proyecto válido.")
            return

        try:
            tierra = float(self.f_tierra.get()) if self.f_tierra.get() else 0.0
        except ValueError:
            messagebox.showerror("GSC",
                                  "La continuidad de tierra debe ser un número.")
            return

        datos = {
            "proyecto_id":           proy_id,
            "fecha_visita":          self.f_fecha.get(),
            "tecnico_encargado":     self.f_tecnico.get(),
            "estado_estructura":     round(self.sl_estr.get()),
            "estado_cableado":       round(self.sl_cab.get()),
            "limpieza_paneles":      self.var_limpieza.get(),
            "continuidad_tierra_ohm": tierra,
            "ruta_fotos":            self.entry_fotos.get(),
            "ruta_acta_pdf":         self.entry_pdf.get(),
            "observaciones_criticas": self.txt_obs.get("1.0", "end").strip(),
        }

        try:
            self.db.crear_mantenimiento(datos)
            messagebox.showinfo("GSC", "Mantenimiento registrado.")
            self._limpiar()
            self._cargar_lista()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _limpiar(self):
        for f in [self.f_fecha, self.f_tecnico, self.f_tierra]:
            f.clear()
        self.sl_estr.set(3)
        self.sl_cab.set(3)
        self.var_limpieza.set(False)
        self.entry_fotos.delete(0, "end")
        self.entry_pdf.delete(0, "end")
        self.txt_obs.delete("1.0", "end")