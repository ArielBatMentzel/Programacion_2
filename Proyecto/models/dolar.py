# archivo: Proyecto/models/dolar.py
import sqlite3
import requests
import os
import time
import threading
from typing import List
from models.instruments import FixedIncomeInstrument

# Ruta absoluta/relativa a la DB desde este archivo
DB_PATH = os.path.join(os.path.dirname(__file__), "..", "db", "datos_financieros", "datos_financieros.db")


class Dolar:
    """
    Modelo Dolar (Observer).  
    - Carga valor inicial leyendo la tabla `dolar` (columna venta).  
    - Al actualizar, inserta una fila compatible con la estructura real:
      (tipo, compra, venta, variacion).
    - Puede monitorear la base de datos y detectar cambios automáticos.
    """

    def __init__(self, valor_inicial: float = None, tipo_por_defecto: str = "DÓLAR BLUE"):
        self.tipo_por_defecto = tipo_por_defecto
        self.valor_actual = valor_inicial if valor_inicial is not None else self._cargar_desde_db()
        self.observadores: List[FixedIncomeInstrument] = []
        self._monitoreo_activo = False

    # --- Observer ---
    def suscribir(self, instrumento: FixedIncomeInstrument):
        if instrumento not in self.observadores:
            self.observadores.append(instrumento)

    def desuscribir(self, instrumento: FixedIncomeInstrument):
        if instrumento in self.observadores:
            self.observadores.remove(instrumento)

    # --- Actualización manual ---
    def actualizar_valor(self, nuevo_valor: float, tipo: str = None):
        tipo = tipo or self.tipo_por_defecto
        self.valor_actual = nuevo_valor
        try:
            self._guardar_en_db(nuevo_valor, tipo)
        except Exception as e:
            print(f"⚠️ Error guardando dólar en DB: {e}")
        self._notificar_observadores()

    def _notificar_observadores(self):
        for instrumento in self.observadores:
            try:
                instrumento.actualizar(self.valor_actual)
            except Exception as e:
                print(f"⚠️ Error al notificar {getattr(instrumento, 'nombre', instrumento)}: {e}")

    # --- Lectura desde DB ---
    def _cargar_desde_db(self) -> float:
        try:
            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()
            cur.execute("""
                SELECT venta FROM dolar
                WHERE tipo = ?
                ORDER BY id DESC
                LIMIT 1
            """, (self.tipo_por_defecto,))
            row = cur.fetchone()
            if not row:
                cur.execute("SELECT venta FROM dolar ORDER BY id DESC LIMIT 1")
                row = cur.fetchone()
            conn.close()
            return float(row[0]) if row and row[0] is not None else 0.0
        except Exception:
            return 0.0

    # --- Escritura en DB ---
    def _guardar_en_db(self, venta_valor: float, tipo: str):
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS dolar (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tipo TEXT,
                compra REAL,
                venta REAL,
                variacion REAL
            )
        """)
        cur.execute(
            "INSERT INTO dolar (tipo, compra, venta, variacion) VALUES (?, ?, ?, ?)",
            (tipo, None, venta_valor, None)
        )
        conn.commit()
        conn.close()

    # --- Scraper opcional ---
    def actualizar_desde_api_ejemplo(self):
        try:
            url = "https://api.bluelytics.com.ar/v2/latest"
            resp = requests.get(url, timeout=10)
            data = resp.json()
            nuevo_valor = float(data["oficial"]["value_sell"])
            self.actualizar_valor(nuevo_valor, tipo="DÓLAR OFICIAL")
        except Exception as e:
            print(f"⚠️ No se pudo obtener dólar desde la API de ejemplo: {e}")

    # --- Monitoreo automático ---
    def iniciar_monitoreo(self, intervalo_segundos: int = 60):
        """
        Revisa periódicamente la base de datos y detecta si el valor cambió.
        Si hay cambio, actualiza internamente y notifica a los instrumentos.
        """
        if self._monitoreo_activo:
            return
        self._monitoreo_activo = True

        def ciclo():
            print(f"🕒 Monitoreo de dólar iniciado (cada {intervalo_segundos}s)")
            while self._monitoreo_activo:
                try:
                    nuevo_valor = self._cargar_desde_db()
                    if nuevo_valor and abs(nuevo_valor - self.valor_actual) > 0.0001:
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
        """Detiene el hilo de monitoreo."""
        self._monitoreo_activo = False
