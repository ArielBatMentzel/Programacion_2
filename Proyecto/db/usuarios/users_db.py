# archivo: db/usuarios/users_db.py

from typing import Optional, List
from models.user import User, Session
from db.abstract_db import AbstractDatabase
import sqlite3
from pathlib import Path

# Ruta hacia la base de datos
RUTA_DB = Path(__file__).resolve().parent.parent / "usuarios" / "usuarios.db"

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
                    username TEXT UNIQUE,
                    hashed_password TEXT,
                    full_name TEXT,
                    tipo TEXT,
                    email TEXT UNIQUE,
                    telefono INTEGER
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


    def crear_usuario(self, 
                      nombre_usuario: str, 
                      contraseña_hash: str, 
                      nombre_completo: str = "", 
                      tipo: str = "normal", 
                      email: Optional[str] = None, 
                      telefono: Optional[int] = None):
        """Inserta un nuevo usuario compatible con el sistema JWT."""
        
        with sqlite3.connect(self.conexion) as conn:
            
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO usuarios (username, hashed_password, full_name, tipo, email, telefono)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (nombre_usuario, contraseña_hash, nombre_completo, tipo, email, telefono))
            conn.commit()


    def buscar_usuario_por_nombre(self, nombre_usuario: str):
        """Busca un usuario por su nombre de usuario y devuelve un diccionario."""
        
        with sqlite3.connect(self.conexion) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT username, hashed_password, full_name, tipo, email, telefono
                FROM usuarios
                WHERE username = ?
            """, (nombre_usuario,))
            fila = cursor.fetchone()
            if fila:
                return {
                    "username": fila[0],
                    "hashed_password": fila[1],
                    "full_name": fila[2],
                    "tipo": fila[3],
                    "email": fila[4],
                    "telefono": fila[5]
                }
            return None

    def obtener_id_usuario(self, username: str) -> Optional[int]:
        """
        Devuelve el ID del usuario según su nombre.
        """
        with sqlite3.connect(self.conexion) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM usuarios WHERE username = ?", (username,))
            fila = cursor.fetchone()
            return fila[0] if fila else None

    # ==============================
    # MÉTODOS DE USUARIOS
    # ==============================



    def guardar(self, usuario: User):
        """Guarda un usuario nuevo desde modelo User."""
        
        with sqlite3.connect(self.conexion) as conn:
            cursor = conn.cursor()
            try:
                cursor.execute("""
                    INSERT INTO usuarios (username, hashed_password, full_name, tipo, email, telefono)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (usuario.nombre, usuario.contraseña, usuario.nombre, usuario.tipo, usuario.email, usuario.telefono))
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
                if campo not in {"id", "username", "full_name", "tipo", "email", "telefono"}:
                    raise ValueError(f"Campo no válido: {campo}")
                consulta = f"SELECT id, username, full_name, tipo, email, telefono FROM usuarios WHERE {campo} = ?"
                cursor.execute(consulta, (valor,))
            else:
                cursor.execute("SELECT id, username, full_name, tipo, email, telefono FROM usuarios")
            filas = cursor.fetchall()
            for fila in filas:
                usuario = User(
                    email=fila[4],
                    nombre=fila[2],
                    tipo=fila[3]
                )
                usuarios_encontrados.append(usuario)
        return usuarios_encontrados
    


    # ==============================
    # MÉTODOS DE ACTUALIZACIÓN DE USUARIOS
    # ==============================


    def actualizar_campo(self, id_usuario: int, campo: str, valor) -> bool:
        """
        Actualiza un único campo del usuario.
        :param id_usuario: id del usuario a modificar
        :param campo: nombre del campo a actualizar
        :param valor: nuevo valor
        :return: True si se actualizó correctamente
        """
        campos_validos = {"username", "hashed_password", "full_name", "tipo", "email", "telefono"}

        if campo not in campos_validos:
            raise ValueError(f"Campo '{campo}' no válido para actualización")

        with sqlite3.connect(self.conexion) as conn:
            cursor = conn.cursor()
            consulta = f"UPDATE usuarios SET {campo} = ? WHERE id = ?"
            cursor.execute(consulta, (valor, id_usuario))
            conn.commit()
            return cursor.rowcount > 0
        


    def actualizar_completo(self, usuario: User) -> bool:
        """
        Actualiza todos los campos de un usuario (solo los no None).
        :param usuario: instancia de User con id y valores nuevos
        """
        campos_actualizados = 0

        if usuario.nombre and self.actualizar_campo(usuario.id, "username", usuario.nombre):
            campos_actualizados += 1
        if usuario.email and self.actualizar_campo(usuario.id, "email", usuario.email):
            campos_actualizados += 1
        if usuario.tipo and self.actualizar_campo(usuario.id, "tipo", usuario.tipo):
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
        
    def eliminar_sesion_por_usuario(self, nombre_usuario: str) -> bool:
        """Elimina la sesión activa de un usuario dado su nombre de usuario."""
        usuario_id = self.obtener_id_usuario(nombre_usuario)
        if not usuario_id:
            return False
        with sqlite3.connect(self.conexion) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM sesiones WHERE usuario_id = ?", (usuario_id,))
            conn.commit()
            return cursor.rowcount > 0