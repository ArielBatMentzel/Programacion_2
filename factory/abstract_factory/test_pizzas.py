import pytest
from factory.abstract_factory.store import (
    NYPizzaStore, 
    ChicagoPizzaStore 
    )
from factory.abstract_factory.pizza import (
    VeggiePizza, PepperoniPizza, 
    ClamPizza, CheesePizza
    )

# Paso 3
def test_pizzas_ny ():
    store = NYPizzaStore()
    pizza1 = store.order_pizza('veggie')
    assert isinstance(pizza1, VeggiePizza)
    
    pizza2 = store.order_pizza('Cheese')
    assert isinstance(pizza2, CheesePizza)
    
    pizza3 = store.order_pizza('Pepperoni')
    assert isinstance(pizza3, PepperoniPizza)
    
    pizza4 = store.order_pizza('Clam')
    assert isinstance(pizza4, ClamPizza)
    
    assert "NY Style" in pizza4.name

def test_pizzas_chi ():
    store = ChicagoPizzaStore()
    pizza1 = store.order_pizza('veggie')
    assert isinstance(pizza1, VeggiePizza)
    
    pizza2 = store.order_pizza('Cheese')
    assert isinstance(pizza2, CheesePizza)
    
    pizza3 = store.order_pizza('Pepperoni')
    assert isinstance(pizza3, PepperoniPizza)
    
    pizza4 = store.order_pizza('Clam')
    assert isinstance(pizza4, ClamPizza)
    
    assert "Chicago Style" in pizza4.name

def test_ingredients_ny_cheese():
    store = NYPizzaStore()
    pizza = store.order_pizza('Cheese')
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

def test_ingredients_chi_clam():
    store = ChicagoPizzaStore()
    pizza = store.order_pizza('clam')
    assert pizza.dough.name == "Thick Crust Dough"
    assert pizza.sauce.name == "Plum Tomato Sauce"
    assert pizza.cheese.name == "Mozzarella Cheese"
    assert pizza.clam.name == "Frozen Clams"
    

##### chicago clam, ingreddientes correctos
def test_chicago_clam_ingredients():
    store = ChicagoPizzaStore()
    pizza = store.order_pizza("clam")
    assert pizza.clam.name == "Frozen Clams"


'''

pytest .\factory\abstract_factory\test_pizzas.py -v


'''
