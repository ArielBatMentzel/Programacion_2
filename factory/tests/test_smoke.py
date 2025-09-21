import pytest
from factory.factory_method.store import (
    NYPizzaStore as NYFMStore, 
    ChicagoPizzaStore as ChicagoFMStore
    )
from factory.abstract_factory.store import (
    NYPizzaStore as NYAFStore, 
    ChicagoPizzaStore as ChicagoAFStore
    )
from factory.factory_method.pizza import (
    NYStyleCheesePizza, NYStyleVeggiePizza, 
    NYStylePepperoniPizza, ChicagoStyleCheesePizza, 
    ChicagoStyleVeggiePizza, ChicagoStylePepperoniPizza
    )

@pytest.fixture
def ny_fm_store():
    return NYFMStore()

@pytest.fixture
def chi_fm_store():
    return ChicagoFMStore()

def test_imports():
    import factory.simple_factory.main as s
    import factory.factory_method.main as fm
    import factory.abstract_factory.main as af
    assert callable(s.main) and callable(fm.main) and callable(af.main), \
        "s.main, fm.main o af.main no son llamables"

def test_sabores(ny_fm_store, chi_fm_store):
    ny = ny_fm_store
    chi = chi_fm_store

    p1 = ny.order_pizza("cheese")
    assert isinstance(p1, NYStyleCheesePizza)

    p2 = chi.order_pizza("cheese")
    assert isinstance(p2, ChicagoStyleCheesePizza)

    # Nuevos sabores
    p3 = ny.order_pizza("veggie")
    assert isinstance(p3, NYStyleVeggiePizza)

    p4 = chi.order_pizza("veggie")
    assert isinstance(p4, ChicagoStyleVeggiePizza)

    p5 = ny.order_pizza("pepperoni")
    assert isinstance(p5, NYStylePepperoniPizza)
    
    p6 = chi.order_pizza("pepperoni")
    assert isinstance(p6, ChicagoStylePepperoniPizza)
    