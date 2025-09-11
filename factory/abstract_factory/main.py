from .store import NYPizzaStore, ChicagoPizzaStore

def main():
    ny = NYPizzaStore(); chi = ChicagoPizzaStore()
    print("*"*25, "ABSTRACT", "*"*25)
    ny.order_pizza("cheese")
    print("*"*50)
    chi.order_pizza("clam")

if __name__ == "__main__":
    main()
