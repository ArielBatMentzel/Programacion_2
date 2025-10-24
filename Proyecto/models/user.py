# archivo: models/user.py

from datetime import datetime
from typing import Optional

class User:
    """
    Representa un usuario del sistema.
    Atributos:
        - tipo: 'admin' o 'normal'
        - email: correo electrónico del usuario
        - nombre: nombre del usuario
        - otros atributos opcionales según necesidad
    """

    def __init__(self, email: str, nombre: str, tipo: str = "normal"):
        self.email = email
        self.nombre = nombre
        self.tipo = tipo

    def solicitar_datos(self):
        """
        Método para que el usuario solicite datos desde la API o DB.
        """
        pass

    def consultar_instrumentos(self):
        """
        Permite al usuario consultar instrumentos financieros.
        """
        pass

class Session:
    """
    Representa una sesión activa de un usuario.
    Atributos:
        - token: identificador único de la sesión
        - usuario: instancia de User
        - fecha_expiracion: datetime de expiración de la sesión
    """

    def __init__(self, token: str, usuario: User, fecha_expiracion: datetime):
        self.token = token
        self.usuario = usuario
        self.fecha_expiracion = fecha_expiracion


"""
Sí, en este caso conviene que User y Session estén en el mismo archivo user.py, porque están 
íntimamente relacionados:

- Session no tiene sentido sin un User al que pertenezca.

- Facilita importar y mantener el código.

- Mantiene la consistencia con la estructura de modelos (models/).

Solo separarías en archivos distintos si alguno de los dos fuera muy grande o complejo, 
lo cual no aplica aquí.
"""