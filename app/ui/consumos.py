"""
consumos.py — Módulo de Consumo v2.1
Sincronización ciclo Air-e, agente inteligente con kWh/día,
detección de subsidio 173 kWh (Barranquilla).
"""

import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime, date
from app.theme import COLORS, FONTS
from app.ui.widgets import FormField, ActionButton, SectionTitle


# ─── Motor de Cálculo ─────────────────────────────────────────────────────────

class CalculadoraCiclo:
    """Toda la matemática de facturación en un solo lugar."""

    LIMITE_SUBSIDIO = 173   # kWh — consumo de subsistencia Barranquilla

    @staticmethod
    def calcular(kwh_total: float, kwh_gsc: float, t_aire: float, t_gsc: float,
                 cargos: float, descuentos: float) -> dict:
        """
        Retorna dict con todos los valores calculados.
        kwh_total       = generación GSC + lectura medidor red
        kwh_gsc         = solo lo que produjeron los paneles
        """
        excedente        = max(kwh_total - kwh_gsc, 0)
        bruto_aire       = kwh_total * t_aire                        # sin paneles
        total_gsc        = kwh_gsc * t_gsc                           # cuota GSC
        costo_exc        = excedente * t_aire if excedente > 0 else 0
        total_red        = max(costo_exc + cargos - descuentos, 0)   # factura red
        total_real       = total_gsc + total_red                     # pago real
        ahorro_neto      = max(bruto_aire - total_real, 0)
        subsidio_ok      = excedente <= CalculadoraCiclo.LIMITE_SUBSIDIO

        return {
            "excedente":   excedente,
            "bruto_aire":  bruto_aire,
            "total_gsc":   total_gsc,
            "costo_exc":   costo_exc,
            "total_red":   total_red,
            "total_real":  total_real,
            "ahorro_neto": ahorro_neto,
            "subsidio_ok": subsidio_ok,
            "cobertura_pct": min(kwh_gsc / kwh_total * 100, 100) if kwh_total > 0 else 0,
        }

    @staticmethod
    def calcular_dias(fecha_ini: str, fecha_fin: str) -> int:
        """Calcula días entre dos fechas YYYY-MM-DD."""
        try:
            d1 = date.fromisoformat(fecha_ini)
            d2 = date.fromisoformat(fecha_fin)
            return max((d2 - d1).days, 1)
        except Exception:
            return 30


# ─── Agente de Análisis Inteligente ──────────────────────────────────────────

class AgenteConsumo:
    """
    Compara kWh/día actual vs mes anterior y emite alertas dinámicas.
    """

    PROMESA_KWH = 240

    @classmethod
    def analizar(cls, registros: list) -> dict:
        if not registros:
            return cls._r("Sin datos",
                          "Aún no hay registros para este cliente.",
                          COLORS["text_muted"], "📭", None)

        ultimo = registros[0]
        kwh_u  = ultimo.get("kwh_consumidos") or 0
        dias_u = ultimo.get("dias_ciclo") or 30
        kd_u   = kwh_u / dias_u if dias_u else 0   # kWh/día actual

        # Comparar con anterior
        if len(registros) >= 2:
            prev   = registros[1]
            kwh_p  = prev.get("kwh_consumidos") or 0
            dias_p = prev.get("dias_ciclo") or 30
            kd_p   = kwh_p / dias_p if dias_p else 0

            if kd_p > 0:
                cambio_pct = ((kd_u - kd_p) / kd_p) * 100
            else:
                cambio_pct = 0

            cobertura = ultimo.get("kwh_generados_gsc", 0) or 0
            cob_pct   = min(cobertura / kwh_u * 100, 100) if kwh_u > 0 else 0
            tendencia = "📈 Consumo subiendo" if cambio_pct > 0 else "📉 Consumo bajando"

            if cambio_pct > 10:
                return cls._r(
                    "⚠️  Alerta: Incremento detectado",
                    f"El consumo subió un {cambio_pct:.1f}% vs el período anterior "
                    f"({kd_u:.1f} vs {kd_p:.1f} kWh/día). "
                    "El cliente está demandando más energía de la red.",
                    COLORS["danger"], "⚠️", tendencia)

            if cob_pct >= 100:
                return cls._r(
                    "✅  Eficiencia Óptima",
                    f"Los paneles cubrieron el {cob_pct:.0f}% del hogar este ciclo. "
                    f"Consumo estable: {kd_u:.1f} kWh/día.",
                    COLORS["success"], "✅", "📉 Consumo estable o bajando")

            return cls._r(
                f"✅  Eficiencia al {cob_pct:.0f}%",
                f"Los paneles cubren el {cob_pct:.0f}% del hogar. "
                f"Consumo: {kd_u:.1f} kWh/día ({tendencia.lower()}). "
                f"Variación vs anterior: {cambio_pct:+.1f}%.",
                COLORS["accent_primary"] if cob_pct >= 70 else COLORS["warning"],
                "⚡" if cob_pct >= 70 else "🔆", tendencia)

        # Solo un registro
        cobertura = ultimo.get("kwh_generados_gsc", 0) or 0
        cob_pct   = min(cobertura / kwh_u * 100, 100) if kwh_u > 0 else 0
        return cls._r(
            "📊  Primer Registro",
            f"Consumo: {kwh_u:.1f} kWh ({kd_u:.1f} kWh/día). "
            f"Cobertura GSC: {cob_pct:.0f}%. Continue registrando para ver tendencias.",
            COLORS["info"], "📊", None)

    @staticmethod
    def _r(etiqueta, descripcion, color, emoji, tendencia):
        return {"etiqueta": etiqueta, "descripcion": descripcion,
                "color": color, "emoji": emoji, "tendencia": tendencia}


# ─── Página UI ────────────────────────────────────────────────────────────────

class ConsumosPage(ctk.CTkFrame):
    def __init__(self, parent, db):
        super().__init__(parent, fg_color="transparent")
        self.db = db
        self._construir_ui()
        self._cargar_lista()

    # ── Layout principal ──────────────────────────────────────────────────────

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

        # Lista
        left = ctk.CTkFrame(panels, fg_color=COLORS["bg_card"],
                             corner_radius=12, border_width=1,
                             border_color=COLORS["border_primary"])
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        self._construir_lista(left)

        # Formulario
        right = ctk.CTkScrollableFrame(panels, fg_color=COLORS["bg_card"],
                                        corner_radius=12)
        right.grid(row=0, column=1, sticky="nsew", padx=(8, 0))
        self._construir_formulario(right)

    # ── Panel izquierdo: historial ─────────────────────────────────────────────

    def _construir_lista(self, parent):
        ctk.CTkLabel(parent, text="Historial de Ciclos",
                     font=FONTS["title_small"],
                     text_color=COLORS["text_secondary"]).pack(
                         anchor="w", padx=16, pady=(14, 6))

        clientes = self.db.obtener_clientes()
        self.cli_map = {c["nombre_titular"]: c["id"] for c in clientes}
        opts = ["Todos los clientes"] + list(self.cli_map.keys())

        self.combo_filtro = ctk.CTkComboBox(
            parent, values=opts, height=32,
            fg_color=COLORS["bg_input"], border_color=COLORS["border_primary"],
            text_color=COLORS["text_primary"], font=FONTS["body_small"],
            command=lambda v: self._cargar_lista())
        self.combo_filtro.pack(fill="x", padx=12, pady=(0, 8))

        self.lista_scroll = ctk.CTkScrollableFrame(parent, fg_color="transparent")
        self.lista_scroll.pack(fill="both", expand=True, padx=8, pady=(0, 12))

    # ── Panel derecho: formulario ─────────────────────────────────────────────

    def _construir_formulario(self, parent):
        inner = ctk.CTkFrame(parent, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=20, pady=16)

        ctk.CTkLabel(inner, text="Registrar Ciclo de Consumo",
                     font=FONTS["title_medium"],
                     text_color=COLORS["text_primary"]).pack(anchor="w", pady=(0, 14))

        # ── CLIENTE ───────────────────────────────────────────────
        SectionTitle(inner, "▸ Cliente").pack(anchor="w", pady=(0, 4))
        ctk.CTkLabel(inner, text="Cliente *", font=FONTS["label"],
                     text_color=COLORS["text_secondary"]).pack(anchor="w")
        self.cb_cliente = ctk.CTkComboBox(
            inner, values=list(self.cli_map.keys()),
            height=36, fg_color=COLORS["bg_input"],
            border_color=COLORS["border_primary"],
            text_color=COLORS["text_primary"], font=FONTS["body_medium"],
            command=lambda v: self._actualizar_agente())
        self.cb_cliente.pack(fill="x", pady=(3, 12))

        # ── CICLO AIR-E ───────────────────────────────────────────
        SectionTitle(inner, "▸ Período del Ciclo Air-e").pack(anchor="w", pady=(0, 6))

        g_ciclo = ctk.CTkFrame(inner, fg_color="transparent")
        g_ciclo.pack(fill="x")
        g_ciclo.columnconfigure((0, 1, 2), weight=1)

        self.f_fecha_ini = FormField(g_ciclo, "Fecha Inicio Ciclo *",
                                      "YYYY-MM-DD", required=True)
        self.f_fecha_ini.grid(row=0, column=0, sticky="ew", padx=(0, 6), pady=4)
        self.f_fecha_ini.entry.bind("<FocusOut>", lambda e: self._calcular_dias())

        self.f_fecha_fin = FormField(g_ciclo, "Fecha Fin Ciclo *",
                                      "YYYY-MM-DD", required=True)
        self.f_fecha_fin.grid(row=0, column=1, sticky="ew", padx=6, pady=4)
        self.f_fecha_fin.entry.bind("<FocusOut>", lambda e: self._calcular_dias())

        # Días calculados
        dias_frame = ctk.CTkFrame(g_ciclo, fg_color=COLORS["bg_secondary"],
                                   corner_radius=8)
        dias_frame.grid(row=0, column=2, sticky="ew", padx=(6, 0), pady=4)
        ctk.CTkLabel(dias_frame, text="Días ciclo",
                     font=FONTS["caption"],
                     text_color=COLORS["text_muted"]).pack(pady=(6, 0))
        self.lbl_dias = ctk.CTkLabel(dias_frame, text="—",
                                      font=FONTS["kpi_small"],
                                      text_color=COLORS["accent_primary"])
        self.lbl_dias.pack()
        self.lbl_dias_warn = ctk.CTkLabel(dias_frame, text="",
                                           font=FONTS["caption"],
                                           text_color=COLORS["warning"])
        self.lbl_dias_warn.pack(pady=(0, 6))

        # Mes/Año para indexar
        g_mes = ctk.CTkFrame(inner, fg_color="transparent")
        g_mes.pack(fill="x")
        g_mes.columnconfigure((0, 1), weight=1)

        meses = ["01 — Enero","02 — Febrero","03 — Marzo","04 — Abril",
                 "05 — Mayo","06 — Junio","07 — Julio","08 — Agosto",
                 "09 — Septiembre","10 — Octubre","11 — Noviembre","12 — Diciembre"]
        ctk.CTkLabel(g_mes, text="Mes factura *", font=FONTS["label"],
                     text_color=COLORS["text_secondary"]).grid(
                         row=0, column=0, sticky="w", padx=(0, 6))
        self.cb_mes = ctk.CTkComboBox(
            g_mes, values=meses, height=34,
            fg_color=COLORS["bg_input"], border_color=COLORS["border_primary"],
            text_color=COLORS["text_primary"], font=FONTS["body_small"])
        self.cb_mes.grid(row=1, column=0, sticky="ew", padx=(0, 6), pady=(3, 8))
        self.cb_mes.set(meses[datetime.now().month - 1])

        self.f_anio = FormField(g_mes, "Año *", "Ej: 2025", required=True)
        self.f_anio.grid(row=1, column=1, sticky="ew", pady=(3, 8))
        self.f_anio.set(str(datetime.now().year))

        # ── LECTURAS ──────────────────────────────────────────────
        SectionTitle(inner, "▸ Lecturas de Energía").pack(anchor="w", pady=(8, 6))

        g_lec = ctk.CTkFrame(inner, fg_color="transparent")
        g_lec.pack(fill="x")
        g_lec.columnconfigure((0, 1), weight=1)

        self.f_kwh_gsc = FormField(g_lec, "kWh Generados GSC *",
                                    "Ej: 240.0 (solo paneles)", required=True)
        self.f_kwh_gsc.grid(row=0, column=0, sticky="ew", padx=(0, 6), pady=4)
        self.f_kwh_gsc.entry.bind("<KeyRelease>", lambda e: self._calcular_preview())

        self.f_medidor = FormField(g_lec, "Lectura Medidor Red (kWh)",
                                    "Ej: 80.5 (de Air-e)")
        self.f_medidor.grid(row=0, column=1, sticky="ew", padx=(6, 0), pady=4)
        self.f_medidor.entry.bind("<KeyRelease>", lambda e: self._calcular_preview())

        # Consumo total calculado
        total_frame = ctk.CTkFrame(inner, fg_color=COLORS["bg_secondary"],
                                    corner_radius=8)
        total_frame.pack(fill="x", pady=(0, 8))
        tf_row = ctk.CTkFrame(total_frame, fg_color="transparent")
        tf_row.pack(fill="x", padx=14, pady=8)
        ctk.CTkLabel(tf_row, text="Consumo Total del Período:",
                     font=FONTS["label"],
                     text_color=COLORS["text_secondary"]).pack(side="left")
        self.lbl_consumo_total = ctk.CTkLabel(
            tf_row, text="— kWh",
            font=FONTS["title_small"],
            text_color=COLORS["accent_primary"])
        self.lbl_consumo_total.pack(side="right")

        # ── TARIFAS Y CARGOS ──────────────────────────────────────
        SectionTitle(inner, "▸ Tarifas y Cargos").pack(anchor="w", pady=(8, 6))

        g_tar = ctk.CTkFrame(inner, fg_color="transparent")
        g_tar.pack(fill="x")
        g_tar.columnconfigure((0, 1), weight=1)

        self.f_tarifa_aire = FormField(g_tar, "Tarifa Air-e ($/kWh)", "Ej: 890")
        self.f_tarifa_aire.grid(row=0, column=0, sticky="ew", padx=(0, 6), pady=4)
        self.f_tarifa_aire.entry.bind("<KeyRelease>", lambda e: self._calcular_preview())

        self.f_tarifa_gsc = FormField(g_tar, "Tarifa GSC ($/kWh)", "Ej: 650")
        self.f_tarifa_gsc.grid(row=0, column=1, sticky="ew", padx=(6, 0), pady=4)
        self.f_tarifa_gsc.entry.bind("<KeyRelease>", lambda e: self._calcular_preview())

        self.f_cargos = FormField(g_tar, "Cargos Adicionales Red ($)",
                                   "Alumb. público, fijos…")
        self.f_cargos.grid(row=1, column=0, sticky="ew", padx=(0, 6), pady=4)
        self.f_cargos.entry.bind("<KeyRelease>", lambda e: self._calcular_preview())

        self.f_descuentos = FormField(g_tar, "Descuentos Red ($)", "Saldos a favor…")
        self.f_descuentos.grid(row=1, column=1, sticky="ew", padx=(6, 0), pady=4)
        self.f_descuentos.entry.bind("<KeyRelease>", lambda e: self._calcular_preview())

        self.f_subsidio_cop = FormField(inner, "Subsidio Air-e ($)", "Monto subsidio aplicado")
        self.f_subsidio_cop.pack(fill="x", pady=4)

        # ── PREVIEW DE CÁLCULO ────────────────────────────────────
        SectionTitle(inner, "▸ Vista Previa del Período").pack(anchor="w", pady=(12, 6))

        prev = ctk.CTkFrame(inner, fg_color=COLORS["bg_secondary"],
                             corner_radius=10, border_width=1,
                             border_color=COLORS["border_primary"])
        prev.pack(fill="x", pady=(0, 10))
        pi = ctk.CTkFrame(prev, fg_color="transparent")
        pi.pack(fill="x", padx=14, pady=12)

        def _krow(lbl_txt, attr, color=COLORS["text_primary"]):
            f = ctk.CTkFrame(pi, fg_color="transparent")
            f.pack(fill="x", pady=2)
            ctk.CTkLabel(f, text=lbl_txt, font=FONTS["body_small"],
                         text_color=COLORS["text_secondary"],
                         width=240, anchor="w").pack(side="left")
            lbl = ctk.CTkLabel(f, text="—", font=FONTS["label"], text_color=color)
            lbl.pack(side="right")
            setattr(self, attr, lbl)

        _krow("Si pagara 100% a Air-e:", "lbl_bruto_aire", COLORS["danger"])
        _krow("Pago a GSC:", "lbl_total_gsc", COLORS["accent_primary"])
        _krow("Excedente (kWh a Red):", "lbl_excedente", COLORS["warning"])
        _krow("Costo excedente Red:", "lbl_costo_exc", COLORS["warning"])

        # Subsidio badge
        self.lbl_subsidio_badge = ctk.CTkLabel(
            pi, text="", font=FONTS["label"],
            text_color=COLORS["success"],
            fg_color=COLORS["bg_card"], corner_radius=6)
        self.lbl_subsidio_badge.pack(fill="x", pady=(4, 4))

        ctk.CTkFrame(pi, height=1,
                      fg_color=COLORS["border_primary"]).pack(fill="x", pady=4)
        _krow("💰  Total Real a Pagar:", "lbl_total_real",
              COLORS["text_primary"])
        _krow("✅  Ahorro Neto:", "lbl_ahorro_neto", COLORS["success"])

        # ── AGENTE ────────────────────────────────────────────────
        SectionTitle(inner, "▸ Agente de Análisis GSC").pack(anchor="w", pady=(12, 6))

        ag_card = ctk.CTkFrame(inner, fg_color=COLORS["bg_secondary"],
                                corner_radius=10, border_width=1,
                                border_color=COLORS["border_primary"])
        ag_card.pack(fill="x", pady=(0, 10))
        ag_inner = ctk.CTkFrame(ag_card, fg_color="transparent")
        ag_inner.pack(fill="x", padx=14, pady=12)

        self.lbl_ag_emoji = ctk.CTkLabel(ag_inner, text="📭",
                                          font=("Segoe UI Emoji", 26))
        self.lbl_ag_emoji.pack(side="left", padx=(0, 10))
        ag_txt = ctk.CTkFrame(ag_inner, fg_color="transparent")
        ag_txt.pack(side="left", fill="x", expand=True)
        self.lbl_ag_titulo = ctk.CTkLabel(ag_txt, text="Seleccione un cliente",
                                           font=FONTS["title_small"],
                                           text_color=COLORS["text_muted"])
        self.lbl_ag_titulo.pack(anchor="w")
        self.lbl_ag_desc = ctk.CTkLabel(ag_txt, text="",
                                         font=FONTS["body_small"],
                                         text_color=COLORS["text_muted"],
                                         wraplength=320)
        self.lbl_ag_desc.pack(anchor="w")
        self.lbl_tendencia = ctk.CTkLabel(ag_txt, text="",
                                           font=FONTS["caption"],
                                           text_color=COLORS["info"])
        self.lbl_tendencia.pack(anchor="w")

        # Barra cobertura
        bar_row = ctk.CTkFrame(inner, fg_color="transparent")
        bar_row.pack(fill="x", pady=(0, 4))
        ctk.CTkLabel(bar_row, text="Cobertura GSC del hogar:",
                     font=FONTS["caption"],
                     text_color=COLORS["text_muted"]).pack(side="left")
        self.lbl_cob_pct = ctk.CTkLabel(bar_row, text="—",
                                         font=FONTS["caption"],
                                         text_color=COLORS["accent_primary"])
        self.lbl_cob_pct.pack(side="right")
        self.barra_cob = ctk.CTkProgressBar(inner, height=8, corner_radius=4,
                                             fg_color=COLORS["bg_input"],
                                             progress_color=COLORS["accent_primary"])
        self.barra_cob.pack(fill="x", pady=(0, 14))
        self.barra_cob.set(0)

        ActionButton(inner, text="💾  Registrar Ciclo",
                     command=self._guardar).pack(fill="x")

    # ── Lógica ────────────────────────────────────────────────────────────────

    def _calcular_dias(self):
        fi = self.f_fecha_ini.get()
        ff = self.f_fecha_fin.get()
        if fi and ff:
            dias = CalculadoraCiclo.calcular_dias(fi, ff)
            self.lbl_dias.configure(text=str(dias))
            if dias > 32:
                self.lbl_dias_warn.configure(text="⚠ Período inusual")
            elif dias < 25:
                self.lbl_dias_warn.configure(text="⚠ Ciclo corto")
            else:
                self.lbl_dias_warn.configure(text="✓")

    def _calcular_preview(self, *_):
        try:
            kwh_gsc  = float(self.f_kwh_gsc.get() or 0)
            medidor  = float(self.f_medidor.get() or 0)
            t_aire   = float(self.f_tarifa_aire.get() or 0)
            t_gsc    = float(self.f_tarifa_gsc.get() or 0)
            cargos   = float(self.f_cargos.get() or 0)
            desc     = float(self.f_descuentos.get() or 0)
        except ValueError:
            return

        kwh_total = kwh_gsc + medidor
        self.lbl_consumo_total.configure(
            text=f"{kwh_total:.1f} kWh  ({kwh_gsc:.1f} GSC + {medidor:.1f} Red)")

        if t_aire == 0 or t_gsc == 0:
            return

        c = CalculadoraCiclo.calcular(kwh_total, kwh_gsc, t_aire, t_gsc, cargos, desc)

        self.lbl_bruto_aire.configure(text=f"$ {c['bruto_aire']:,.0f}".replace(",", "."))
        self.lbl_total_gsc.configure(text=f"$ {c['total_gsc']:,.0f}".replace(",", "."))
        self.lbl_excedente.configure(text=f"{c['excedente']:.1f} kWh")
        self.lbl_costo_exc.configure(text=f"$ {c['costo_exc']:,.0f}".replace(",", "."))
        self.lbl_total_real.configure(text=f"$ {c['total_real']:,.0f}".replace(",", "."))
        self.lbl_ahorro_neto.configure(text=f"$ {c['ahorro_neto']:,.0f}".replace(",", "."))

        if c["subsidio_ok"] and c["excedente"] > 0:
            self.lbl_subsidio_badge.configure(
                text=f"  🎯 ¡BENEFICIO SUBSIDIO AIR-E DETECTADO!  "
                     f"Excedente {c['excedente']:.1f} kWh ≤ 173 kWh  ",
                text_color=COLORS["success"],
                fg_color=COLORS["bg_card"])
        elif c["excedente"] == 0:
            self.lbl_subsidio_badge.configure(
                text="  🎉 Cobertura 100% — Sin cobro a la red  ",
                text_color=COLORS["success"],
                fg_color=COLORS["bg_card"])
        else:
            self.lbl_subsidio_badge.configure(
                text=f"  Excedente {c['excedente']:.1f} kWh supera límite subsidio  ",
                text_color=COLORS["warning"],
                fg_color=COLORS["bg_card"])

    def _actualizar_agente(self, _=None):
        nombre = self.cb_cliente.get()
        cid = self.cli_map.get(nombre)
        if not cid:
            return

        # Auto-cargar tarifas del cliente
        cliente = self.db.obtener_cliente_por_id(cid)
        if cliente:
            if cliente.get("tarifa_aire_actual"):
                self.f_tarifa_aire.set(str(cliente["tarifa_aire_actual"]))
            if cliente.get("tarifa_gsc"):
                self.f_tarifa_gsc.set(str(cliente["tarifa_gsc"]))

        registros = self.db.obtener_consumos(cid)
        diag = AgenteConsumo.analizar(registros)

        self.lbl_ag_emoji.configure(text=diag["emoji"])
        self.lbl_ag_titulo.configure(text=diag["etiqueta"],
                                      text_color=diag["color"])
        self.lbl_ag_desc.configure(text=diag["descripcion"],
                                    text_color=COLORS["text_secondary"])
        self.lbl_tendencia.configure(
            text=diag["tendencia"] if diag["tendencia"] else "")

        if registros:
            kwh_u = registros[0].get("kwh_consumidos") or 0
            gsc_u = registros[0].get("kwh_generados_gsc") or 0
            pct   = min(gsc_u / kwh_u, 1.0) if kwh_u > 0 else 0
            self.barra_cob.set(pct)
            self.barra_cob.configure(progress_color=diag["color"])
            self.lbl_cob_pct.configure(
                text=f"{pct*100:.1f}%  ({gsc_u:.1f} / {kwh_u:.1f} kWh)",
                text_color=diag["color"])
        else:
            self.barra_cob.set(0)
            self.lbl_cob_pct.configure(text="—")

    def _cargar_lista(self, _=None):
        for w in self.lista_scroll.winfo_children():
            w.destroy()

        filtro = self.combo_filtro.get()
        cid = self.cli_map.get(filtro)
        registros = self.db.obtener_consumos(cid)

        if not registros:
            ctk.CTkLabel(self.lista_scroll, text="Sin registros.",
                         font=FONTS["body_medium"],
                         text_color=COLORS["text_muted"]).pack(pady=20)
            return

        for r in registros:
            self._item_consumo(r)

    def _item_consumo(self, r: dict):
        kwh_total = r.get("kwh_consumidos") or 0
        kwh_gsc   = r.get("kwh_generados_gsc") or 0
        dias      = r.get("dias_ciclo") or 30
        pct       = min(kwh_gsc / kwh_total, 1.0) if kwh_total > 0 else 0
        kd        = kwh_total / dias if dias else 0
        color     = (COLORS["success"] if pct >= 0.90
                     else COLORS["warning"] if pct >= 0.60
                     else COLORS["danger"])

        item = ctk.CTkFrame(self.lista_scroll, fg_color=COLORS["bg_secondary"],
                             corner_radius=8)
        item.pack(fill="x", pady=2, padx=2)

        top = ctk.CTkFrame(item, fg_color="transparent")
        top.pack(fill="x", padx=12, pady=(8, 2))

        # Período
        fi = r.get("fecha_inicio_ciclo", "")
        ff = r.get("fecha_fin_ciclo", "")
        periodo = f"{fi} → {ff}" if fi and ff else \
                  f"{str(r.get('mes','?')).zfill(2)}/{r.get('anio','?')}"

        ctk.CTkLabel(top, text=periodo, font=FONTS["label"],
                     text_color=COLORS["text_primary"]).pack(side="left")
        ctk.CTkLabel(top, text=r.get("nombre_titular", ""),
                     font=FONTS["body_small"],
                     text_color=COLORS["text_secondary"]).pack(side="left", padx=6)
        ctk.CTkLabel(top, text=f"{kwh_total:.0f} kWh | {kd:.1f}/día",
                     font=FONTS["body_small"], text_color=color).pack(side="right")

        bar = ctk.CTkProgressBar(item, height=5, corner_radius=3,
                                  fg_color=COLORS["bg_input"],
                                  progress_color=color)
        bar.pack(fill="x", padx=12, pady=(0, 3))
        bar.set(pct)

        bot = ctk.CTkFrame(item, fg_color="transparent")
        bot.pack(fill="x", padx=12, pady=(0, 8))
        ctk.CTkLabel(bot,
                     text=f"GSC: {kwh_gsc:.1f} kWh  |  Red: {r.get('lectura_medidor_red',0):.1f} kWh  "
                          f"|  Cobertura: {pct*100:.0f}%  |  {dias} días",
                     font=FONTS["caption"],
                     text_color=COLORS["text_muted"]).pack(anchor="w")

    def _guardar(self):
        nombre = self.cb_cliente.get()
        cid = self.cli_map.get(nombre)
        if not cid:
            messagebox.showwarning("GSC", "Seleccione un cliente.")
            return
        if not self.f_fecha_ini.validate() or not self.f_fecha_fin.validate():
            return
        if not self.f_kwh_gsc.validate() or not self.f_anio.validate():
            return

        try:
            kwh_gsc  = float(self.f_kwh_gsc.get() or 0)
            medidor  = float(self.f_medidor.get() or 0)
            kwh_tot  = kwh_gsc + medidor
            mes_str  = self.cb_mes.get()[:2]
            fi       = self.f_fecha_ini.get()
            ff       = self.f_fecha_fin.get()
            dias     = CalculadoraCiclo.calcular_dias(fi, ff)

            if dias > 32:
                if not messagebox.askyesno(
                        "Advertencia",
                        f"El ciclo tiene {dias} días, lo cual es inusual.\n"
                        "¿Desea guardar de todas formas?"):
                    return

            datos = {
                "cliente_id":            cid,
                "mes":                   int(mes_str),
                "anio":                  int(self.f_anio.get()),
                "kwh_generados_gsc":     kwh_gsc,
                "lectura_medidor_red":   medidor,
                "kwh_consumidos":        kwh_tot,
                "consumo_total_periodo": kwh_tot,
                "fecha_inicio_ciclo":    fi,
                "fecha_fin_ciclo":       ff,
                "dias_ciclo":            dias,
                "subsidio_aire":         float(self.f_subsidio_cop.get() or 0),
                "cargos_adicionales":    float(self.f_cargos.get() or 0),
                "descuentos_adicionales": float(self.f_descuentos.get() or 0),
            }
            self.db.crear_consumo(datos)
            messagebox.showinfo("GSC", f"Ciclo registrado — {dias} días, {kwh_tot:.1f} kWh totales.")

            for f in [self.f_fecha_ini, self.f_fecha_fin, self.f_kwh_gsc,
                      self.f_medidor, self.f_cargos, self.f_descuentos,
                      self.f_subsidio_cop, self.f_tarifa_aire, self.f_tarifa_gsc]:
                f.clear()
            self.f_anio.set(str(datetime.now().year))
            self.lbl_dias.configure(text="—")
            self.lbl_dias_warn.configure(text="")
            self.lbl_consumo_total.configure(text="— kWh")
            self._cargar_lista()
            self._actualizar_agente()

        except Exception as e:
            messagebox.showerror("Error", str(e))