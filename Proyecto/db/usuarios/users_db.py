# archivo: db/usuarios/users_db.py

from typing import Optional, List
from models.user import User, Session
from db.abstract_db import AbstractDatabase
import sqlite3
from pathlib import Path

# Ruta hacia la base de datos
RUTA_DB = Path(__file__).resolve().parent.parent / "datos_financieros" / "datos_financieros.db"

class DataBaseUsuario(AbstractDatabase):
    """
    Maneja la persistencia de usuarios y sesiones.
    Hereda de AbstractDatabase y cumple la interfaz común.
    """

    def __init__(self, conexion: str):
        self.conexion = conexion
        self._crear_tablas()

    
    def _crear_tablas(self):
        """Crea las tablas, si no existen."""
        with sqlite3.connect(self.conexion) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS usuarios (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tipo TEXT,
                    nombre TEXT,
                    contraseña TEXT,
                    email TEXT UNIQUE,
                    telefono INTEGER,
                    hashed_password TEXT,
                    full_name TEXT
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sesiones (
                    token TEXT PRIMARY KEY,
                    usuario_id INTEGER,
                    fecha_inicio TEXT,
                    fecha_expiracion TEXT,
                    FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
                )
            """)
            conn.commit()




    # ========================================================
    # FUNCIONES DE ALTO NIVEL PARA AUTH_SERVICE Y AUTH_API
    # ========================================================


    def crear_usuario(nombre_usuario: str, contraseña_hash: str, nombre_completo: str = ""):
        """Inserta un nuevo usuario compatible con el sistema JWT."""
        with sqlite3.connect(RUTA_DB) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS usuarios (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE,
                    hashed_password TEXT,
                    full_name TEXT
                )
            """)
            cursor.execute("""
                INSERT INTO usuarios (username, hashed_password, full_name)
                VALUES (?, ?, ?)
            """, (nombre_usuario, contraseña_hash, nombre_completo))
            conn.commit()


    def buscar_usuario_por_nombre(nombre_usuario: str):
        """Busca un usuario por nombre de usuario y devuelve un diccionario."""
        with sqlite3.connect(RUTA_DB) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS usuarios (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE,
                    hashed_password TEXT,
                    full_name TEXT
                )
            """)
            cursor.execute("SELECT username, hashed_password, full_name FROM usuarios WHERE username = ?", (nombre_usuario,))
            fila = cursor.fetchone()
            if fila:
                return {"username": fila[0], "hashed_password": fila[1], "full_name": fila[2]}
            return None


    # ==============================
    # MÉTODOS DE USUARIOS
    # ==============================



    def guardar(self, usuario: User):
        """Guarda un usuario nuevo."""
        with sqlite3.connect(self.conexion) as conn:
            cursor = conn.cursor()
            try:
                cursor.execute("""
                    INSERT INTO usuarios (nombre, contraseña, email, tipo, telefono)
                    VALUES (?, ?, ?, ?, ?)
                """, (usuario.nombre, usuario.contraseña, usuario.email, usuario.tipo, usuario.telefono))
                conn.commit()
                return True
            except sqlite3.IntegrityError:
                return False

    def eliminar(self, id: str) -> bool:
        """Elimina un usuario y sus sesiones."""
        with sqlite3.connect(self.conexion) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM sesiones WHERE usuario_id = ?", (id,))
            cursor.execute("DELETE FROM usuarios WHERE id = ?", (id,))
            conn.commit()
            return cursor.rowcount > 0

    def consultar(self, campo: Optional[str] = None, valor: Optional[str] = None) -> List[User]:
        """Devuelve los usuarios, opcionalmente filtrados."""
        usuarios_encontrados = []

        with sqlite3.connect(self.conexion) as conn:
            cursor = conn.cursor()
            if campo and valor:
                if campo not in {"id", "tipo", "nombre", "contraseña", "email", "telefono"}:
                    raise ValueError(f"Campo no válido: {campo}")
                consulta = f"""
                    SELECT id, tipo, nombre, contraseña, email, telefono
                    FROM usuarios
                    WHERE {campo} = ?
                """
                cursor.execute(consulta, (valor,))
            else:
                cursor.execute("""
                    SELECT id, tipo, nombre, contraseña, email, telefono
                    FROM usuarios
                """)
            filas = cursor.fetchall()
            for fila in filas:
                usuario = User(
                    id=fila[0], tipo=fila[1], nombre=fila[2],
                    contraseña=fila[3], email=fila[4], telefono=fila[5]
                )
                usuarios_encontrados.append(usuario)
        return usuarios_encontrados

    def actualizar_campo(self, id_usuario: int, campo: str, valor) -> bool:
        """Actualiza un campo de un usuario."""
        campos_validos = {"tipo", "nombre", "contraseña", "email", "telefono"}
        if campo not in campos_validos:
            raise ValueError(f"Campo '{campo}' no válido")
        with sqlite3.connect(self.conexion) as conn:
            cursor = conn.cursor()
            consulta = f"UPDATE usuarios SET {campo} = ? WHERE id = ?"
            cursor.execute(consulta, (valor, id_usuario))
            conn.commit()
            return cursor.rowcount > 0

    def actualizar_completo(self, usuario: User) -> bool:
        """Actualiza todos los campos de un usuario."""
        campos_actualizados = 0
        if usuario.tipo and self.actualizar_campo(usuario.id, "tipo", usuario.tipo):
            campos_actualizados += 1
        if usuario.nombre and self.actualizar_campo(usuario.id, "nombre", usuario.nombre):
            campos_actualizados += 1
        if usuario.contraseña and self.actualizar_campo(usuario.id, "contraseña", usuario.contraseña):
            campos_actualizados += 1
        if usuario.email and self.actualizar_campo(usuario.id, "email", usuario.email):
            campos_actualizados += 1
        if usuario.telefono and self.actualizar_campo(usuario.id, "telefono", usuario.telefono):
            campos_actualizados += 1
        return campos_actualizados > 0



    # ==============================
    # MÉTODOS DE SESIONES
    # ==============================



    def guardar_sesion(self, sesion: Session) -> bool:
        """Guarda una sesión activa."""
        try:
            with sqlite3.connect(self.conexion) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO sesiones (token, usuario_id, fecha_inicio, fecha_expiracion)
                    VALUES (?, ?, ?, ?)
                """, (sesion.token, sesion.usuario_id, sesion.fecha_inicio, sesion.fecha_expiracion))
                conn.commit()
            return True
        except sqlite3.IntegrityError as e:
            print(f"Error al guardar sesión: {e}")
            return False

    def consultar_sesion(self, token: str) -> Optional[Session]:
        """Devuelve la sesión correspondiente al token."""
        with sqlite3.connect(self.conexion) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT token, usuario_id, fecha_inicio, fecha_expiracion
                FROM sesiones WHERE token = ?
            """, (token,))
            fila = cursor.fetchone()
            if fila:
                return Session(
                    token=fila[0],
                    usuario_id=fila[1],
                    fecha_inicio=fila[2],
                    fecha_expiracion=fila[3]
                )
            return None

    def eliminar_sesion(self, token: str) -> bool:
        """Elimina una sesión activa por su token."""
        with sqlite3.connect(self.conexion) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM sesiones WHERE token = ?", (token,))
            conn.commit()
            return cursor.rowcount > 0
