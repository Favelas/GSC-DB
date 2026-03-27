import sqlite3
import os

class DatabaseManager:
    def __init__(self, db_path="solar_caribe.db"):
        self.db_path = db_path
        self._inicializar_db()

    def _conectar(self):
        """Establece conexión con la base de datos local."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Permite acceder a columnas por nombre
        return conn

    def _inicializar_db(self):
        """Crea las tablas y aplica migraciones automáticas si faltan columnas."""
        with self._conectar() as conn:
            cursor = conn.cursor()
            
            # 1. TABLA CLIENTES (Estructura base)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS clientes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre_titular TEXT NOT NULL,
                    cedula_nit TEXT UNIQUE NOT NULL
                )
            """)
            
            # MIGRACIÓN: Columnas técnicas y de contacto para Clientes
            cols_clientes = {
                "direccion_completa": "TEXT",
                "barrio_sector": "TEXT",
                "estrato": "INTEGER",
                "tarifa_aire_actual": "REAL",
                "telefono": "TEXT",
                "email": "TEXT"
            }
            self._aplicar_migraciones(cursor, "clientes", cols_clientes)

            # 2. TABLA PROYECTOS (Estructura base)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS proyectos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    cliente_id INTEGER,
                    FOREIGN KEY (cliente_id) REFERENCES clientes(id)
                )
            """)
            
            # MIGRACIÓN: Especificaciones técnicas de la instalación
            cols_proyectos = {
                "nombre_proyecto": "TEXT",
                "fecha_instalacion": "DATE",
                "kwp_instalados": "REAL",
                "marca_paneles": "TEXT",
                "seriales_paneles": "TEXT",
                "marca_inversor": "TEXT",
                "estatus_retie": "TEXT DEFAULT 'Pendiente'",
                "ruta_fotos_entrega": "TEXT"
            }
            self._aplicar_migraciones(cursor, "proyectos", cols_proyectos)

            # 3. TABLA USUARIOS (Para el Login)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS usuarios (
                    id INTEGER PRIMARY KEY, 
                    usuario TEXT UNIQUE, 
                    password TEXT, 
                    nombre_completo TEXT
                )
            """)
            
            # Usuario admin por defecto si la tabla está vacía
            if cursor.execute("SELECT COUNT(*) FROM usuarios").fetchone()[0] == 0:
                cursor.execute("INSERT INTO usuarios (usuario, password, nombre_completo) VALUES ('admin', 'admin123', 'Fabián Velásquez')")
            
            conn.commit()

    def _aplicar_migraciones(self, cursor, tabla, columnas):
        """Agrega columnas dinámicamente si no existen en la tabla actual."""
        cursor.execute(f"PRAGMA table_info({tabla})")
        existentes = [col[1] for col in cursor.fetchall()]
        for col_nom, col_tipo in columnas.items():
            if col_nom not in existentes:
                cursor.execute(f"ALTER TABLE {tabla} ADD COLUMN {col_nom} {col_tipo}")

    # --- MÉTODOS PARA CLIENTES ---
    
    def obtener_clientes(self):
        """Retorna todos los clientes con todas sus columnas."""
        with self._conectar() as conn:
            # El * asegura que traiga Email, Teléfono, etc., recién agregados
            return [dict(r) for r in conn.execute("SELECT * FROM clientes ORDER BY nombre_titular").fetchall()]

    def crear_cliente(self, d):
        """Inserta un nuevo cliente en la base de datos."""
        with self._conectar() as conn:
            sql = """INSERT INTO clientes (
                        nombre_titular, cedula_nit, direccion_completa, 
                        barrio_sector, estrato, tarifa_aire_actual, 
                        telefono, email
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)"""
            conn.execute(sql, (
                d['nombre'], d['nit'], d['dir'], d['barrio'], 
                d['estrato'], d['tarifa'], d['tel'], d['mail']
            ))
            conn.commit()

    def actualizar_cliente(self, id_c, d):
        """Actualiza la información de un cliente existente por su ID."""
        with self._conectar() as conn:
            sql = """UPDATE clientes SET 
                        nombre_titular=?, cedula_nit=?, direccion_completa=?, 
                        barrio_sector=?, estrato=?, tarifa_aire_actual=?, 
                        telefono=?, email=? 
                     WHERE id=?"""
            conn.execute(sql, (
                d['nombre'], d['nit'], d['dir'], d['barrio'], 
                d['estrato'], d['tarifa'], d['tel'], d['mail'], id_c
            ))
            conn.commit()

    # --- MÉTODOS PARA PROYECTOS ---

    def obtener_proyectos(self):
        """Retorna proyectos vinculados con el nombre del cliente."""
        with self._conectar() as conn:
            query = """
                SELECT p.*, c.nombre_titular as cliente_nombre 
                FROM proyectos p 
                JOIN clientes c ON p.cliente_id = c.id
                ORDER BY p.id DESC
            """
            return [dict(r) for r in conn.execute(query).fetchall()]

    def crear_proyecto(self, d):
        """Registra un nuevo proyecto técnico."""
        with self._conectar() as conn:
            sql = """INSERT INTO proyectos (
                        cliente_id, nombre_proyecto, fecha_instalacion, 
                        kwp_instalados, marca_paneles, seriales_paneles, 
                        marca_inversor, estatus_retie
                    ) VALUES (?, ?, date('now'), ?, ?, ?, ?, ?)"""
            conn.execute(sql, (
                d['cliente_id'], d['nombre'], d['kwp'], 
                d['paneles'], d['seriales'], d['inversor'], d['retie']
            ))
            conn.commit()

    # --- OTROS MÉTODOS ---

    def obtener_kpis(self):
        """Calcula los totales para el Dashboard."""
        with self._conectar() as conn:
            kwp = conn.execute("SELECT SUM(kwp_instalados) FROM proyectos").fetchone()[0] or 0.0
            cnt = conn.execute("SELECT COUNT(*) FROM clientes").fetchone()[0] or 0
            return {"kwp": round(kwp, 2), "clientes": cnt}

    def verify_login(self, u, p):
        """Verifica credenciales de acceso."""
        with self._conectar() as conn:
            r = conn.execute("SELECT * FROM usuarios WHERE usuario=? AND password=?", (u, p)).fetchone()
            return dict(r) if r else None