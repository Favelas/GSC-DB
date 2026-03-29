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

        g = ctk.CTkFrame(fac_inner, fg_color="transparent")
        g.pack(fill="x")
        g.columnconfigure((0, 1, 2), weight=1)

        # Campos de facturación
        ctk.CTkLabel(g, text="kWh Consumidos *", font=FONTS["label"],
                     text_color=COLORS["text_secondary"]).grid(
                         row=0, column=0, sticky="w", padx=(0, 6))
        self.e_kwh = ctk.CTkEntry(g, height=34, fg_color=COLORS["bg_input"],
                                   border_color=COLORS["border_primary"],
                                   text_color=COLORS["text_primary"],
                                   font=FONTS["body_medium"])
        self.e_kwh.grid(row=1, column=0, sticky="ew", padx=(0, 6), pady=(3, 10))
        self.e_kwh.bind("<KeyRelease>", lambda e: self._calcular_preview())

        ctk.CTkLabel(g, text="Tarifa Air-e ($/kWh)", font=FONTS["label"],
                     text_color=COLORS["text_secondary"]).grid(
                         row=0, column=1, sticky="w", padx=6)
        self.e_tarifa_aire = ctk.CTkEntry(
            g, height=34, fg_color=COLORS["bg_input"],
            border_color=COLORS["border_primary"],
            text_color=COLORS["text_primary"], font=FONTS["body_medium"])
        self.e_tarifa_aire.grid(row=1, column=1, sticky="ew",
                                padx=6, pady=(3, 10))
        self.e_tarifa_aire.bind("<KeyRelease>", lambda e: self._calcular_preview())

        ctk.CTkLabel(g, text="Tarifa GSC ($/kWh)", font=FONTS["label"],
                     text_color=COLORS["text_secondary"]).grid(
                         row=0, column=2, sticky="w", padx=(6, 0))
        self.e_tarifa_gsc = ctk.CTkEntry(
            g, height=34, fg_color=COLORS["bg_input"],
            border_color=COLORS["border_primary"],
            text_color=COLORS["text_primary"], font=FONTS["body_medium"])
        self.e_tarifa_gsc.grid(row=1, column=2, sticky="ew",
                               padx=(6, 0), pady=(3, 10))
        self.e_tarifa_gsc.bind("<KeyRelease>", lambda e: self._calcular_preview())

        # Campo deducciones
        ctk.CTkLabel(fac_inner, text="Deducciones Air-e ($):",
                     font=FONTS["label"],
                     text_color=COLORS["text_secondary"]).pack(anchor="w")
        self.e_deducciones = ctk.CTkEntry(
            fac_inner, placeholder_text="Descuentos, subsidios, rebajas a restar del total Air-e",
            height=34, fg_color=COLORS["bg_input"],
            border_color=COLORS["border_primary"],
            text_color=COLORS["text_primary"], font=FONTS["body_small"])
        self.e_deducciones.pack(fill="x", pady=(3, 12))
        self.e_deducciones.bind("<KeyRelease>", lambda e: self._calcular_preview())

        # Preview de cálculo
        prev_card = ctk.CTkFrame(fac_inner, fg_color=COLORS["bg_secondary"],
                                  corner_radius=10)
        prev_card.pack(fill="x", pady=(0, 14))
        prev_inner = ctk.CTkFrame(prev_card, fg_color="transparent")
        prev_inner.pack(fill="x", padx=16, pady=12)

        ctk.CTkLabel(prev_inner, text="Vista Previa de Cálculo:",
                     font=FONTS["label"],
                     text_color=COLORS["text_secondary"]).pack(anchor="w", pady=(0, 6))

        def row_calc(parent, label, var_attr, color=COLORS["text_primary"]):
            f = ctk.CTkFrame(parent, fg_color="transparent")
            f.pack(fill="x", pady=2)
            ctk.CTkLabel(f, text=label, font=FONTS["body_small"],
                         text_color=COLORS["text_secondary"],
                         width=200, anchor="w").pack(side="left")
            lbl = ctk.CTkLabel(f, text="$0", font=FONTS["label"],
                                text_color=color)
            lbl.pack(side="right")
            setattr(self, var_attr, lbl)

        row_calc(prev_inner, "Total Air-e (con deducciones):",
                 "lbl_total_aire", COLORS["warning"])
        row_calc(prev_inner, "Total GSC:", "lbl_total_gsc",
                 COLORS["accent_primary"])

        sep2 = ctk.CTkFrame(prev_inner, height=1,
                             fg_color=COLORS["border_primary"])
        sep2.pack(fill="x", pady=6)

        row_calc(prev_inner, "💰  Monto Ahorrado:", "lbl_ahorro",
                 COLORS["success"])

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
        """Auto-carga las tarifas del cliente seleccionado."""
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
            kwh  = float(self.e_kwh.get() or 0)
            t_aire = float(self.e_tarifa_aire.get() or 0)
            t_gsc  = float(self.e_tarifa_gsc.get() or 0)
            ded    = float(self.e_deducciones.get() or 0)
        except ValueError:
            return

        total_aire = max(kwh * t_aire - ded, 0)
        total_gsc  = kwh * t_gsc
        ahorro     = max(total_aire - total_gsc, 0)

        self.lbl_total_aire.configure(text=f"${total_aire:,.0f}")
        self.lbl_total_gsc.configure(text=f"${total_gsc:,.0f}")
        self.lbl_ahorro.configure(text=f"${ahorro:,.0f}")

    def _generar_factura_pdf(self):
        nombre_cli = self.cb_cli_fac.get()
        cliente = self.cli_map.get(nombre_cli)
        if not cliente:
            messagebox.showwarning("GSC", "Seleccione un cliente.")
            return
        try:
            kwh    = float(self.e_kwh.get() or 0)
            t_aire = float(self.e_tarifa_aire.get() or 0)
            t_gsc  = float(self.e_tarifa_gsc.get() or 0)
            ded    = float(self.e_deducciones.get() or 0)
        except ValueError:
            messagebox.showerror("GSC", "Ingrese valores numéricos válidos.")
            return

        total_aire = max(kwh * t_aire - ded, 0)
        total_gsc  = kwh * t_gsc
        ahorro     = max(total_aire - total_gsc, 0)

        ruta = _pdf_factura(cliente, kwh, t_aire, t_gsc, ded,
                             total_aire, total_gsc, ahorro)
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


def _pdf_factura(cliente, kwh, t_aire, t_gsc, ded,
                  total_aire, total_gsc, ahorro) -> str | None:
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.lib import colors
        from reportlab.lib.units import cm
        from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer,
                                         Table, TableStyle, HRFlowable)
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.enums import TA_CENTER, TA_RIGHT

        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = os.path.join(
            _docs_dir(),
            f"Factura_{cliente.get('cedula_nit','cli')}_{ts}.pdf")

        doc = SimpleDocTemplate(path, pagesize=letter,
                                leftMargin=2*cm, rightMargin=2*cm,
                                topMargin=1.5*cm, bottomMargin=1.5*cm)
        styles = getSampleStyleSheet()
        verde  = colors.HexColor("#00C896")
        oscuro = colors.HexColor("#0D1117")
        gris   = colors.HexColor("#8B949E")

        titulo_st = ParagraphStyle("tit", parent=styles["Title"],
                                    textColor=verde, fontSize=18,
                                    spaceAfter=2)
        sub_st    = ParagraphStyle("sub", parent=styles["Normal"],
                                    textColor=gris, fontSize=9,
                                    alignment=TA_CENTER)
        label_st  = ParagraphStyle("lbl", parent=styles["Normal"],
                                    textColor=colors.HexColor("#E6EDF3"),
                                    fontSize=10)
        val_st    = ParagraphStyle("val", parent=styles["Normal"],
                                    textColor=colors.white, fontSize=10,
                                    alignment=TA_RIGHT)

        story = []

        # Encabezado
        story.append(Paragraph("GESTIÓN SOLAR DEL CARIBE S.A.S.", titulo_st))
        story.append(Paragraph(
            "Barranquilla, Colombia  |  www.gestion-solar-caribe.com", sub_st))
        story.append(HRFlowable(width="100%", color=verde,
                                 thickness=1.5, spaceAfter=12))

        story.append(Paragraph(
            f"<b>FACTURA DE AHORRO SOLAR</b>  —  "
            f"{datetime.now().strftime('%d/%m/%Y')}",
            ParagraphStyle("fac", parent=styles["Normal"],
                            textColor=colors.white, fontSize=12,
                            spaceAfter=12)))

        # Datos cliente
        cli_data = [
            ["Cliente:", cliente.get("nombre_titular", "N/A")],
            ["Cédula/NIT:", cliente.get("cedula_nit", "N/A")],
            ["Dirección:", (cliente.get("direccion_completa") or "N/A") +
             f" — {cliente.get('barrio_sector') or ''}"],
            ["Teléfono:", cliente.get("telefono", "N/A")],
        ]
        cli_tbl = Table(cli_data, colWidths=[4*cm, 12*cm])
        cli_tbl.setStyle(TableStyle([
            ("TEXTCOLOR",   (0, 0), (-1, -1), colors.HexColor("#8B949E")),
            ("TEXTCOLOR",   (1, 0), (1, -1),  colors.white),
            ("FONTSIZE",    (0, 0), (-1, -1),  9),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]))
        story.append(cli_tbl)
        story.append(Spacer(1, 16))

        # Tabla de cálculo
        calc_data = [
            ["Concepto", "Detalle", "Valor"],
            ["kWh Consumidos", f"{kwh:.2f} kWh", "—"],
            ["Tarifa Air-e", f"${t_aire:,.2f}/kWh", "—"],
            ["Subtotal Air-e", "", f"${kwh*t_aire:,.0f}"],
            ["Deducciones Air-e", "Subsidios / descuentos", f"- ${ded:,.0f}"],
            ["TOTAL AIR-E", "", f"${total_aire:,.0f}"],
            ["Tarifa GSC", f"${t_gsc:,.2f}/kWh", "—"],
            ["TOTAL GSC", "", f"${total_gsc:,.0f}"],
        ]
        calc_tbl = Table(calc_data, colWidths=[6*cm, 7*cm, 4*cm])
        calc_tbl.setStyle(TableStyle([
            ("BACKGROUND",  (0, 0), (-1, 0),  colors.HexColor("#0D4B35")),
            ("TEXTCOLOR",   (0, 0), (-1, 0),  verde),
            ("FONTNAME",    (0, 0), (-1, 0),  "Helvetica-Bold"),
            ("BACKGROUND",  (0, 1), (-1, -1), colors.HexColor("#1C2333")),
            ("TEXTCOLOR",   (0, 1), (-1, -1), colors.white),
            ("FONTSIZE",    (0, 0), (-1, -1),  9),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1),
             [colors.HexColor("#1C2333"), colors.HexColor("#21262D")]),
            ("GRID",        (0, 0), (-1, -1), 0.5,
             colors.HexColor("#30363D")),
            ("ALIGN",       (2, 0), (2, -1), "RIGHT"),
            ("FONTNAME",    (0, 5), (-1, 5), "Helvetica-Bold"),
            ("FONTNAME",    (0, 7), (-1, 7), "Helvetica-Bold"),
            ("TOPPADDING",  (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ]))
        story.append(calc_tbl)
        story.append(Spacer(1, 16))

        # Caja de ahorro
        ahorro_data = [["💰  MONTO AHORRADO ESTE MES", f"${ahorro:,.0f}"]]
        ah_tbl = Table(ahorro_data, colWidths=[13*cm, 4*cm])
        ah_tbl.setStyle(TableStyle([
            ("BACKGROUND",    (0, 0), (-1, -1), colors.HexColor("#0D4B35")),
            ("TEXTCOLOR",     (0, 0), (-1, -1), verde),
            ("FONTNAME",      (0, 0), (-1, -1), "Helvetica-Bold"),
            ("FONTSIZE",      (0, 0), (-1, -1), 14),
            ("ALIGN",         (1, 0), (1, 0), "RIGHT"),
            ("TOPPADDING",    (0, 0), (-1, -1), 10),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
            ("LEFTPADDING",   (0, 0), (-1, -1), 12),
        ]))
        story.append(ah_tbl)
        story.append(Spacer(1, 20))

        # Pie de página
        story.append(HRFlowable(width="100%", color=verde,
                                 thickness=0.5, spaceAfter=6))
        story.append(Paragraph(
            f"Generado el {datetime.now().strftime('%d/%m/%Y %H:%M')}  |  "
            "Sistema GSC v2.0  |  Gestión Solar del Caribe S.A.S.",
            ParagraphStyle("footer", parent=styles["Normal"],
                            textColor=gris, fontSize=7,
                            alignment=TA_CENTER)))

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
