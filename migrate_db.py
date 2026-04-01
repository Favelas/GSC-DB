"""
migrate_db.py — Migración automática: password (texto) → password_hash (SHA-256)
Ejecutar ANTES de iniciar main.py por primera vez con v3.0
"""

import sqlite3
import hashlib
import os
from datetime import datetime


def migrar_contrasenas():
    """Migra contraseñas de texto plano a hash SHA-256."""
    
    db_path = "solar_caribe.db"
    
    if not os.path.exists(db_path):
        print("❌ No se encontró solar_caribe.db. Ejecuta primero: python main.py")
        return False
    
    print("=" * 60)
    print("MIGRACIÓN: password (texto) → password_hash (SHA-256)")
    print("=" * 60)
    
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    try:
        # 1. Verificar si la tabla usuarios existe
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='usuarios'")
        if not cur.fetchone():
            print("❌ Tabla 'usuarios' no existe. Algo está mal.")
            return False
        
        # 2. Verificar qué columnas existen
        cur.execute("PRAGMA table_info(usuarios)")
        columnas = {row[1] for row in cur.fetchall()}
        
        print(f"\n📋 Columnas encontradas: {columnas}")
        
        # 3. Si ya existe password_hash, la migración ya fue hecha
        if "password_hash" in columnas:
            print("✅ Columna 'password_hash' ya existe. Migración completada anteriormente.")
            
            # Verificar que no haya passwords en texto plano
            if "password" in columnas:
                cur.execute("SELECT COUNT(*) FROM usuarios WHERE password_hash IS NULL OR password_hash = ''")
                con_null = cur.fetchone()[0]
                
                if con_null == 0:
                    print("✅ Todos los usuarios tienen password_hash. Migrando...")
                    cur.execute("ALTER TABLE usuarios DROP COLUMN password")
                    conn.commit()
                    print("✅ Columna 'password' eliminada.")
            
            return True
        
        # 4. Si NO existe password_hash pero SÍ password, hacer migración
        if "password" in columnas:
            print("\n⚠️  Se detectó columna 'password' (texto plano).")
            print("📝 Iniciando migración a SHA-256...\n")
            
            # Agregar columna password_hash
            print("  1. Agregando columna 'password_hash'...", end="")
            cur.execute("ALTER TABLE usuarios ADD COLUMN password_hash TEXT")
            conn.commit()
            print(" ✅")
            
            # Agregar columna fecha_cambio_pwd si no existe
            if "fecha_cambio_pwd" not in columnas:
                print("  2. Agregando columna 'fecha_cambio_pwd'...", end="")
                cur.execute("ALTER TABLE usuarios ADD COLUMN fecha_cambio_pwd TEXT")
                conn.commit()
                print(" ✅")
            else:
                print("  2. Columna 'fecha_cambio_pwd' ya existe ✅")
            
            # Migrar contraseñas de password → password_hash
            print("  3. Migrando contraseñas a hash SHA-256...", end="")
            cur.execute("SELECT id, password FROM usuarios")
            usuarios = cur.fetchall()
            
            for user_id, password in usuarios:
                if password:
                    hash_pwd = hashlib.sha256(password.encode()).hexdigest()
                    fecha = datetime.now().isoformat()
                    cur.execute(
                        "UPDATE usuarios SET password_hash=?, fecha_cambio_pwd=? WHERE id=?",
                        (hash_pwd, fecha, user_id)
                    )
            
            conn.commit()
            print(f" ✅ ({len(usuarios)} usuarios migrados)")
            
            # Eliminar columna password vieja
            print("  4. Eliminando columna 'password' antigua...", end="")
            cur.execute("""
                CREATE TABLE usuarios_nueva (
                    id INTEGER PRIMARY KEY,
                    usuario TEXT UNIQUE,
                    password_hash TEXT,
                    nombre_completo TEXT,
                    fecha_cambio_pwd TEXT
                )
            """)
            cur.execute("""
                INSERT INTO usuarios_nueva (id, usuario, password_hash, nombre_completo, fecha_cambio_pwd)
                SELECT id, usuario, password_hash, nombre_completo, fecha_cambio_pwd FROM usuarios
            """)
            cur.execute("DROP TABLE usuarios")
            cur.execute("ALTER TABLE usuarios_nueva RENAME TO usuarios")
            conn.commit()
            print(" ✅")
            
            print("\n✅ MIGRACIÓN COMPLETADA EXITOSAMENTE")
            print("\n📊 Estado final:")
            cur.execute("SELECT usuario, LENGTH(password_hash) FROM usuarios")
            for user, hash_len in cur.fetchall():
                estado = "✅ SHA-256" if hash_len == 64 else "❌ Incorrecto"
                print(f"   • {user}: {estado} ({hash_len} caracteres)")
            
            return True
        
        else:
            print("❌ No se encontró columna 'password' ni 'password_hash'.")
            print("   Estado de tabla incoherente. Contacta al desarrollador.")
            return False
    
    except sqlite3.OperationalError as e:
        print(f"❌ Error SQL: {e}")
        return False
    
    finally:
        conn.close()


if __name__ == "__main__":
    print()
    exito = migrar_contrasenas()
    print()
    
    if exito:
        print("=" * 60)
        print("🎉 LISTA PARA USAR GSC v3.0")
        print("=" * 60)
        print("\nAhora ejecuta: python main.py")
        print()
    else:
        print("=" * 60)
        print("❌ LA MIGRACIÓN FALLÓ")
        print("=" * 60)
        print("\nContacta al desarrollador con el error anterior.")
        print()
