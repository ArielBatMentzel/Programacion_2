# archivo: db/usuarios/users_db.py
from typing import Optional, List
from models.user import User, Session
from db.abstract_db import AbstractDatabase
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.conexion_db import crear_engine

engine = crear_engine()

class DataBaseUsuario(AbstractDatabase):
    """
    Maneja la persistencia de usuarios y sesiones.
    Hereda de AbstractDatabase y cumple la interfaz común.
    """

    def __init__(self):
        self.engine = engine
        self._crear_tablas()
    
    def _crear_tablas(self):
        """Crea las tablas, si no existen en Supabase"""
       
        with self.engine.begin() as conn:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS usuarios.usuarios (
                    id SERIAL PRIMARY KEY,
                    username TEXT UNIQUE,
                    hashed_password TEXT,
                    full_name TEXT,
                    tipo TEXT,
                    email TEXT UNIQUE,
                    telefono BIGINT
                )
            """))
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS usuarios.sesiones (
                    token TEXT PRIMARY KEY,
                    usuario_id INTEGER REFERENCES usuarios(id),
                    fecha_inicio TEXT,
                    fecha_expiracion TEXT
                )
            """))


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
        with self.engine.begin() as conn:
            conn.execute(text("""
                INSERT INTO usuarios.usuarios (username, hashed_password, full_name, tipo, email, telefono)
                VALUES (:username, :hashed_password, :full_name, :tipo, :email, :telefono)
            """), {
                "username": nombre_usuario,
                "hashed_password": contraseña_hash,
                "full_name": nombre_completo,
                "tipo": tipo,
                "email": email,
                "telefono": telefono
            })

    def buscar_usuario_por_nombre(self, nombre_usuario: str):
        """Busca un usuario por su nombre de usuario y devuelve un diccionario."""
        
        with self.engine.begin() as conn:
            fila = conn.execute(text("""
                SELECT username, hashed_password, full_name, tipo, email, telefono
                FROM usuarios.usuarios WHERE username = :username
            """), {"username": nombre_usuario}).mappings().first()
            return dict(fila) if fila else None

    def obtener_id_usuario(self, username: str) -> Optional[int]:
        """
        Devuelve el ID del usuario según su nombre.
        """
        with self.engine.begin() as conn:
            fila = conn.execute(text("SELECT id FROM usuarios.usuarios WHERE username = :username"),
                                {"username": username}).first()
            return fila[0] if fila else None


    # ==============================
    # MÉTODOS DE USUARIOS
    # ==============================


    def guardar(self, usuario: User):
        """Guarda un usuario nuevo desde modelo User."""
        try:
            with self.engine.begin() as conn:
                conn.execute(text("""
                    INSERT INTO usuarios.usuarios (username, hashed_password, full_name, tipo, email, telefono)
                    VALUES (:username, :hashed_password, :full_name, :tipo, :email, :telefono)
                """), {
                    "username": usuario.nombre,
                    "hashed_password": usuario.contraseña,
                    "full_name": usuario.nombre,
                    "tipo": usuario.tipo,
                    "email": usuario.email,
                    "telefono": usuario.telefono
                })
            return True
        except IntegrityError:
            return False

    def eliminar(self, id: int) -> bool:
        """Elimina un usuario y sus sesiones en base a su id."""
        with self.engine.begin() as conn:
            conn.execute(text("DELETE FROM usuarios.sesiones WHERE usuario_id = :id"), {"id": id})
            conn.execute(text("DELETE FROM usuarios.usuarios WHERE id = :id"), {"id": id})
        return True
    
    def consultar(self, campo: Optional[str] = None, valor: Optional[str] = None) -> List[User]:
        """Devuelve los usuarios, opcionalmente filtrados."""
        usuarios_encontrados = []
        with self.engine.begin() as conn:
            if campo and valor:
                if campo not in {"id", "username", "full_name", "tipo", "email", "telefono"}:
                    raise ValueError(f"Campo no válido: {campo}")
                consulta = text(f"SELECT id, username, full_name, tipo, email, telefono FROM usuarios.usuarios WHERE {campo} = :valor")
                filas = conn.execute(consulta, {"valor": valor}).mappings().all()
            else:
                filas = conn.execute(text("SELECT id, username, full_name, tipo, email, telefono FROM usuarios.usuarios")).mappings().all()
        for fila in filas:
            usuarios_encontrados.append(User(email=fila["email"], nombre=fila["full_name"], tipo=fila["tipo"]))
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
        with self.engine.begin() as conn:
            res = conn.execute(text(f"UPDATE usuarios.usuarios SET {campo} = :valor WHERE id = :id"),
                            {"valor": valor, "id": id_usuario})
            return res.rowcount > 0

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
            with self.engine.begin() as conn:
                conn.execute(
                    text("""
                        INSERT INTO usuarios.sesiones (token, usuario_id, fecha_inicio, fecha_expiracion)
                        VALUES (:token, :usuario_id, :fecha_inicio, :fecha_expiracion)
                    """),
                    {
                        "token": sesion.token,
                        "usuario_id": sesion.usuario_id,
                        "fecha_inicio": str(sesion.fecha_inicio),
                        "fecha_expiracion": str(sesion.fecha_expiracion)
                    }
                )
            return True
        except Exception as e:
            print(f"⚠️ Error al guardar sesión: {e}")
            return False

    def consultar_sesion(self, token: str) -> Optional[Session]:
        """Devuelve la sesión correspondiente al token."""
        with self.engine.connect() as conn:
            res = conn.execute(
                text("""
                    SELECT token, usuario_id, fecha_inicio, fecha_expiracion
                    FROM usuarios.sesiones
                    WHERE token = :token
                """),
                {"token": token}
            ).fetchone()
            if res:
                return Session(
                    token=res[0],
                    usuario_id=res[1],
                    fecha_inicio=res[2],
                    fecha_expiracion=res[3]
                )
            return None

    def eliminar_sesion(self, token: str) -> bool:
        """Elimina una sesión activa por su token."""
        with self.engine.begin() as conn:
            res = conn.execute(
                text("DELETE FROM usuarios.sesiones WHERE token = :token"),
                {"token": token}
            )
            return res.rowcount > 0
        
    def eliminar_sesion_por_usuario(self, nombre_usuario: str) -> bool:
        """Elimina la sesión activa de un usuario dado su nombre de usuario."""
        usuario_id = self.obtener_id_usuario(nombre_usuario)
        if not usuario_id:
            return False
        with self.engine.begin() as conn:
            res = conn.execute(
                text("DELETE FROM usuarios.sesiones WHERE usuario_id = :usuario_id"),
                {"usuario_id": usuario_id}
            )
            return res.rowcount > 0