# Decorator

## Como executar os exemplos

```bash
# exemplo utilizando arquivo
poetry run input_test
# exemplo da loja de pizzas
poetry run pizza_store
# exemplo da cafeteria
poetry run starbuzz_coffee
# exemplo da cafeteria com tamanhos
poetry run starbuzz_coffee_with_sizes
```

## Notas

O padrão decorator é utilizado para adicionar funcionalidades a classes.

Herança nominal é utilizada na implementação do padrão decorator. Estamos deefinindo classes abstratas que devem ser extendidas e seus respectivos métodos devem ser sobrescritos.

Os decoradores podem ser vistos nas classes `ToppingDecorator` e `CondimentDecorator`, que são classes que encapsulam outras classes adicionando alguma funcionalidade.

As classes envolvidas por um decorador, continuam se comportando como a classe que o decorador extende. Por exemplo `Mocha` e `Whip`, que são classes que encapsulam a classe Beverage, mas ainda se comportam como `Beverage`.
