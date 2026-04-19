# Smalltalk Infections

Each infection is an AST validation that rejects Python constructs incompatible with Smalltalk's philosophy. New infections follow the same pattern: a `Validator` class in `poop/validators/`, registered in `DEFAULT_VALIDATORS`.

## Princípios

- Em Smalltalk, **tudo é objeto** e toda operação é **passagem de mensagem**.
- Não existem estruturas de controle de fluxo — condicionais e iterações são mensagens enviadas a objetos.
- Não existem funções livres — todo comportamento vive em métodos de classes.

## Infecções ativas

### No `if` — `poop/validators/no_if.py`

| Nó AST | Motivo |
|---|---|
| `ast.If` | `if/elif/else` são estruturas de controle; Smalltalk usa polimorfismo (`ifTrue:`, `ifFalse:`) |
| `ast.IfExp` | Expressão ternária `x if cond else y` — mesma razão |

### No loops — `poop/validators/no_loops.py`

| Nó AST | Motivo |
|---|---|
| `ast.For` | Iteração por índice/coleção; Smalltalk usa `do:`, `timesRepeat:`, recursão |
| `ast.While` | Loop condicional; Smalltalk usa `whileTrue:`, `whileFalse:` |
| `ast.AsyncFor` | Variante assíncrona do `for` |

### No free functions — `poop/validators/no_free_functions.py`

| Nó AST | Contexto | Motivo |
|---|---|---|
| `ast.FunctionDef` | fora de classe | Funções livres não existem em Smalltalk; todo comportamento é método |
| `ast.AsyncFunctionDef` | fora de classe | Variante assíncrona |

Funções dentro de classes (`class_depth > 0`) são permitidas como métodos.

## Decisões em aberto

- **Lambdas** (`ast.Lambda`): análogos aos blocos Smalltalk — provavelmente **permitidos**.
- **Compreensões** (`ast.ListComp`, `ast.SetComp`, `ast.DictComp`, `ast.GeneratorExp`): contêm iteração implícita — avaliar se devem ser banidas junto com loops.
- **`try/except`** (`ast.Try`): Smalltalk trata erros com `on:do:` — candidato a próxima infecção.
- **Atribuição aumentada / múltipla**: avaliar consistência com o modelo de objetos.
