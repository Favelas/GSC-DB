from fpdf import FPDF
from datetime import datetime
import os

class GSC_PDF_Generator:
    """Generador de documentos oficiales para Gestión Solar del Caribe S.A.S."""
    
    def __init__(self):
        self.company_name = "GESTIÓN SOLAR DEL CARIBE S.A.S."
        self.nit = "NIT: 901.XXX.XXX-X" # Reemplaza con el real
        self.contacto = "Barranquilla, Colombia | Tel: +57 XXX XXX XXXX"

    def generar_cotizacion(self, cliente, proyecto, items, total):
        pdf = FPDF()
        pdf.add_page()
        
        # --- ENCABEZADO ---
        pdf.set_font("Arial", "B", 16)
        pdf.set_text_color(44, 62, 80) # Azul oscuro
        pdf.cell(0, 10, self.company_name, ln=True, align="C")
        
        pdf.set_font("Arial", "", 10)
        pdf.cell(0, 5, self.nit, ln=True, align="C")
        pdf.cell(0, 5, self.contacto, ln=True, align="C")
        pdf.ln(10)

        # --- INFO CLIENTE ---
        pdf.set_fill_color(240, 240, 240)
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, f" COTIZACIÓN # {datetime.now().strftime('%Y%m%d%H%M')}", ln=True, fill=True)
        pdf.ln(5)

        pdf.set_font("Arial", "B", 10)
        pdf.cell(30, 7, "Cliente:", 0)
        pdf.set_font("Arial", "", 10)
        pdf.cell(0, 7, cliente['nombre_titular'], ln=True)

        pdf.set_font("Arial", "B", 10)
        pdf.cell(30, 7, "Cédula/NIT:", 0)
        pdf.set_font("Arial", "", 10)
        pdf.cell(0, 7, cliente['cedula_nit'], ln=True)

        pdf.set_font("Arial", "B", 10)
        pdf.cell(30, 7, "Dirección:", 0)
        pdf.set_font("Arial", "", 10)
        pdf.cell(0, 7, f"{cliente['direccion_completa']} - {cliente['barrio_sector']}", ln=True)
        pdf.ln(10)

        # --- TABLA DE ITEMS ---
        pdf.set_font("Arial", "B", 10)
        pdf.set_fill_color(52, 152, 219) # Azul GSC
        pdf.set_text_color(255, 255, 255)
        
        pdf.cell(110, 8, "Descripción del Sistema Solar", 1, 0, "C", True)
        pdf.cell(40, 8, "Capacidad/Cant", 1, 0, "C", True)
        pdf.cell(40, 8, "Subtotal", 1, 1, "C", True)

        pdf.set_text_color(0, 0, 0)
        pdf.set_font("Arial", "", 10)
        
        # Ejemplo de llenado (puedes pasar una lista de diccionarios)
        for item in items:
            pdf.cell(110, 8, item['desc'], 1)
            pdf.cell(40, 8, str(item['cant']), 1, 0, "C")
            pdf.cell(40, 8, f"$ {item['precio']:,.0f}", 1, 1, "R")

        # --- TOTAL ---
        pdf.ln(5)
        pdf.set_font("Arial", "B", 12)
        pdf.cell(150, 10, "VALOR TOTAL DE LA INVERSIÓN:", 0, 0, "R")
        pdf.cell(40, 10, f"$ {total:,.0f}", 0, 1, "R")

        # --- NOTA TÉCNICA ---
        pdf.ln(10)
        pdf.set_font("Arial", "I", 8)
        pdf.multi_cell(0, 5, "Nota: Esta cotización incluye instalación, puesta en marcha y gestión de trámites ante el operador de red. Validez: 15 días calendario.")

        # Guardar
        filename = f"Cotizacion_{cliente['cedula_nit']}.pdf"
        pdf.output(filename)
        return filename