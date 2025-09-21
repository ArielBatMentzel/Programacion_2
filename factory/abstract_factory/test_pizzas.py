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
    