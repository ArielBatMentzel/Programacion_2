# archivo: api/cotizar_api.py

"""
Módulo CotizarAPI
Se encarga de obtener datos financieros desde fuentes externas, actualizar la base de datos
y notificar cambios a los instrumentos registrados.
"""

from typing import List
from models.instruments import FixedIncomeInstrument
from Proyecto.db.instrumentos.instruments_db import DBInstruments
from models.dolar import Dolar

class CotizarAPI:
    """
    Clase que gestiona la conexión con APIs externas para obtener información de:
    - Bonos, letras, pases
    - Tasas de interés
    - Tipo de cambio y bandas cambiarias
    """

    def __init__(self, db: DBInstruments, dolar: Dolar):
        self.db = db          # Base de datos de instrumentos
        self.dolar = dolar    # Objeto Dolar para notificar cambios

    def obtener_datos(self, tipo: str) -> List[FixedIncomeInstrument]:
        """
        Obtiene datos desde la fuente externa según el tipo de instrumento.
        tipo: 'bono', 'letra', 'pase', etc.
        Devuelve una lista de instrumentos creados a partir de los datos obtenidos.
        """
        # Placeholder: implementación de la conexión a la API
        return []

    def calcular_rendimiento(self, instrumento: FixedIncomeInstrument) -> float:
        """
        Calcula el rendimiento estimado de un instrumento.
        """
        # Placeholder: llama a instrument.calculate() u otra lógica
        return instrumento.calculate()

    def notificar_cambios(self):
        """
        Notifica a todos los instrumentos registrados sobre cambios en el dólar.
        Llama al método actualizar() de cada instrumento.
        """
        for instrumento in self.db.obtener_todos():
            instrumento.actualizar(self.dolar.valor_actual)

    def consultar_bd(self, query: str):
        """
        Permite realizar consultas personalizadas a la base de datos de instrumentos.
        """
        return self.db.consultar(query)

    def guardar_datos(self, objeto: FixedIncomeInstrument):
        """
        Guarda o actualiza un instrumento en la base de datos.
        """
        self.db.guardar(objeto)

    def actualizar_precio_dolar(self):
        """
        Actualiza el valor del dólar desde la fuente externa y notifica cambios.
        """
        # Placeholder: obtener nuevo valor del dólar desde API
        nuevo_valor = 100.0  # ejemplo
        self.dolar.valor_actual = nuevo_valor
        self.notificar_cambios()
