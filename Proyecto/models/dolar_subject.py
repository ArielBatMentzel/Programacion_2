# archivo: Proyecto/models/dolar.py
class DolarSubject:
    """
    Subject del patrón Observer.
    Notifica a todas las alertas registradas cuando el dólar cambia.
    """

    def __init__(self):
        self.observers = []
        self.valor_dolar_actual = None

    def registrar(self, observer):
        self.observers.append(observer)

    def desregistrar(self, observer):
        self.observers.remove(observer)

    def set_valor_dolar(self, nuevo_valor):
        """
        Actualiza el dólar y notifica a los observers.
        """
        self.valor_dolar_actual = nuevo_valor
        self.notify()

    def notify(self):
        for observer in self.observers:
            observer.update(self)
