# Factory

## Como executar os exemplos

```bash
# exemplo fábrica simples
poetry run pizza_test_drive
# exemplo calendário
poetry run calendar_test_drive = "poop.hfdp.factory.challenge.calendar_test_drive:main"
# exemplo fábrica abstrata
poetry run pizza_af = "poop.hfdp.factory.pizzaaf.pizza_test_drive:main"
# exemplo método fábrica abstrato
poetry run pizza_fm = "poop.hfdp.factory.pizzafm.pizza_test_drive:main"
```

## Notas

O Abstract Factory é um padrão de projeto criacional que permite que você produza famílias de objetos relacionados sem ter que especificar suas classes concretas.

Nos exemplos foi utilizado tipagem nomimal (herança simples) para representar o padrão fábrica.

No exemplo de método fábrica (pizza_fm), a classe deve ser extendida e seus métodos devem ser implementados. O método fábrica `create_pizza` é uma método fábrica, para uma determinada família de pizzas.

No exemplo da fábrica abstrata, temos um conjunto de métodos que devem ser implementados para criar uma família de itens relacionados. Um exemplo é fábrica de ingredientes (ingredient_factory) que possui um método para cada item (dough, sauce, cheese, veggies etc).

Um problema que pode ser reparado na implementação da fábrica abstrata é que se eu adicionar um novo ingrediente, eu preciso alterar todas as classes adicionando o novo ingrediente.

No exemplo da fábrica abstrata a classe PizzaStore tem um método fábrica que é implementado utilizando uma abstração da fábrica de ingredientes (por exemplo NYPizzaIngredientStore) que está abstraído em uma fábrica abstrata 🤯.
