import customtkinter as ctk
from tkinter import messagebox
from app.theme import COLORS, FONTS

class ClientesPage(ctk.CTkFrame):
    def __init__(self, parent, db):
        super().__init__(parent, fg_color="transparent")
        self.db = db
        self.cliente_editando_id = None
        self._construir_ui()
        self._actualizar_tabla_completa()

    def _construir_ui(self):
        self.scroll_principal = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll_principal.pack(fill="both", expand=True, padx=20, pady=10)

        self.lbl_titulo = ctk.CTkLabel(self.scroll_principal, text="📋 EXPEDIENTES GESTIÓN SOLAR DEL CARIBE", 
                                       font=FONTS["title_large"], text_color=COLORS["accent_primary"])
        self.lbl_titulo.pack(pady=10)

        # --- FORMULARIO ---
        self.form = ctk.CTkFrame(self.scroll_principal, fg_color=COLORS["bg_card"], corner_radius=15)
        self.form.pack(fill="x", padx=20, pady=10)

        grid_form = ctk.CTkFrame(self.form, fg_color="transparent")
        grid_form.pack(pady=20, padx=20, fill="x")
        grid_form.columnconfigure((0, 1), weight=1)

        self.entries = {}
        campos = [
            ("Titular / Razón Social", "nombre", 0,0), ("Cédula / NIT", "nit", 0,1),
            ("Dirección", "dir", 1,0), ("Barrio", "barrio", 1,1),
            ("Estrato (1-6)", "estrato", 2,0), ("Geolocalización", "geo", 2,1),
            ("Teléfono", "tel", 3,0), ("Correo Electrónico", "mail", 3,1),
            ("Tarifa Air-e ($/kWh)", "tarifa", 4,0)
        ]

        for label, key, r, c in campos:
            f = ctk.CTkFrame(grid_form, fg_color="transparent")
            f.grid(row=r, column=c, padx=15, pady=8, sticky="nsew")
            ctk.CTkLabel(f, text=label, font=FONTS["label"]).pack(anchor="w")
            ent = ctk.CTkEntry(f, height=35)
            ent.pack(fill="x", pady=2)
            self.entries[key] = ent

        btn_frame = ctk.CTkFrame(self.form, fg_color="transparent")
        btn_frame.pack(pady=20)

        self.btn_guardar = ctk.CTkButton(btn_frame, text="GUARDAR REGISTRO", 
                                         fg_color=COLORS["accent_primary"], text_color="#000000",
                                         font=FONTS["title_small"], height=45, width=200,
                                         command=self._guardar_cliente)
        self.btn_guardar.pack(side="left", padx=10)

        self.btn_cancelar = ctk.CTkButton(btn_frame, text="CANCELAR", fg_color="#444444", 
                                          height=45, width=120, command=self._cancelar_edicion)

        # --- TABLA DE EXPEDIENTES ---
        ctk.CTkLabel(self.scroll_principal, text="👤 LISTADO COMPLETO (Click para editar)", 
                     font=FONTS["title_medium"]).pack(pady=(20, 5))
        
        self.tabla_frame = ctk.CTkFrame(self.scroll_principal, fg_color=COLORS["bg_secondary"], corner_radius=10)
        self.tabla_frame.pack(fill="x", padx=10, pady=10)

    def _actualizar_tabla_completa(self):
        for widget in self.tabla_frame.winfo_children():
            widget.destroy()

        clientes = self.db.obtener_clientes()
        if not clientes:
            ctk.CTkLabel(self.tabla_frame, text="Sin registros.").pack(pady=20)
            return

        # Encabezados usando GRID para evitar conflictos
        h = ctk.CTkFrame(self.tabla_frame, fg_color="transparent")
        h.pack(fill="x", padx=10, pady=5)
        
        headers = [("Nombre", 0, 200), ("NIT", 1, 100), ("Barrio", 2, 120), ("Estrato", 3, 60), 
                   ("Tarifa", 4, 80), ("Teléfono", 5, 110), ("Email", 6, 200)]
        
        for text, col, wd in headers:
            lbl = ctk.CTkLabel(h, text=text, width=wd, anchor="w", font=FONTS["label"], text_color="#AAAAAA")
            lbl.grid(row=0, column=col, padx=5)

        # Filas
        for i, c in enumerate(clientes):
            row = ctk.CTkFrame(self.tabla_frame, fg_color=COLORS["bg_card"], height=40, corner_radius=5)
            row.pack(fill="x", padx=10, pady=2)
            row.grid_columnconfigure((0,1,2,3,4,5,6), weight=0)

            # Datos con el mismo ancho que el header
            ctk.CTkLabel(row, text=c['nombre_titular'], width=200, anchor="w").grid(row=0, column=0, padx=5)
            ctk.CTkLabel(row, text=c['cedula_nit'], width=100, anchor="w").grid(row=0, column=1, padx=5)
            ctk.CTkLabel(row, text=c['barrio_sector'] or "-", width=120, anchor="w").grid(row=0, column=2, padx=5)
            ctk.CTkLabel(row, text=str(c['estrato'] or "-"), width=60).grid(row=0, column=3, padx=5)
            ctk.CTkLabel(row, text=f"${c['tarifa_aire_actual'] or 0}", width=80, text_color=COLORS["accent_primary"]).grid(row=0, column=4, padx=5)
            ctk.CTkLabel(row, text=c['telefono'] or "-", width=110, anchor="w").grid(row=0, column=5, padx=5)
            ctk.CTkLabel(row, text=c['email'] or "-", width=200, anchor="w").grid(row=0, column=6, padx=5)

            # Hacer que toda la fila sea clickeable para editar
            row.bind("<Button-1>", lambda e, obj=c: self._cargar_modo_edicion(obj))
            for child in row.winfo_children():
                child.bind("<Button-1>", lambda e, obj=c: self._cargar_modo_edicion(obj))

    def _cargar_modo_edicion(self, cliente):
        self._cancelar_edicion()
        self.cliente_editando_id = cliente['id']
        self.lbl_titulo.configure(text=f"✏️ EDITANDO: {cliente['nombre_titular']}", text_color=COLORS["solar_yellow"])
        self.btn_guardar.configure(text="ACTUALIZAR DATOS")
        self.btn_cancelar.pack(side="left", padx=10)
        
        mapping = {
            'nombre': cliente['nombre_titular'], 'nit': cliente['cedula_nit'], 
            'dir': cliente['direccion_completa'], 'barrio': cliente['barrio_sector'],
            'estrato': str(cliente['estrato'] or ""), 'geo': cliente['geolocalizacion'],
            'tel': cliente['telefono'], 'mail': cliente['email'], 
            'tarifa': str(cliente['tarifa_aire_actual'] or "")
        }
        for k, val in mapping.items():
            if val is not None: self.entries[k].insert(0, val)

    def _cancelar_edicion(self):
        self.cliente_editando_id = None
        for e in self.entries.values(): e.delete(0, 'end')
        self.lbl_titulo.configure(text="📋 EXPEDIENTES GESTIÓN SOLAR DEL CARIBE", text_color=COLORS["accent_primary"])
        self.btn_guardar.configure(text="GUARDAR REGISTRO")
        self.btn_cancelar.pack_forget()

    def _guardar_cliente(self):
        data = {k: v.get() for k, v in self.entries.items()}
        if not data['nombre'] or not data['nit']:
            messagebox.showwarning("GSC", "Nombre y NIT obligatorios")
            return
        try:
            if self.cliente_editando_id:
                self.db.actualizar_cliente(self.cliente_editando_id, data)
            else:
                self.db.crear_cliente(data)
            self._cancelar_edicion()
            self._actualizar_tabla_completa()
            messagebox.showinfo("GSC", "Datos guardados")
        except Exception as e:
            messagebox.showerror("Error", str(e))