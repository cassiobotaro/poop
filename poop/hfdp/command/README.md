# Command

## Como executar os exemplos

```bash
# exemplo de pedido de um jantar
poetry run diner
# exemplo de pedido de um jantar utilizando lambdas
poetry run diner_lambda
# exemplo de um controle remoto de festa
poetry run party
# exemplo de um controle remoto
poetry run remote
# exemplo de um controle remoto utilizando lambdas
poetry run remote_wl
# exemplo de um controle remoto simples
poetry run simpleremote
# exemplo de um controle remoto simples utilizando lambdas
poetry run simpleremote_wl
# exemplo de comando em interface gráfica
poetry run tkinter_command
# exemplo de controle remoto com opção de desfazer o comando
poetry run undo
```

## Notas

O padrão command serve para desacoplar o processo de execução de um comando de seu contexto.

No exemplo da interface gráfica (tkinter), o padrão command é utilizado para desacoplar quem executa o comando (botões) de quem sabe como executar o comando (luzes).

Não é necessário heranças pois estamos utilizando tipagem estrutural implícita (Protocols).

Os exemplos reescritos utilizando lambdas são mais simples. Trocamos a utilização de protocols por simples funções.

Os objetos que invocam os comandos não possuem conhecimento sobre aqueles que realmente executam ações.

No exemplo do jantar(diner), a garçonete (waitress) é responsável por executar o comando, porém não conhece o cozinheiro (cook) que é quem realiza a ação.

`Callable[[], None]` pode ser satisfeito por uma função ou método sem parametros e sem retorno.

`MacroCommand` agrupa uma série de comandos a serem executados.

O padrão `Command` pode ter uma interface com apenas a opção de execução `execute` ou também com a opção de desfazer um comando `redo`.

Quando implementamos o padrão utilizando `Callable` ao invés de `Protocol`, não temos a opção de desfazer o comando, embora o código se torne mais simples.

`NoCommand` é um comando que não faz nada, é implementação de um outro padrão chama [null object](https://en.wikipedia.org/wiki/Null_object_pattern).
