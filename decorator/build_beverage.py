from beverages import Espresso, DarkRoast, HouseBlend, Decaf
from condiments import Mocha, Whip, Soy, Caramel, Milk

CONDIMENTS = {
    "Mocha": Mocha,
    "Soy": Soy,
    "Whip": Whip,
    "Caramel": Caramel,
    "Milk": Milk
}

BEVERAGES = {
    "Espresso": Espresso,
    "DarkRoast": DarkRoast,
    "HouseBlend": HouseBlend,
    "Decaf": Decaf
}


def build_beverage(base: str, size: str, condiments: list[str]):
    '''
    Genera la bebida ya decorada
    '''
    
    if base not in BEVERAGES:
        raise ValueError(f"Bebida desconocida: {base}")
    beverage = BEVERAGES[base]()
    beverage.set_size(size)
    
    for condiment in condiments:
        if condiment not in CONDIMENTS:
            raise ValueError(f"Agregado desconocido: {condiment}")
        beverage = CONDIMENTS[condiment](beverage)
        
    return beverage