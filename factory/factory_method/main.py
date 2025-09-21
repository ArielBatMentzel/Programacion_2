from factory.factory_method.store import NYPizzaStore, ChicagoPizzaStore

def main():
    ny = NYPizzaStore(); chi = ChicagoPizzaStore()
    p1 = ny.order_pizza("cheese"); print("Ethan ordered:", p1)
    print('- Pedido Finalizado')
    p2 = chi.order_pizza("cheese"); print("Joel ordered:", p2)
    print('- Pedido Finalizado')
    
    print('-----------------')
    print('Testeos sobre las nuevas implementaciones')
    print('-----------------')
    print('--- Paso 1: Extendemos las tiendas para que implementen nuevos sabores de pizzas')
    p3 = ny.order_pizza("Veggie"); print("Samuel ordered:", p3)
    print('- Pedido Finalizado')
    p4 = chi.order_pizza("Veggie"); print("Samuel ordered:", p4)
    print('- Pedido Finalizado')
    p5 = ny.order_pizza("Pepperoni"); print("Samuel ordered:", p5)
    print('- Pedido Finalizado')
    
    print('--- Paso 2: ')
if __name__ == "__main__":
    main()
