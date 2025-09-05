from beverages import Beverage
from condiments import Mocha, Whip, Soy, Caramel, Milk

QUANTITY = {
    2: 'Doble',
    3: 'Triple'
}


class PrettyPrint(Beverage):
    def __init__(self, beverage: Beverage):
        self.description = beverage.get_description()
        self._beverage = beverage
    
    def get_description(self) -> str:
        """
        Devuelve la descripción formateada de la bebida.
        """
        descp = ''
        list_descp = self.description.split()
        CONDIMENTS = { 'Mocha': 0,
              'Crema': 0,
              'Soja': 0, 
              'Caramelo': 0,
              'Leche': 0
              }
    
        for elemento in list_descp:
            elemento = elemento.replace(',', '')
            if elemento in CONDIMENTS:
                CONDIMENTS[elemento] += 1
        
        for elemento in CONDIMENTS: 
            if CONDIMENTS[elemento] == 1:
                descp += ', ' + elemento
            elif 1 < CONDIMENTS[elemento] <= 3:
                descp += ', ' + QUANTITY[CONDIMENTS[elemento]] + ' ' + elemento
            elif CONDIMENTS[elemento] > 3:
                descp += ', X' + str(CONDIMENTS[elemento]) + ' ' + elemento
        
        return self._beverage.get_base() + descp
    
    def cost(self) -> float:
        return self._beverage.cost()