# archivo: Proyecto/main.py
"""
Este script actúa como una PRUEBA INTEGRAL del funcionamiento del sistema de inversión.

Qué se prueba:
1. **Conexión con la base de datos:** Se obtiene el último valor del dólar almacenado.
2. **Patrón Observer:** Se crea un objeto `Dolar` (observado) y se suscriben dos instrumentos
   financieros (`PlazoFijo` y `Bono`) que reaccionarán automáticamente ante cambios del dólar.
3. **Factory Pattern:** Los instrumentos se crean mediante la `FixedIncomeInstrumentFactory`,
   verificando que el diseño de creación funciona correctamente.
4. **Actualización del dólar:** Se simula un aumento del 2% en su valor y se notifica a los
   instrumentos suscriptos.
5. **Cálculo de rendimientos:** Se calcula y muestra el rendimiento actualizado de cada instrumento
   tras la variación del dólar, verificando que los métodos de cálculo funcionen correctamente.

En resumen, este archivo demuestra la integración de los principales módulos del proyecto:
base de datos, modelo del dólar, instrumentos financieros, patrón Observer y Factory.
"""

import sqlite3
import os
from factory.fixed_income_factory import FixedIncomeInstrumentFactory
from models.dolar import Dolar

DB_PATH = os.path.join(os.path.dirname(__file__), "db", "datos_financieros", "datos_financieros.db")


def obtener_ultimo_valor_dolar(tipo="DÓLAR BLUE"):
    """
    Devuelve el último valor de venta del dólar para el tipo indicado.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT venta 
        FROM dolar 
        WHERE tipo = ? 
        ORDER BY id DESC 
        LIMIT 1
    """, (tipo,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return float(row[0])
    else:
        raise ValueError(f"No se encontró el valor del dólar para el tipo '{tipo}'.")


def main():
    valor_dolar = obtener_ultimo_valor_dolar("DÓLAR BLUE")
    print(f"💵 Valor inicial del dólar: {valor_dolar}")

    # Crear instancia del dólar (observado)
    dolar = Dolar(valor_inicial=valor_dolar)

    # Crear la factory
    factory = FixedIncomeInstrumentFactory()

    # Crear instrumentos de prueba desde la factory
    plazo_fijo = factory.crear_instrumento(
        tipo="plazo_fijo",
        nombre="PF_30_dias",
        moneda="ARS",
        dias=30,
        tasa_tna=110.0
    )

    bono = factory.crear_instrumento(
        tipo="bono",
        nombre="Bono_T2X5",
        moneda="USD",
        ultimo=95.0,
        mes_pct=2.5,
        anio_pct=25.0
    )

    # Suscribimos los instrumentos al dólar
    dolar.suscribir(plazo_fijo)
    dolar.suscribir(bono)

    # Simular un cambio en el valor del dólar
    nuevo_valor_dolar = valor_dolar * 1.02
    print(f"\n📈 Actualizando valor del dólar a {nuevo_valor_dolar} ...\n")
    dolar.actualizar_valor(nuevo_valor_dolar)

    # Calcular rendimientos para verificar el funcionamiento
    print("Rendimiento Plazo Fijo:")
    print(plazo_fijo.calcular_rendimiento(100000, nuevo_valor_dolar))

    print("\nRendimiento Bono:")
    print(bono.calcular_rendimiento(100000, nuevo_valor_dolar))



if __name__ == "__main__":
    main()