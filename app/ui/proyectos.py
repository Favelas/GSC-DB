"""
proyectos.py — Instalaciones técnicas con vista detallada por casa.
Permite edición sin crear duplicados.
"""

import customtkinter as ctk
from tkinter import messagebox, filedialog
from app.theme import COLORS, FONTS
from app.ui.widgets import FormField, ActionButton, SectionTitle


class ProyectosPage(ctk.CTkFrame):
    def __init__(self, parent, db):
        super().__init__(parent, fg_color="transparent")
        self.db = db
        self.proyecto_id = None   # None = nuevo, int = edición
        self._construir_ui()
        self._cargar_proyectos()

    # ─────────────────────────────────────────────────────────────────────────
    # UI
    # ─────────────────────────────────────────────────────────────────────────

    def _construir_ui(self):
        cont = ctk.CTkFrame(self, fg_color="transparent")
        cont.pack(fill="both", expand=True, padx=24, pady=16)

        hdr = ctk.CTkFrame(cont, fg_color="transparent")
        hdr.pack(fill="x", pady=(0, 14))
        ctk.CTkLabel(hdr, text="🔧  Proyectos de Instalación",
                     font=FONTS["title_large"],
                     text_color=COLORS["text_primary"]).pack(side="left")
        ActionButton(hdr, text="+ Nueva Instalación",
                     command=self._modo_nuevo).pack(side="right")

        panels = ctk.CTkFrame(cont, fg_color="transparent")
        panels.pack(fill="both", expand=True)
        panels.columnconfigure(0, weight=2)
        panels.columnconfigure(1, weight=3)

        # ── LISTA ─────────────────────────────────────────────────
        left = ctk.CTkFrame(panels, fg_color=COLORS["bg_card"],
                             corner_radius=12, border_width=1,
                             border_color=COLORS["border_primary"])
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 8))

        # Filtro por cliente
        top_l = ctk.CTkFrame(left, fg_color="transparent")
        top_l.pack(fill="x", padx=14, pady=(14, 6))
        ctk.CTkLabel(top_l, text="Filtrar por cliente:",
                     font=FONTS["label"],
                     text_color=COLORS["text_secondary"]).pack(anchor="w")

        clientes = self.db.obtener_clientes()
        self.cli_map = {"Todos": None}
        self.cli_map.update({c["nombre_titular"]: c["id"] for c in clientes})
        self.cli_combo = ctk.CTkComboBox(
            top_l, values=list(self.cli_map.keys()),
            height=32, fg_color=COLORS["bg_input"],
            border_color=COLORS["border_primary"],
            text_color=COLORS["text_primary"], font=FONTS["body_small"],
            command=lambda v: self._cargar_proyectos())
        self.cli_combo.pack(fill="x", pady=(4, 0))

        self.lista_scroll = ctk.CTkScrollableFrame(
            left, fg_color="transparent")
        self.lista_scroll.pack(fill="both", expand=True, padx=8, pady=(8, 12))

        # ── FORMULARIO ────────────────────────────────────────────
        right = ctk.CTkScrollableFrame(
            panels, fg_color=COLORS["bg_card"], corner_radius=12)
        right.grid(row=0, column=1, sticky="nsew", padx=(8, 0))
        self._construir_formulario(right)

    def _construir_formulario(self, parent):
        inner = ctk.CTkFrame(parent, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=20, pady=16)

        self.lbl_form = ctk.CTkLabel(inner, text="Nueva Instalación",
                                      font=FONTS["title_medium"],
                                      text_color=COLORS["accent_primary"])
        self.lbl_form.pack(anchor="w", pady=(0, 14))

        SectionTitle(inner, "▸ Cliente Asociado").pack(anchor="w", pady=(0, 6))

        clientes = self.db.obtener_clientes()
        self.form_cli_map = {c["nombre_titular"]: c["id"] for c in clientes}
        ctk.CTkLabel(inner, text="Cliente *", font=FONTS["label"],
                     text_color=COLORS["text_secondary"]).pack(anchor="w")
        self.cb_cliente = ctk.CTkComboBox(
            inner, values=list(self.form_cli_map.keys()),
            height=36, fg_color=COLORS["bg_input"],
            border_color=COLORS["border_primary"],
            text_color=COLORS["text_primary"], font=FONTS["body_small"])
        self.cb_cliente.pack(fill="x", pady=(3, 14))

        SectionTitle(inner, "▸ Datos de Instalación").pack(anchor="w", pady=(0, 6))

        g = ctk.CTkFrame(inner, fg_color="transparent")
        g.pack(fill="x")
        g.columnconfigure((0, 1), weight=1)

        self.f = {}
        self.f["nombre"] = FormField(g, "Nombre Proyecto", "Ej: Casa García Prado")
        self.f["nombre"].grid(row=0, column=0, columnspan=2,
                               sticky="ew", pady=4)

        self.f["fecha_instalacion"] = FormField(
            g, "Fecha Instalación *", "YYYY-MM-DD", required=True)
        self.f["fecha_instalacion"].grid(row=1, column=0,
                                          sticky="ew", padx=(0, 6), pady=4)

        self.f["kwp"] = FormField(g, "kWp Instalados *", "Ej: 2.2", required=True)
        self.f["kwp"].grid(row=1, column=1, sticky="ew",
                            padx=(6, 0), pady=4)

        self.f["paneles"] = FormField(g, "Marca Paneles", "Ej: Canadian Solar")
        self.f["paneles"].grid(row=2, column=0, sticky="ew",
                                padx=(0, 6), pady=4)

        self.f["inversor"] = FormField(g, "Marca Inversor", "Ej: Growatt")
        self.f["inversor"].grid(row=2, column=1, sticky="ew",
                                 padx=(6, 0), pady=4)

        self.f["serial_inversor"] = FormField(
            g, "Serial Inversor", "Número de serie")
        self.f["serial_inversor"].grid(row=3, column=0,
                                        sticky="ew", padx=(0, 6), pady=4)

        self.f["capacidad_inversor_kw"] = FormField(g, "Cap. Inversor (kW)", "Ej: 3.0")
        self.f["capacidad_inversor_kw"].grid(row=3, column=1,
                                              sticky="ew", padx=(6, 0), pady=4)

        ctk.CTkLabel(inner, text="Seriales de Paneles", font=FONTS["label"],
                     text_color=COLORS["text_secondary"]).pack(anchor="w", pady=(10, 2))
        self.txt_seriales = ctk.CTkTextbox(
            inner, height=55, fg_color=COLORS["bg_input"],
            border_color=COLORS["border_primary"],
            text_color=COLORS["text_primary"], font=FONTS["body_small"])
        self.txt_seriales.pack(fill="x")

        SectionTitle(inner, "▸ Documentación").pack(anchor="w", pady=(14, 6))

        # RETIE
        retie_row = ctk.CTkFrame(inner, fg_color="transparent")
        retie_row.pack(fill="x", pady=4)
        ctk.CTkLabel(retie_row, text="Estado RETIE:", font=FONTS["label"],
                     text_color=COLORS["text_secondary"]).pack(side="left", padx=(0, 12))
        self.var_retie = ctk.StringVar(value="Pendiente")
        for op in ["Pendiente", "Certificado"]:
            ctk.CTkRadioButton(
                retie_row, text=op, variable=self.var_retie, value=op,
                fg_color=COLORS["accent_primary"],
                text_color=COLORS["text_primary"],
                font=FONTS["body_medium"],
            ).pack(side="left", padx=8)

        # Ruta fotos
        ruta_row = ctk.CTkFrame(inner, fg_color="transparent")
        ruta_row.pack(fill="x", pady=4)
        ctk.CTkLabel(ruta_row, text="Carpeta de Fotos:", font=FONTS["label"],
                     text_color=COLORS["text_secondary"]).pack(anchor="w")
        ri = ctk.CTkFrame(ruta_row, fg_color="transparent")
        ri.pack(fill="x")
        self.entry_fotos = ctk.CTkEntry(
            ri, placeholder_text="Ruta local…",
            height=34, fg_color=COLORS["bg_input"],
            border_color=COLORS["border_primary"],
            text_color=COLORS["text_primary"], font=FONTS["body_small"])
        self.entry_fotos.pack(side="left", fill="x", expand=True, padx=(0, 6))
        ctk.CTkButton(ri, text="📂", width=40, height=34,
                      fg_color=COLORS["bg_secondary"],
                      hover_color=COLORS["bg_hover"],
                      text_color=COLORS["text_primary"],
                      command=self._sel_carpeta).pack(side="right")

        # Botones
        btn_row = ctk.CTkFrame(inner, fg_color="transparent")
        btn_row.pack(fill="x", pady=(20, 0))

        self.btn_registrar = ActionButton(
            btn_row, text="💾  Registrar Proyecto", command=self._registrar)
        self.btn_registrar.pack(side="left", padx=(0, 8))

        self.btn_actualizar = ActionButton(
            btn_row, text="✏️  Actualizar", command=self._actualizar, variant="info")

        ActionButton(btn_row, text="✗  Limpiar",
                     command=self._modo_nuevo, variant="ghost").pack(side="left")

    # ─────────────────────────────────────────────────────────────────────────
    # LISTA
    # ─────────────────────────────────────────────────────────────────────────

    def _cargar_proyectos(self, _=None):
        sel = self.cli_combo.get()
        cid = self.cli_map.get(sel)          # None = Todos
        proyectos = self.db.obtener_proyectos(cid)

        for w in self.lista_scroll.winfo_children():
            w.destroy()

        if not proyectos:
            ctk.CTkLabel(self.lista_scroll, text="Sin proyectos.",
                         font=FONTS["body_medium"],
                         text_color=COLORS["text_muted"]).pack(pady=20)
            return

        for p in proyectos:
            self._item_proyecto(p)

    def _item_proyecto(self, p: dict):
        """Tarjeta detallada de un proyecto (vista por casa)."""
        color_r = COLORS["success"] if p.get("estatus_retie") == "Certificado" \
            else COLORS["warning"]

        card = ctk.CTkFrame(self.lista_scroll, fg_color=COLORS["bg_secondary"],
                             corner_radius=8, cursor="hand2")
        card.pack(fill="x", pady=3, padx=2)

        # Barra lateral de color RETIE
        barra = ctk.CTkFrame(card, width=4, fg_color=color_r, corner_radius=2)
        barra.pack(side="left", fill="y", padx=(0, 10))

        info = ctk.CTkFrame(card, fg_color="transparent")
        info.pack(fill="x", pady=8, padx=(0, 10))

        # Fila 1: nombre cliente + kwp
        f1 = ctk.CTkFrame(info, fg_color="transparent")
        f1.pack(fill="x")
        ctk.CTkLabel(f1, text=p.get("cliente_nombre", "N/A"),
                     font=FONTS["label"],
                     text_color=COLORS["text_primary"]).pack(side="left")
        ctk.CTkLabel(f1, text=f"⚡ {p.get('kwp_instalados','?')} kWp",
                     font=FONTS["body_small"],
                     text_color=COLORS["accent_primary"]).pack(side="right")

        # Fila 2: dirección (viene del JOIN pero no está; mostramos nombre proy)
        if p.get("nombre_proyecto"):
            ctk.CTkLabel(info, text=p["nombre_proyecto"],
                         font=FONTS["body_small"],
                         text_color=COLORS["text_secondary"]).pack(anchor="w")

        # Fila 3: seriales + fecha
        f3 = ctk.CTkFrame(info, fg_color="transparent")
        f3.pack(fill="x")
        inv_txt = (f"Inv: {p.get('marca_inversor','?')} — S/N: "
                   f"{p.get('serial_inversor','?')}")
        ctk.CTkLabel(f3, text=inv_txt, font=FONTS["caption"],
                     text_color=COLORS["text_muted"]).pack(side="left")
        ctk.CTkLabel(f3, text=f"📅 {p.get('fecha_instalacion','?')}",
                     font=FONTS["caption"],
                     text_color=COLORS["text_muted"]).pack(side="right")

        # Fila 4: paneles seriales
        if p.get("seriales_paneles"):
            ctk.CTkLabel(info,
                         text=f"Pan: {p['seriales_paneles'][:60]}…" if
                         len(p.get("seriales_paneles", "")) > 60 else
                         f"Pan: {p.get('seriales_paneles','')}",
                         font=FONTS["caption"],
                         text_color=COLORS["text_muted"]).pack(anchor="w")

        # Fila 5: RETIE badge
        ctk.CTkLabel(info, text=f"RETIE: {p.get('estatus_retie','?')}",
                     font=FONTS["caption"],
                     text_color=color_r).pack(anchor="w")

        # Bind clic → modo edición
        for widget in [card, barra, info] + info.winfo_children():
            try:
                widget.bind("<Button-1>",
                             lambda e, obj=p: self._modo_edicion(obj))
            except Exception:
                pass

    # ─────────────────────────────────────────────────────────────────────────
    # MODOS
    # ─────────────────────────────────────────────────────────────────────────

    def _modo_nuevo(self):
        self.proyecto_id = None
        self.lbl_form.configure(text="Nueva Instalación",
                                text_color=COLORS["accent_primary"])
        for f in self.f.values():
            f.clear()
        self.txt_seriales.delete("1.0", "end")
        self.var_retie.set("Pendiente")
        self.entry_fotos.delete(0, "end")
        self.btn_registrar.pack(side="left", padx=(0, 8))
        self.btn_actualizar.pack_forget()

    def _modo_edicion(self, p: dict):
        self.proyecto_id = p["id"]
        self.lbl_form.configure(
            text=f"✏️  Editando proyecto #{p['id']}",
            text_color=COLORS["solar_yellow"])

        # Seleccionar cliente en combo
        cli_nombre = p.get("cliente_nombre", "")
        if cli_nombre in self.form_cli_map:
            self.cb_cliente.set(cli_nombre)

        self.f["nombre"].set(p.get("nombre_proyecto"))
        self.f["fecha_instalacion"].set(p.get("fecha_instalacion"))
        self.f["kwp"].set(p.get("kwp_instalados"))
        self.f["paneles"].set(p.get("marca_paneles"))
        self.f["inversor"].set(p.get("marca_inversor"))
        self.f["serial_inversor"].set(p.get("serial_inversor"))
        self.f["capacidad_inversor_kw"].set(p.get("capacidad_inversor_kw"))
        self.txt_seriales.delete("1.0", "end")
        self.txt_seriales.insert("1.0", p.get("seriales_paneles") or "")
        self.var_retie.set(p.get("estatus_retie", "Pendiente"))
        self.entry_fotos.delete(0, "end")
        self.entry_fotos.insert(0, p.get("ruta_fotos_entrega") or "")

        self.btn_registrar.pack_forget()
        self.btn_actualizar.pack(side="left", padx=(0, 8))

    # ─────────────────────────────────────────────────────────────────────────
    # CRUD
    # ─────────────────────────────────────────────────────────────────────────

    def _datos(self) -> dict:
        cli_nombre = self.cb_cliente.get()
        return {
            "cliente_id":          self.form_cli_map.get(cli_nombre),
            "nombre":              self.f["nombre"].get(),
            "fecha_instalacion":   self.f["fecha_instalacion"].get(),
            "kwp":                 self.f["kwp"].get(),
            "paneles":             self.f["paneles"].get(),
            "seriales":            self.txt_seriales.get("1.0", "end").strip(),
            "inversor":            self.f["inversor"].get(),
            "serial_inversor":     self.f["serial_inversor"].get(),
            "capacidad_inversor_kw": self.f["capacidad_inversor_kw"].get(),
            "retie":               self.var_retie.get(),
            "ruta_fotos":          self.entry_fotos.get(),
        }

    def _validar(self, d: dict) -> bool:
        if not d.get("cliente_id"):
            messagebox.showwarning("GSC", "Seleccione un cliente.")
            return False
        if not self.f["fecha_instalacion"].validate():
            return False
        if not self.f["kwp"].validate():
            return False
        try:
            float(d["kwp"])
        except (ValueError, TypeError):
            messagebox.showerror("GSC", "kWp debe ser un número.")
            return False
        return True

    def _registrar(self):
        d = self._datos()
        if not self._validar(d):
            return
        try:
            self.db.crear_proyecto(d)
            messagebox.showinfo("GSC", "Proyecto registrado.")
            self._modo_nuevo()
            self._cargar_proyectos()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _actualizar(self):
        if not self.proyecto_id:
            return
        d = self._datos()
        if not self._validar(d):
            return
        try:
            self.db.actualizar_proyecto(self.proyecto_id, d)
            messagebox.showinfo("GSC", "Proyecto actualizado.")
            self._modo_nuevo()
            self._cargar_proyectos()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _sel_carpeta(self):
        ruta = filedialog.askdirectory(title="Seleccionar carpeta de fotos")
        if ruta:
            self.entry_fotos.delete(0, "end")
            self.entry_fotos.insert(0, ruta)
