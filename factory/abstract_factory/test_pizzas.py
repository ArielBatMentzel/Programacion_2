import pytest
from .store import NYPizzaStore, ChicagoPizzaStore
from .ingredients import Dough, Sauce, Cheese, Clams

####### que son pizzas del tipo correcto
def test_ny_style():
    store = NYPizzaStore()
    pizza = store.order_pizza("cheese")
    assert "NY Style" in pizza.name

def test_chicago_style():
    store = ChicagoPizzaStore()
    pizza = store.order_pizza("clam")
    assert "Chicago Style" in pizza.name

###### ny queso, ingredientes correctos
def test_ny_cheese_ingredients():
    store = NYPizzaStore()
    pizza = store.order_pizza("cheese")
    assert pizza.dough.name == "Thin Crust Dough"
    assert pizza.sauce.name == "Marinara Sauce"
    assert pizza.cheese.name == "Reggiano Cheese"


##### chicago clam, ingreddientes correctos
def test_chicago_clam_ingredients():
    store = ChicagoPizzaStore()
    pizza = store.order_pizza("clam")
    assert pizza.clam.name == "Frozen Clams"


'''

pytest .\factory\abstract_factory\test_pizzas.py -v


'''