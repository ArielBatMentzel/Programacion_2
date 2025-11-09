from factory.abstract_factory.store import NYPizzaStore, ChicagoPizzaStore

def main():
    ny = NYPizzaStore(); chi = ChicagoPizzaStore()
    ny.order_pizza("cheese")
    chi.order_pizza("clam")

if __name__ == "__main__":
    main()
from .store import NYPizzaStore, ChicagoPizzaStore

def main():
    print("*"*25, "ABSTRACT FACTORY", "*"*25)
    ny = NYPizzaStore()
    chi = ChicagoPizzaStore()

# NY
    print("\n--- New York Orders ---")
    for kind in ["cheese", "clam", "veggie", "pepperoni"]:
        pizza = ny.order_pizza(kind)
        print("Ethan ordered:", pizza)
        print("-"*40)

# Chicago
    print("\n--- Chicago Orders ---")
    for kind in ["cheese", "clam", "veggie", "pepperoni"]:
        pizza = chi.order_pizza(kind)
        print("Joel ordered:", pizza)
        print("-"*40)

if __name__ == "__main__":
    main()

'''

python -m factory.abstract_factory.main

'''
