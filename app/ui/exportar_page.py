"""
exportar_page.py — Exportación Excel + Facturación PDF v3.0
Refactor completo: estética bancaria moderna, 3 secciones claras, colores corporativos.
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

        ctk.CTkLabel(cont, text="Exportar y Facturación",
                     font=FONTS["title_large"],
                     text_color=COLORS["text_primary"]).pack(anchor="w", pady=(0, 4))
        ctk.CTkLabel(cont,
                     text="Exporte tablas a Excel, genere PDFs de facturación y reportes.",
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
        SectionTitle(cont, "▸ Factura de Ahorro Solar (PDF v3.0)").pack(
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

        # ── Datos de cálculo ───────────────────────────────────────
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

        g2 = ctk.CTkFrame(fac_inner, fg_color="transparent")
        g2.pack(fill="x")
        g2.columnconfigure((0, 1, 2), weight=1)

        _entry(g2, "Tarifa GSC ($/kWh)",          "e_tarifa_gsc",  0, 0, (0, 6),  "Ej: 650")
        _entry(g2, "Cargos Adicionales ($)",      "e_cargos",      0, 1, (6, 6),  "Alumb, fijos")
        _entry(g2, "Descuentos ($)",              "e_descuentos",  0, 2, (6, 0),  "Saldos a favor")

        # ── Preview ───────────────────────────────────────────────
        prev_card = ctk.CTkFrame(fac_inner, fg_color=COLORS["bg_secondary"],
                                  corner_radius=10, border_width=1,
                                  border_color=COLORS["border_primary"])
        prev_card.pack(fill="x", pady=(8, 14))
        prev_inner = ctk.CTkFrame(prev_card, fg_color="transparent")
        prev_inner.pack(fill="x", padx=16, pady=12)

        ctk.CTkLabel(prev_inner, text="Vista Previa",
                     font=FONTS["label"],
                     text_color=COLORS["text_secondary"]).pack(anchor="w", pady=(0, 8))

        def _kpi_row(parent, label, attr, color=COLORS["text_primary"]):
            f = ctk.CTkFrame(parent, fg_color="transparent")
            f.pack(fill="x", pady=2)
            ctk.CTkLabel(f, text=label,
                         font=FONTS["body_small"],
                         text_color=COLORS["text_secondary"],
                         width=260, anchor="w").pack(side="left")
            lbl = ctk.CTkLabel(f, text="$0",
                                font=FONTS["label"],
                                text_color=color)
            lbl.pack(side="right")
            setattr(self, attr, lbl)

        _kpi_row(prev_inner, "Si pagara 100% a Air-e:",      "lbl_bruto_aire",  COLORS["danger"])
        _kpi_row(prev_inner, "Paga a GSC:",                  "lbl_total_gsc",   COLORS["accent_primary"])
        _kpi_row(prev_inner, "Excedente (kWh):",             "lbl_excedente",   COLORS["warning"])
        _kpi_row(prev_inner, "💰  Total a Pagar:",           "lbl_total_real",  COLORS["text_primary"])
        _kpi_row(prev_inner, "✅  Ahorro Neto:",             "lbl_ahorro_neto", COLORS["success"])

        ActionButton(fac_inner, text="📄  Generar Factura PDF v3.0",
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

        ActionButton(mi, text="📄  Generar Informe PDF",
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
                                        f"Guardado en:\n{ruta}\n\n¿Abrir?"):
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
        c = self.cli_map.get(nombre)
        if not c:
            return
        self.e_tarifa_aire.delete(0, "end")
        self.e_tarifa_aire.insert(0, str(c.get("tarifa_aire_actual") or ""))
        self.e_tarifa_gsc.delete(0, "end")
        self.e_tarifa_gsc.insert(0, str(c.get("tarifa_gsc") or ""))
        self._calcular_preview()

    def _calcular_preview(self, *_):
        try:
            kwh     = float(self.e_kwh.get() or 0)
            kwh_gsc = float(self.e_kwh_gsc.get() or 0)
            t_aire  = float(self.e_tarifa_aire.get() or 0)
            t_gsc   = float(self.e_tarifa_gsc.get() or 0)
            cargos  = float(self.e_cargos.get() or 0)
            desc    = float(self.e_descuentos.get() or 0)
        except ValueError:
            return

        def cop(v):
            return f"$ {v:,.0f}".replace(",", ".")

        excedente   = max(kwh - kwh_gsc, 0)
        bruto_aire  = kwh * t_aire
        total_gsc   = kwh_gsc * t_gsc
        total_red   = max((excedente * t_aire if excedente > 0 else 0) + cargos - desc, 0)
        total_real  = total_gsc + total_red
        ahorro_neto = max(bruto_aire - total_real, 0)

        self.lbl_bruto_aire.configure(text=cop(bruto_aire))
        self.lbl_total_gsc.configure(text=cop(total_gsc))
        self.lbl_excedente.configure(text=f"{excedente:.1f} kWh")
        self.lbl_total_real.configure(text=cop(total_real))
        self.lbl_ahorro_neto.configure(text=cop(ahorro_neto))

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
                                   "Complete al menos kWh y ambas tarifas.")
            return

        ruta = _pdf_factura(cliente, kwh, kwh_gsc, t_aire, t_gsc, cargos, desc)
        if ruta:
            if messagebox.askyesno("PDF Generado",
                                    f"Guardado en:\n{ruta}\n\n¿Abrir?"):
                _abrir(ruta)
        else:
            messagebox.showerror(
                "Error",
                "No se pudo generar el PDF.\nInstale reportlab:\n  pip install reportlab")

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
                "No se pudo generar el PDF.\nInstale reportlab:\n  pip install reportlab")


# ─────────────────────────────────────────────────────────────────────────────
# FUNCIONES DE GENERACIÓN (fuera de clase)
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

        ws.merge_cells(f"A1:{chr(64+len(columnas))}1")
        c = ws["A1"]
        c.value = f"GESTIÓN SOLAR DEL CARIBE S.A.S. — {nombre}"
        c.font = Font(bold=True, size=13, color="00C896")
        c.alignment = center
        c.fill = PatternFill(start_color="161B22", end_color="161B22",
                              fill_type="solid")
        ws.row_dimensions[1].height = 26

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
    PDF v3.0 — Estética bancaria moderna, 3 secciones:
    ① Comparativa de Eficiencia
    ② Nota Informativa de Red (si hay excedente)
    ③ Resumen General
    """
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.lib import colors
        from reportlab.lib.units import cm
        from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer,
                                         Table, TableStyle, HRFlowable)
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT

        # ── CÁLCULOS ───────────────────────────────────────────────
        LIMITE_SUBSIDIO = 173
        excedente    = max(kwh - kwh_gsc, 0)
        bruto_aire   = kwh * t_aire
        total_gsc    = kwh_gsc * t_gsc
        costo_exc    = excedente * t_aire if excedente > 0 else 0
        total_red    = max(costo_exc + cargos - desc, 0) if excedente > 0 else 0
        total_real   = total_gsc + total_red
        ahorro_neto  = max(bruto_aire - total_real, 0)
        subsidio_ok  = excedente <= LIMITE_SUBSIDIO

        def cop(v):
            return f"$ {v:,.0f}".replace(",", ".")

        # ── ARCHIVO ───────────────────────────────────────────────
        ts   = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = os.path.join(
            _docs_dir(),
            f"Factura_GSC_{cliente.get('cedula_nit','cli')}_{ts}.pdf")

        doc = SimpleDocTemplate(path, pagesize=letter,
                                leftMargin=1.5*cm, rightMargin=1.5*cm,
                                topMargin=1.2*cm, bottomMargin=1.2*cm)

        # ── COLORES CORPORATIVOS ───────────────────────────────────
        C_VERDE      = colors.HexColor("#00C896")
        C_VERDE_OSC  = colors.HexColor("#0D4B35")
        C_GRIS       = colors.HexColor("#8B949E")
        C_BLANCO     = colors.white
        C_WARN       = colors.HexColor("#D29922")

        styles = getSampleStyleSheet()

        def st(name, **kw):
            return ParagraphStyle(name, parent=styles["Normal"], **kw)

        # ── ESTILOS ───────────────────────────────────────────────
        tit_st  = st("T", textColor=C_VERDE, fontSize=18,
                      fontName="Helvetica-Bold", alignment=TA_CENTER, spaceAfter=3)
        sub_st  = st("S", textColor=C_GRIS,  fontSize=9,  alignment=TA_CENTER)
        sec_st  = st("SE", textColor=C_VERDE, fontSize=11,
                      fontName="Helvetica-Bold", spaceBefore=10, spaceAfter=4)
        body_st = st("B",  textColor=C_BLANCO, fontSize=9, leading=12)
        note_st = st("N",  textColor=C_VERDE, fontSize=9,
                      fontName="Helvetica-Bold",
                      backColor=C_VERDE_OSC, leftIndent=8, rightIndent=8,
                      spaceBefore=6, spaceAfter=6)

        def mk_tbl(data, widths, extra_styles=None):
            t = Table(data, colWidths=widths)
            base = [
                ("BACKGROUND",    (0,0),(-1,0),  C_VERDE_OSC),
                ("TEXTCOLOR",     (0,0),(-1,0),  C_VERDE),
                ("FONTNAME",      (0,0),(-1,0),  "Helvetica-Bold"),
                ("FONTSIZE",      (0,0),(-1,-1),  8),
                ("ROWBACKGROUNDS",(0,1),(-1,-1),  [colors.HexColor("#1C2333"), colors.HexColor("#21262D")]),
                ("TEXTCOLOR",     (0,1),(-1,-1),  C_BLANCO),
                ("GRID",          (0,0),(-1,-1), 0.3, colors.HexColor("#30363D")),
                ("ALIGN",         (1,0),(1,-1),  "RIGHT"),
                ("TOPPADDING",    (0,0),(-1,-1),  3),
                ("BOTTOMPADDING", (0,0),(-1,-1),  3),
                ("LEFTPADDING",   (0,0),(-1,-1),  6),
            ]
            if extra_styles:
                base.extend(extra_styles)
            t.setStyle(TableStyle(base))
            return t

        story = []

        # ══════════════════════════════════════════════════════════
        # ENCABEZADO
        # ══════════════════════════════════════════════════════════
        story.append(Paragraph("GESTIÓN SOLAR DEL CARIBE S.A.S.", tit_st))
        story.append(Paragraph(
            "Factura de Ahorro Solar  ·  Barranquilla, Colombia",
            sub_st))
        story.append(HRFlowable(width="100%", color=C_VERDE,
                                 thickness=2, spaceAfter=6))

        # Datos cliente
        cli_rows = [
            ["CLIENTE", ""],
            ["Titular:",    cliente.get("nombre_titular", "N/A")],
            ["Cédula/NIT:",  cliente.get("cedula_nit", "N/A")],
        ]
        story.append(mk_tbl(cli_rows, [3*cm, 13*cm]))
        story.append(Spacer(1, 6))

        # ══════════════════════════════════════════════════════════
        # ① COMPARATIVA DE EFICIENCIA
        # ══════════════════════════════════════════════════════════
        story.append(Paragraph("① Comparativa de Eficiencia Solar", sec_st))
        story.append(Paragraph(
            f"Sistema GSC cubrió <b>{kwh_gsc:.0f} kWh</b> de los "
            f"<b>{kwh:.0f} kWh</b> consumidos.",
            body_st))
        story.append(Spacer(1, 4))

        sec1 = [
            ["Escenario", "Valor"],
            [f"100% Air-e  ({kwh:.0f} kWh × {cop(t_aire)}/kWh)",
             cop(bruto_aire)],
            [f"Con GSC  ({kwh_gsc:.0f} kWh × {cop(t_gsc)}/kWh)",
             cop(total_gsc)],
        ]
        if excedente > 0:
            sec1.append([f"Excedente Red  ({excedente:.0f} kWh + cargos)",
                        cop(total_red)])
        sec1.append(["Total a Pagar (GSC + Red)", cop(total_real)])

        story.append(mk_tbl(sec1, [10*cm, 6*cm], extra_styles=[
            ("BACKGROUND", (0,len(sec1)-1),(-1,len(sec1)-1), C_VERDE_OSC),
            ("TEXTCOLOR",  (0,len(sec1)-1),(-1,len(sec1)-1), C_VERDE),
            ("FONTNAME",   (0,len(sec1)-1),(-1,len(sec1)-1), "Helvetica-Bold"),
        ]))
        story.append(Spacer(1, 6))

        # ══════════════════════════════════════════════════════════
        # ② NOTA INFORMATIVA DE RED (condicional)
        # ══════════════════════════════════════════════════════════
        if excedente > 0:
            titulo = f"② Nota Informativa de Red  ·  Excedente: {excedente:.0f} kWh"
            story.append(Paragraph(
                titulo,
                st("S2", textColor=C_WARN, fontSize=10,
                    fontName="Helvetica-Bold", spaceBefore=8, spaceAfter=4)))

            story.append(Paragraph(
                f"Los <b>{excedente:.0f} kWh</b> no cubiertos por GSC "
                f"se cobran a Air-e a ${t_aire:,.0f}/kWh.",
                body_st))

            if subsidio_ok:
                story.append(Paragraph(
                    f"🎯  ¡BENEFICIO SUBSIDIO DETECTADO! "
                    f"Excedente ≤ {LIMITE_SUBSIDIO} kWh = tarifa subsidiada.",
                    note_st))
            else:
                story.append(Paragraph(
                    f"⚠️  Su excedente supera el límite de subsidio ({LIMITE_SUBSIDIO} kWh).",
                    note_st))
            story.append(Spacer(1, 6))

        # ══════════════════════════════════════════════════════════
        # ③ RESUMEN FINAL
        # ══════════════════════════════════════════════════════════
        story.append(Paragraph("③ Resumen General", sec_st))

        # Total destacado
        total_data = [["TOTAL A PAGAR ESTE MES", cop(total_real)]]
        total_tbl = Table(total_data, colWidths=[10*cm, 6*cm])
        total_tbl.setStyle(TableStyle([
            ("BACKGROUND",    (0,0),(-1,0), colors.HexColor("#1A3A4A")),
            ("TEXTCOLOR",     (0,0),(-1,0), C_BLANCO),
            ("FONTNAME",      (0,0),(-1,0), "Helvetica-Bold"),
            ("FONTSIZE",      (0,0),(-1,0), 12),
            ("ALIGN",         (1,0),(1,0),  "RIGHT"),
            ("TOPPADDING",    (0,0),(-1,0),  6),
            ("BOTTOMPADDING", (0,0),(-1,0),  6),
            ("LEFTPADDING",   (0,0),(-1,0),  8),
            ("GRID",          (0,0),(-1,0), 0.2, C_GRIS),
        ]))
        story.append(total_tbl)
        story.append(Spacer(1, 4))

        # Ahorro neto
        ahorro_data = [["💰  AHORRO NETO", cop(ahorro_neto)]]
        ahorro_tbl = Table(ahorro_data, colWidths=[10*cm, 6*cm])
        ahorro_tbl.setStyle(TableStyle([
            ("BACKGROUND",    (0,0),(-1,0), C_VERDE_OSC),
            ("TEXTCOLOR",     (0,0),(-1,0), C_VERDE),
            ("FONTNAME",      (0,0),(-1,0), "Helvetica-Bold"),
            ("FONTSIZE",      (0,0),(-1,0), 11),
            ("ALIGN",         (1,0),(1,0),  "RIGHT"),
            ("TOPPADDING",    (0,0),(-1,0),  5),
            ("BOTTOMPADDING", (0,0),(-1,0),  5),
            ("LEFTPADDING",   (0,0),(-1,0),  8),
        ]))
        story.append(ahorro_tbl)

        # ── FOOTER ────────────────────────────────────────────────
        story.append(Spacer(1, 8))
        story.append(HRFlowable(width="100%", color=C_VERDE,
                                 thickness=0.5, spaceAfter=6))
        story.append(Paragraph(
            f"📱 Contacto: +57 XXX XXX XXXX  |  📧 contacto@gsc.com.co  |  "
            f"Generado: {datetime.now().strftime('%d/%m/%Y')}",
            st("FT", textColor=C_GRIS, fontSize=7, alignment=TA_CENTER)))

        doc.build(story)
        return path

    except ImportError:
        return None
    except Exception as e:
        print(f"[PDF Factura] {e}")
        return None


def _pdf_mantenimiento(m: dict, p: dict, c: dict) -> str | None:
    """PDF de mantenimiento."""
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.lib import colors
        from reportlab.lib.units import cm
        from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer,
                                         Table, TableStyle, HRFlowable)
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.enums import TA_CENTER

        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = os.path.join(
            _docs_dir(),
            f"Mant_{c.get('cedula_nit','cli')}_{ts}.pdf")

        doc = SimpleDocTemplate(path, pagesize=letter,
                                leftMargin=1.5*cm, rightMargin=1.5*cm,
                                topMargin=1.2*cm, bottomMargin=1.2*cm)
        styles = getSampleStyleSheet()
        verde = colors.HexColor("#00C896")
        gris  = colors.HexColor("#8B949E")

        story = []

        story.append(Paragraph(
            "GESTIÓN SOLAR DEL CARIBE S.A.S.",
            ParagraphStyle("h", parent=styles["Title"],
                            textColor=verde, fontSize=14)))
        story.append(Paragraph(
            "INFORME DE MANTENIMIENTO TÉCNICO",
            ParagraphStyle("s", parent=styles["Normal"],
                            textColor=gris, fontSize=10,
                            spaceAfter=4, alignment=TA_CENTER)))
        story.append(HRFlowable(width="100%", color=verde,
                                 thickness=1, spaceAfter=8))

        info_data = [
            ["CLIENTE", c.get("nombre_titular", "N/A")],
            ["Cédula", c.get("cedula_nit", "N/A")],
            ["SISTEMA", f"{p.get('kwp_instalados','?')} kWp  ·  {p.get('marca_paneles','N/A')}"],
            ["VISITA", m.get("fecha_visita", "N/A")],
            ["TÉCNICO", m.get("tecnico_encargado", "N/A")],
        ]
        info_tbl = Table(info_data, colWidths=[3*cm, 13*cm])
        info_tbl.setStyle(TableStyle([
            ("BACKGROUND",    (0,0),(-1,-1), colors.HexColor("#1C2333")),
            ("TEXTCOLOR",     (0,0),(-1,-1), colors.white),
            ("FONTSIZE",      (0,0),(-1,-1), 8),
            ("GRID",          (0,0),(-1,-1), 0.2, gris),
            ("TOPPADDING",    (0,0),(-1,-1),  3),
            ("BOTTOMPADDING", (0,0),(-1,-1),  3),
        ]))
        story.append(info_tbl)

        story.append(Spacer(1, 10))
        story.append(Paragraph(
            f"Generado: {datetime.now().strftime('%d/%m/%Y')}  |  GSC v3.0",
            ParagraphStyle("footer", parent=styles["Normal"],
                            textColor=gris, fontSize=7, alignment=TA_CENTER)))

        doc.build(story)
        return path
    except ImportError:
        return None
    except Exception as e:
        print(f"[PDF Mant] {e}")
        return None