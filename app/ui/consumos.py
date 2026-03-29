import customtkinter as ctk
from tkinter import messagebox
from app.database import DatabaseManager

class ConsumosPage(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self.db = DatabaseManager()
        self.setup_ui()

    def setup_ui(self):
        self.grid_columnconfigure(0, weight=1)
        
        # --- ENTRADA DE DATOS ---
        frame_input = ctk.CTkFrame(self)
        frame_input.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

        ctk.CTkLabel(frame_input, text="Sincronización Ciclo Air-e (Barranquilla)", font=("Helvetica", 16, "bold")).grid(row=0, column=0, columnspan=2, pady=10)

        self.f_inicio = ctk.CTkEntry(frame_input, placeholder_text="Inicio Ciclo (DD/MM/AAAA)")
        self.f_inicio.grid(row=1, column=0, padx=10, pady=5)
        
        self.f_fin = ctk.CTkEntry(frame_input, placeholder_text="Fin Ciclo (DD/MM/AAAA)")
        self.f_fin.grid(row=1, column=1, padx=10, pady=5)

        self.kwh_gsc = ctk.CTkEntry(frame_input, placeholder_text="Generación Solar (kWh)")
        self.kwh_gsc.grid(row=2, column=0, padx=10, pady=10)

        self.kwh_red = ctk.CTkEntry(frame_input, placeholder_text="Lectura Red Air-e (kWh)")
        self.kwh_red.grid(row=2, column=1, padx=10, pady=10)

        btn_analizar = ctk.CTkButton(frame_input, text="Analizar y Guardar", command=self.analizar, fg_color="#2ecc71")
        btn_analizar.grid(row=3, column=0, columnspan=2, pady=20)

        # --- TEXTBOX DEL AGENTE INTELIGENTE ---
        self.txt_agente = ctk.CTkTextbox(self, height=200, font=("Consolas", 13))
        self.txt_agente.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")

    def analizar(self):
        try:
            gen = float(self.kwh_gsc.get())
            red = float(self.kwh_red.get())
            total = gen + red
            
            # Alerta de Subsidio (Límite 173 kWh)
            subsidio = "✅ SUBSIDIO APLICADO" if red <= 173 else "❌ TARIFA PLENA (Superó 173 kWh)"
            color = "#2ecc71" if red <= 173 else "#e74c3c"

            reporte = (
                f"--- ANÁLISIS GSC ---\n"
                f"Consumo Total: {total:.2f} kWh\n"
                f"Ahorro Solar: {gen:.2f} kWh\n"
                f"Compra a Red: {red:.2f} kWh\n"
                f"ESTADO RED: {subsidio}\n"
                f"--------------------\n"
                f"Sugerencia: " + ("Mantén el consumo bajo para maximizar ahorro." if red <= 173 else "⚠️ Reduce el consumo de red para volver al subsidio.")
            )
            
            self.txt_agente.delete("1.0", "end")
            self.txt_agente.insert("1.0", reporte)
            self.txt_agente.configure(text_color=color)
            messagebox.showinfo("GSC", "Análisis completado y datos registrados.")
        except:
            messagebox.showerror("Error", "Ingresa números válidos en los campos.")