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
- **`__slots__` em todos os tipos POOP**: variáveis de instância em Smalltalk são declaradas na definição da classe e fixas — nunca adicionadas dinamicamente a instâncias. `__slots__` reflete isso: previne atributos arbitrários em instâncias e reduz consumo de memória. Extensão de *métodos* em runtime (open classes) continua funcionando normalmente, pois `__slots__` não afeta atributos de classe. Subclasses que precisarem de novas variáveis de instância podem declarar seus próprios `__slots__` ou omiti-los (ganhando `__dict__` próprio).

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

### No `try` — `poop/validators/no_try.py`

| Nó AST | Motivo |
|---|---|
| `ast.Try` | `try/except/finally` são estruturas de controle; Smalltalk usa `on:do:` |
| `ast.TryStar` | Variante `try/except*` (exception groups) |

### No `not` — `poop/validators/no_not.py`

| Nó AST | Motivo |
|---|---|
| `ast.UnaryOp` com `ast.Not` | `not x` é estrutura de controle; use `x.not_()` |

### No unary minus — `poop/validators/no_unary_minus.py`

| Nó AST | Condição | Motivo |
|---|---|---|
| `ast.UnaryOp` com `ast.USub` | operando não é `ast.Constant` | `-x` não existe em Smalltalk; use `x.negated()` |

Literais negativos (`-1`, `-3.14`) são permitidos — apenas `-variavel` e `-expressao` são bloqueados.

### No bitwise invert — `poop/validators/no_invert.py`

| Nó AST | Motivo |
|---|---|
| `ast.UnaryOp` com `ast.Invert` | `~x` não existe em Smalltalk; use `x.bit_invert()` |

## Tipos ativos

### Object — `poop/types/object.py`

Raiz concreta de todos os tipos POOP. Fornece implementações default para métodos universais:

| Smalltalk | Python | Comportamento |
|---|---|---|
| `isNil` | `is_none()` | sempre `false` para Object |
| `notNil` | `not_none()` | sempre `true` para Object |
| `not` | `not_()` | `false if bool(self) else true` |
| `class` | `class_name()` | `type(self).__name__` |
| `respondsTo:` | `responds_to(symbol)` | `hasattr` como base |

`__str__` retorna `"<ClassName>"` como fallback; `__repr__` delega para `__str__`.

### NoneClass — `poop/types/none.py`

`NoneClass(Object)` com singleton `none`. Transformer reescreve `ast.Constant(value=None)` → `_poop_none`. Sobrescreve `is_none`/`not_none` de `Object`:

| Método | `Object` | `NoneClass` |
|---|---|---|
| `is_none()` | `false` | `true` |
| `not_none()` | `true` | `false` |

`__bool__` retorna `False` (falsy, como `None` em Python). `__str__` retorna `"None"`.

### Boolean — `poop/types/boolean.py`

`Boolean(Object, ABC)` com subclasses privadas `_TrueClass` e `_FalseClass`. Herda `is_nil`, `not_nil` de `Object`. Singletons `true`/`false` internos, substituem `True`/`False` via transformer. Métodos Smalltalk implementados:

| Smalltalk | Python |
|---|---|
| `ifTrue:` / `ifFalse:` | `if_true(block)` / `if_false(block)` |
| `ifTrue:ifFalse:` / `ifFalse:ifTrue:` | `if_true_if_false(t, f)` / `if_false_if_true(f, t)` |
| `and:` / `or:` (lazy) | `and_(block)` / `or_(block)` |
| `not` / `xor:` / `eqv:` | `not_()` / `xor(other)` / `eqv(other)` |
| `&` / `\|` (eager) | `__and__(other)` / `__or__(other)` |

### Interval — `poop/types/interval.py`

`Interval(Object)` representa um intervalo inteiro fechado [start, stop]. Criado via `Int.to_(limit)`. Implementa mensagens de coleção Smalltalk:

| Smalltalk | Python | Comportamento |
|---|---|---|
| `do:` | `do(block)` | itera com deque hack — sem alocar lista |
| `collect:` | `collect(block)` | transforma → `list` (futuro: `OrderedCollection`) |
| `select:` | `select(block)` | filtra → `list` |
| `reject:` | `reject(block)` | filtra inverso → `list` |
| `detect:` | `detect(block)` | primeiro que satisfaz, ou `None` |
| `inject:into:` | `inject_into(init, block)` | reduce |
| `size` | `size()` | retorna `Int` |

### Transcript — `poop/types/transcript.py`

Singleton `_TranscriptClass` injetado no namespace de execução como `Transcript`. Métodos:

| Smalltalk | Python |
|---|---|
| `Transcript show: obj` | `Transcript.show(obj)` — chama `str(obj)` |
| `Transcript nl` | `Transcript.nl()` — imprime linha vazia |

## Transformers ativos

### Float — `poop/transformers/float.py`

| Nó AST | Substituição | Motivo |
|---|---|---|
| `ast.Constant(value=float)` | `ast.Call(_poop_float, [n])` | Literais float tornam-se instâncias de `Float` |

### Int — `poop/transformers/int.py`

| Nó AST | Substituição | Motivo |
|---|---|---|
| `ast.Constant(value=int)` (exceto `bool`) | `ast.Call(_poop_int, [n])` | Literais inteiros tornam-se instâncias de `Int` |

### Boolean — `poop/transformers/boolean.py`

| Nó AST | Substituição | Motivo |
|---|---|---|
| `ast.Constant(value=True)` | `ast.Name(id="_poop_true")` | `True` passa a ser instância de `TrueClass` (estilo Smalltalk) |
| `ast.Constant(value=False)` | `ast.Name(id="_poop_false")` | `False` passa a ser instância de `FalseClass` (estilo Smalltalk) |

Os nomes `_poop_true` e `_poop_false` são injetados no namespace interno do executor — invisíveis para o código do usuário. `TrueClass` e `FalseClass` implementam os métodos Smalltalk (`ifTrue:`, `ifFalse:`, `and:`, `or:`, `not`, `xor:`, `eqv:`) em `poop/types/boolean.py`.

### TODO — operações que retornam booleano

As operações abaixo ainda retornam `bool` Python nativo. Futuramente devem retornar instâncias de `TrueClass`/`FalseClass`:

- ~~Comparações em `Int`/`Float`: `==`, `!=`, `<`, `>`, `<=`, `>=`~~ ✓ implementado.
- Operador `is` / `is not`
- Funções built-in: `isinstance`, `hasattr`, `callable`, etc.

## Backlog

### No bitwise invert — `poop/validators/no_invert.py`

| Nó AST | Motivo |
|---|---|
| `ast.UnaryOp` com `ast.Invert` | `~x` não existe em Smalltalk; use `x.bit_invert()` |

### No unary minus — `poop/validators/no_unary_minus.py`

| Nó AST | Condição | Motivo |
|---|---|---|
| `ast.UnaryOp` com `ast.USub` | operando não é `ast.Constant` | `-x` não existe em Smalltalk; use `x.negated()` |

Literais negativos (`-1`, `-3.14`) são permitidos — apenas `-variavel` e `-expressao` são bloqueados.

### No `not` — `poop/validators/no_not.py`

| Nó AST | Motivo |
|---|---|
| `ast.UnaryOp` com `ast.Not` | `not x` é estrutura de controle; use `x.not_()` |

`-x` (`ast.USub`) e `~x` (`ast.Invert`) são permitidos por ora — apenas `not` é bloqueado.

### No `try` — `poop/validators/no_try.py`

| Nó AST | Motivo |
|---|---|
| `ast.Try` | `try/except/finally` são estruturas de controle; Smalltalk usa `on:do:` |
| `ast.TryStar` | Variante `try/except*` (exception groups) |

### Próximas infecções (validators)
- ~~**Operador unário `-`**~~ ✓ implementado em `poop/validators/no_unary_minus.py`.
- ~~**Operador unário `~`**~~ ✓ implementado em `poop/validators/no_invert.py`.
- **Operadores `is` / `is not`** (`ast.Is`, `ast.IsNot`): mapeamento Smalltalk pendente de decisão. Candidatos: `x.is_nil()` / `x.not_nil()` para o caso `None`; `x.is_identical(y)` / `x.not_identical(y)` (usando `id()` internamente) para identidade geral — equivalentes a `==` / `~~` do Smalltalk. Implementação depende de `Object` como base.
- **`match/case`** (`ast.Match`): pattern matching estrutural é control flow — Smalltalk usa polimorfismo e despacho de mensagens.
- **`with`/`async with`** (`ast.With`, `ast.AsyncWith`): context managers são Python-específicos; sem equivalente em Smalltalk.
- **`raise`** (`ast.Raise`): Smalltalk lança exceções via `signal` em objetos de erro (`Error signal: 'msg'`); `raise` expõe a estrutura de controle diretamente.
- **`del`** (`ast.Delete`): destruição explícita de variável não existe em Smalltalk.
- **`assert`** (`ast.Assert`): Python-específico; asserções em Smalltalk são mensagens (`assert:` em TestCase etc.).
- **`global`/`nonlocal`** (`ast.Global`, `ast.Nonlocal`): manipulação de escopo explícita não existe em Smalltalk — estado vive em instâncias.
- **`yield`/`yield from`** (`ast.Yield`, `ast.YieldFrom`): geradores são Python-específicos; Smalltalk usa blocos e mensagens de coleção.
- **`:=` (walrus operator)** (`ast.NamedExpr`): atribuição dentro de expressão é Python-específico.

### Próximos tipos
- **`NoneClass` — `if_none`/`if_not_none`**: adicionar mensagens `if_none(block)` e `if_not_none(block)` como blocos condicionais análogos ao `ifNil:`/`ifNotNil:` do Smalltalk.
- **`StringObject`**: string com mensagens `size()`, `at(index)`, `includes(char)`, `reversed()`, `__str__`. Transformer reescreve literais string → `StringObject`.
- **`OrderedCollection`**: substitui `list`; mensagens `do(block)`, `collect(block)`, `select(block)`, `reject(block)`, `detect(block)`, `inject_into(init, block)`, `add(obj)`, `size()`, `includes(obj)`. Quando implementado, `Interval.collect`/`select`/`reject` passam a retornar `OrderedCollection`.
- **`Int` — métodos ausentes**: `abs()`, `sqrt()` → `Float`, `as_float()` → `Float`, `factorial()`, `gcd(other)`, `lcm(other)`.
- **`Float` — métodos ausentes**: `truncated()` → `Int`, `rounded()` → `Int`, `ceiling()` → `Int`, `floor()` → `Int`, `abs()`, `sqrt()`.
- **`Object` — métodos ausentes**: `yourself()` (retorna `self`, essencial para cascatas), `print_string()` (alias legível para `__str__`).
- **`Interval` — métodos ausentes**: `includes(x)`, `reversed()`, `first()`, `last()`, `to_by_(limit, step)` (Smalltalk `to:by:`).

### Próximos transformers
- ~~Literais inteiros (`ast.Constant` int) → `Int`.~~ ✓ implementado.
- ~~Literais float (`ast.Constant` float) → `Float`.~~ ✓ implementado.
- Literais string (`ast.Constant` str) → `StringObject`.
- Literais lista (`ast.List`) → `OrderedCollection`.
- Chamada `range(...)` (`ast.Call` com `func.id == "range"`) → instância de `Interval`. O usuário escreve `range(1, 10)` e recebe um `Interval` POOP com mensagens `do`, `collect`, etc. Requer `Interval` implementado.
- Comparações (`==`, `!=`, `<`, `>`, `<=`, `>=`), `is`/`is not` e `not` → retornar `TrueClass`/`FalseClass`.
- Chamada `len(x)` (`ast.Call` com `func.id == "len"`) → reescrever para `x.size()` (ou banir via validator).
- Chamadas `isinstance(x, T)`, `hasattr(x, s)`, `callable(x)` → devem retornar `Boolean` POOP em vez de `bool` nativo.

### Bugs / inconsistências
- **`Interval.detect` retorna `None` nativo** em vez do singleton `none` POOP quando nenhum elemento satisfaz o bloco.
- **`Object.class_name()` retorna `str` nativo** — deveria retornar `StringObject` quando o tipo estiver implementado.
- **Funções built-in** (`len`, `isinstance`, `hasattr`, `callable`) vazam tipos Python nativos (`int`, `bool`) para dentro do modelo POOP.

### Arquitetura / DX
- **REPL**: loop interativo estilo Smalltalk workspace — `poop` sem argumentos abre o REPL.
- **Mensagens de erro mais ricas**: `ValidationError` poderia sugerir o equivalente POOP (ex.: `"use x.not_() instead of 'not x'"`).
- **`Transcript.show` retornar `self`**: permitiria cascatas futuras (`Transcript.show(x).nl()`).

### Exemplos de código
- Expandir `examples/` à medida que novas funcionalidades forem implementadas.

### ~~CLI como entry point instalável~~ ✓ (concluído)


## Decisões em aberto

- **Lambdas** (`ast.Lambda`): análogos aos blocos Smalltalk — **permitidos**.
- **Compreensões** (`ast.ListComp`, `ast.SetComp`, `ast.DictComp`, `ast.GeneratorExp`): contêm iteração implícita — avaliar se devem ser banidas junto com loops.
- **Atribuição aumentada / múltipla**: avaliar consistência com o modelo de objetos.
- **`import`** (`ast.Import`, `ast.ImportFrom`): Smalltalk não tem sistema de módulos equivalente — avaliar se deve ser banido ou restrito (ex.: permitir apenas imports de módulos POOP).
