#!/usr/bin/env python3
"""
Script para resetear la contraseña del usuario admin
Ejecuta: python reset_admin_password.py
"""

import sqlite3
import os
from werkzeug.security import generate_password_hash

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'entregas.db')

def reset_admin_password():
    """Resetea la contraseña del admin a admin123"""
    if not os.path.exists(DB_PATH):
        print(f"Error: No se encontró la base de datos en {DB_PATH}")
        return False
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Verificar que la tabla usuarios existe
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='usuarios'")
        if not cursor.fetchone():
            print("Error: La tabla 'usuarios' no existe en la base de datos")
            conn.close()
            return False
        
        # Generar hash para la contraseña 'admin123'
        new_password = generate_password_hash('admin123')
        
        # Actualizar contraseña del admin
        cursor.execute('UPDATE usuarios SET password = ? WHERE username = ?', (new_password, 'admin'))
        conn.commit()
        
        if cursor.rowcount > 0:
            print("✓ Contraseña del admin reseteada a 'admin123'")
            print("✓ Usuario: admin")
            print("✓ Contraseña: admin123")
            conn.close()
            return True
        else:
            print("Error: No se encontró el usuario 'admin'")
            conn.close()
            return False
    
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == '__main__':
    print("=== Reset de Contraseña Admin ===")
    print()
    if reset_admin_password():
        print()
        print("✓ Proceso completado exitosamente")
    else:
        print()
        print("✗ Error al resetear la contraseña")
