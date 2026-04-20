# Smalltalk Infections

Infections come in two kinds:
- **Validators** (`poop/validators/`) — rejeitam código incompatível com POOP; seguem o padrão `Validator` + `ast.NodeVisitor`.
- **Transformers** (`poop/transformers/`) — reescrevem o AST antes da execução para substituir construtos Python por equivalentes POOP; seguem o padrão `Transformer` + `ast.NodeTransformer`.

Pipeline: `parse → validate → transform → execute(namespace)`

## Princípios

- **Tudo é objeto** e toda operação é **passagem de mensagem**.
- Não existem estruturas de controle de fluxo — condicionais e iterações são mensagens enviadas a objetos.
- Não existem funções livres — todo comportamento vive em métodos de classes.
- **Estética de mensagem**: o critério central de uma infecção não é "existe em Smalltalk?" mas sim "parece um objeto recebendo uma mensagem?". Operadores (`-x`, `not x`, `~x`) e funções livres (`len(x)`, `abs(x)`) têm aparência procedural mesmo quando chamam métodos internamente — devem ser substituídos por `x.negated()`, `x.not_()`, `x.bit_invert()`, `x.size()`, `x.abs()`. O código POOP deve parecer uma conversa entre objetos, não uma sequência de operações.
- **Ativar validator apenas quando o substituto existe**: bloquear sem oferecer alternativa só quebra código sem ensinar nada. Validators sem substituto implementado vivem no backlog até a alternativa estar pronta.
- **Representação**: todos os tipos POOP implementam `__str__` (e `__repr__` delega para ele). `Transcript.show` chama `str(obj)` internamente.
- **`__slots__` em todos os tipos POOP**: variáveis de instância são declaradas na definição da classe e fixas — nunca adicionadas dinamicamente a instâncias. Extensão de *métodos* em runtime continua funcionando normalmente. Subclasses que precisarem de novas variáveis de instância podem declarar seus próprios `__slots__` ou omiti-los.

## Infecções ativas

### No `if` — `poop/validators/no_if.py`

| Nó AST | Motivo |
|---|---|
| `ast.If` | `if/elif/else` têm aparência de controle de fluxo; use `x.if_true(block)` / `x.if_false(block)` |
| `ast.IfExp` | Expressão ternária `x if cond else y` — mesma razão |

### No loops — `poop/validators/no_loops.py`

| Nó AST | Motivo |
|---|---|
| `ast.For` | Loop tem aparência procedural; use `col.do(block)`, `col.collect(block)`, recursão |
| `ast.While` | Idem; use `cond.while_true(block)` |
| `ast.AsyncFor` | Variante assíncrona do `for` |

### No free functions — `poop/validators/no_free_functions.py`

| Nó AST | Contexto | Motivo |
|---|---|---|
| `ast.FunctionDef` | fora de classe | Função livre não é uma mensagem a nenhum objeto |
| `ast.AsyncFunctionDef` | fora de classe | Variante assíncrona |

Funções dentro de classes (`class_depth > 0`) são permitidas como métodos.

### No `print` — `poop/validators/no_print.py`

| Chamada | Motivo | Substituto |
|---|---|---|
| `print(...)` | Função livre com aparência procedural | `Transcript.show(obj)` |

### No `try` — `poop/validators/no_try.py`

| Nó AST | Motivo |
|---|---|
| `ast.Try` | Estrutura de controle — aparência procedural; substituto futuro: `block.on_error(handler)` |
| `ast.TryStar` | Variante `try/except*` (exception groups) |

### No `not` — `poop/validators/no_not.py`

| Nó AST | Motivo | Substituto |
|---|---|---|
| `ast.UnaryOp` com `ast.Not` | `not x` tem aparência de operador; não é uma mensagem a `x` | `x.not_()` |

### No unary minus — `poop/validators/no_unary_minus.py`

| Nó AST | Condição | Motivo | Substituto |
|---|---|---|---|
| `ast.UnaryOp` com `ast.USub` | operando não é `ast.Constant` | `-x` tem aparência de operador | `x.negated()` |

Literais negativos (`-1`, `-3.14`) são permitidos — apenas `-variavel` e `-expressao` são bloqueados.

### No bitwise invert — `poop/validators/no_invert.py`

| Nó AST | Motivo | Substituto |
|---|---|---|
| `ast.UnaryOp` com `ast.Invert` | `~x` tem aparência de operador | `x.bit_invert()` |

### No `is` / `is not` — `poop/validators/no_is.py`

| Nó AST | Motivo | Substituto |
|---|---|---|
| `ast.Compare` com `ast.Is` | `is` tem aparência de operador | `x.is_none()` ou `x.is_identical(other)` |
| `ast.Compare` com `ast.IsNot` | `is not` tem aparência de operador | `x.not_none()` ou `x.not_identical(other)` |

## Tipos ativos

### Object — `poop/types/object.py`

Raiz concreta de todos os tipos POOP. Fornece implementações default para métodos universais:

| Mensagem | Método | Comportamento |
|---|---|---|
| `isNil` | `is_none()` | sempre `false` para Object |
| `notNil` | `not_none()` | sempre `true` para Object |
| `not` | `not_()` | `false if bool(self) else true` |
| `class` | `class_name()` | `type(self).__name__` como `Str` |
| `respondsTo:` | `responds_to(symbol)` | `hasattr` como base |

`__str__` retorna `"<ClassName>"` como fallback; `__repr__` delega para `__str__`.

### NoneClass — `poop/types/none.py`

`NoneClass(Object)` com singleton `none`. Transformer reescreve `ast.Constant(value=None)` → `_poop_none`.

| Método | `Object` | `NoneClass` |
|---|---|---|
| `is_none()` | `false` | `true` |
| `not_none()` | `true` | `false` |
| `if_none(block)` | não executa | executa bloco |
| `if_not_none(block)` | executa passando `self` | não executa |

`__bool__` retorna `False`. `__str__` retorna `"None"`.

### Boolean — `poop/types/boolean.py`

`Boolean(Object, ABC)` com subclasses privadas `_TrueClass` e `_FalseClass`. Singletons `true`/`false` substituem `True`/`False` via transformer.

| Mensagem | Método |
|---|---|
| `ifTrue:` / `ifFalse:` | `if_true(block)` / `if_false(block)` |
| `ifTrue:ifFalse:` / `ifFalse:ifTrue:` | `if_true_if_false(t, f)` / `if_false_if_true(f, t)` |
| `and:` / `or:` (lazy) | `and_(block)` / `or_(block)` |
| `not` / `xor:` / `eqv:` | `not_()` / `xor(other)` / `eqv(other)` |
| `&` / `\|` (eager) | `__and__(other)` / `__or__(other)` |

### Interval — `poop/types/interval.py`

`Interval(Object)` representa um intervalo inteiro fechado [start, stop]. Criado via `Int.to_(limit)`.

| Mensagem | Método | Comportamento |
|---|---|---|
| `do:` | `do(block)` | itera sem alocar lista |
| `collect:` | `collect(block)` | transforma → `list` (futuro: `OrderedCollection`) |
| `select:` | `select(block)` | filtra → `list` |
| `reject:` | `reject(block)` | filtra inverso → `list` |
| `detect:` | `detect(block)` | primeiro que satisfaz, ou `none` POOP |
| `inject:into:` | `inject_into(init, block)` | reduce |
| `size` | `size()` | retorna `Int` |

### Transcript — `poop/types/transcript.py`

Singleton injetado no namespace de execução.

| Mensagem | Método |
|---|---|
| `Transcript show: obj` | `Transcript.show(obj)` — chama `str(obj)` |
| `Transcript nl` | `Transcript.nl()` — imprime linha vazia |

## Transformers ativos

### Int — `poop/transformers/int.py`

| Nó AST | Substituição |
|---|---|
| `ast.Constant(value=int)` (exceto `bool`) | `_poop_int(n)` |
| `ast.UnaryOp(USub, Constant(int))` | `_poop_int(-n)` — literal negativo colapsado |

### Float — `poop/transformers/float.py`

| Nó AST | Substituição |
|---|---|
| `ast.Constant(value=float)` | `_poop_float(n)` |
| `ast.UnaryOp(USub, Constant(float))` | `_poop_float(-n)` — literal negativo colapsado |

### Boolean — `poop/transformers/boolean.py`

| Nó AST | Substituição |
|---|---|
| `ast.Constant(value=True)` | `_poop_true` |
| `ast.Constant(value=False)` | `_poop_false` |

### None — `poop/transformers/none.py`

| Nó AST | Substituição |
|---|---|
| `ast.Constant(value=None)` | `_poop_none` |

### Str — `poop/transformers/str.py`

| Nó AST | Substituição |
|---|---|
| `ast.Constant(value=str)` | `_poop_str(s)` |

### TODO — operações que retornam booleano nativo

- Operador `is` / `is not`
- Funções built-in: `isinstance`, `hasattr`, `callable`, etc.

## Backlog

### Validators — com substituto pronto (pode ativar)

| Construct | Validator | Substituto disponível |
|---|---|---|
| `global` / `nonlocal` | `no_global.py` | use variáveis de instância |
| `del x` | `no_del.py` | simplesmente não deletar — objetos não têm destruição explícita |
| `yield` / `yield from` | `no_yield.py` | `do(block)`, `collect(block)`, `select(block)` |
| `:=` walrus | `no_walrus.py` | reestruturar como atribuição separada |
| `match/case` | `no_match.py` | polimorfismo + `if_true`/`if_false` |
| `input(...)` | `no_builtins.py` | sem substituto POOP necessário — banir |
| `exec` / `eval` / `compile` | `no_builtins.py` | sem substituto — banir |
| `breakpoint` | `no_builtins.py` | sem substituto — banir |
| `exit` / `quit` | `no_builtins.py` | sem substituto — banir |
| `globals` / `locals` / `vars` / `dir` | `no_builtins.py` | use instâncias e `responds_to` |
| `setattr` / `delattr` | `no_builtins.py` | use métodos da classe |
| `iter` / `next` / `aiter` / `anext` | `no_builtins.py` | `do(block)` |
| `enumerate` / `zip` | `no_builtins.py` | `collect`, `inject_into` |
| `slice` | `no_builtins.py` | use `at(index)` |
| `format` | `no_builtins.py` | futuro `Str.format(spec)` |

### Validators — aguardando substituto

| Construct | Validator | Substituto pendente |
|---|---|---|
| `raise` | `no_raise.py` | `Error` com `.signal()` |
| `with` / `async with` | `no_with.py` | mecanismo `on_do` |
| `assert` | `no_assert.py` | `assert_:` em framework de testes |

### Próximos tipos

- **`OrderedCollection`**: substitui `list`; mensagens `do(block)`, `collect(block)`, `select(block)`, `reject(block)`, `detect(block)`, `inject_into(init, block)`, `add(obj)`, `size()`, `includes(obj)`. Quando implementado, `Interval.collect`/`select`/`reject` passam a retornar `OrderedCollection`.
- **`Array`**: substitui `tuple`; imutável; mensagens `size()`, `at(index)`, `do(block)`, `collect(block)`, `select(block)`, `reject(block)`, `detect(block)`, `inject_into(init, block)`, `includes(obj)`. Transformer reescreve literais `(a, b, c)` → `Array`.
- **`Dictionary`**: substitui `dict`; mensagens `at(key)`, `at_put(key, val)`, `includes_key(key)`, `keys()`, `values()`, `do(block)`, `size()`. Transformer reescreve literais `{k: v}` → `Dictionary`.
- **`Set`**: substitui `set`; mensagens `includes(obj)`, `add(obj)`, `remove(obj)`, `size()`, `do(block)`. Transformer reescreve literais `{a, b}` → `Set`.
- **`Error`**: classe base para exceções POOP; método `signal()` e `signal_with(msg)` como mensagens ao objeto de erro. Desbloqueia `no_raise` e `no_with`.
- **`Str` — métodos ausentes**:
  - Dunders: `__contains__`, `__len__`, `__getitem__`, `__iter__`, `__mul__`, `__lt__`, `__le__`, `__gt__`, `__ge__`
  - Métodos: `upper()`, `lower()`, `strip()`, `lstrip()`, `rstrip()`, `split()`, `replace()`, `startswith()`, `endswith()`, `find()`, `index()`, `count()`, `join()`, `capitalize()`, `title()`, `swapcase()`, `isalpha()`, `isdigit()`, `isalnum()`, `isspace()`, `isupper()`, `islower()`
- **`Interval` — métodos ausentes**: `includes(x)`, `reversed()`, `first()`, `last()`, `to_by_(limit, step)`.

### Próximos transformers

- Literais lista (`ast.List`) → `OrderedCollection`.
- Literais tupla (`ast.Tuple`) → `Array`.
- Literais dict (`ast.Dict`) → `Dictionary`.
- Literais set (`ast.Set`) → `Set`.
- `range(...)` → `Interval`.
- ~~`len(x)` → `x.len()`~~ — banir via validator com sugestão; ver seção Builtins.
- ~~`abs(x)` → `x.abs()`~~ — banir via validator com sugestão; ver seção Builtins.
- `isinstance(x, T)` → `x.is_instance(T)` retornando `Boolean` POOP.
- `hasattr(x, s)` → `x.responds_to(s)` retornando `Boolean` POOP.
- `callable(x)` → `x.is_callable()` retornando `Boolean` POOP.
- Comparações (`==`, `!=`, `<`, `>`, `<=`, `>=`) → retornar `TrueClass`/`FalseClass`.

### Builtins Python — mapa completo

#### Transformar (reescrever para mensagem ao objeto)

| Builtin | Equivalente POOP | Status |
|---|---|---|
| `round(x)` | `x.round()` | ✓ em Int/Float |
| `str(x)` | chama `__str__` | ✓ funciona |
| `int(x)` | `x.as_int()` | pendente |
| `float(x)` | `x.as_float()` | ✓ em Int |
| `type(x)` | `x.class_name()` | ✓ em Object |
| `reversed(x)` | `x.reversed()` | ✓ em Interval |
| `sorted(x)` | `x.sorted()` | futuro (depende de OrderedCollection) |
| `map(f, col)` | `col.collect(f)` | ✓ collect existe |
| `filter(f, col)` | `col.select(f)` | ✓ select existe |

#### Banir (validator)

| Builtin | Motivo |
|---|---|
| `print` | ✓ bloqueado — use `Transcript.show` |
| `len(x)` | função livre — use `x.len()` |
| `abs(x)` | função livre — use `x.abs()` |
| `range(n)` | função livre — use `(1).to_(n)` ou similar |
| `hash(x)` | função livre — use `x.hash()` |
| `id(x)` | função livre — use `x.identity_hash()` |
| `all(col)` | função livre — use `col.all_satisfy(block)` |
| `any(col)` | função livre — use `col.any_satisfy(block)` |
| `min(a, b)` / `max(a, b)` | função livre — use `a.min(b)` / `a.max(b)` |
| `isinstance(x, T)` | função livre — use `x.is_instance(T)` |
| `hasattr(x, s)` | função livre — use `x.responds_to(s)` |
| `callable(x)` | função livre — use `x.is_callable()` |
| `divmod(a, b)` | função livre — use `a.divmod(b)` |
| `pow(a, b)` | função livre — use `a.raised_to(b)` |
| `bin(n)` / `hex(n)` / `oct(n)` | função livre — use `n.as_binary()` / `n.as_hex()` / `n.as_octal()` |
| `chr(n)` / `ord(c)` | função livre — futuro `n.as_char()` / `c.ascii_value()` |
| `input` | I/O sem substituto POOP |
| `open` | I/O sem substituto POOP |
| `exec` / `eval` / `compile` | metaprogramação — banir |
| `breakpoint` | debug Python-específico |
| `exit` / `quit` | controle de processo |
| `globals` / `locals` / `vars` / `dir` | introspecção de escopo — use instâncias |
| `setattr` / `delattr` | manipulação explícita de atributos — use métodos |
| `iter` / `next` / `aiter` / `anext` | protocolo iterator — use `do(block)` |
| `enumerate` / `zip` | iteração procedural — use mensagens de coleção |
| `slice` | Python-específico — use `at(index)` |
| `format` | função livre — use `x.format(spec)` |
| `ascii` | Python-específico |

#### Permitir / Decidir depois

| Builtin | Observação |
|---|---|
| `super` | necessário para herança |
| `property` / `classmethod` / `staticmethod` | definição de classe |
| `getattr` | usado internamente por `responds_to` |
| `list` / `dict` / `set` / `tuple` | serão substituídos pelos tipos POOP |
| `int` / `float` / `str` / `bool` | construtores cobertos por transformers |
| `complex` / `bytes` / `bytearray` / `memoryview` | baixo nível — provavelmente banir |
| `frozenset` | avaliar quando `Set` for implementado |
| `issubclass` | avaliar junto com `isinstance` |
| `repr` | delega para `__repr__` → `__str__` |
| `sum` | usar `inject_into(0, block)` — banir quando transformer existir |

### Bugs / inconsistências

- ~~**`Interval.detect` retorna `None` nativo**~~ ✓ corrigido.
- ~~**`Object.class_name()` retorna `str` nativo**~~ ✓ corrigido.
- **Funções built-in** (`len`, `isinstance`, `hasattr`, `callable`) vazam tipos Python nativos para dentro do modelo POOP.

### Renomeações pendentes (nomes Smalltalk → nomes Python)

Métodos já implementados que usam nomes Smalltalk em vez do nome Python correspondente:

| Tipo | Método atual | Deveria ser | Motivo |
|---|---|---|---|
| `Object` | `responds_to(s)` | `has_attr(s)` | `hasattr` → `has_attr` |
| `Int` | `as_float()` | `float()` | `float(x)` → `x.float()` |

Backlog (ainda não implementados — usar nome correto quando implementar):

| Builtin | Nome errado | Nome correto |
|---|---|---|
| `int(x)` | `as_int()` | `int()` |
| `id(x)` | `identity_hash()` | `id()` |
| `all(col, block)` | `all_satisfy(block)` | `all(block)` |
| `any(col, block)` | `any_satisfy(block)` | `any(block)` |
| `pow(a, b)` | `raised_to(b)` | `pow(b)` |
| `bin(n)` | `as_binary()` | `bin()` |
| `hex(n)` | `as_hex()` | `hex()` |
| `oct(n)` | `as_octal()` | `oct()` |
| `chr(n)` | `as_char()` | `chr()` |
| `ord(c)` | `ascii_value()` | `ord()` |
| `callable(x)` | `is_callable()` | `callable()` — avaliar; `is_callable()` lê melhor |

### Arquitetura / DX

- **REPL**: loop interativo — `poop` sem argumentos abre o REPL.
- **Mensagens de erro mais ricas**: `ValidationError` poderia sugerir o equivalente POOP (ex.: `"use x.not_() instead of 'not x'"`).
- **`Transcript.show` retornar `self`**: permitiria cascatas (`Transcript.show(x).nl()`).

### Exemplos de código

- Expandir `examples/` à medida que novas funcionalidades forem implementadas.

### ~~CLI como entry point instalável~~ ✓ (concluído)


## Decisões em aberto

- **Dunders expostos como métodos regulares**: todo dunder relevante de um tipo POOP ganha um alias com o nome Python sem underscores — `__len__` → `len()`, `__abs__` → `abs()`, `__contains__` → `contains()`, `__iter__` → `iter()`, `__hash__` → `hash()`, etc. A regra é: remover os underscores, manter o nome Python — não traduzir para Smalltalk. Transformers reescrevem `len(x)` → `x.len()`, `abs(x)` → `x.abs()`, etc. Métodos Smalltalk como `size()` e `includes()` continuam existindo como mensagens adicionais — os aliases dunder são um complemento, não um substituto.
- **`isEmpty` não será implementado em `Str`**: usar `obj == ''` — chama `Str.__eq__` e retorna `Boolean` POOP.
- **`as_string()` / `printString` não serão implementados**: usar `str(obj)` — chama `__str__` de cada tipo POOP.
- **Lambdas** (`ast.Lambda`): análogos aos blocos Smalltalk — **permitidos**.
- **Compreensões** (`ast.ListComp`, `ast.SetComp`, `ast.DictComp`, `ast.GeneratorExp`): contêm iteração implícita — avaliar se devem ser banidas junto com loops.
- **Atribuição aumentada / múltipla**: avaliar consistência com o modelo de objetos.
- **`import`** (`ast.Import`, `ast.ImportFrom`): avaliar se deve ser banido ou restrito a imports de módulos POOP.
