import customtkinter as ctk
from tkinter import messagebox
from app.theme import COLORS, FONTS

class ProyectosPage(ctk.CTkFrame):
    def __init__(self, parent, db):
        super().__init__(parent, fg_color="transparent")
        self.db = db
        self.cli_map = {}
        self._construir_ui()
        self._cargar_combos()
        self._actualizar_tabla()

    def _construir_ui(self):
        self.scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll.pack(fill="both", expand=True, padx=20, pady=10)

        ctk.CTkLabel(self.scroll, text="🚀 INSTALACIONES TÉCNICAS", font=FONTS["title_large"], text_color=COLORS["accent_primary"]).pack(pady=10)
        
        # Form
        f = ctk.CTkFrame(self.scroll, fg_color=COLORS["bg_card"], corner_radius=15)
        f.pack(fill="x", padx=20, pady=10)
        grid = ctk.CTkFrame(f, fg_color="transparent"); grid.pack(pady=20, padx=20, fill="x")
        grid.columnconfigure((0,1), weight=1)

        ctk.CTkLabel(grid, text="Cliente:", font=FONTS["label"]).grid(row=0, column=0, sticky="w", padx=10)
        self.cb_cli = ctk.CTkComboBox(grid, width=300); self.cb_cli.grid(row=1, column=0, padx=10, pady=(0,15))

        self.e_nom = self._campo(grid, "Nombre Proyecto", 0, 1)
        self.e_kwp = self._campo(grid, "kWp Instalados", 2, 0)
        self.e_pan = self._campo(grid, "Marca Paneles", 2, 1)
        self.e_ser = self._campo(grid, "Seriales", 4, 0)
        self.e_inv = self._campo(grid, "Marca Inversor", 4, 1)
        
        ctk.CTkLabel(grid, text="RETIE:", font=FONTS["label"]).grid(row=6, column=0, sticky="w", padx=10)
        self.cb_ret = ctk.CTkComboBox(grid, values=["Pendiente", "Certificado"], width=300); self.cb_ret.grid(row=7, column=0, padx=10)

        ctk.CTkButton(f, text="VINCULAR", fg_color=COLORS["accent_primary"], text_color="#000", command=self._save).pack(pady=20)

        self.tabla = ctk.CTkFrame(self.scroll, fg_color=COLORS["bg_secondary"]); self.tabla.pack(fill="both", expand=True, padx=20, pady=10)

    def _campo(self, p, l, r, c):
        ctk.CTkLabel(p, text=l, font=FONTS["label"]).grid(row=r, column=c, sticky="w", padx=10)
        e = ctk.CTkEntry(p, width=300); e.grid(row=r+1, column=c, padx=10, pady=(0,15))
        return e

    def _cargar_combos(self):
        clis = self.db.obtener_clientes()
        if clis:
            self.cli_map = {c['nombre_titular']: c['id'] for c in clis}
            self.cb_cli.configure(values=list(self.cli_map.keys()))
            self.cb_cli.set(list(self.cli_map.keys())[0])

    def _actualizar_tabla(self):
        for w in self.tabla.winfo_children(): w.destroy()
        for p in self.db.obtener_proyectos():
            row = ctk.CTkFrame(self.tabla, fg_color=COLORS["bg_card"], height=40); row.pack(fill="x", pady=2)
            ctk.CTkLabel(row, text=p['cliente_nombre'], width=200).pack(side="left", padx=10)
            ctk.CTkLabel(row, text=f"{p['kwp_instalados']} kWp", text_color=COLORS["accent_primary"]).pack(side="left", padx=10)
            ctk.CTkLabel(row, text=p['estatus_retie']).pack(side="left", padx=10)

    def _save(self):
        try:
            d = {'cliente_id': self.cli_map[self.cb_cli.get()], 'nombre': self.e_nom.get(), 'kwp': float(self.e_kwp.get()),
                 'paneles': self.e_pan.get(), 'seriales': self.e_ser.get(), 'inversor': self.e_inv.get(), 'retie': self.cb_ret.get()}
            self.db.crear_proyecto(d); self._actualizar_tabla(); messagebox.showinfo("GSC", "Listo")
        except Exception as e: messagebox.showerror("Error", str(e))