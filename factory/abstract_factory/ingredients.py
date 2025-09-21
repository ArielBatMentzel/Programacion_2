from abc import ABC, abstractmethod

# Ingredient products
class Dough:    
    def __init__(self, name): 
        self.name=name;  
    
    def __str__(self): 
        return self.name
    
class Sauce:    
    def __init__(self, name): 
        self.name=name;  
        
    def __str__(self): 
        return self.name
    
class Cheese:   
    def __init__(self, name): 
        self.name=name
    
    def __str__(self): 
        return self.name
    
class Clams:    
    def __init__(self, name): 
        self.name=name
        
    def __str__(self): 
        return self.name

# 2.1
### Vegetables
class Veggie(ABC):
    def __str__(self): 
        ...

class Onion(Veggie):
    def __str__(self): 
        return "Onion"

class SweetPepper(Veggie):
    def __str__(self): 
        return "Sweet Pepper"

class Mushroom(Veggie):
    def __str__(self): 
        return "Mushroom"

class Basil(Veggie):
    def __str__(self): 
        return "Basil"

class Spinach(Veggie):
    def __str__(self): 
        return "Spinach"
    
### Pepperoni
class Pepperoni(ABC):
    def __str__(self): 
        ...
    
class SlicedPepperoni(Pepperoni):
    def __str__(self): 
        return "Sliced Pepperoni"
    

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
    
    # 2.2
    @abstractmethod
    def create_veggies() -> list[Veggie]:
        ...
    @abstractmethod
    def create_pepperoni() -> Pepperoni:
        ...

# Concrete factories
class NYPizzaIngredientFactory(PizzaIngredientFactory):
    def create_dough(self) -> Dough:  return Dough("Thin Crust Dough")
    def create_sauce(self) -> Sauce:  return Sauce("Marinara Sauce")
    def create_cheese(self) -> Cheese:return Cheese("Reggiano Cheese")
    def create_clam(self) -> Clams:   return Clams("Fresh Clams")
    
    # 2.3
    def create_veggies() -> list[Veggie]:
        return [Onion(), Basil(), SweetPepper()]
    
    def create_pepperoni() -> Pepperoni:
        return SlicedPepperoni()
    
class ChicagoPizzaIngredientFactory(PizzaIngredientFactory):
    def create_dough(self) -> Dough:  return Dough("Thick Crust Dough")
    def create_sauce(self) -> Sauce:  return Sauce("Plum Tomato Sauce")
    def create_cheese(self) -> Cheese:return Cheese("Mozzarella Cheese")
    def create_clam(self) -> Clams:   return Clams("Frozen Clams")
    
    # 2.3
    def create_veggies() -> list[Veggie]:
        return [Spinach(), Mushroom(), Onion()]  
    
    def create_pepperoni() -> Pepperoni:
        return SlicedPepperoni()
