class Alerta:
    """
    Observer (patrón Observer).
    Cada alerta observa al dólar y decide si la condición se cumple.
    """

    def __init__(self, usuario, instrumento, mensaje_ok, mensaje_alerta):
        self.usuario = usuario              # dict con los datos del usuario
        self.instrumento = instrumento      # PlazoFijo
        self.mensaje_ok = mensaje_ok
        self.mensaje_alerta = mensaje_alerta

    def update(self, subject, collect=False):
        """
        Consulta al Subject para obtener el valor del 
        dólar actual (modelo pull).
        """

        # 1) Intentamos primero con el subject, si no, usamos el del instrumento
        dolar_actual = subject.valor_dolar_actual
        if dolar_actual is None:
            dolar_actual = getattr(self.instrumento, "valor_dolar", None)

        datos = self.instrumento.rendimiento_vs_banda(
            monto_inicial=self.instrumento.monto_inicial,
            mes=None
        )

        if datos is None:
            return None

        dolar_equilibrio = datos["dolar_equilibrio"]

        # 2) Si falta info devolvemos mensaje "neutral"
        if dolar_actual is None or dolar_equilibrio is None:
            mensaje = "No se puede calcular alerta"
        else:
            mensaje = (
                self.mensaje_alerta
                if dolar_actual >= dolar_equilibrio
                else self.mensaje_ok
            )

        if collect:
            return {
                "mensaje": mensaje,
                "dolar_actual": dolar_actual,
                "dolar_equilibrio": dolar_equilibrio,
                "usuario": self.usuario['username'],
                "instrumento": self.instrumento.nombre
            }
        else:
            print(
                f"[NOTIFICACIÓN] Usuario {self.usuario['username']}: "
                f"{mensaje} | USD actual={dolar_actual}, equilibrio={dolar_equilibrio}"
            )
