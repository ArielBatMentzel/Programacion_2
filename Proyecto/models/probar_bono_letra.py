import os
import sqlite3
import argparse
from datetime import date
from models.instruments import Bono, Letra
from utils.obtener_ultimo_valor_dolar import obtener_dolar_oficial
from utils.obtener_banda_cambiaria import obtener_banda_cambiaria

DB_PATH = os.path.join(
    os.path.dirname(
        __file__), "..", "db", "datos_financieros", "datos_financieros.db"
)


def _connect():
    return sqlite3.connect(DB_PATH)


def _to_float(val):
    if val is None:
        return None
    if isinstance(val, (int, float)):
        return float(val)
    if isinstance(val, str):
        v = val.strip().replace("%", "").replace(".", "").replace(",", ".")
        try:
            return float(v)
        except:
            return None
    return None


def _fetch_row(tabla: str, nombre: str):
    conn = _connect()
    cur = conn.cursor()
    cur.execute(
        f"""SELECT nombre, moneda, ultimo, dia_pct, mes_pct, anio_pct
            FROM {tabla} WHERE nombre = ? LIMIT 1""",
        (nombre,),
    )
    row = cur.fetchone()
    conn.close()
    return row


def _print_dict(titulo: str, data: dict):
    print(f"{titulo}:")
    if not data:
        print("  (sin datos)")
        return
    for k, v in data.items():
        print(f"  {k}: {v}")


def probar_bonos(nombres: list, monto_inicial: float, mes_banda: str, dias_bono: int):
    if not nombres:
        return
    dolar = obtener_dolar_oficial()
    print(f"\nDólar oficial usado: {dolar if dolar else 'No disponible'}")
    for n in nombres:
        row = _fetch_row("bonos", n)
        if not row:
            print(f"[BONO] {n}: no encontrado en BD")
            continue
        nombre, moneda, ultimo, dia_pct, mes_pct, anio_pct = row
        bono = Bono(
            nombre,
            moneda,
            ultimo,
            dia_pct,
            mes_pct,
            anio_pct,
        )
        print(f"\n== BONO {nombre} ==")
        print("Row BD:", row)
        rend = bono.calcular_rendimiento(
            monto_inicial, tipo_cambio_actual=dolar)
        _print_dict("Rendimiento", rend)

        # ✅ usar los parámetros de la función (NO 'args')
        rb = bono.rendimiento_vs_banda(
            monto_inicial=monto_inicial,
            mes=mes_banda,          # mes de arranque (YYYY-MM)
            dias=dias_bono          # días que ingresó la persona
        )
        _print_dict(f"Vs banda {rb['mes_banda_usado']}", rb)


def probar_letras(nombres: list, monto_inicial: float, mes_banda: str, dias_default: int, valor_nominal: float):
    if not nombres:
        return
    for n in nombres:
        row = _fetch_row("letras", n)
        if not row:
            print(f"[LETRA] {n}: no encontrada en BD")
            continue
        nombre, moneda, ultimo, dia_pct, mes_pct, anio_pct = row
        letra = Letra(
            nombre,
            moneda,
            precio_actual=ultimo,
            dias_al_vencimiento=dias_default,
            valor_nominal=valor_nominal,
        )
        print(f"\n== LETRA {nombre} ==")
        print("Row BD:", row)
        rend = letra.calcular_rendimiento(monto_inicial)
        _print_dict("Rendimiento", rend)
        rb = letra.rendimiento_vs_banda(monto_inicial, mes=mes_banda)
        _print_dict(f"Vs banda {mes_banda}", rb)


def validar_mes(mes: str):
    # formato yyyy-mm
    try:
        year, month = mes.split("-")
        if len(year) == 4 and len(month) == 2 and 1 <= int(month) <= 12:
            return mes
    except:
        pass
    return date.today().strftime("%Y-%m")


def main():
    parser = argparse.ArgumentParser(description="Probar bonos y letras.")
    parser.add_argument(
        "--bonos", help="Nombres de bonos separados por coma (ej: GD30D,AL30D)")
    parser.add_argument(
        "--letras", help="Nombres de letras separados por coma (ej: LELITENOV)")
    parser.add_argument("--monto", type=float, default=1000,
                        help="Monto inicial en la moneda del instrumento")
    parser.add_argument(
        "--mes", default=date.today().strftime("%Y-%m"), help="Mes banda yyyy-mm")
    parser.add_argument("--dias_letra", type=int, default=30,
                        help="Días al vencimiento para letras si aplica")
    parser.add_argument("--vn_letra", type=float, default=100,
                        help="Valor nominal supuesto para letras")
    parser.add_argument("--dias_bono", type=int, default=30,
                        help="Días a mantener los bonos (p.ej. 90, 120, 130)")

    args = parser.parse_args()

    mes_banda = validar_mes(args.mes)
    piso, techo = obtener_banda_cambiaria(mes_banda)
    print(f"Mes banda: {mes_banda} | Piso: {piso} | Techo: {techo}")

    bonos = [b.strip() for b in args.bonos.split(",")] if args.bonos else []
    letras = [l.strip() for l in args.letras.split(",")] if args.letras else []

    if not bonos and not letras:
        print("Indicar --bonos y/o --letras.")
        return

    probar_bonos(bonos, args.monto, mes_banda, args.dias_bono)
    probar_letras(letras, args.monto, mes_banda,
                  args.dias_letra, args.vn_letra)


if __name__ == "__main__":
    main()
