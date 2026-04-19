# Smalltalk Infections

Infections come in two kinds:
- **Validators** (`poop/validators/`) — rejeitam código incompatível com Smalltalk; seguem o padrão `Validator` + `ast.NodeVisitor`.
- **Transformers** (`poop/transformers/`) — reescrevem o AST antes da execução para substituir construtos Python por equivalentes POOP; seguem o padrão `Transformer` + `ast.NodeTransformer`.

Pipeline: `parse → validate → transform → execute(namespace)`

## Princípios

- Em Smalltalk, **tudo é objeto** e toda operação é **passagem de mensagem**.
- Não existem estruturas de controle de fluxo — condicionais e iterações são mensagens enviadas a objetos.
- Não existem funções livres — todo comportamento vive em métodos de classes.
- **Representação**: todos os tipos POOP implementam `__str__` (e `__repr__` delega para ele) — mantém o modelo pythônico em vez de `printString` do Smalltalk. `Transcript.show` chama `str(obj)` internamente.

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

### No `print` — `poop/validators/no_print.py`

| Chamada | Motivo |
|---|---|
| `print(...)` | Saída padrão em Smalltalk é via `Transcript show:`; use `Transcript.show(obj)` |

## Tipos ativos

### Boolean — `poop/types/boolean.py`

`Boolean` (ABC) com subclasses privadas `_TrueClass` e `_FalseClass`. Singletons `true`/`false` internos, substituem `True`/`False` via transformer. Métodos Smalltalk implementados:

| Smalltalk | Python |
|---|---|
| `ifTrue:` / `ifFalse:` | `if_true(block)` / `if_false(block)` |
| `ifTrue:ifFalse:` / `ifFalse:ifTrue:` | `if_true_if_false(t, f)` / `if_false_if_true(f, t)` |
| `and:` / `or:` (lazy) | `and_(block)` / `or_(block)` |
| `not` / `xor:` / `eqv:` | `not_()` / `xor(other)` / `eqv(other)` |
| `&` / `\|` (eager) | `__and__(other)` / `__or__(other)` |

### Transcript — `poop/types/transcript.py`

Singleton `_TranscriptClass` injetado no namespace de execução como `Transcript`. Métodos:

| Smalltalk | Python |
|---|---|
| `Transcript show: obj` | `Transcript.show(obj)` — chama `str(obj)` |
| `Transcript nl` | `Transcript.nl()` — imprime linha vazia |

## Transformers ativos

### Boolean — `poop/transformers/boolean.py`

| Nó AST | Substituição | Motivo |
|---|---|---|
| `ast.Constant(value=True)` | `ast.Name(id="_poop_true")` | `True` passa a ser instância de `TrueClass` (estilo Smalltalk) |
| `ast.Constant(value=False)` | `ast.Name(id="_poop_false")` | `False` passa a ser instância de `FalseClass` (estilo Smalltalk) |

Os nomes `_poop_true` e `_poop_false` são injetados no namespace interno do executor — invisíveis para o código do usuário. `TrueClass` e `FalseClass` implementam os métodos Smalltalk (`ifTrue:`, `ifFalse:`, `and:`, `or:`, `not`, `xor:`, `eqv:`) em `poop/types/boolean.py`.

### TODO — operações que retornam booleano

As operações abaixo ainda retornam `bool` Python nativo. Futuramente devem retornar instâncias de `TrueClass`/`FalseClass`:

- Comparações: `==`, `!=`, `<`, `>`, `<=`, `>=`
- Operador `is` / `is not`
- Operador `not`
- Funções built-in: `isinstance`, `hasattr`, `callable`, etc.

## Backlog

### Próximas infecções (validators)
- **`try/except`** (`ast.Try`): Smalltalk trata erros com `on:do:` — candidato imediato.

### Próximos tipos
- **`Object`**: raiz de todos os tipos POOP; métodos universais `is_nil()`, `not_nil()`, `class_name()`, `responds_to(symbol)`, `__str__` e `__repr__`.
- **`NilClass`**: singleton `nil`; responde a `is_nil()` → `true`, `if_nil(block)`, `if_not_nil(block)`.
- **`SmallInt` / `Float`**: números com mensagens `times_repeat(block)`, `to_do(limit, block)`, `max(other)`, `min(other)`, `__str__`.
- **`StringObject`**: string com mensagens `size()`, `at(index)`, `includes(char)`, `reversed()`, `__str__`.
- **`OrderedCollection`**: substitui `list`; mensagens `do(block)`, `collect(block)`, `select(block)`, `reject(block)`, `detect(block)`, `inject_into(init, block)`, `add(obj)`, `size()`, `includes(obj)`.
- **`Interval`**: substitui `range`; mensagens `do(block)`, `collect(block)`, `select(block)`, `detect(block)`, `inject_into(init, block)`, `size()`.

### Próximos transformers
- Literais numéricos (`ast.Constant` int/float) → `SmallInt` / `Float`.
- Literais string (`ast.Constant` str) → `StringObject`.
- Literais lista (`ast.List`) → `OrderedCollection`.
- Comparações (`==`, `!=`, `<`, `>`, `<=`, `>=`), `is`/`is not` e `not` → retornar `TrueClass`/`FalseClass`.

### Exemplos de código
- Expandir `examples/` à medida que novas funcionalidades forem implementadas.

### CLI como entry point instalável
- Expor `poop` como comando de linha via `[project.scripts]` no `pyproject.toml`, permitindo `poop examples/hello_world.py` após `uv sync`.

## Decisões em aberto

- **Lambdas** (`ast.Lambda`): análogos aos blocos Smalltalk — provavelmente **permitidos**.
- **Compreensões** (`ast.ListComp`, `ast.SetComp`, `ast.DictComp`, `ast.GeneratorExp`): contêm iteração implícita — avaliar se devem ser banidas junto com loops.
- **Atribuição aumentada / múltipla**: avaliar consistência com o modelo de objetos.
