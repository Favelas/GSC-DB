import customtkinter as ctk
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import LETTER
from reportlab.lib import colors

class ExportarPage(ctk.CTkFrame):
    # ... (inicialización similar a las otras)

    def format_cop(self, valor):
        """Formatea números a Moneda Colombiana: $ 1.000.000"""
        return f"$ {valor:,.0f}".replace(",", ".")

    def generar_pdf_high_impact(self, datos_factura):
        c = canvas.Canvas("Factura_GSC.pdf", pagesize=LETTER)
        
        # ENCABEZADO
        c.setFont("Helvetica-Bold", 20)
        c.drawString(50, 750, "GESTIÓN SOLAR DEL CARIBE")
        
        # RECUADRO DE PAGO (HIGHLIGHT)
        c.setFillColor(colors.hexColor("#2c3e50"))
        c.rect(50, 630, 500, 60, fill=1)
        c.setFillColor(colors.white)
        c.setFont("Helvetica-Bold", 18)
        total_texto = f"TOTAL A PAGAR: {self.format_cop(datos_factura['total'])}"
        c.drawCentredString(300, 655, total_texto)

        # DETALLES
        c.setFillColor(colors.black)
        c.setFont("Helvetica", 12)
        c.drawString(50, 600, f"Periodo: {datos_factura['inicio']} al {datos_factura['fin']}")
        c.drawString(50, 580, f"Consumo de Red: {datos_factura['red']} kWh")
        
        # NOTA DE SUBSIDIO
        if datos_factura['red'] <= 173:
            c.setFillColor(colors.green)
            c.drawString(50, 550, "¡OPTIMIZACIÓN POR SUBSIDIO APLICADA (173 kWh)!")
        
        # FOOTER DE CONTACTO
        c.setStrokeColor(colors.lightgrey)
        c.line(50, 100, 550, 100)
        c.setFillColor(colors.grey)
        c.setFont("Helvetica-Oblique", 10)
        c.drawString(50, 80, "¿Dudas? WhatsApp: +57 3XX XXX XXXX | Email: soporte@gsc.com")
        
        c.save()