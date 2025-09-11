from .store import NYPizzaStore, ChicagoPizzaStore

def main():
    print("*"*20, "FACTORY_METHOD", "*"*25)
    ny = NYPizzaStore(); chi = ChicagoPizzaStore()
    p1 = ny.order_pizza("cheese"); print("Ethan ordered:", p1)
    print("*"*50)
    p2 = chi.order_pizza("cheese"); print("Joel ordered:", p2)

if __name__ == "__main__":
    main()
