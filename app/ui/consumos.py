"""
consumos.py — Historial de Consumo con Agente de Análisis Inteligente.
Tabla: consumos (id, cliente_id, mes, anio, kwh_consumidos, …)
El agente detecta tendencias automáticamente y emite un comentario.
"""

import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime
from app.theme import COLORS, FONTS
from app.ui.widgets import FormField, ActionButton, SectionTitle


# ─── Agente de Análisis de Consumo ────────────────────────────────────────────

class AgenteConsumo:
    """
    Analiza el histórico de kWh y emite un diagnóstico textual.
    Reglas basadas en tendencia lineal de los últimos 6 meses.
    """

    PROMESA_KWH = 240   # kWh prometidos por sistema de 2.2 kWp/mes

    @classmethod
    def analizar(cls, registros: list) -> dict:
        """
        Recibe lista de dicts con campo 'kwh_consumidos'.
        Retorna dict: {etiqueta, descripcion, color, emoji}
        """
        if not registros:
            return {
                "etiqueta":    "Sin datos",
                "descripcion": "Aún no hay registros de consumo para este cliente.",
                "color":       COLORS["text_muted"],
                "emoji":       "📭",
            }

        valores = [r["kwh_consumidos"] for r in registros[-6:]]

        if len(valores) == 1:
            kwh = valores[0]
            pct = kwh / cls.PROMESA_KWH
            if pct >= 0.90:
                return cls._resultado("Generación Óptima",
                                      f"El sistema generó {kwh:.1f} kWh, cerca de la promesa.",
                                      COLORS["success"], "✅")
            return cls._resultado("Inicio de Monitoreo",
                                  f"Primer registro: {kwh:.1f} kWh. Continúe midiendo.",
                                  COLORS["info"], "📈")

        # Tendencia: comparar primera mitad vs segunda mitad
        mitad = len(valores) // 2
        prom_ini = sum(valores[:mitad]) / mitad if mitad else 0
        prom_fin = sum(valores[mitad:]) / (len(valores) - mitad)
        delta = prom_fin - prom_ini
        pct_ultimo = valores[-1] / cls.PROMESA_KWH

        if delta > 15 and pct_ultimo >= 0.85:
            return cls._resultado("Tendencia al Alza ↑",
                                  f"Generación creciendo (+{delta:.1f} kWh vs período anterior). "
                                  f"Último mes: {valores[-1]:.1f} kWh.",
                                  COLORS["success"], "🚀")
        if delta < -15:
            return cls._resultado("Tendencia a la Baja ↓",
                                  f"Generación decreciendo ({delta:.1f} kWh vs período anterior). "
                                  "Se recomienda revisión técnica.",
                                  COLORS["danger"], "⚠️")
        if pct_ultimo >= 0.90:
            return cls._resultado("Consumo Estable — Óptimo",
                                  f"Generación estable y sobre el 90 % de la promesa. "
                                  f"Último mes: {valores[-1]:.1f} kWh.",
                                  COLORS["accent_primary"], "⚡")
        if pct_ultimo >= 0.70:
            return cls._resultado("Consumo Estable — Moderado",
                                  f"Generación estable pero por debajo de la promesa "
                                  f"({valores[-1]:.1f}/{cls.PROMESA_KWH} kWh). "
                                  "Evalúe limpieza de paneles.",
                                  COLORS["warning"], "🔆")
        if pct_ultimo < 0.50:
            return cls._resultado("Ahorro Comprometido",
                                  f"Generación muy por debajo de la promesa "
                                  f"({valores[-1]:.1f}/{cls.PROMESA_KWH} kWh). "
                                  "Revisar inversor y conexiones urgente.",
                                  COLORS["danger"], "🔴")

        # Ahorro detectado: generación consistente + baja varianza
        varianza = max(valores) - min(valores)
        if varianza < 20 and pct_ultimo >= 0.80:
            return cls._resultado("Ahorro Detectado ✓",
                                  f"Generación muy consistente (varianza {varianza:.1f} kWh). "
                                  "El sistema opera eficientemente.",
                                  COLORS["success"], "💚")

        return cls._resultado("Normal",
                              f"Sin anomalías detectadas. Último: {valores[-1]:.1f} kWh.",
                              COLORS["text_secondary"], "📊")

    @staticmethod
    def _resultado(etiqueta, descripcion, color, emoji) -> dict:
        return {"etiqueta": etiqueta, "descripcion": descripcion,
                "color": color, "emoji": emoji}


# ─── Página UI ────────────────────────────────────────────────────────────────

class ConsumosPage(ctk.CTkFrame):
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
        ctk.CTkLabel(hdr, text="📊  Consumo y Generación Solar",
                     font=FONTS["title_large"],
                     text_color=COLORS["text_primary"]).pack(side="left")

        panels = ctk.CTkFrame(cont, fg_color="transparent")
        panels.pack(fill="both", expand=True)
        panels.columnconfigure(0, weight=2)
        panels.columnconfigure(1, weight=3)

        # ── LISTA + FILTRO ─────────────────────────────────────────
        left = ctk.CTkFrame(panels, fg_color=COLORS["bg_card"],
                             corner_radius=12, border_width=1,
                             border_color=COLORS["border_primary"])
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 8))

        ctk.CTkLabel(left, text="Registros Mensuales",
                     font=FONTS["title_small"],
                     text_color=COLORS["text_secondary"]).pack(
                         anchor="w", padx=16, pady=(14, 6))

        clientes = self.db.obtener_clientes()
        self.cli_map = {c["nombre_titular"]: c["id"] for c in clientes}
        opts = ["Todos los clientes"] + list(self.cli_map.keys())

        self.combo_filtro = ctk.CTkComboBox(
            left, values=opts, height=32,
            fg_color=COLORS["bg_input"],
            border_color=COLORS["border_primary"],
            text_color=COLORS["text_primary"], font=FONTS["body_small"],
            command=lambda v: self._cargar_lista())
        self.combo_filtro.pack(fill="x", padx=12, pady=(0, 8))

        self.lista_scroll = ctk.CTkScrollableFrame(
            left, fg_color="transparent", height=400)
        self.lista_scroll.pack(fill="both", expand=True, padx=8, pady=(0, 12))

        # ── FORMULARIO ────────────────────────────────────────────
        right = ctk.CTkScrollableFrame(
            panels, fg_color=COLORS["bg_card"], corner_radius=12)
        right.grid(row=0, column=1, sticky="nsew", padx=(8, 0))
        self._construir_formulario(right)

    def _construir_formulario(self, parent):
        inner = ctk.CTkFrame(parent, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=20, pady=16)

        ctk.CTkLabel(inner, text="Registrar Consumo Mensual",
                     font=FONTS["title_medium"],
                     text_color=COLORS["text_primary"]).pack(anchor="w", pady=(0, 14))

        SectionTitle(inner, "▸ Cliente y Período").pack(anchor="w", pady=(0, 6))

        ctk.CTkLabel(inner, text="Cliente *", font=FONTS["label"],
                     text_color=COLORS["text_secondary"]).pack(anchor="w")
        self.cb_cliente = ctk.CTkComboBox(
            inner, values=list(self.cli_map.keys()),
            height=36, fg_color=COLORS["bg_input"],
            border_color=COLORS["border_primary"],
            text_color=COLORS["text_primary"], font=FONTS["body_medium"],
            command=lambda v: self._actualizar_agente())
        self.cb_cliente.pack(fill="x", pady=(3, 12))

        g = ctk.CTkFrame(inner, fg_color="transparent")
        g.pack(fill="x")
        g.columnconfigure((0, 1), weight=1)

        # Mes y año
        meses = ["01 — Enero","02 — Febrero","03 — Marzo","04 — Abril",
                 "05 — Mayo","06 — Junio","07 — Julio","08 — Agosto",
                 "09 — Septiembre","10 — Octubre","11 — Noviembre","12 — Diciembre"]
        ctk.CTkLabel(g, text="Mes *", font=FONTS["label"],
                     text_color=COLORS["text_secondary"]).grid(
                         row=0, column=0, sticky="w", padx=(0, 6))
        self.cb_mes = ctk.CTkComboBox(
            g, values=meses, height=34,
            fg_color=COLORS["bg_input"],
            border_color=COLORS["border_primary"],
            text_color=COLORS["text_primary"], font=FONTS["body_small"])
        self.cb_mes.grid(row=1, column=0, sticky="ew", padx=(0, 6), pady=(3, 10))
        self.cb_mes.set(meses[datetime.now().month - 1])

        self.f_anio = FormField(g, "Año *", "Ej: 2025", required=True)
        self.f_anio.grid(row=1, column=1, sticky="ew", padx=(6, 0), pady=(3, 10))
        self.f_anio.set(str(datetime.now().year))

        SectionTitle(inner, "▸ Lecturas").pack(anchor="w", pady=(8, 6))

        g2 = ctk.CTkFrame(inner, fg_color="transparent")
        g2.pack(fill="x")
        g2.columnconfigure((0, 1), weight=1)

        self.f_kwh = FormField(g2, "kWh Generados (Inversor)", "Ej: 245.0")
        self.f_kwh.grid(row=0, column=0, sticky="ew", padx=(0, 6), pady=4)

        self.f_medidor = FormField(g2, "Lectura Medidor Red", "Ej: 80.5")
        self.f_medidor.grid(row=0, column=1, sticky="ew", padx=(6, 0), pady=4)

        SectionTitle(inner, "▸ Valores Económicos").pack(anchor="w", pady=(12, 6))

        g3 = ctk.CTkFrame(inner, fg_color="transparent")
        g3.pack(fill="x")
        g3.columnconfigure((0, 1), weight=1)

        self.f_subsidio = FormField(g3, "Subsidio Air-e ($)", "Ej: 12000")
        self.f_subsidio.grid(row=0, column=0, sticky="ew", padx=(0, 6), pady=4)

        self.f_deducciones = FormField(g3, "Deducciones Air-e ($)",
                                        "Descuentos manuales")
        self.f_deducciones.grid(row=0, column=1, sticky="ew",
                                 padx=(6, 0), pady=4)

        # ── PANEL AGENTE ──────────────────────────────────────────
        SectionTitle(inner, "▸ Análisis Inteligente (Agente GSC)").pack(
            anchor="w", pady=(16, 6))

        self.agente_card = ctk.CTkFrame(
            inner, fg_color=COLORS["bg_secondary"],
            corner_radius=10, border_width=1,
            border_color=COLORS["border_primary"])
        self.agente_card.pack(fill="x", pady=(0, 12))

        ag_inner = ctk.CTkFrame(self.agente_card, fg_color="transparent")
        ag_inner.pack(fill="x", padx=16, pady=12)

        self.lbl_ag_emoji = ctk.CTkLabel(
            ag_inner, text="📭", font=("Segoe UI Emoji", 28))
        self.lbl_ag_emoji.pack(side="left", padx=(0, 12))

        ag_text = ctk.CTkFrame(ag_inner, fg_color="transparent")
        ag_text.pack(side="left", fill="x", expand=True)

        self.lbl_ag_titulo = ctk.CTkLabel(
            ag_text, text="Seleccione un cliente",
            font=FONTS["title_small"],
            text_color=COLORS["text_muted"])
        self.lbl_ag_titulo.pack(anchor="w")

        self.lbl_ag_desc = ctk.CTkLabel(
            ag_text, text="El agente analizará el histórico automáticamente.",
            font=FONTS["body_small"],
            text_color=COLORS["text_muted"],
            wraplength=340)
        self.lbl_ag_desc.pack(anchor="w")

        # Barra de promesa
        barra_row = ctk.CTkFrame(inner, fg_color="transparent")
        barra_row.pack(fill="x", pady=(0, 6))
        ctk.CTkLabel(barra_row, text="Meta mensual 240 kWh:",
                     font=FONTS["caption"],
                     text_color=COLORS["text_muted"]).pack(side="left")
        self.lbl_pct = ctk.CTkLabel(barra_row, text="—",
                                     font=FONTS["caption"],
                                     text_color=COLORS["text_muted"])
        self.lbl_pct.pack(side="right")

        self.barra_promesa = ctk.CTkProgressBar(
            inner, height=8, corner_radius=4,
            fg_color=COLORS["bg_input"],
            progress_color=COLORS["accent_primary"])
        self.barra_promesa.pack(fill="x", pady=(0, 14))
        self.barra_promesa.set(0)

        # Botón guardar
        ActionButton(inner, text="💾  Registrar Consumo",
                     command=self._guardar).pack(fill="x")

    # ─────────────────────────────────────────────────────────────────────────
    # LISTA
    # ─────────────────────────────────────────────────────────────────────────

    def _cargar_lista(self, _=None):
        for w in self.lista_scroll.winfo_children():
            w.destroy()

        filtro = self.combo_filtro.get()
        cid = self.cli_map.get(filtro)

        registros = self.db.obtener_consumos(cid)

        if not registros:
            ctk.CTkLabel(self.lista_scroll, text="Sin registros de consumo.",
                         font=FONTS["body_medium"],
                         text_color=COLORS["text_muted"]).pack(pady=20)
            return

        for r in registros:
            self._item_consumo(r)

    def _item_consumo(self, r: dict):
        kwh = r.get("kwh_consumidos", 0) or 0
        pct = min(kwh / AgenteConsumo.PROMESA_KWH, 1.0)
        color = (COLORS["success"] if pct >= 0.90
                 else COLORS["warning"] if pct >= 0.60
                 else COLORS["danger"])

        item = ctk.CTkFrame(self.lista_scroll, fg_color=COLORS["bg_secondary"],
                             corner_radius=8)
        item.pack(fill="x", pady=2, padx=2)

        top = ctk.CTkFrame(item, fg_color="transparent")
        top.pack(fill="x", padx=12, pady=(8, 3))
        ctk.CTkLabel(top,
                     text=f"{str(r.get('mes','?')).zfill(2)}/{r.get('anio','?')}",
                     font=FONTS["label"],
                     text_color=COLORS["text_primary"]).pack(side="left")
        ctk.CTkLabel(top, text=r.get("nombre_titular", ""),
                     font=FONTS["body_small"],
                     text_color=COLORS["text_secondary"]).pack(side="left", padx=8)
        ctk.CTkLabel(top, text=f"{kwh:.1f} / 240 kWh",
                     font=FONTS["body_small"],
                     text_color=color).pack(side="right")

        bar = ctk.CTkProgressBar(item, height=5, corner_radius=3,
                                  fg_color=COLORS["bg_input"],
                                  progress_color=color)
        bar.pack(fill="x", padx=12, pady=(0, 4))
        bar.set(pct)

        bot = ctk.CTkFrame(item, fg_color="transparent")
        bot.pack(fill="x", padx=12, pady=(0, 8))
        sub = (f"Red: {r.get('lectura_medidor_red',0):.1f} kWh  |  "
               f"Subsidio: ${r.get('subsidio_aire',0):,.0f}  |  "
               f"Ded: ${r.get('deducciones_aire',0):,.0f}")
        ctk.CTkLabel(bot, text=sub, font=FONTS["caption"],
                     text_color=COLORS["text_muted"]).pack(anchor="w")

    # ─────────────────────────────────────────────────────────────────────────
    # AGENTE
    # ─────────────────────────────────────────────────────────────────────────

    def _actualizar_agente(self, _=None):
        """Recalcula el diagnóstico cuando cambia el cliente seleccionado."""
        nombre = self.cb_cliente.get()
        cid = self.cli_map.get(nombre)
        if not cid:
            return

        registros = self.db.obtener_consumos(cid)
        diag = AgenteConsumo.analizar(registros)

        self.lbl_ag_emoji.configure(text=diag["emoji"])
        self.lbl_ag_titulo.configure(text=diag["etiqueta"],
                                      text_color=diag["color"])
        self.lbl_ag_desc.configure(text=diag["descripcion"],
                                    text_color=COLORS["text_secondary"])

        if registros:
            ultimo_kwh = registros[0].get("kwh_consumidos", 0) or 0
            pct = min(ultimo_kwh / AgenteConsumo.PROMESA_KWH, 1.0)
            self.barra_promesa.set(pct)
            self.barra_promesa.configure(progress_color=diag["color"])
            self.lbl_pct.configure(
                text=f"{pct*100:.1f}%  ({ultimo_kwh:.1f} kWh)",
                text_color=diag["color"])
        else:
            self.barra_promesa.set(0)
            self.lbl_pct.configure(text="—")

    # ─────────────────────────────────────────────────────────────────────────
    # GUARDAR
    # ─────────────────────────────────────────────────────────────────────────

    def _guardar(self):
        nombre = self.cb_cliente.get()
        cid = self.cli_map.get(nombre)
        if not cid:
            messagebox.showwarning("GSC", "Seleccione un cliente.")
            return

        if not self.f_anio.validate():
            return

        try:
            mes_str = self.cb_mes.get()[:2]
            datos = {
                "cliente_id":         cid,
                "mes":                int(mes_str),
                "anio":               int(self.f_anio.get()),
                "kwh_consumidos":     float(self.f_kwh.get() or 0),
                "lectura_medidor_red": float(self.f_medidor.get() or 0),
                "subsidio_aire":      float(self.f_subsidio.get() or 0),
                "deducciones_aire":   float(self.f_deducciones.get() or 0),
            }
            self.db.crear_consumo(datos)
            messagebox.showinfo("GSC", "Consumo registrado correctamente.")
            for f in [self.f_kwh, self.f_medidor, self.f_subsidio,
                      self.f_deducciones, self.f_anio]:
                f.clear()
            self.f_anio.set(str(datetime.now().year))
            self._cargar_lista()
            self._actualizar_agente()
        except Exception as e:
            messagebox.showerror("Error", str(e))
