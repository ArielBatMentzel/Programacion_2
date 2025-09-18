from .store import NYPizzaStore, ChicagoPizzaStore

def main():
    print("*" * 20, "FACTORY_METHOD", "*" * 25)

    ny = NYPizzaStore()
    chi = ChicagoPizzaStore()

    # NY pizzas
    print("\n--- New York Orders ---")
    pedidos =["cheese", "veggie", "pepperoni"]
    for orden in pedidos:
        pizza = ny.order_pizza(orden)
        print("Ethan ordered:", pizza)
        print("-" * 40)

    # Chicago pizzas
    print("\n--- Chicago Orders ---")
    pedidos = ["cheese", "veggie", "pepperoni"]
    for orden in pedidos :
        pizza = chi.order_pizza(orden)
        print("Joel ordered:", pizza)
        print("-" * 40)


if __name__ == "__main__":
    main()
