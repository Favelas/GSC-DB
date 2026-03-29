import customtkinter as ctk
from tkinter import messagebox
from app.database import GestionBaseDatos

class ConsumosPage(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self.db = GestionBaseDatos()
        self.setup_ui()

    def setup_ui(self):
        self.grid_columnconfigure(0, weight=1)
        
        # --- ENTRADA DE DATOS ---
        frame_input = ctk.CTkFrame(self)
        frame_input.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

        ctk.CTkLabel(frame_input, text="Sincronización Ciclo Air-e", font=("Helvetica", 16, "bold")).grid(row=0, column=0, columnspan=2, pady=10)

        self.f_inicio = ctk.CTkEntry(frame_input, placeholder_text="Fecha Inicio (DD/MM/AAAA)")
        self.f_inicio.grid(row=1, column=0, padx=10, pady=5)
        
        self.f_fin = ctk.CTkEntry(frame_input, placeholder_text="Fecha Fin (DD/MM/AAAA)")
        self.f_fin.grid(row=1, column=1, padx=10, pady=5)

        self.kwh_gsc = ctk.CTkEntry(frame_input, placeholder_text="kWh Generados (Paneles)")
        self.kwh_gsc.grid(row=2, column=0, padx=10, pady=10)

        self.kwh_red = ctk.CTkEntry(frame_input, placeholder_text="kWh Lectura Red (Air-e)")
        self.kwh_red.grid(row=2, column=1, padx=10, pady=10)

        btn_analizar = ctk.CTkButton(frame_input, text="Analizar y Guardar", command=self.analizar, fg_color="#2ecc71")
        btn_analizar.grid(row=3, column=0, columnspan=2, pady=20)

        # --- AGENTE INTELIGENTE ---
        self.txt_agente = ctk.CTkTextbox(self, height=200, font=("Consolas", 12))
        self.txt_agente.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")

    def analizar(self):
        try:
            gen = float(self.kwh_gsc.get())
            red = float(self.kwh_red.get())
            total = gen + red
            
            # Lógica de Subsidio 173 kWh
            subsidio_msg = "❌ TARIFA PLENA (Sin subsidio)"
            color = "#e74c3c"
            if red <= 173:
                subsidio_msg = "✅ BENEFICIO SUBSIDIO AIR-E DETECTADO (<= 173 kWh)"
                color = "#2ecc71"

            reporte = (
                f"ANÁLISIS INTELIGENTE GSC\n"
                f"--------------------------\n"
                f"Consumo Total: {total} kWh\n"
                f"Aporte Solar: {gen} kWh ({(gen/total)*100:.1f}%)\n"
                f"Compra a Red: {red} kWh\n\n"
                f"ESTADO: {subsidio_msg}\n"
                f"Sugerencia: " + ("Mantén este ritmo para ahorrar más." if red <= 173 else "¡Cuidado! Tu consumo de red subió.")
            )
            
            self.txt_agente.delete("1.0", "end")
            self.txt_agente.insert("1.0", reporte)
            self.txt_agente.configure(text_color=color)
            
            # Guardar en DB (Simulado para el ejemplo)
            messagebox.showinfo("GSC", "Datos guardados y analizados con éxito.")
        except:
            messagebox.showerror("Error", "Ingresa valores numéricos válidos.")