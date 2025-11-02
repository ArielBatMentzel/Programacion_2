from abc import ABC, abstractmethod

# Ingredient products
class Dough:    
    def __init__(self, name): self.name=name;  
    def __str__(self): return self.name
    
class Sauce:    
    def __init__(self, name): self.name=name;  
    def __str__(self): return self.name

class Cheese:   
    def __init__(self, name): self.name=name;  
    def __str__(self): return self.name

class Clams:    
    def __init__(self, name): self.name=name;  
    def __str__(self): return self.name

# #########################
# VEGETALES
class Veggie(ABC):
    @abstractmethod
    def __str__(self):
        ...
#concretas:
class Garlic(Veggie):
    def __str__(self): return "Garlic"

class Onion(Veggie):
    def __str__(self): return "Onion"

class Mushroom(Veggie):
    def __str__(self): return "Mushroom"

class RedPepper(Veggie):
    def __str__(self): return "Red Pepper"

class BlackOlives(Veggie):
    def __str__(self): return "Black Olives"

class Spinach(Veggie):
    def __str__(self): return "Spinach"

class Eggplant(Veggie):
    def __str__(self): return "Eggplant"

# Pepperoni
class Pepperoni(ABC):
    @abstractmethod
    def __str__(self):
        ...
class SlicedPepperoni(Pepperoni):
    def __str__(self): return "Sliced Pepperoni"

# Abstract Factory
class PizzaIngredientFactory(ABC):
    @abstractmethod
    def create_dough(self) -> Dough: ...
    @abstractmethod
    def create_sauce(self) -> Sauce: ...
    @abstractmethod
    def create_cheese(self) -> Cheese: ...
    @abstractmethod
    def create_clam(self) -> Clams: ...
    
    #2
    @abstractmethod
    def create_veggies(self) -> list[Veggie]: ...
    @abstractmethod
    def create_pepperoni(self) -> Pepperoni: ...

# Concrete factories
class NYPizzaIngredientFactory(PizzaIngredientFactory):
    def create_dough(self) -> Dough:
        return Dough("Thin Crust Dough")
    def create_sauce(self) -> Sauce:
        return Sauce("Marinara Sauce")
    def create_cheese(self) -> Cheese:
        return Cheese("Reggiano Cheese")
    def create_clam(self) -> Clams:
        return Clams("Fresh Clams")
    
    #3
    def create_veggies(self) -> list[Veggie]:
        return [Garlic(), Onion(), Mushroom(), RedPepper()]
    def create_pepperoni(self) -> Pepperoni:
        return SlicedPepperoni()

class ChicagoPizzaIngredientFactory(PizzaIngredientFactory):
    def create_dough(self) -> Dough:
        return Dough("Thick Crust Dough")
    def create_sauce(self) -> Sauce:
        return Sauce("Plum Tomato Sauce")
    def create_cheese(self) -> Cheese:
        return Cheese("Mozzarella Cheese")
    def create_clam(self) -> Clams:
        return Clams("Frozen Clams")
    
    #3
    def create_veggies(self) -> list[Veggie]:
        return [BlackOlives(), Spinach(), Eggplant()]
    def create_pepperoni(self) -> Pepperoni:
        return SlicedPepperoni()
