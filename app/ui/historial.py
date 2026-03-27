"""
Módulo de Historial de Consumo — Registro mensual de generación.
"""

import customtkinter as ctk
from tkinter import messagebox
from app.theme import COLORS, FONTS
from app.ui.widgets import ActionButton, FormField, SectionTitle


class HistorialPage(ctk.CTkFrame):
    """Registro y visualización del historial de consumo mensual."""

    def __init__(self, parent, db):
        super().__init__(parent, fg_color="transparent")
        self.db = db

        self._construir_ui()
        self._cargar_historial()

    def _construir_ui(self):
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=24, pady=16)

        header = ctk.CTkFrame(container, fg_color="transparent")
        header.pack(fill="x", pady=(0, 16))
        ctk.CTkLabel(header, text="📊  Historial de Consumo y Generación",
                     font=FONTS["title_large"], text_color=COLORS["text_primary"]).pack(side="left")

        panels = ctk.CTkFrame(container, fg_color="transparent")
        panels.pack(fill="both", expand=True)
        panels.columnconfigure(0, weight=2)
        panels.columnconfigure(1, weight=3)

        # Lista de historial
        left = ctk.CTkFrame(panels, fg_color=COLORS["bg_card"], corner_radius=12,
                             border_width=1, border_color=COLORS["border_primary"])
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 8))

        ctk.CTkLabel(left, text="Registros Mensuales",
                     font=FONTS["title_small"], text_color=COLORS["text_secondary"]
                     ).pack(anchor="w", padx=16, pady=(14, 6))

        # Filtro por cliente
        clientes = self.db.obtener_clientes()
        self.clientes_map = {f"{c['nombre_titular']}": c["id"] for c in clientes}
        opts = ["Todos los clientes"] + list(self.clientes_map.keys())

        self.combo_filtro = ctk.CTkComboBox(
            left, values=opts, height=32,
            fg_color=COLORS["bg_input"], border_color=COLORS["border_primary"],
            text_color=COLORS["text_primary"], font=FONTS["body_small"],
            command=lambda v: self._cargar_historial()
        )
        self.combo_filtro.pack(fill="x", padx=12, pady=(0, 8))

        self.lista_frame = ctk.CTkScrollableFrame(left, fg_color="transparent", height=480)
        self.lista_frame.pack(fill="both", expand=True, padx=8, pady=(0, 12))

        # Formulario
        form_scroll = ctk.CTkScrollableFrame(panels, fg_color=COLORS["bg_card"], corner_radius=12)
        form_scroll.grid(row=0, column=1, sticky="nsew", padx=(8, 0))

        inner = ctk.CTkFrame(form_scroll, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=20, pady=16)

        ctk.CTkLabel(inner, text="Registrar Consumo Mensual",
                     font=FONTS["title_medium"], text_color=COLORS["text_primary"]
                     ).pack(anchor="w", pady=(0, 16))

        SectionTitle(inner, "▸ Cliente y Período").pack(anchor="w", pady=(0, 6))

        ctk.CTkLabel(inner, text="Cliente *", font=FONTS["label"],
                     text_color=COLORS["text_secondary"]).pack(anchor="w")
        self.combo_cliente = ctk.CTkComboBox(
            inner, values=list(self.clientes_map.keys()),
            height=36, fg_color=COLORS["bg_input"],
            border_color=COLORS["border_primary"],
            text_color=COLORS["text_primary"], font=FONTS["body_medium"]
        )
        self.combo_cliente.pack(fill="x", pady=(3, 12))

        self.f_mes = FormField(inner, "Mes/Año *", "YYYY-MM (Ej: 2024-11)", required=True)
        self.f_mes.pack(fill="x", pady=4)

        SectionTitle(inner, "▸ Lecturas").pack(anchor="w", pady=(14, 6))

        grid = ctk.CTkFrame(inner, fg_color="transparent")
        grid.pack(fill="x")
        grid.columnconfigure((0, 1), weight=1)

        self.f_medidor_red = FormField(grid, "Lectura Medidor Red (kWh)", "Ej: 145.5")
        self.f_medidor_red.grid(row=0, column=0, sticky="ew", padx=(0, 6), pady=4)

        self.f_inversor_gsc = FormField(grid, "Lectura Inversor GSC (kWh)", "Ej: 240.0")
        self.f_inversor_gsc.grid(row=0, column=1, sticky="ew", padx=(6, 0), pady=4)

        SectionTitle(inner, "▸ Valores Económicos").pack(anchor="w", pady=(14, 6))

        self.f_subsidio = FormField(inner, "Subsidio Red Aplicado ($)", "Ej: 15000")
        self.f_subsidio.pack(fill="x", pady=4)

        self.f_valor_gsc = FormField(inner, "Valor Base GSC ($)", "Ej: 85000")
        self.f_valor_gsc.pack(fill="x", pady=4)

        # Indicador promesa
        promesa_frame = ctk.CTkFrame(inner, fg_color=COLORS["bg_secondary"],
                                      corner_radius=8)
        promesa_frame.pack(fill="x", pady=(14, 0))
        ctk.CTkLabel(
            promesa_frame,
            text="ℹ  Meta de generación: 240 kWh/mes por sistema de 2.2 kWp",
            font=FONTS["body_small"], text_color=COLORS["info"]
        ).pack(padx=12, pady=10)

        btn_frame = ctk.CTkFrame(inner, fg_color="transparent")
        btn_frame.pack(fill="x", pady=(16, 0))
        ActionButton(btn_frame, text="💾  Registrar Consumo", command=self._guardar_historial).pack(side="left")

    def _cargar_historial(self):
        for w in self.lista_frame.winfo_children():
            w.destroy()

        filtro = self.combo_filtro.get()
        cliente_id = self.clientes_map.get(filtro) if filtro != "Todos los clientes" else None

        if cliente_id:
            registros = self.db.obtener_historial_cliente(cliente_id)
        else:
            # Obtener todos los historiales
            registros = []
            for cid in self.clientes_map.values():
                registros.extend(self.db.obtener_historial_cliente(cid))
            registros.sort(key=lambda x: x["mes_ano"], reverse=True)

        if not registros:
            ctk.CTkLabel(self.lista_frame, text="Sin registros de consumo",
                         font=FONTS["body_medium"], text_color=COLORS["text_muted"]).pack(pady=20)
            return

        for r in registros:
            self._crear_item_historial(r)

    def _crear_item_historial(self, registro: dict):
        item = ctk.CTkFrame(self.lista_frame, fg_color=COLORS["bg_secondary"],
                             corner_radius=8)
        item.pack(fill="x", pady=2, padx=2)

        kwh = registro.get("lectura_inversor_gsc", 0)
        # Indicador visual de cumplimiento de la promesa (240 kWh)
        pct = min(kwh / 240, 1.0)
        color_barra = COLORS["success"] if pct >= 0.9 else (COLORS["warning"] if pct >= 0.6 else COLORS["danger"])

        top_row = ctk.CTkFrame(item, fg_color="transparent")
        top_row.pack(fill="x", padx=12, pady=(8, 4))

        ctk.CTkLabel(top_row, text=registro.get("mes_ano", ""),
                     font=FONTS["label"], text_color=COLORS["text_primary"]).pack(side="left")
        ctk.CTkLabel(top_row, text=f"{kwh:.1f} / 240 kWh",
                     font=FONTS["body_small"], text_color=color_barra).pack(side="right")

        # Barra de progreso
        barra = ctk.CTkProgressBar(item, height=6, corner_radius=3,
                                    fg_color=COLORS["bg_input"],
                                    progress_color=color_barra)
        barra.pack(fill="x", padx=12, pady=(0, 4))
        barra.set(pct)

        detalle = ctk.CTkFrame(item, fg_color="transparent")
        detalle.pack(fill="x", padx=12, pady=(0, 8))
        subsidio = registro.get("subsidio_red_aplicado", 0)
        valor_gsc = registro.get("valor_base_gsc", 0)
        ctk.CTkLabel(detalle,
                     text=f"Red: {registro.get('lectura_medidor_red', 0):.1f} kWh  |  Subsidio: ${subsidio:,.0f}  |  GSC: ${valor_gsc:,.0f}",
                     font=FONTS["caption"], text_color=COLORS["text_muted"]).pack(anchor="w")

    def _guardar_historial(self):
        if not self.f_mes.validate():
            return

        cliente_key = self.combo_cliente.get()
        cliente_id = self.clientes_map.get(cliente_key)
        if not cliente_id:
            messagebox.showwarning("Validación", "Seleccione un cliente válido.")
            return

        try:
            datos = {
                "cliente_id": cliente_id,
                "mes_ano": self.f_mes.get(),
                "lectura_medidor_red": float(self.f_medidor_red.get() or 0),
                "lectura_inversor_gsc": float(self.f_inversor_gsc.get() or 0),
                "subsidio_red_aplicado": float(self.f_subsidio.get() or 0),
                "valor_base_gsc": float(self.f_valor_gsc.get() or 0),
            }
            self.db.crear_historial(datos)
            messagebox.showinfo("Éxito", "Consumo registrado correctamente.")
            for f in [self.f_mes, self.f_medidor_red, self.f_inversor_gsc,
                      self.f_subsidio, self.f_valor_gsc]:
                f.clear()
            self._cargar_historial()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar:\n{e}")
