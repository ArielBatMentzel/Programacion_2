class DolarSubject:
    """
    Subject (patrón Observer).
    Notifica a todas las alertas registradas cuando el dólar cambia.
    """

    def __init__(self):
        self.observers = []
        self.valor_dolar_actual = None

    def registrar(self, observer):
        """Registra un nuevo observer."""
        self.observers.append(observer)

    def desregistrar(self, observer):
        """Elimina un observer registrado."""
        self.observers.remove(observer)

    def set_valor_dolar(self, nuevo_valor):
        """
        Actualiza el valor del dólar y notifica 
        a los observers (modelo push).
        """
        self.valor_dolar_actual = nuevo_valor
        self.notify()

    def notify(self):
        """Notifica a todos los observers."""
        for observer in self.observers:
            observer.update(self)
