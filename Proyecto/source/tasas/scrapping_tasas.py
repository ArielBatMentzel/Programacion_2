
import os
import sqlite3
import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime


class TasaManager:
    def __init__(self, db_path="Proyecto/db/tasas_database.db"):
        self.db_path = db_path
        self._crear_tabla()
        print("🔄 Actualizando tasas automáticamente al iniciar...")
        tasas = self.obtener_tasas_bna()
        self.guardar_tasas(tasas)



    # =============================
    # PARTE 1 — BASE DE DATOS
    # =============================



    def _crear_tabla(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasas_bna (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha TEXT,
            hora TEXT,
            tna REAL,
            tea REAL,
            tem REAL
        )
        """)
        conn.commit()
        conn.close()



    # =============================
    # PARTE 2 — SCRAPING
    # =============================



    def _extraer_numero(self, texto):
        match = re.search(r"(\d+[\.,]?\d*)%", texto)
        return float(match.group(1).replace(",", ".")) if match else None

    def obtener_tasas_bna(self):
        """Extrae tasas desde la web del Banco Nación"""
        url = "https://www.bna.com.ar/Home/InformacionAlUsuarioFinanciero"
        response = requests.get(url)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        tasas = {"TNA": None, "TEA": None, "TEM": None}

        for li in soup.find_all("li"):
            texto = li.get_text(strip=True)
            if "T.N.A" in texto or "Tasa Nominal Anual" in texto:
                tasas["TNA"] = self._extraer_numero(texto)
            elif "T.E.A" in texto or "Tasa Efectiva Anual" in texto:
                tasas["TEA"] = self._extraer_numero(texto)
            elif "T.E.M" in texto or "Tasa Efectiva Mensual" in texto:
                tasas["TEM"] = self._extraer_numero(texto)

        return tasas



    # =============================
    # PARTE 3 — GUARDADO EN BASE
    # =============================



    def guardar_tasas(self, tasas):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        fecha = datetime.now().strftime("%Y-%m-%d")
        hora = datetime.now().strftime("%H:%M")

        cursor.execute("""
            INSERT INTO tasas_bna (fecha, hora, tna, tea, tem)
            VALUES (?, ?, ?, ?, ?)
        """, (fecha, hora, tasas["TNA"], tasas["TEA"], tasas["TEM"]))

        conn.commit()
        conn.close()
        print(f"💾 Tasas guardadas correctamente ({fecha} {hora})")



    # =============================
    # PARTE 4 — CONSULTA
    # =============================


    def obtener_ultima_tasa(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tasas_bna ORDER BY id DESC LIMIT 1")
        resultado = cursor.fetchone()
        conn.close()
        return resultado



# =============================
# USO PRÁCTICO
# =============================



if __name__ == "__main__":
    manager = TasaManager()
    tasas = manager.obtener_tasas_bna()
    manager.guardar_tasas(tasas)
