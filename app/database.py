import sqlite3
import os

class DatabaseManager:
    def __init__(self, db_name="solar_caribe.db"):
        self.db_name = db_name
        self.inicializar_db()

    def inicializar_db(self):
        conexion = sqlite3.connect(self.db_name)
        cursor = conexion.cursor()
        
        # Tabla Clientes
        cursor.execute('''CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            tarifa_gsc REAL DEFAULT 0
        )''')

        # Tabla Consumos Base
        cursor.execute('''CREATE TABLE IF NOT EXISTS consumos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_id INTEGER,
            fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(cliente_id) REFERENCES clientes(id)
        )''')
        
        conexion.commit()
        conexion.close()
        self.ejecutar_migraciones()

    def ejecutar_migraciones(self):
        """Agrega las nuevas columnas para el ciclo Air-e (Barranquilla)"""
        columnas = [
            ("fecha_inicio_ciclo", "TEXT"),
            ("fecha_fin_ciclo", "TEXT"),
            ("kwh_generados_gsc", "REAL"),
            ("lectura_red_aire", "REAL"),
            ("cargos_adicionales", "REAL"),
            ("descuentos_adicionales", "REAL"),
            ("consumo_total_periodo", "REAL")
        ]
        
        conexion = sqlite3.connect(self.db_name)
        cursor = conexion.cursor()
        cursor.execute("PRAGMA table_info(consumos)")
        existentes = [col[1] for col in cursor.fetchall()]

        for nombre, tipo in columnas:
            if nombre not in existentes:
                try:
                    cursor.execute(f"ALTER TABLE consumos ADD COLUMN {nombre} {tipo} DEFAULT 0")
                    print(f"✅ Columna {nombre} sincronizada.")
                except: pass
        
        conexion.commit()
        conexion.close()

    def guardar_registro_completo(self, datos):
        try:
            conexion = sqlite3.connect(self.db_name)
            cursor = conexion.cursor()
            query = '''INSERT INTO consumos (
                cliente_id, fecha_inicio_ciclo, fecha_fin_ciclo, kwh_generados_gsc, 
                lectura_red_aire, cargos_adicionales, descuentos_adicionales, consumo_total_periodo
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)'''
            cursor.execute(query, datos)
            conexion.commit()
            conexion.close()
            return True
        except Exception as e:
            print(f"Error DB: {e}")
            return False