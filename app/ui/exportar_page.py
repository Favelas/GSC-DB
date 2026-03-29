import customtkinter as ctk
from tkinter import filedialog, messagebox
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import LETTER
from reportlab.lib import colors

class ExportarPage(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self.setup_ui()

    def setup_ui(self):
        self.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(self, text="Exportar Factura GSC", font=("Helvetica", 24, "bold")).pack(pady=20)
        
        self.btn_pdf = ctk.CTkButton(self, text="Generar PDF High-Impact", 
                                     command=self.demo_pdf, fg_color="#2c3e50")
        self.btn_pdf.pack(pady=10)

    def format_cop(self, valor):
        """Moneda COP: $ 1.000.000"""
        return f"$ {valor:,.0f}".replace(",", ".")

    def demo_pdf(self):
        # Datos simulados para la prueba
        datos = {'cliente': "Fabian Velasquez", 'red': 150.0, 'total': 285000}
        path = filedialog.asksaveasfilename(defaultextension=".pdf")
        if path:
            self.crear_pdf(path, datos)

    def crear_pdf(self, path, d):
        c = canvas.Canvas(path, pagesize=LETTER)
        
        # Encabezado GSC
        c.setFont("Helvetica-Bold", 22)
        c.setFillColor(colors.hexColor("#2c3e50"))
        c.drawString(50, 750, "GESTIÓN SOLAR DEL CARIBE")
        
        # BLOQUE RESALTADO (TOTAL A PAGAR)
        c.setFillColor(colors.hexColor("#2ecc71"))
        c.rect(50, 640, 500, 60, fill=1, stroke=0)
        c.setFillColor(colors.white)
        c.setFont("Helvetica-Bold", 20)
        c.drawCentredString(300, 665, f"TOTAL A PAGAR: {self.format_cop(d['total'])}")

        # Nota Técnica y Subsidio
        c.setFillColor(colors.black)
        c.setFont("Helvetica", 12)
        c.drawString(50, 610, f"Cliente: {d['cliente']}")
        
        if d['red'] <= 173:
            c.setFillColor(colors.darkgreen)
            c.drawString(50, 580, "✓ APLICADO: Tarifa de Subsistencia (Menos de 173 kWh)")

        # Footer de contacto
        c.setStrokeColor(colors.lightgrey)
        c.line(50, 80, 550, 80)
        c.setFillColor(colors.grey)
        c.setFont("Helvetica", 9)
        c.drawCentredString(300, 60, "Contacto Soporte: WhatsApp +57 [Número] | Email: soporte@gsc.com")
        
        c.save()
        messagebox.showinfo("Éxito", "PDF generado correctamente.")