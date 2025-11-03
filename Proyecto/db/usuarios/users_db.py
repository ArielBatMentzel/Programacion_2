# archivo: db/users_db.py

from typing import Optional, List
from models.user import User, Session
from db.abstract_db import AbstractDatabase
import sqlite3

class DataBaseUsuario(AbstractDatabase):
    """
    DataBaseUsuario maneja la persistencia de usuarios y sesiones.
    Hereda de AbstractDatabase y cumple la interfaz común de las bases de datos.
    """

    def __init__(self, conexion: str):
        """
        Inicializa la base de datos de usuarios y crea las tablas usuarios y sesiones.
        :param conexion: string de conexión o path a archivo/base de datos
        """
        self.conexion = conexion
        self._crear_tablas()
        
    def _crear_tablas(self):
        """Crea las tablas, si es que no existen todavía."""
        with sqlite3.connect(self.conexion) as conn: # Permite hacer la conexion y cerrarla sola sin definirlo explícitamente
            cursor = conn.cursor() # Para ejecutar consultas
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS usuarios (
                    id  INTEGER PRIMARY KEY AUTOINCREMENT,
                    tipo TEXT NOT NULL,
                    nombre TEXT,
                    contraseña TEXT,
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

    def guardar(self, usuario: User):
        """
        Guarda un usuario en la base interna.
        :param usuario: instancia de User
        """
        with sqlite3.connect(self.conexion) as conn: 
            cursor = conn.cursor()
            try:
                cursor.execute("""
                    INSERT INTO usuarios (nombre, contraseña, email, tipo, telefono)
                    VALUES (?, ?, ?, ?, ?)
                """, (usuario.nombre, usuario.contraseña, usuario.email, usuario.tipo, usuario.telefono))
                conn.commit()
                return True  # Usuario agregado exitosamente
            except sqlite3.IntegrityError: 
                # Esto ocurre porque definimos "email" como Unique, entonces si lo volvemos a declarar se rompe y puede tomar otros errores también
                return False  # No se agregó, email ya existe
            

    def eliminar(self, id: str) -> bool:
        """
        Elimina un usuario de la base por su identificador y sus respectivas sesiones.
        :param id: identificador del usuario
        :return: True si se eliminó, False si no se encontró
        """
        with sqlite3.connect(self.conexion) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM sesiones WHERE usuario_id = ?", (id,))
            cursor.execute("DELETE FROM usuarios WHERE id = ?", (id,))
            conn.commit()
            return cursor.rowcount > 0  # .rowcount devuelve la cantidad de filas afectadas en la última operación    

    def consultar(self, campo: Optional[str] = None, valor: Optional[str] = None) -> List[User]:
        """
        Devuelve los usuarios almacenados, opcionalmente filtrados por un campo específico.
        :param campo: nombre del campo por el cual filtrar (por ejemplo 'email' o 'tipo')
        :param valor: valor del campo a buscar
        :return: lista de instancias User
        """
        usuarios_encontrados = []

        with sqlite3.connect(self.conexion) as conn:
            cursor = conn.cursor()

            if campo and valor:
                # Validamos que el campoe exista en la tabla
                if campo not in {"id", "tipo", "nombre", "contraseña", "email", "telefono"}:
                    raise ValueError(f"Campo no válido para filtrar: {campo}")

                consulta = f"""
                    SELECT id, tipo, nombre, contraseña, email, telefono
                    FROM usuarios
                    WHERE {campo} = ?
                """
                cursor.execute(consulta, (valor,))
            else:
                # Si no hay filtro, traer todos
                cursor.execute("""
                    SELECT id, tipo, nombre, contraseña, email, telefono
                    FROM usuarios
                """)

            filas = cursor.fetchall()

            for fila in filas:
                usuario = User(
                    id=fila[0],
                    tipo=fila[1],
                    nombre=fila[2],
                    contraseña=fila[3],
                    email=fila[4],
                    telefono=fila[5]
                )
                usuarios_encontrados.append(usuario)

        return usuarios_encontrados

    def actualizar_campo(self, id_usuario: int, campo: str, valor) -> bool:
        """
        Actualiza un único campo del usuario.
        :param id_usuario: id del usuario a modificar
        :param campo: nombre del campo a actualizar (por ejemplo 'email' o 'telefono')
        :param valor: nuevo valor para ese campo
        :return: True si se actualizó correctamente, False si no se encontró el usuario
        """
        campos_validos = {"tipo", "nombre", "contraseña", "email", "telefono"}

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
        Actualiza todos los campos de un usuario, usando actualizar_campo().
        Solo actualiza los campos que no sean None.
        :param usuario: instancia de User con el id y los nuevos valores
        :return: True si se actualizó al menos un campo, False si no se encontró o no se cambió nada
        """
        campos_actualizados = 0

        if usuario.tipo is not None:
            if self.actualizar_campo(usuario.id, "tipo", usuario.tipo):
                campos_actualizados += 1

        if usuario.nombre is not None:
            if self.actualizar_campo(usuario.id, "nombre", usuario.nombre):
                campos_actualizados += 1

        if usuario.contraseña is not None:
            if self.actualizar_campo(usuario.id, "contraseña", usuario.contraseña):
                campos_actualizados += 1

        if usuario.email is not None:
            if self.actualizar_campo(usuario.id, "email", usuario.email):
                campos_actualizados += 1

        if usuario.telefono is not None:
            if self.actualizar_campo(usuario.id, "telefono", usuario.telefono):
                campos_actualizados += 1

        return campos_actualizados > 0


    # Métodos específicos para sesiones
    def guardar_sesion(self, sesion: Session) -> bool:
        """
        Guarda una sesión activa en la base interna
        :param sesion: instancia de Session
        :return: True si se guardo, False si no se logro guardar
        """
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
        """
        Devuelve la sesión correspondiente al token dado
        :param token: token de la sesión
        :return: Objeto Session si se encontro, None si no
        """
        with sqlite3.connect(self.conexion) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT token, usuario_id, fecha_inicio, fecha_expiracion
                FROM sesiones
                WHERE token = ?
            """, (token,))
            fila = cursor.fetchone()

            if fila:
                return Session(
                    token=fila[0],
                    usuario_id=fila[1],
                    fecha_inicio=fila[2],
                    fecha_expiracion=fila[3]
                )
            else:
                return None

    def eliminar_sesion(self, token: str) -> bool:
        """
        Elimina una sesión activa por su token.
        :param token: token de la sesión
        :return: True si se eliminó, False si no se encontró
        """
        with sqlite3.connect(self.conexion) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM sesiones WHERE token = ?", (token,))
            conn.commit()
            return cursor.rowcount > 0
