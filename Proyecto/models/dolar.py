# archivo: Proyecto/models/dolar.py

import sqlite3
import requests
import os
import time
import threading
from typing import List
from models.instruments import FixedIncomeInstrument

# Ruta a la DB desde este archivo
DB_PATH = os.path.join(
    os.path.dirname(__file__), "..", "db", "datos_financieros",
    "datos_financieros.db"
)


class Dolar:
    """
    Modelo Dolar (Observer).

    - Carga valor inicial leyendo tabla `dolar` (columna venta).
    - Inserta fila compatible: tipo, compra, venta, variacion.
    - Monitorea cambios en la base automáticamente.
    """

    def __init__(self, valor_inicial: float = None,
                 tipo_por_defecto: str = "DÓLAR BLUE"):
        """
        Inicializa el modelo Dolar.

        :param valor_inicial: valor inicial del dólar (opcional)
        :param tipo_por_defecto: tipo de dólar por defecto
        """
        self.tipo_por_defecto = tipo_por_defecto
        self.valor_actual = valor_inicial or self._cargar_desde_db()
        self.observadores: List[FixedIncomeInstrument] = []
        self._monitoreo_activo = False

    # ======================
    # Observer
    # ======================

    def suscribir(self, instrumento: FixedIncomeInstrument):
        """
        Suscribe un instrumento para recibir notificaciones.

        :param instrumento: instancia de FixedIncomeInstrument
        """
        if instrumento not in self.observadores:
            self.observadores.append(instrumento)

    def desuscribir(self, instrumento: FixedIncomeInstrument):
        """
        Elimina un instrumento de la lista de observadores.

        :param instrumento: instancia de FixedIncomeInstrument
        """
        if instrumento in self.observadores:
            self.observadores.remove(instrumento)

    # ======================
    # Actualización manual
    # ======================

    def actualizar_valor(self, nuevo_valor: float, tipo: str = None):
        """
        Actualiza el valor del dólar y notifica observadores.

        :param nuevo_valor: nuevo valor del dólar
        :param tipo: tipo de dólar (opcional)
        """
        tipo = tipo or self.tipo_por_defecto
        self.valor_actual = nuevo_valor
        try:
            self._guardar_en_db(nuevo_valor, tipo)
        except Exception as e:
            print(f"⚠️ Error guardando dólar en DB: {e}")
        self._notificar_observadores()

    def _notificar_observadores(self):
        """
        Notifica a todos los instrumentos suscritos sobre el cambio.
        """
        for instrumento in self.observadores:
            try:
                instrumento.actualizar(self.valor_actual)
            except Exception as e:
                nombre_instr = getattr(instrumento, "nombre", instrumento)
                print(f"⚠️ Error al notificar {nombre_instr}: {e}")

    # ======================
    # Lectura desde DB
    # ======================

    def _cargar_desde_db(self) -> float:
        """
        Carga el último valor del dólar desde la base de datos.

        :return: valor del dólar, 0.0 si no se encuentra
        """
        try:
            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()
            cur.execute(
                "SELECT venta FROM dolar WHERE tipo = ? ORDER BY id DESC "
                "LIMIT 1",
                (self.tipo_por_defecto,)
            )
            row = cur.fetchone()
            if not row:
                cur.execute(
                    "SELECT venta FROM dolar ORDER BY id DESC LIMIT 1"
                )
                row = cur.fetchone()
            conn.close()
            return float(row[0]) if row and row[0] is not None else 0.0
        except Exception:
            return 0.0

    # ======================
    # Escritura en DB
    # ======================

    def _guardar_en_db(self, venta_valor: float, tipo: str):
        """
        Guarda un nuevo valor del dólar en la base de datos.

        :param venta_valor: valor de venta del dólar
        :param tipo: tipo de dólar
        """
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute(
            "CREATE TABLE IF NOT EXISTS dolar ("
            "id INTEGER PRIMARY KEY AUTOINCREMENT,"
            "tipo TEXT, compra REAL, venta REAL, variacion REAL)"
        )
        cur.execute(
            "INSERT INTO dolar (tipo, compra, venta, variacion) "
            "VALUES (?, ?, ?, ?)",
            (tipo, None, venta_valor, None)
        )
        conn.commit()
        conn.close()

    # ======================
    # Scraper opcional
    # ======================

    def actualizar_desde_api_ejemplo(self):
        """
        Obtiene el valor del dólar oficial desde un API de ejemplo
        y actualiza internamente.
        """
        try:
            url = "https://api.bluelytics.com.ar/v2/latest"
            resp = requests.get(url, timeout=10)
            data = resp.json()
            nuevo_valor = float(data["oficial"]["value_sell"])
            self.actualizar_valor(nuevo_valor, tipo="DÓLAR OFICIAL")
        except Exception as e:
            print(f"⚠️ No se pudo obtener dólar desde la API: {e}")

    # ======================
    # Monitoreo automático
    # ======================

    def iniciar_monitoreo(self, intervalo_segundos: int = 60):
        """
        Revisa periódicamente la base de datos y detecta cambios.

        :param intervalo_segundos: frecuencia de revisión en segundos
        """
        if self._monitoreo_activo:
            return
        self._monitoreo_activo = True

        def ciclo():
            print(f"🕒 Monitoreo dólar iniciado (cada {intervalo_segundos}s)")
            while self._monitoreo_activo:
                try:
                    nuevo_valor = self._cargar_desde_db()
                    if (nuevo_valor and abs(
                            nuevo_valor - self.valor_actual
                                            ) > 0.0001):

                        print(f"📈 Nuevo valor detectado en DB: {nuevo_valor}")
                        self.valor_actual = nuevo_valor
                        self._notificar_observadores()
                except Exception as e:
                    print(f"⚠️ Error durante monitoreo: {e}")
                time.sleep(intervalo_segundos)
            print("🛑 Monitoreo detenido.")

        hilo = threading.Thread(target=ciclo, daemon=True)
        hilo.start()

    def detener_monitoreo(self):
        """
        Detiene el hilo de monitoreo.
        """
        self._monitoreo_activo = False
