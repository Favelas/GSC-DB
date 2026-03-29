"""
exportar_page.py — Exportación Excel + Facturación con PDF profesional.
Lógica de ahorro: Total Air-e vs Total GSC → Monto Ahorrado.
"""

import os
import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime
from app.theme import COLORS, FONTS, TABLAS_EXPORTABLES
from app.ui.widgets import ActionButton, SectionTitle


class ExportarPage(ctk.CTkFrame):
    def __init__(self, parent, db):
        super().__init__(parent, fg_color="transparent")
        self.db = db
        self._construir_ui()

    def _construir_ui(self):
        cont = ctk.CTkScrollableFrame(self, fg_color="transparent")
        cont.pack(fill="both", expand=True, padx=24, pady=16)

        ctk.CTkLabel(cont, text="📤  Exportar y Facturación",
                     font=FONTS["title_large"],
                     text_color=COLORS["text_primary"]).pack(anchor="w", pady=(0, 4))
        ctk.CTkLabel(cont,
                     text="Exporte tablas a Excel, genere PDFs de facturación y reportes de mantenimiento.",
                     font=FONTS["body_medium"],
                     text_color=COLORS["text_secondary"]).pack(anchor="w", pady=(0, 20))

        # ── EXPORTAR A EXCEL ──────────────────────────────────────
        SectionTitle(cont, "▸ Exportar Tablas a Excel").pack(
            anchor="w", pady=(0, 10))

        grid_excel = ctk.CTkFrame(cont, fg_color="transparent")
        grid_excel.pack(fill="x", pady=(0, 20))
        grid_excel.columnconfigure((0, 1), weight=1)

        tabla_info = [
            ("clientes",       "👤", "Clientes",              COLORS["info"]),
            ("proyectos",      "🔧", "Proyectos",             COLORS["accent_primary"]),
            ("consumos",       "📊", "Historial de Consumo",  COLORS["solar_yellow"]),
            ("mantenimientos", "🛠", "Mantenimientos",        COLORS["warning"]),
        ]
        for i, (tabla, icono, nombre, color) in enumerate(tabla_info):
            r, c = divmod(i, 2)
            card = ctk.CTkFrame(grid_excel, fg_color=COLORS["bg_card"],
                                corner_radius=12, border_width=1,
                                border_color=COLORS["border_primary"])
            card.grid(row=r, column=c, padx=8, pady=8, sticky="nsew")

            inn = ctk.CTkFrame(card, fg_color="transparent")
            inn.pack(fill="both", expand=True, padx=16, pady=14)

            hh = ctk.CTkFrame(inn, fg_color="transparent")
            hh.pack(fill="x", pady=(0, 6))
            ctk.CTkLabel(hh, text=icono, font=("Segoe UI Emoji", 22),
                         text_color=color).pack(side="left", padx=(0, 8))
            ctk.CTkLabel(hh, text=nombre, font=FONTS["title_small"],
                         text_color=COLORS["text_primary"]).pack(side="left")

            try:
                _, filas = self.db.exportar_tabla(tabla)
                n = len(filas)
            except Exception:
                n = 0
            ctk.CTkLabel(inn, text=f"{n} registros",
                         font=FONTS["caption"],
                         text_color=color).pack(anchor="w", pady=(0, 8))
            ActionButton(inn, text="📥  Exportar a Excel",
                         command=lambda t=tabla, nm=nombre: self._exportar_excel(t, nm)
                         ).pack(fill="x")

        sep = ctk.CTkFrame(cont, height=1, fg_color=COLORS["border_primary"])
        sep.pack(fill="x", pady=(4, 20))

        # ── FACTURACIÓN PDF ───────────────────────────────────────
        SectionTitle(cont, "▸ Factura de Ahorro Solar (PDF)").pack(
            anchor="w", pady=(0, 10))

        fac_card = ctk.CTkFrame(cont, fg_color=COLORS["bg_card"],
                                 corner_radius=12, border_width=1,
                                 border_color=COLORS["border_primary"])
        fac_card.pack(fill="x", pady=(0, 20))

        fac_inner = ctk.CTkFrame(fac_card, fg_color="transparent")
        fac_inner.pack(fill="x", padx=20, pady=16)

        # Selector de cliente
        clientes = self.db.obtener_clientes()
        self.cli_map = {c["nombre_titular"]: c for c in clientes}

        ctk.CTkLabel(fac_inner, text="Cliente:", font=FONTS["label"],
                     text_color=COLORS["text_secondary"]).pack(anchor="w")
        self.cb_cli_fac = ctk.CTkComboBox(
            fac_inner,
            values=list(self.cli_map.keys()) if self.cli_map else ["Sin clientes"],
            height=34, fg_color=COLORS["bg_input"],
            border_color=COLORS["border_primary"],
            text_color=COLORS["text_primary"], font=FONTS["body_small"],
            command=lambda v: self._actualizar_precios(v))
        self.cb_cli_fac.pack(fill="x", pady=(3, 12))

        # ── Fila 1: consumo total / generado GSC / tarifa Air-e ───────
        g = ctk.CTkFrame(fac_inner, fg_color="transparent")
        g.pack(fill="x")
        g.columnconfigure((0, 1, 2), weight=1)

        def _entry(parent, label, attr, row, col, padx=(0,0), placeholder=""):
            ctk.CTkLabel(parent, text=label, font=FONTS["label"],
                         text_color=COLORS["text_secondary"]).grid(
                             row=row, column=col, sticky="w",
                             padx=padx, pady=(8, 0))
            e = ctk.CTkEntry(parent, height=34, fg_color=COLORS["bg_input"],
                              border_color=COLORS["border_primary"],
                              text_color=COLORS["text_primary"],
                              font=FONTS["body_medium"],
                              placeholder_text=placeholder)
            e.grid(row=row+1, column=col, sticky="ew",
                   padx=padx, pady=(3, 6))
            e.bind("<KeyRelease>", lambda ev: self._calcular_preview())
            setattr(self, attr, e)

        _entry(g, "kWh Consumidos *",      "e_kwh",       0, 0, (0, 6),  "Ej: 320")
        _entry(g, "kWh Generados GSC *",   "e_kwh_gsc",   0, 1, (6, 6),  "Ej: 240")
        _entry(g, "Tarifa Air-e ($/kWh)",  "e_tarifa_aire", 0, 2, (6, 0), "Ej: 890")

        # ── Fila 2: tarifa GSC / cargos adicionales / descuentos ──────
        g2 = ctk.CTkFrame(fac_inner, fg_color="transparent")
        g2.pack(fill="x")
        g2.columnconfigure((0, 1, 2), weight=1)

        _entry(g2, "Tarifa GSC ($/kWh)",          "e_tarifa_gsc",  0, 0, (0, 6),  "Ej: 650")
        _entry(g2, "Cargos Adicionales Red ($)",   "e_cargos",      0, 1, (6, 6),  "Alumb. público, fijos…")
        _entry(g2, "Descuentos Adicionales Red ($)","e_descuentos", 0, 2, (6, 0),  "Saldos a favor…")

        # ── Preview dinámico ──────────────────────────────────────────
        prev_card = ctk.CTkFrame(fac_inner, fg_color=COLORS["bg_secondary"],
                                  corner_radius=10, border_width=1,
                                  border_color=COLORS["border_primary"])
        prev_card.pack(fill="x", pady=(8, 14))
        prev_inner = ctk.CTkFrame(prev_card, fg_color="transparent")
        prev_inner.pack(fill="x", padx=16, pady=12)

        ctk.CTkLabel(prev_inner, text="Vista Previa de Cálculo",
                     font=FONTS["label"],
                     text_color=COLORS["text_secondary"]).pack(anchor="w", pady=(0, 8))

        def _kpi_row(parent, label, attr, color=COLORS["text_primary"], bold=False):
            f = ctk.CTkFrame(parent, fg_color="transparent")
            f.pack(fill="x", pady=2)
            ctk.CTkLabel(f, text=label,
                         font=FONTS["label"] if bold else FONTS["body_small"],
                         text_color=COLORS["text_secondary"] if not bold else COLORS["text_primary"],
                         width=260, anchor="w").pack(side="left")
            lbl = ctk.CTkLabel(f, text="$0",
                                font=FONTS["title_small"] if bold else FONTS["label"],
                                text_color=color)
            lbl.pack(side="right")
            setattr(self, attr, lbl)

        # Sección 1 — comparativa
        ctk.CTkLabel(prev_inner, text="① Comparativa de Eficiencia",
                     font=FONTS["body_small"],
                     text_color=COLORS["info"]).pack(anchor="w", pady=(0, 2))
        _kpi_row(prev_inner, "Si pagara 100% a Air-e:",      "lbl_bruto_aire",  COLORS["danger"])
        _kpi_row(prev_inner, "Paga a GSC (consumo total):",  "lbl_total_gsc",   COLORS["accent_primary"])
        _kpi_row(prev_inner, "→ Ahorro Directo GSC:",        "lbl_ahorro_directo", COLORS["success"])

        ctk.CTkFrame(prev_inner, height=1,
                      fg_color=COLORS["border_primary"]).pack(fill="x", pady=6)

        # Sección 2 — excedente (condicional)
        self.lbl_sec2_titulo = ctk.CTkLabel(prev_inner,
                                             text="② Cobro Red (Excedente): —",
                                             font=FONTS["body_small"],
                                             text_color=COLORS["warning"])
        self.lbl_sec2_titulo.pack(anchor="w", pady=(0, 2))
        _kpi_row(prev_inner, "Excedente (kWh sin cubrir):",  "lbl_excedente_kwh", COLORS["warning"])
        _kpi_row(prev_inner, "Costo excedente Air-e:",       "lbl_costo_exc",     COLORS["warning"])
        _kpi_row(prev_inner, "+ Cargos adicionales red:",    "lbl_cargos_prev",   COLORS["warning"])
        _kpi_row(prev_inner, "− Descuentos red:",            "lbl_desc_prev",     COLORS["success"])
        _kpi_row(prev_inner, "→ Total a pagar a red:",       "lbl_total_red",     COLORS["warning"])

        ctk.CTkFrame(prev_inner, height=1,
                      fg_color=COLORS["border_primary"]).pack(fill="x", pady=6)

        # Sección 3 — resumen
        ctk.CTkLabel(prev_inner, text="③ Resumen General",
                     font=FONTS["body_small"],
                     text_color=COLORS["accent_primary"]).pack(anchor="w", pady=(0, 2))
        _kpi_row(prev_inner, "Total GSC + Red (pago real):", "lbl_total_real", COLORS["text_primary"], bold=True)
        _kpi_row(prev_inner, "💰 Ahorro Neto Final:",         "lbl_ahorro_neto", COLORS["success"], bold=True)

        # Nota de cobertura total
        self.lbl_cobertura = ctk.CTkLabel(
            prev_inner,
            text="",
            font=FONTS["body_small"],
            text_color=COLORS["success"],
            wraplength=420)
        self.lbl_cobertura.pack(anchor="w", pady=(6, 0))

        ActionButton(fac_inner, text="📄  Generar Factura PDF",
                     command=self._generar_factura_pdf).pack(fill="x")

        sep3 = ctk.CTkFrame(cont, height=1,
                             fg_color=COLORS["border_primary"])
        sep3.pack(fill="x", pady=(4, 20))

        # ── INFORME DE MANTENIMIENTO ──────────────────────────────
        SectionTitle(cont, "▸ Informe de Mantenimiento (PDF)").pack(
            anchor="w", pady=(0, 10))

        mant_card = ctk.CTkFrame(cont, fg_color=COLORS["bg_card"],
                                  corner_radius=12, border_width=1,
                                  border_color=COLORS["border_primary"])
        mant_card.pack(fill="x")

        mi = ctk.CTkFrame(mant_card, fg_color="transparent")
        mi.pack(fill="x", padx=20, pady=16)
        mi.columnconfigure((0, 1), weight=1)

        ctk.CTkLabel(mi, text="Cliente:", font=FONTS["label"],
                     text_color=COLORS["text_secondary"]).grid(
                         row=0, column=0, sticky="w")
        self.cb_cli_mant = ctk.CTkComboBox(
            mi, values=list(self.cli_map.keys()) if self.cli_map else ["Sin clientes"],
            height=34, fg_color=COLORS["bg_input"],
            border_color=COLORS["border_primary"],
            text_color=COLORS["text_primary"], font=FONTS["body_small"],
            command=lambda v: self._cargar_mantenimientos_cliente(v))
        self.cb_cli_mant.grid(row=1, column=0, sticky="ew",
                               padx=(0, 8), pady=(3, 0))

        ctk.CTkLabel(mi, text="Mantenimiento:", font=FONTS["label"],
                     text_color=COLORS["text_secondary"]).grid(
                         row=0, column=1, sticky="w")
        self.cb_mant = ctk.CTkComboBox(
            mi, values=["Seleccione un cliente primero"],
            height=34, fg_color=COLORS["bg_input"],
            border_color=COLORS["border_primary"],
            text_color=COLORS["text_primary"], font=FONTS["body_small"])
        self.cb_mant.grid(row=1, column=1, sticky="ew", pady=(3, 0))
        self.mant_map = {}

        ActionButton(mi, text="📄  Generar Informe de Mantenimiento PDF",
                     command=self._generar_informe_mant
                     ).grid(row=2, column=0, columnspan=2,
                             sticky="ew", pady=(14, 0))

    # ─────────────────────────────────────────────────────────────────────────
    # EXCEL
    # ─────────────────────────────────────────────────────────────────────────

    def _exportar_excel(self, tabla: str, nombre: str):
        try:
            columnas, datos = self.db.exportar_tabla(tabla)
            if not datos:
                messagebox.showinfo("GSC", f"La tabla '{nombre}' no tiene datos.")
                return
            ruta = _excel(columnas, datos, nombre)
            if ruta:
                if messagebox.askyesno("Éxito",
                                        f"Guardado en:\n{ruta}\n\n¿Abrir el archivo?"):
                    _abrir(ruta)
            else:
                messagebox.showerror("Error",
                                     "Instale openpyxl:\n  pip install openpyxl")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    # ─────────────────────────────────────────────────────────────────────────
    # FACTURACIÓN
    # ─────────────────────────────────────────────────────────────────────────

    def _actualizar_precios(self, nombre: str):
        """Auto-carga tarifas del cliente seleccionado."""
        c = self.cli_map.get(nombre)
        if not c:
            return
        self.e_tarifa_aire.delete(0, "end")
        self.e_tarifa_aire.insert(0, str(c.get("tarifa_aire_actual") or ""))
        self.e_tarifa_gsc.delete(0, "end")
        self.e_tarifa_gsc.insert(0, str(c.get("tarifa_gsc") or ""))
        self._calcular_preview()

    def _calcular_preview(self, *_):
        """
        Nueva lógica con excedente:
          excedente    = kwh_consumidos - kwh_gsc
          costo_exc    = (excedente * t_aire + cargos - descuentos)  si exc > 0
          total_real   = total_gsc + costo_exc
          ahorro_neto  = bruto_aire - total_real
        """
        try:
            kwh       = float(self.e_kwh.get() or 0)
            kwh_gsc   = float(self.e_kwh_gsc.get() or 0)
            t_aire    = float(self.e_tarifa_aire.get() or 0)
            t_gsc     = float(self.e_tarifa_gsc.get() or 0)
            cargos    = float(self.e_cargos.get() or 0)
            desc      = float(self.e_descuentos.get() or 0)
        except ValueError:
            return

        # Sección 1 — comparativa
        bruto_aire   = kwh * t_aire          # si pagara todo a Air-e
        total_gsc    = kwh * t_gsc           # cuota GSC por consumo total
        ahorro_directo = max(bruto_aire - total_gsc, 0)

        self.lbl_bruto_aire.configure(text=f"${bruto_aire:,.0f}")
        self.lbl_total_gsc.configure(text=f"${total_gsc:,.0f}")
        self.lbl_ahorro_directo.configure(text=f"${ahorro_directo:,.0f}")

        # Sección 2 — excedente
        excedente = kwh - kwh_gsc            # kWh no cubiertos por paneles

        if excedente > 0:
            costo_exc  = excedente * t_aire
            total_red  = max(costo_exc + cargos - desc, 0)
            self.lbl_sec2_titulo.configure(
                text=f"② Cobro Red (Excedente: {excedente:.1f} kWh):",
                text_color=COLORS["warning"])
            self.lbl_excedente_kwh.configure(text=f"{excedente:.1f} kWh")
            self.lbl_costo_exc.configure(text=f"${costo_exc:,.0f}")
            self.lbl_cargos_prev.configure(text=f"${cargos:,.0f}")
            self.lbl_desc_prev.configure(text=f"${desc:,.0f}")
            self.lbl_total_red.configure(text=f"${total_red:,.0f}")
            self.lbl_cobertura.configure(text="")
        else:
            total_red = 0
            self.lbl_sec2_titulo.configure(
                text="② Cobro Red: ¡Cobertura completa!",
                text_color=COLORS["success"])
            for lbl in [self.lbl_excedente_kwh, self.lbl_costo_exc,
                         self.lbl_cargos_prev, self.lbl_desc_prev,
                         self.lbl_total_red]:
                lbl.configure(text="$0")
            self.lbl_cobertura.configure(
                text="🎉 ¡Felicidades! Su sistema GSC cubrió el 100% "
                     "de su consumo este mes.")

        # Sección 3 — resumen
        total_real  = total_gsc + total_red
        ahorro_neto = max(bruto_aire - total_real, 0)

        self.lbl_total_real.configure(text=f"${total_real:,.0f}")
        self.lbl_ahorro_neto.configure(text=f"${ahorro_neto:,.0f}")

    def _generar_factura_pdf(self):
        nombre_cli = self.cb_cli_fac.get()
        cliente = self.cli_map.get(nombre_cli)
        if not cliente:
            messagebox.showwarning("GSC", "Seleccione un cliente.")
            return
        try:
            kwh     = float(self.e_kwh.get() or 0)
            kwh_gsc = float(self.e_kwh_gsc.get() or 0)
            t_aire  = float(self.e_tarifa_aire.get() or 0)
            t_gsc   = float(self.e_tarifa_gsc.get() or 0)
            cargos  = float(self.e_cargos.get() or 0)
            desc    = float(self.e_descuentos.get() or 0)
        except ValueError:
            messagebox.showerror("GSC", "Ingrese valores numéricos válidos.")
            return

        if kwh <= 0 or t_aire <= 0 or t_gsc <= 0:
            messagebox.showwarning("GSC",
                                   "Complete al menos kWh consumidos y ambas tarifas.")
            return

        ruta = _pdf_factura(cliente, kwh, kwh_gsc, t_aire, t_gsc, cargos, desc)
        if ruta:
            if messagebox.askyesno("PDF Generado",
                                    f"Guardado en:\n{ruta}\n\n¿Abrir?"):
                _abrir(ruta)
        else:
            messagebox.showerror(
                "Error",
                "No se pudo generar el PDF.\n"
                "Instale reportlab:\n  pip install reportlab")

    # ─────────────────────────────────────────────────────────────────────────
    # INFORME MANTENIMIENTO
    # ─────────────────────────────────────────────────────────────────────────

    def _cargar_mantenimientos_cliente(self, nombre: str):
        cliente = self.cli_map.get(nombre)
        if not cliente:
            return
        proyectos = self.db.obtener_proyectos(cliente["id"])
        self.mant_map = {}
        opts = []
        for p in proyectos:
            for m in self.db.obtener_mantenimientos(p["id"]):
                key = f"Visita {m['fecha_visita']} — {m.get('tecnico_encargado','?')}"
                self.mant_map[key] = (m, p, cliente)
                opts.append(key)
        if opts:
            self.cb_mant.configure(values=opts)
            self.cb_mant.set(opts[0])
        else:
            self.cb_mant.configure(values=["Sin mantenimientos"])
            self.cb_mant.set("Sin mantenimientos")

    def _generar_informe_mant(self):
        key = self.cb_mant.get()
        data = self.mant_map.get(key)
        if not data:
            messagebox.showwarning("GSC", "Seleccione un mantenimiento válido.")
            return
        m, p, c = data
        ruta = _pdf_mantenimiento(m, p, c)
        if ruta:
            if messagebox.askyesno("PDF Generado",
                                    f"Guardado en:\n{ruta}\n\n¿Abrir?"):
                _abrir(ruta)
        else:
            messagebox.showerror(
                "Error",
                "No se pudo generar el PDF.\n"
                "Instale reportlab:\n  pip install reportlab")


# ─────────────────────────────────────────────────────────────────────────────
# FUNCIONES DE EXPORTACIÓN (fuera de la clase para reusabilidad)
# ─────────────────────────────────────────────────────────────────────────────

def _docs_dir() -> str:
    d = os.path.join(os.path.expanduser("~"), "Documents", "GSC_Exportes")
    os.makedirs(d, exist_ok=True)
    return d


def _abrir(ruta: str):
    import platform, subprocess
    try:
        if platform.system() == "Windows":
            os.startfile(ruta)
        elif platform.system() == "Darwin":
            subprocess.Popen(["open", ruta])
        else:
            subprocess.Popen(["xdg-open", ruta])
    except Exception:
        pass


def _excel(columnas, datos, nombre) -> str | None:
    try:
        import openpyxl
        from openpyxl.styles import PatternFill, Font, Alignment, Border, Side

        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = nombre[:31]

        hdr_fill = PatternFill(start_color="0D4B35", end_color="0D4B35",
                                fill_type="solid")
        hdr_font = Font(color="00C896", bold=True, size=10)
        alt_fill = PatternFill(start_color="1C2333", end_color="1C2333",
                                fill_type="solid")
        border = Border(
            left=Side(style="thin", color="30363D"),
            right=Side(style="thin", color="30363D"),
            top=Side(style="thin", color="30363D"),
            bottom=Side(style="thin", color="30363D"),
        )
        center = Alignment(horizontal="center", vertical="center")

        # Título
        ws.merge_cells(f"A1:{chr(64+len(columnas))}1")
        c = ws["A1"]
        c.value = f"GESTIÓN SOLAR DEL CARIBE S.A.S. — {nombre}"
        c.font = Font(bold=True, size=13, color="00C896")
        c.alignment = center
        c.fill = PatternFill(start_color="161B22", end_color="161B22",
                              fill_type="solid")
        ws.row_dimensions[1].height = 26

        ws.merge_cells(f"A2:{chr(64+len(columnas))}2")
        d = ws["A2"]
        d.value = f"Exportado: {datetime.now().strftime('%d/%m/%Y %H:%M')}"
        d.font = Font(italic=True, size=9, color="8B949E")
        d.alignment = center

        for ci, col in enumerate(columnas, 1):
            cell = ws.cell(row=4, column=ci,
                            value=col.replace("_", " ").title())
            cell.fill = hdr_fill
            cell.font = hdr_font
            cell.alignment = center
            cell.border = border
        ws.row_dimensions[4].height = 20

        for ri, row_data in enumerate(datos, 5):
            fill = alt_fill if ri % 2 == 0 else None
            for ci, col in enumerate(columnas, 1):
                val = row_data.get(col, "")
                cell = ws.cell(row=ri, column=ci, value=val)
                cell.border = border
                cell.alignment = Alignment(vertical="center", wrap_text=True)
                if fill:
                    cell.fill = fill

        for ci, col in enumerate(columnas, 1):
            letter = chr(64 + ci) if ci <= 26 else f"A{chr(64+ci-26)}"
            max_len = max(
                len(str(col)),
                max((len(str(r.get(col) or "")) for r in datos), default=0)
            )
            ws.column_dimensions[letter].width = min(max_len + 4, 42)

        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = os.path.join(_docs_dir(), f"GSC_{nombre}_{ts}.xlsx")
        wb.save(path)
        return path
    except ImportError:
        return None
    except Exception as e:
        print(f"[Excel] {e}")
        return None


def _pdf_factura(cliente, kwh, kwh_gsc, t_aire, t_gsc, cargos, desc) -> str | None:
    """
    PDF estructurado en 3 secciones:
      1. Comparativa de eficiencia
      2. Cobro de red por excedente (condicional)
      3. Resumen general + ahorro neto
    """
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.lib import colors
        from reportlab.lib.units import cm
        from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer,
                                         Table, TableStyle, HRFlowable)
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT

        # ── Cálculos ─────────────────────────────────────────────
        excedente   = max(kwh - kwh_gsc, 0)
        bruto_aire  = kwh * t_aire
        total_gsc   = kwh * t_gsc
        costo_exc   = excedente * t_aire if excedente > 0 else 0
        total_red   = max(costo_exc + cargos - desc, 0) if excedente > 0 else 0
        total_real  = total_gsc + total_red
        ahorro_neto = max(bruto_aire - total_real, 0)
        cobertura_pct = min(kwh_gsc / kwh * 100, 100) if kwh > 0 else 0

        # ── Archivo ───────────────────────────────────────────────
        ts   = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = os.path.join(
            _docs_dir(),
            f"Factura_{cliente.get('cedula_nit','cli')}_{ts}.pdf")

        doc = SimpleDocTemplate(path, pagesize=letter,
                                leftMargin=2*cm, rightMargin=2*cm,
                                topMargin=1.5*cm, bottomMargin=1.5*cm)
        styles = getSampleStyleSheet()

        # Colores corporativos
        C_VERDE  = colors.HexColor("#00C896")
        C_OSCURO = colors.HexColor("#0D1117")
        C_CARD   = colors.HexColor("#1C2333")
        C_CARD2  = colors.HexColor("#21262D")
        C_GRIS   = colors.HexColor("#8B949E")
        C_WARN   = colors.HexColor("#D29922")
        C_DANGER = colors.HexColor("#F85149")
        C_BLANCO = colors.white
        C_VERDE_OSC = colors.HexColor("#0D4B35")

        def st(name, **kw):
            return ParagraphStyle(name, parent=styles["Normal"], **kw)

        tit_st   = st("tit",  textColor=C_VERDE,  fontSize=18, fontName="Helvetica-Bold",
                       spaceAfter=2, alignment=TA_CENTER)
        sub_st   = st("sub",  textColor=C_GRIS,   fontSize=9,  alignment=TA_CENTER)
        sec_st   = st("sec",  textColor=C_VERDE,  fontSize=11, fontName="Helvetica-Bold",
                       spaceBefore=14, spaceAfter=4)
        body_st  = st("body", textColor=C_BLANCO, fontSize=9,  leading=14)
        note_st  = st("note", textColor=C_VERDE,  fontSize=10, fontName="Helvetica-Bold",
                       backColor=C_VERDE_OSC, leftIndent=10, rightIndent=10,
                       spaceBefore=6, spaceAfter=6)

        def tbl(data, col_widths, row_styles=None):
            t = Table(data, colWidths=col_widths)
            base = [
                ("BACKGROUND",    (0, 0), (-1, 0),  C_VERDE_OSC),
                ("TEXTCOLOR",     (0, 0), (-1, 0),  C_VERDE),
                ("FONTNAME",      (0, 0), (-1, 0),  "Helvetica-Bold"),
                ("FONTSIZE",      (0, 0), (-1, -1),  9),
                ("BACKGROUND",    (0, 1), (-1, -1),  C_CARD),
                ("ROWBACKGROUNDS",(0, 1), (-1, -1),  [C_CARD, C_CARD2]),
                ("TEXTCOLOR",     (0, 1), (-1, -1),  C_BLANCO),
                ("GRID",          (0, 0), (-1, -1), 0.4, colors.HexColor("#30363D")),
                ("ALIGN",         (1, 0), (1, -1),  "RIGHT"),
                ("TOPPADDING",    (0, 0), (-1, -1),  5),
                ("BOTTOMPADDING", (0, 0), (-1, -1),  5),
                ("LEFTPADDING",   (0, 0), (-1, -1),  8),
            ]
            if row_styles:
                base.extend(row_styles)
            t.setStyle(TableStyle(base))
            return t

        story = []

        # ── ENCABEZADO ────────────────────────────────────────────
        story.append(Paragraph("GESTIÓN SOLAR DEL CARIBE S.A.S.", tit_st))
        story.append(Paragraph(
            "Barranquilla, Colombia  |  Factura de Servicio Solar",
            sub_st))
        story.append(HRFlowable(width="100%", color=C_VERDE,
                                 thickness=2, spaceAfter=10))

        # Fecha + número de factura
        story.append(Paragraph(
            f"<b>FACTURA DE AHORRO SOLAR</b>  ·  "
            f"Fecha: {datetime.now().strftime('%d/%m/%Y')}  ·  "
            f"Período de consumo ingresado",
            st("fh", textColor=C_BLANCO, fontSize=10, alignment=TA_CENTER,
                spaceAfter=10)))

        # Datos del cliente
        cli_data = [
            ["DATOS DEL CLIENTE", ""],
            ["Titular:",         cliente.get("nombre_titular", "N/A")],
            ["Cédula / NIT:",    cliente.get("cedula_nit", "N/A")],
            ["Dirección:",       (cliente.get("direccion_completa") or "N/A") +
                                 (f" — {cliente.get('barrio_sector','')}" if
                                  cliente.get("barrio_sector") else "")],
            ["Teléfono:",        cliente.get("telefono", "N/A")],
            ["Email:",           cliente.get("email", "N/A")],
        ]
        story.append(tbl(cli_data, [4.5*cm, 12.5*cm]))
        story.append(Spacer(1, 10))

        # ═══════════════════════════════════════════════════════════
        # SECCIÓN 1 — COMPARATIVA DE EFICIENCIA
        # ═══════════════════════════════════════════════════════════
        story.append(Paragraph("① Comparativa de Eficiencia", sec_st))
        story.append(Paragraph(
            f"Su sistema generó <b>{kwh_gsc:.1f} kWh</b> de los "
            f"<b>{kwh:.1f} kWh</b> consumidos este período "
            f"(<b>{cobertura_pct:.1f}%</b> de cobertura).",
            body_st))
        story.append(Spacer(1, 6))

        sec1_data = [
            ["Concepto", "Valor"],
            [f"Si pagara TODO a Air-e  ({kwh:.1f} kWh × ${t_aire:,.2f})",
             f"${bruto_aire:,.0f}"],
            [f"Paga a GSC  ({kwh:.1f} kWh × ${t_gsc:,.2f})",
             f"${total_gsc:,.0f}"],
            ["→  Ahorro Directo GSC", f"${bruto_aire - total_gsc:,.0f}"],
        ]
        sec1_tbl = tbl(sec1_data, [13*cm, 4*cm], row_styles=[
            ("TEXTCOLOR",  (0, 3), (-1, 3), C_VERDE),
            ("FONTNAME",   (0, 3), (-1, 3), "Helvetica-Bold"),
            ("BACKGROUND", (0, 3), (-1, 3), C_VERDE_OSC),
        ])
        story.append(sec1_tbl)

        # ═══════════════════════════════════════════════════════════
        # SECCIÓN 2 — COBRO DE RED (condicional)
        # ═══════════════════════════════════════════════════════════
        if excedente > 0:
            story.append(Paragraph(
                f"② Aproximado Cobro de Red  (Excedente: {excedente:.1f} kWh)",
                st("sec2", textColor=C_WARN, fontSize=11,
                    fontName="Helvetica-Bold", spaceBefore=14, spaceAfter=4)))
            story.append(Paragraph(
                f"Su sistema no cubrió <b>{excedente:.1f} kWh</b>. "
                "Estos kWh serán cobrados por Air-e a tarifa normal, "
                "más los cargos fijos aplicables.",
                body_st))
            story.append(Spacer(1, 6))

            sec2_data = [
                ["Concepto", "Valor"],
                [f"Excedente no cubierto  ({excedente:.1f} kWh × ${t_aire:,.2f})",
                 f"${costo_exc:,.0f}"],
                ["+ Cargos adicionales red (alumb. público, fijos, etc.)",
                 f"${cargos:,.0f}"],
                ["− Descuentos / saldos a favor red",
                 f"− ${desc:,.0f}"],
                ["→  Total a pagar a la red Air-e",
                 f"${total_red:,.0f}"],
            ]
            sec2_tbl = tbl(sec2_data, [13*cm, 4*cm], row_styles=[
                ("TEXTCOLOR",  (0, 4), (-1, 4), C_WARN),
                ("FONTNAME",   (0, 4), (-1, 4), "Helvetica-Bold"),
            ])
            story.append(sec2_tbl)
        else:
            story.append(Spacer(1, 10))
            story.append(Paragraph(
                "🎉  ¡Felicidades! Su sistema GSC cubrió el 100% de su "
                "consumo este mes. No generó ningún cobro adicional a la red.",
                note_st))

        # ═══════════════════════════════════════════════════════════
        # SECCIÓN 3 — RESUMEN GENERAL
        # ═══════════════════════════════════════════════════════════
        story.append(Paragraph("③ Resumen General", sec_st))

        sec3_data = [
            ["Concepto", "Valor"],
            ["Cuota GSC (por consumo total)", f"${total_gsc:,.0f}"],
            ["Cobro adicional a red Air-e",   f"${total_red:,.0f}"],
            ["TOTAL REAL A PAGAR (GSC + Red)", f"${total_real:,.0f}"],
            ["Si no tuviera paneles (pago Air-e puro)", f"${bruto_aire:,.0f}"],
            ["💰  AHORRO NETO FINAL", f"${ahorro_neto:,.0f}"],
        ]
        sec3_tbl = tbl(sec3_data, [13*cm, 4*cm], row_styles=[
            ("FONTNAME",   (0, 3), (-1, 3), "Helvetica-Bold"),
            ("FONTSIZE",   (0, 3), (-1, 3), 10),
            ("BACKGROUND", (0, 3), (-1, 3), colors.HexColor("#1A3A4A")),
            ("TEXTCOLOR",  (0, 5), (-1, 5), C_VERDE),
            ("FONTNAME",   (0, 5), (-1, 5), "Helvetica-Bold"),
            ("FONTSIZE",   (0, 5), (-1, 5), 12),
            ("BACKGROUND", (0, 5), (-1, 5), C_VERDE_OSC),
            ("TOPPADDING", (0, 5), (-1, 5), 8),
            ("BOTTOMPADDING", (0, 5), (-1, 5), 8),
        ])
        story.append(sec3_tbl)

        # ── PIE DE PÁGINA ─────────────────────────────────────────
        story.append(Spacer(1, 16))
        story.append(HRFlowable(width="100%", color=C_VERDE,
                                 thickness=0.5, spaceAfter=6))

        # Firmas
        firma_data = [["Firma Técnico GSC:", "_______________________",
                        "Recibido / Cliente:", "_______________________"]]
        firma_tbl = Table(firma_data, colWidths=[3.5*cm, 6*cm, 3.5*cm, 4*cm])
        firma_tbl.setStyle(TableStyle([
            ("TEXTCOLOR",     (0, 0), (-1, -1), C_GRIS),
            ("FONTSIZE",      (0, 0), (-1, -1), 8),
            ("TOPPADDING",    (0, 0), (-1, -1), 6),
        ]))
        story.append(firma_tbl)

        story.append(Spacer(1, 8))
        story.append(Paragraph(
            f"Generado: {datetime.now().strftime('%d/%m/%Y %H:%M')}  |  "
            "GSC v2.1  |  Gestión Solar del Caribe S.A.S.",
            st("footer", textColor=C_GRIS, fontSize=7, alignment=TA_CENTER)))

        doc.build(story)
        return path

    except ImportError:
        return None
    except Exception as e:
        print(f"[PDF Factura] {e}")
        return None


def _pdf_mantenimiento(m: dict, p: dict, c: dict) -> str | None:
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.lib import colors
        from reportlab.lib.units import cm
        from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer,
                                         Table, TableStyle, HRFlowable, Image)
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.enums import TA_CENTER

        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = os.path.join(
            _docs_dir(),
            f"Mantenimiento_{c.get('cedula_nit','cli')}_{ts}.pdf")

        doc = SimpleDocTemplate(path, pagesize=letter,
                                leftMargin=2*cm, rightMargin=2*cm,
                                topMargin=1.5*cm, bottomMargin=1.5*cm)
        styles = getSampleStyleSheet()
        verde = colors.HexColor("#00C896")
        gris  = colors.HexColor("#8B949E")
        blanc = colors.white

        story = []

        # Encabezado
        story.append(Paragraph(
            "GESTIÓN SOLAR DEL CARIBE S.A.S.",
            ParagraphStyle("h", parent=styles["Title"],
                            textColor=verde, fontSize=16)))
        story.append(Paragraph(
            "INFORME DE MANTENIMIENTO TÉCNICO",
            ParagraphStyle("s", parent=styles["Normal"],
                            textColor=blanc, fontSize=11,
                            spaceAfter=4, alignment=TA_CENTER)))
        story.append(HRFlowable(width="100%", color=verde,
                                 thickness=1.5, spaceAfter=12))

        def tabla_info(data):
            t = Table(data, colWidths=[5*cm, 12*cm])
            t.setStyle(TableStyle([
                ("TEXTCOLOR", (0, 0), (0, -1), gris),
                ("TEXTCOLOR", (1, 0), (1, -1), blanc),
                ("FONTSIZE",  (0, 0), (-1, -1), 9),
                ("GRID",      (0, 0), (-1, -1), 0.3,
                 colors.HexColor("#30363D")),
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#1C2333")),
                ("ROWBACKGROUNDS", (0, 0), (-1, -1),
                 [colors.HexColor("#1C2333"), colors.HexColor("#21262D")]),
                ("TOPPADDING",    (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ("LEFTPADDING",   (0, 0), (-1, -1), 8),
            ]))
            return t

        labels_e = {1: "Crítico", 2: "Deficiente", 3: "Regular",
                    4: "Bueno", 5: "Excelente"}

        story.append(Paragraph(
            "Cliente", ParagraphStyle("sec", parent=styles["Normal"],
                                       textColor=verde, fontSize=10,
                                       fontName="Helvetica-Bold",
                                       spaceBefore=10, spaceAfter=4)))
        story.append(tabla_info([
            ["Nombre:", c.get("nombre_titular", "N/A")],
            ["Cédula/NIT:", c.get("cedula_nit", "N/A")],
            ["Dirección:", (c.get("direccion_completa") or "N/A") +
             f" — Estrato {c.get('estrato','?')}"],
            ["Teléfono:", c.get("telefono", "N/A")],
        ]))

        story.append(Paragraph(
            "Sistema Solar", ParagraphStyle("sec2", parent=styles["Normal"],
                                             textColor=verde, fontSize=10,
                                             fontName="Helvetica-Bold",
                                             spaceBefore=10, spaceAfter=4)))
        story.append(tabla_info([
            ["Capacidad:", f"{p.get('kwp_instalados','?')} kWp"],
            ["Inversor:", f"{p.get('marca_inversor','?')} — S/N: {p.get('serial_inversor','?')}"],
            ["Paneles:", p.get("marca_paneles", "N/A")],
            ["Seriales:", p.get("seriales_paneles", "N/A")],
            ["Fecha Inst.:", p.get("fecha_instalacion", "N/A")],
            ["RETIE:", p.get("estatus_retie", "N/A")],
        ]))

        story.append(Paragraph(
            "Registro de Visita", ParagraphStyle("sec3", parent=styles["Normal"],
                                                  textColor=verde, fontSize=10,
                                                  fontName="Helvetica-Bold",
                                                  spaceBefore=10, spaceAfter=4)))
        story.append(tabla_info([
            ["Fecha Visita:", m.get("fecha_visita", "N/A")],
            ["Técnico:", m.get("tecnico_encargado", "N/A")],
            ["Estructura:", f"{m.get('estado_estructura','?')}/5 — "
             f"{labels_e.get(m.get('estado_estructura',0),'N/A')}"],
            ["Cableado:", f"{m.get('estado_cableado','?')}/5 — "
             f"{labels_e.get(m.get('estado_cableado',0),'N/A')}"],
            ["Limpieza:", "Realizada" if m.get("limpieza_paneles") else "No realizada"],
            ["Tierra:", f"{m.get('continuidad_tierra_ohm',0)} Ω"],
            ["Fotos:", m.get("ruta_fotos") or "No adjuntado"],
            ["Acta PDF:", m.get("ruta_acta_pdf") or "No adjuntado"],
        ]))

        # Observaciones
        story.append(Spacer(1, 10))
        story.append(Paragraph(
            "Observaciones Críticas", ParagraphStyle(
                "sec4", parent=styles["Normal"], textColor=verde,
                fontSize=10, fontName="Helvetica-Bold", spaceAfter=4)))
        obs = m.get("observaciones_criticas") or "Sin observaciones críticas."
        story.append(Paragraph(obs, ParagraphStyle(
            "obs", parent=styles["Normal"], textColor=blanc, fontSize=9,
            backColor=colors.HexColor("#1C2333"),
            leftIndent=8, rightIndent=8,
            spaceBefore=4, spaceAfter=4)))

        # Miniaturas de imágenes (si la carpeta existe)
        ruta_fotos = m.get("ruta_fotos")
        if ruta_fotos and os.path.isdir(ruta_fotos):
            imgs = [f for f in os.listdir(ruta_fotos)
                    if f.lower().endswith((".jpg", ".jpeg", ".png"))][:4]
            if imgs:
                story.append(Spacer(1, 10))
                story.append(Paragraph(
                    "Evidencia Fotográfica (miniaturas)",
                    ParagraphStyle("sec5", parent=styles["Normal"],
                                    textColor=verde, fontSize=10,
                                    fontName="Helvetica-Bold", spaceAfter=4)))
                img_cells = []
                for img_name in imgs:
                    img_path = os.path.join(ruta_fotos, img_name)
                    try:
                        img_cells.append(Image(img_path, width=4*cm, height=3*cm))
                    except Exception:
                        img_cells.append(Paragraph(img_name, styles["Normal"]))
                while len(img_cells) % 4 != 0:
                    img_cells.append("")
                rows = [img_cells[i:i+4] for i in range(0, len(img_cells), 4)]
                img_tbl = Table(rows, colWidths=[4.3*cm]*4)
                img_tbl.setStyle(TableStyle([
                    ("ALIGN",   (0, 0), (-1, -1), "CENTER"),
                    ("VALIGN",  (0, 0), (-1, -1), "MIDDLE"),
                    ("GRID",    (0, 0), (-1, -1), 0.3,
                     colors.HexColor("#30363D")),
                    ("BACKGROUND", (0, 0), (-1, -1),
                     colors.HexColor("#1C2333")),
                ]))
                story.append(img_tbl)

        story.append(Spacer(1, 20))
        story.append(HRFlowable(width="100%", color=verde,
                                 thickness=0.5, spaceAfter=8))

        # Firmas
        firmas = [["Firma Técnico:", "_______________________",
                   "Firma Cliente:", "_______________________"]]
        ft = Table(firmas, colWidths=[3.5*cm, 6*cm, 3.5*cm, 4*cm])
        ft.setStyle(TableStyle([
            ("TEXTCOLOR", (0, 0), (-1, -1), gris),
            ("FONTSIZE",  (0, 0), (-1, -1), 9),
            ("TOPPADDING",    (0, 0), (-1, -1), 6),
        ]))
        story.append(ft)

        story.append(Spacer(1, 8))
        story.append(Paragraph(
            f"Generado: {datetime.now().strftime('%d/%m/%Y %H:%M')}  |  GSC v2.0",
            ParagraphStyle("footer", parent=styles["Normal"],
                            textColor=gris, fontSize=7,
                            alignment=TA_CENTER)))

        doc.build(story)
        return path
    except ImportError:
        return None
    except Exception as e:
        print(f"[PDF Mant] {e}")
        return None