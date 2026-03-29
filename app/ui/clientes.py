"""
clientes.py — CRUD de Clientes.
Fixes: prepoblado correcto, botones separados Registrar / Actualizar,
campo Tarifa GSC, lista amplia y limpia.
"""

import customtkinter as ctk
from tkinter import messagebox
from app.theme import COLORS, FONTS
from app.ui.widgets import FormField, ActionButton, SectionTitle


class ClientesPage(ctk.CTkFrame):
    def __init__(self, parent, db):
        super().__init__(parent, fg_color="transparent")
        self.db = db
        self.cliente_id = None   # None = modo Registrar, int = modo Actualizar
        self._construir_ui()
        self._refrescar_lista()

    # ─────────────────────────────────────────────────────────────────────────
    # UI
    # ─────────────────────────────────────────────────────────────────────────

    def _construir_ui(self):
        cont = ctk.CTkFrame(self, fg_color="transparent")
        cont.pack(fill="both", expand=True, padx=24, pady=16)

        # Título
        hdr = ctk.CTkFrame(cont, fg_color="transparent")
        hdr.pack(fill="x", pady=(0, 14))
        self.lbl_titulo = ctk.CTkLabel(
            hdr, text="👤  Gestión de Clientes",
            font=FONTS["title_large"], text_color=COLORS["text_primary"])
        self.lbl_titulo.pack(side="left")

        # Layout 2 paneles
        panels = ctk.CTkFrame(cont, fg_color="transparent")
        panels.pack(fill="both", expand=True)
        panels.columnconfigure(0, weight=5)   # lista más ancha
        panels.columnconfigure(1, weight=3)   # formulario

        # ── LISTA ─────────────────────────────────────────────────
        left = ctk.CTkFrame(panels, fg_color=COLORS["bg_card"],
                             corner_radius=12, border_width=1,
                             border_color=COLORS["border_primary"])
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 8))

        # Barra de búsqueda + botón Nuevo
        top_left = ctk.CTkFrame(left, fg_color="transparent")
        top_left.pack(fill="x", padx=14, pady=(14, 6))

        self.entry_busq = ctk.CTkEntry(
            top_left, placeholder_text="🔍  Buscar por nombre, NIT o teléfono…",
            height=34, fg_color=COLORS["bg_input"],
            border_color=COLORS["border_primary"],
            text_color=COLORS["text_primary"], font=FONTS["body_small"])
        self.entry_busq.pack(side="left", fill="x", expand=True, padx=(0, 8))
        self.entry_busq.bind("<KeyRelease>", lambda e: self._refrescar_lista())

        ActionButton(top_left, text="+ Nuevo", command=self._modo_nuevo,
                     variant="primary").pack(side="right")

        # Encabezado de columnas
        self._cabecera(left)

        # Scroll con filas
        self.lista_scroll = ctk.CTkScrollableFrame(
            left, fg_color="transparent")
        self.lista_scroll.pack(fill="both", expand=True, padx=8, pady=(0, 12))

        # ── FORMULARIO ────────────────────────────────────────────
        right = ctk.CTkScrollableFrame(
            panels, fg_color=COLORS["bg_card"], corner_radius=12)
        right.grid(row=0, column=1, sticky="nsew", padx=(8, 0))
        self._construir_formulario(right)

    def _cabecera(self, parent):
        cols = [
            ("Nombre / Titular",  260, "w"),
            ("NIT / Cédula",      110, "w"),
            ("Barrio",            100, "w"),
            ("Est.",               38, "center"),
            ("Tarifa Air-e",      90, "e"),
            ("Tarifa GSC",        90, "e"),
            ("Teléfono",          110, "w"),
        ]
        hdr = ctk.CTkFrame(parent, fg_color=COLORS["bg_secondary"],
                            corner_radius=0)
        hdr.pack(fill="x", padx=8)
        for txt, w, anc in cols:
            ctk.CTkLabel(hdr, text=txt, width=w, anchor=anc,
                         font=FONTS["label"],
                         text_color=COLORS["text_secondary"]).pack(
                             side="left", padx=6, pady=8)

    def _construir_formulario(self, parent):
        inner = ctk.CTkFrame(parent, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=20, pady=16)

        self.lbl_form = ctk.CTkLabel(inner, text="Registrar Cliente",
                                      font=FONTS["title_medium"],
                                      text_color=COLORS["accent_primary"])
        self.lbl_form.pack(anchor="w", pady=(0, 14))

        SectionTitle(inner, "▸ Datos Personales").pack(anchor="w", pady=(0, 6))

        g = ctk.CTkFrame(inner, fg_color="transparent")
        g.pack(fill="x")
        g.columnconfigure((0, 1), weight=1)

        self.f = {}   # Diccionario de FormField

        self.f["nombre"] = FormField(g, "Nombre / Razón Social *",
                                      "Ej: Juan García", required=True)
        self.f["nombre"].grid(row=0, column=0, columnspan=2,
                               sticky="ew", pady=4)

        self.f["nit"] = FormField(g, "Cédula / NIT *",
                                   "Ej: 1234567890", required=True)
        self.f["nit"].grid(row=1, column=0, sticky="ew", padx=(0, 6), pady=4)

        self.f["estrato"] = FormField(g, "Estrato (1–6)", "Ej: 3")
        self.f["estrato"].grid(row=1, column=1, sticky="ew",
                                padx=(6, 0), pady=4)

        self.f["tel"] = FormField(g, "Teléfono", "Ej: 3001234567")
        self.f["tel"].grid(row=2, column=0, sticky="ew", padx=(0, 6), pady=4)

        self.f["mail"] = FormField(g, "Email", "correo@ejemplo.com")
        self.f["mail"].grid(row=2, column=1, sticky="ew",
                             padx=(6, 0), pady=4)

        SectionTitle(inner, "▸ Ubicación").pack(anchor="w", pady=(14, 6))

        self.f["dir"] = FormField(inner, "Dirección Completa *",
                                   "Cra. 53 # 72-80, Barranquilla", required=True)
        self.f["dir"].pack(fill="x", pady=4)

        g2 = ctk.CTkFrame(inner, fg_color="transparent")
        g2.pack(fill="x")
        g2.columnconfigure((0, 1), weight=1)

        self.f["barrio"] = FormField(g2, "Barrio / Sector", "Ej: El Prado")
        self.f["barrio"].grid(row=0, column=0, sticky="ew",
                               padx=(0, 6), pady=4)

        self.f["geo"] = FormField(g2, "Geolocalización",
                                   "Lat, Lon (Ej: 10.96, -74.79)")
        self.f["geo"].grid(row=0, column=1, sticky="ew",
                            padx=(6, 0), pady=4)

        SectionTitle(inner, "▸ Tarifas").pack(anchor="w", pady=(14, 6))

        g3 = ctk.CTkFrame(inner, fg_color="transparent")
        g3.pack(fill="x")
        g3.columnconfigure((0, 1), weight=1)

        self.f["tarifa"] = FormField(g3, "Tarifa Air-e ($/kWh)",
                                      "Ej: 890.50")
        self.f["tarifa"].grid(row=0, column=0, sticky="ew",
                               padx=(0, 6), pady=4)

        self.f["tarifa_gsc"] = FormField(g3, "Tarifa GSC ($/kWh)",
                                          "Ej: 650.00")
        self.f["tarifa_gsc"].grid(row=0, column=1, sticky="ew",
                                   padx=(6, 0), pady=4)

        # Botones
        btn_row = ctk.CTkFrame(inner, fg_color="transparent")
        btn_row.pack(fill="x", pady=(20, 0))

        self.btn_registrar = ActionButton(
            btn_row, text="💾  Registrar Cliente",
            command=self._registrar, variant="primary")
        self.btn_registrar.pack(side="left", padx=(0, 8))

        self.btn_actualizar = ActionButton(
            btn_row, text="✏️  Actualizar Datos",
            command=self._actualizar, variant="info")
        # se muestra solo en modo edición

        ActionButton(btn_row, text="✗  Limpiar",
                     command=self._modo_nuevo,
                     variant="ghost").pack(side="left")

        self.btn_eliminar = ActionButton(
            btn_row, text="🗑  Eliminar",
            command=self._eliminar, variant="danger")
        # se muestra solo en modo edición

    # ─────────────────────────────────────────────────────────────────────────
    # LISTA
    # ─────────────────────────────────────────────────────────────────────────

    def _refrescar_lista(self):
        busq = self.entry_busq.get()
        clientes = self.db.obtener_clientes(busq)

        for w in self.lista_scroll.winfo_children():
            w.destroy()

        if not clientes:
            ctk.CTkLabel(self.lista_scroll, text="Sin registros.",
                         font=FONTS["body_medium"],
                         text_color=COLORS["text_muted"]).pack(pady=20)
            return

        for i, c in enumerate(clientes):
            bg = COLORS["bg_card"] if i % 2 == 0 else COLORS["bg_secondary"]
            fila = ctk.CTkFrame(self.lista_scroll, fg_color=bg,
                                 corner_radius=6, cursor="hand2", height=38)
            fila.pack(fill="x", pady=1, padx=2)
            fila.pack_propagate(False)

            datos = [
                (c.get("nombre_titular", ""), 260, "w"),
                (c.get("cedula_nit", ""),     110, "w"),
                (c.get("barrio_sector", "") or "—", 100, "w"),
                (str(c.get("estrato") or "—"),  38, "center"),
                (f"${c.get('tarifa_aire_actual') or 0:,.0f}", 90, "e"),
                (f"${c.get('tarifa_gsc') or 0:,.0f}",         90, "e"),
                (c.get("telefono", "") or "—", 110, "w"),
            ]
            for txt, w, anc in datos:
                lbl = ctk.CTkLabel(fila, text=txt, width=w, anchor=anc,
                                   font=FONTS["body_small"],
                                   text_color=COLORS["text_primary"])
                lbl.pack(side="left", padx=6)
                lbl.bind("<Button-1>",
                          lambda e, obj=c: self._modo_edicion(obj))

            fila.bind("<Button-1>", lambda e, obj=c: self._modo_edicion(obj))

    # ─────────────────────────────────────────────────────────────────────────
    # MODOS
    # ─────────────────────────────────────────────────────────────────────────

    def _modo_nuevo(self):
        """Limpia el formulario y pone modo Registrar."""
        self.cliente_id = None
        for f in self.f.values():
            f.clear()
        self.lbl_form.configure(text="Registrar Cliente",
                                text_color=COLORS["accent_primary"])
        self.btn_registrar.pack(side="left", padx=(0, 8))
        self.btn_actualizar.pack_forget()
        self.btn_eliminar.pack_forget()

    def _modo_edicion(self, c: dict):
        """Carga datos del cliente y muestra botones Actualizar/Eliminar."""
        self.cliente_id = c["id"]
        self.lbl_form.configure(
            text=f"✏️  Editando: {c['nombre_titular']}",
            text_color=COLORS["solar_yellow"])

        # Prepoblado correcto de todos los campos
        mapping = {
            "nombre":    c.get("nombre_titular"),
            "nit":       c.get("cedula_nit"),
            "tel":       c.get("telefono"),
            "mail":      c.get("email"),
            "estrato":   c.get("estrato"),
            "dir":       c.get("direccion_completa"),
            "barrio":    c.get("barrio_sector"),
            "geo":       c.get("geolocalizacion"),
            "tarifa":    c.get("tarifa_aire_actual"),
            "tarifa_gsc": c.get("tarifa_gsc"),
        }
        for key, val in mapping.items():
            self.f[key].set(val)

        # Botones: ocultar Registrar, mostrar Actualizar y Eliminar
        self.btn_registrar.pack_forget()
        self.btn_actualizar.pack(side="left", padx=(0, 8))
        self.btn_eliminar.pack(side="right")

    # ─────────────────────────────────────────────────────────────────────────
    # ACCIONES CRUD
    # ─────────────────────────────────────────────────────────────────────────

    def _datos_form(self) -> dict:
        return {k: f.get() for k, f in self.f.items()}

    def _validar(self) -> bool:
        ok = all(f.validate() for f in [self.f["nombre"], self.f["nit"], self.f["dir"]])
        if not ok:
            messagebox.showwarning("GSC", "Complete los campos obligatorios (*).")
        return ok

    def _registrar(self):
        if not self._validar():
            return
        try:
            self.db.crear_cliente(self._datos_form())
            messagebox.showinfo("GSC", "Cliente registrado correctamente.")
            self._modo_nuevo()
            self._refrescar_lista()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _actualizar(self):
        if not self.cliente_id or not self._validar():
            return
        try:
            self.db.actualizar_cliente(self.cliente_id, self._datos_form())
            messagebox.showinfo("GSC", "Cliente actualizado correctamente.")
            self._modo_nuevo()
            self._refrescar_lista()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _eliminar(self):
        if not self.cliente_id:
            return
        nombre = self.f["nombre"].get()
        if messagebox.askyesno("Confirmar",
                               f"¿Eliminar a '{nombre}'?\n"
                               "Se eliminarán también sus proyectos y consumos."):
            try:
                with self.db._conectar() as conn:
                    conn.execute("DELETE FROM consumos WHERE cliente_id=?",
                                 (self.cliente_id,))
                    conn.execute(
                        "DELETE FROM mantenimientos WHERE proyecto_id IN "
                        "(SELECT id FROM proyectos WHERE cliente_id=?)",
                        (self.cliente_id,))
                    conn.execute("DELETE FROM proyectos WHERE cliente_id=?",
                                 (self.cliente_id,))
                    conn.execute("DELETE FROM clientes WHERE id=?",
                                 (self.cliente_id,))
                    conn.commit()
                messagebox.showinfo("GSC", "Cliente eliminado.")
                self._modo_nuevo()
                self._refrescar_lista()
            except Exception as e:
                messagebox.showerror("Error", str(e))