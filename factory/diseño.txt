
Decisiones de diseño – Paso 1

1. **Uso de Factory Method por tienda**

   * Cada `PizzaStore` (NY y Chicago) es responsable de crear sus propias pizzas, evitando dependencias de una fábrica externa.

2. **Clases de pizza por región**

   * Se definieron clases concretas (`NYStyleVeggiePizza`, `ChicagoStylePepperoniPizza`, etc.) para reflejar diferencias de ingredientes y estilo de corte.

3. **Extensibilidad y mantenimiento**

   * Se mantiene abierto a nuevas variedades de pizza: agregar un tipo adicional solo requiere crear la clase correspondiente y actualizar `create_pizza` en la tienda.

4. **Separación de responsabilidades**

   * `order_pizza` gestiona el flujo de preparación (`prepare`, `bake`, `cut`, `box`).
   * `create_pizza` gestiona únicamente la creación de instancias concretas.



### Decisiones de diseño – Paso 2 (Abstract Factory)

* **Separación de responsabilidades:** 
    Las pizzas no crean ingredientes, los obtienen de una fábrica, cumpliendo **DIP**.

* **Extensibilidad:** 
    Se agregan métodos abstractos para nuevos ingredientes (`create_veggies`, `create_pepperoni`), permitiendo añadir pizzas sin modificar clases existentes (**OCP**).

* **Consistencia regional:** 
    Cada fábrica concreta (`NY` o `Chicago`) devuelve los ingredientes específicos de su región.

* **Reutilización:** 
    El método `prepare()` es genérico y reutiliza la fábrica de ingredientes para todas las pizzas.

* **Flexibilidad futura:** 
    Nuevos tipos de pizza o regiones se pueden agregar implementando nuevas fábricas y clases de pizza.
