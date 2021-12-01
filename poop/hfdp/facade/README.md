# Facade

## Como executar os exemplos

```bash
# exemplo home theater
poetry run home_theater
```

## Notas

O padrão de projeto Facade é um padrão de projeto que visa reduzir a complexidade de um sistema,
tornando-o mais simples de ser utilizado.

No exemplo do _home theater_ é criado uma fachada (HomeTheaterFacade) que contém todas as classes
que representam os componentes do sistema.

A interface (conjunto de métodos) exposta por esta classe é muita mais simples do que toda a complexidade envolvida na interação dos componentes do sistema.

O método `watch_movie` é um exemplo de como a complexidade do sistema pode ser reduzida. Toda a complexidade da interação das várias classes (PopcornPooper, Amplifier, Screen etc) está encapsulada.
