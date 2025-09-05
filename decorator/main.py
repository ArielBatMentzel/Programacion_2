# main.py
# Script principal para probar el patrón Decorator.

from beverages import Espresso, DarkRoast, HouseBlend, Decaf
from condiments import Mocha, Whip, Soy, Caramel, Milk
from build_beverage import build_beverage
from PrettyPrint import PrettyPrint

def main():
    """
    Función principal que simula la preparación de cafés en Starbuzz.
    """
    print("Bienvenido a Starbuzz Coffee!")
    print("--- Preparando pedidos ---")
        
    print("----- TP Nivel 1 -----")
    # Pedido 4: Un Decaf Grande con Caramel
    beverage4 = Decaf()
    beverage4.set_size('Grande')
    beverage4 = Caramel(beverage4)
    print(f"Pedido 4: {beverage4.get_description()} ${beverage4.cost():.2f}")
    # Pedido 5: Un Espresso con doble Caramelo
    beverage5 = Espresso()
    beverage5 = Caramel(beverage5)
    beverage5 = Caramel(beverage5)
    print(f"Pedido 5: {beverage5.get_description()} ${beverage5.cost():.2f}")
    
    print("----- TP Nivel 2 -----")    
    # Pedido 6: Un HouseBlend Tall con doble Soja
    beverage6 = HouseBlend()
    beverage6.set_size('Tall')
    beverage6 = Soy(beverage6)
    beverage6 = Soy(beverage6)
    print(f"Pedido 6: {beverage6.get_description()} ${beverage6.cost():.2f}")
    # Pedido 7: Un DarkRoast Venti con Soja, Caramelo, Crema, Leche y Mocha 
    beverage7 = DarkRoast()
    beverage7.set_size('Venti')
    beverage7 = Caramel(Soy(Milk(Whip((Mocha(beverage7))))))
    print(f"Pedido 7: {beverage7.get_description()} ${beverage7.cost():.2f}")
    
    print("----- TP Nivel 3 -----")    
    print("-------- Builder --------")    
    # Pedido 8: Un Espresso Tall con Crema y Mocha 
    beverage8 = build_beverage('Espresso', 'Tall', ['Whip', 'Mocha'])
    print(f"Pedido 8: {beverage8.get_description()} ${beverage8.cost():.2f}")
    print("-------- PrettyPrint --------")
    # Pedido 8: Un Espresso Tall con Crema y Mocha 
    beverage9 = build_beverage('Espresso', 'Tall', ['Whip', 'Mocha', 'Mocha'])
    beverage9 = PrettyPrint(beverage9)
    print(f"Pedido 8: {beverage9.get_description()} ${beverage9.cost():.2f}")
    # Pedido 9: Un Espresso Tall con Crema, Mocha y 2 de Caramelo
    beverage10 = build_beverage('Espresso', 'Tall', ['Whip', 'Mocha', 'Caramel', 'Caramel', 'Caramel', 'Caramel'])
    beverage10 = PrettyPrint(beverage10)
    print(f"Pedido 9: {beverage10.get_description()} ${beverage10.cost():.2f}")
    

if __name__ == "__main__":
    main()