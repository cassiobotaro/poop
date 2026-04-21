# Smalltalk Infections

Infections come in two kinds:
- **Validators** (`poop/validators/`) — rejeitam código incompatível com POOP; seguem o padrão `Validator` + `ast.NodeVisitor`.
- **Transformers** (`poop/transformers/`) — reescrevem o AST antes da execução para substituir construtos Python por equivalentes POOP; seguem o padrão `Transformer` + `ast.NodeTransformer`.

Pipeline: `parse → validate → transform → execute(namespace)`

## Princípios

- **Tudo é objeto** e toda operação é **passagem de mensagem**.
- Não existem estruturas de controle de fluxo — condicionais e iterações são mensagens enviadas a objetos.
- Não existem funções livres — todo comportamento vive em métodos de classes.
- **Estética de mensagem**: o critério central de uma infecção não é "existe em Smalltalk?" mas sim "parece um objeto recebendo uma mensagem?". Operadores (`-x`, `not x`, `~x`) e funções livres (`len(x)`, `abs(x)`) têm aparência procedural mesmo quando chamam métodos internamente — devem ser substituídos por `x.negated()`, `x.not_()`, `x.bit_invert()`, `x.len()`, `x.abs()`. O código POOP deve parecer uma conversa entre objetos, não uma sequência de operações.
- **Nomes de métodos em Python, não Smalltalk**: todos os métodos seguem o nome Python correspondente — builtins, dunders e API de coleções. `for_each` não `do`, `map` não `collect`, `filter` não `select`, `filter_false` não `reject`, `find` não `detect`, `reduce` não `inject_into`. Nomes Smalltalk não são implementados.
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
| `ast.For` | Loop tem aparência procedural; use `col.for_each(block)`, `col.map(block)`, recursão |
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
| `print(...)` | Função livre com aparência procedural | `obj.print()` |

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

### No `global`/`nonlocal` — `poop/validators/no_global.py`

| Nó AST | Motivo |
|---|---|
| `ast.Global` | `global` rompe o encapsulamento — estado vive em instâncias, não em escopo global |
| `ast.Nonlocal` | `nonlocal` manipula escopo externo — use variáveis de instância |

### No `yield` — `poop/validators/no_yield.py`

| Nó AST | Motivo | Substituto |
|---|---|---|
| `ast.Yield` | gerador tem aparência procedural de iteração | `col.for_each(block)`, `col.map(block)` |
| `ast.YieldFrom` | idem | idem |

### No walrus (`:=`) — `poop/validators/no_walrus.py`

| Nó AST | Motivo |
|---|---|
| `ast.NamedExpr` | `:=` combina atribuição e expressão — use atribuição separada |

### No `match/case` — `poop/validators/no_match.py`

| Nó AST | Motivo | Substituto |
|---|---|---|
| `ast.Match` | estrutura de controle com aparência procedural | polimorfismo + `if_true(block)`/`if_false(block)` |

### No `len` — `poop/validators/no_len.py`

| Chamada | Motivo | Substituto |
|---|---|---|
| `len(x)` | função livre com aparência procedural | `x.len()` |

### No `abs` — `poop/validators/no_abs.py`

| Chamada | Motivo | Substituto |
|---|---|---|
| `abs(x)` | função livre com aparência procedural | `x.abs()` |

### No `hash` — `poop/validators/no_hash.py`

| Chamada | Motivo | Substituto |
|---|---|---|
| `hash(x)` | função livre com aparência procedural | `x.hash()` |

### No `isinstance` — `poop/validators/no_isinstance.py`

| Chamada | Motivo | Substituto |
|---|---|---|
| `isinstance(x, T)` | função livre com aparência procedural | `x.is_instance(T)` |

### No `callable` — `poop/validators/no_callable.py`

| Chamada | Motivo | Substituto |
|---|---|---|
| `callable(x)` | função livre com aparência procedural | `x.callable()` |

### No `id` — `poop/validators/no_id.py`

| Chamada | Motivo | Substituto |
|---|---|---|
| `id(x)` | função livre com aparência procedural | `x.id()` |

### No `all` — `poop/validators/no_all.py`

| Chamada | Motivo | Substituto |
|---|---|---|
| `all(col)` | função livre com aparência procedural | `col.all(block)` |

### No `any` — `poop/validators/no_any.py`

| Chamada | Motivo | Substituto |
|---|---|---|
| `any(col)` | função livre com aparência procedural | `col.any(block)` |

### No `min`/`max` — `poop/validators/no_min.py`, `poop/validators/no_max.py`

| Chamada | Motivo | Substituto |
|---|---|---|
| `min(a, b)` | função livre com aparência procedural | `a.min(b)` |
| `max(a, b)` | função livre com aparência procedural | `a.max(b)` |

### No `bin`/`hex`/`oct` — `poop/validators/no_bin.py`

| Chamada | Motivo | Substituto |
|---|---|---|
| `bin(n)` | função livre com aparência procedural | `n.bin()` |
| `hex(n)` | função livre com aparência procedural | `n.hex()` |
| `oct(n)` | função livre com aparência procedural | `n.oct()` |

### No `chr`/`ord` — `poop/validators/no_chr.py`

| Chamada | Motivo | Substituto |
|---|---|---|
| `chr(n)` | função livre com aparência procedural | `n.chr()` |
| `ord(c)` | função livre com aparência procedural | `c.ord()` |

### No `divmod` — `poop/validators/no_divmod.py`

| Chamada | Motivo | Substituto |
|---|---|---|
| `divmod(a, b)` | função livre com aparência procedural | `a.divmod(b)` |

### No `pow` — `poop/validators/no_pow.py`

| Chamada | Motivo | Substituto |
|---|---|---|
| `pow(a, b)` | função livre com aparência procedural | `a.pow(b)` |

### No `hasattr` — `poop/validators/no_hasattr.py`

| Chamada | Motivo | Substituto |
|---|---|---|
| `hasattr(x, s)` | função livre com aparência procedural | `x.has_attr(s)` |

### No `format` — `poop/validators/no_format.py`

| Chamada | Motivo | Substituto |
|---|---|---|
| `format(x, spec)` | função livre com aparência procedural | `x.format(spec)` |

### No `slice` — `poop/validators/no_slice.py`

| Chamada | Motivo | Substituto |
|---|---|---|
| `slice(...)` | construto Python-específico | `obj.at(index)` |

### No `enumerate`/`zip` — `poop/validators/no_enumerate.py`

| Chamada | Motivo | Substituto |
|---|---|---|
| `enumerate(col)` | função livre com aparência procedural | `col.map(block)`, `col.reduce(init, block)` |
| `zip(a, b)` | função livre com aparência procedural | idem |

### No `iter`/`next` — `poop/validators/no_iter.py`

| Chamada | Motivo | Substituto |
|---|---|---|
| `iter(col)` | protocolo iterator com aparência procedural | `col.for_each(block)` |
| `next(it)` | idem | idem |
| `aiter(col)` | variante assíncrona | idem |
| `anext(it)` | variante assíncrona | idem |

### No `setattr`/`delattr` — `poop/validators/no_setattr.py`

| Chamada | Motivo | Substituto |
|---|---|---|
| `setattr(obj, name, val)` | manipulação explícita de atributos | use métodos da classe |
| `delattr(obj, name)` | idem | idem |

### No introspecção — `poop/validators/no_introspection.py`

| Chamada | Motivo |
|---|---|
| `globals()` | introspecção de escopo — estado vive em instâncias |
| `locals()` | idem |
| `vars(obj)` | idem |
| `dir(obj)` | idem |

### No `exec`/`eval`/`compile` — `poop/validators/no_exec.py`

| Chamada | Motivo |
|---|---|
| `exec(code)` | metaprogramação — não permitida em POOP |
| `eval(expr)` | idem |
| `compile(src, ...)` | idem |

### No `exit`/`quit` — `poop/validators/no_exit.py`

| Chamada | Motivo |
|---|---|
| `exit()` | controle de processo — sem equivalente POOP |
| `quit()` | idem |

### No `breakpoint` — `poop/validators/no_breakpoint.py`

| Chamada | Motivo |
|---|---|
| `breakpoint()` | debug Python-específico — sem equivalente POOP |

### No `input` — `poop/validators/no_input.py`

| Chamada | Motivo |
|---|---|
| `input(prompt)` | I/O interativo — sem equivalente POOP |

### No `open` — `poop/validators/no_open.py`

| Chamada | Motivo |
|---|---|
| `open(path, ...)` | I/O de arquivo — sem equivalente POOP |

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

| Mensagem Smalltalk | Método POOP | Comportamento |
|---|---|---|
| `do:` | `for_each(block)` | itera sem alocar lista |
| `collect:` | `map(block)` | transforma → `List` |
| `select:` | `filter(block)` | filtra → `List` |
| `reject:` | `filter_false(block)` | filtra inverso → `List` |
| `detect:` | `find(block)` | primeiro que satisfaz, ou `none` POOP |
| `inject:into:` | `reduce(init, block)` | reduce |
| `len` | `len()` | retorna `Int` |

### Object.print — `poop/types/object.py`

Todo objeto POOP herda `print()` de `Object`. `List` e `Tuple` sobrescrevem para suportar `sep`.

| Mensagem | Comportamento |
|---|---|
| `obj.print()` | imprime `str(obj)` seguido de `\n` e retorna `self` |
| `obj.print(end="")` | controla o terminador |
| `list.print(sep=", ")` | `List`/`Tuple`: une elementos com `sep` (padrão `" "`) |

`"".print()` imprime uma linha em branco. O retorno `self` permite cascatas: `x.print().print()`.

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

### No `del` — `poop/validators/no_del.py`

| Nó AST | Motivo |
|---|---|
| `ast.Delete` | objetos não têm destruição explícita — simplesmente não deletar |

### No subscript — `poop/validators/no_subscript.py`

| Nó AST | Condição | Motivo | Substituto |
|---|---|---|---|
| `ast.Subscript` | slice não é `ast.Slice` | `obj[key]` tem aparência de operador | `obj.at(key)` |

Fatiamento `obj[1:3]` (`ast.Slice`) é permitido por ora — ver backlog (`no_slice`).

### Str — `poop/transformers/str.py`

| Nó AST | Substituição |
|---|---|
| `ast.Constant(value=str)` | `_poop_str(s)` |

### ~~TODO — operações que retornam booleano nativo~~

- ~~Comparações (`==`, `!=`, `<`, `>`, `<=`, `>=`) — ainda retornam `bool` Python nativo em vez de `Boolean` POOP~~
- Resolvido: `Object.__eq__`/`__ne__` retornam `Boolean` por identidade; subclasses (`Int`, `Float`, `Str`, `Interval`) sobrescrevem com lógica de valor.

## Backlog

### Validators — aguardando implementação

Nenhum pendente.

### Validators — aguardando substituto

| Construct | Validator | Substituto pendente |
|---|---|---|
| `raise` | `no_raise.py` | `Error` com `.signal()` |
| `with` / `async with` | `no_with.py` | mecanismo `on_do` |
| `assert` | `no_assert.py` | `assert_:` em framework de testes |

### Próximos tipos

- ~~**`List`**: substitui `list`; mensagens `for_each(block)`, `map(block)`, `filter(block)`, `filter_false(block)`, `find(block)`, `reduce(init, block)`, `add(obj)`, `len()`, `includes(obj)`. Quando implementado, `Interval.map`/`filter`/`filter_false` passam a retornar `List`.~~ — implementado (nomes Smalltalk — renomear, ver Renomeações pendentes).
- ~~**`Tuple`**: substitui `tuple`; imutável; mensagens `len()`, `at(index)`, `for_each(block)`, `map(block)`, `filter(block)`, `filter_false(block)`, `find(block)`, `reduce(init, block)`, `includes(obj)`. Transformer reescreve literais `(a, b, c)` → `Tuple`.~~ — implementado (nomes Smalltalk — renomear, ver Renomeações pendentes).
- **[ALTA PRIORIDADE] `Error`**: classe base para exceções POOP; método `signal()` e `signal_with(msg)` como mensagens ao objeto de erro. **Dependência crítica**: desbloqueia `no_raise`, `no_with` e `no_assert` — enquanto `Error` não existe, código POOP pode usar `raise` e `with` livremente, sem proteção dos princípios.
- ~~**`Dict`**~~: implementado — `at(key)`, `at_put(key, val)`, `includes_key(key)`, `keys()`, `values()`, `for_each(block)` (recebe `Tuple(key, value)`), `len()`. Transformer reescreve literais `{k: v}` → `Dict`.
- ~~**`Set`**~~: implementado — `includes(obj)`, `add(obj)`, `remove(obj)` (semântica `discard`, sem erro se ausente), `len()`, `for_each(block)`, `map(block)`, `filter(block)`, `filter_false(block)`, `find(block)`, `reduce(init, block)`, `all(block)`, `any(block)`. Transformer reescreve literais `{a, b}` → `Set`. Literal `{}` vazio é dict — usar `_poop_set()` para set vazio.
- ~~**`FrozenSet`**~~: implementado — versão imutável de `Set`. `includes(obj)`, `len()`, `for_each(block)`, `map(block)`, `filter(block)`, `filter_false(block)`, `find(block)`, `reduce(init, block)`, `all(block)`, `any(block)`. Hashável (pode ser chave de `Dict`). Transformer reescreve `frozenset(iterable)` → `FrozenSet(*iterable)` e `frozenset()` → `FrozenSet()`.
- **`Complex`**: substitui `complex`; mensagens `real()`, `imag()`, `conjugate()`, `abs()`. Literais `complex(r, i)` → `Complex`. Transformer reescreve `j`-literals (`1+2j`) → `Complex`. Baixa prioridade — uso científico/nicho.
- ~~**`Bytes`**~~: implementado — imutável, hashável (pode ser chave de `Dict`). Mensagens `len()`, `at(index)` → `Int`, `includes(byte: Int)` → `Boolean`, `decode(encoding: Str)` → `Str`, `hex()` → `Str`, `for_each(block)`, `map(block)` → `List`. Transformer reescreve literais `b"..."` → `Bytes`.
- **`ByteArray`**: substitui `bytearray`; versão mutável de `Bytes` — relação análoga a `List`/`Tuple`. Mensagens `len()`, `at(index)`, `at_put(index, byte)`, `includes(byte)`, `decode(encoding)`, `hex()`, `for_each(block)`. Implementar após `Bytes`.
- **`MemoryView`**: substitui `memoryview`; wrapper sobre buffer de bytes. Mensagens `len()`, `at(index)`, `for_each(block)`. Baixa prioridade — uso científico/nicho. Implementar após `Bytes`/`ByteArray`.
- **`Str` — métodos ausentes**: nenhum. Todos os dunders e métodos de string estão implementados.
- **`Interval` — métodos ausentes**: nenhum. Todos os métodos estão implementados.

### Próximos transformers

- ~~Literais lista (`ast.List`) → `List`.~~ — implementado via ListTransformer.
- ~~Literais tupla (`ast.Tuple`) → `Tuple`.~~ — implementado via TupleTransformer.
- ~~Literais dict (`ast.Dict`) → `Dict`.~~
- ~~Literais set (`ast.Set`) → `Set`.~~
- ~~`range(...)` → `Interval`.~~ — implementado via RangeTransformer.
- ~~`len(x)` → `x.len()`~~ — banir via validator com sugestão; ver seção Builtins.
- ~~`abs(x)` → `x.abs()`~~ — banir via validator com sugestão; ver seção Builtins.
- ~~`isinstance(x, T)` → `x.is_instance(T)`~~ — banir via validator; use `x.is_instance(T)`.
- ~~`hasattr(x, s)` → `x.has_attr(s)`~~ — banir via validator; use `x.has_attr(s)`.
- ~~`callable(x)` → `x.callable()`~~ — banir via validator; use `x.callable()`.
- ~~Comparações (`==`, `!=`, `<`, `>`, `<=`, `>=`) → retornar `TrueClass`/`FalseClass`.~~ — implementado via `Object.__eq__`/`__ne__` e overrides em subclasses.

### Builtins Python — mapa completo

#### Transformar (reescrever para mensagem ao objeto)

| Builtin | Equivalente POOP | Status |
|---|---|---|
| `round(x)` | `x.round()` | ✓ em Int/Float |
| `str(x)` | chama `__str__` | ✓ funciona |
| `int(x)` | `x.int()` | ✓ em Int, Float, Str |
| `float(x)` | `x.float()` | ✓ em Int, Float, Str |
| `type(x)` | `x.class_name()` | ✓ em Object |
| `reversed(x)` | `x.reversed()` | ✓ em Interval, Str |
| `sorted(x)` | `x.sorted()` | pendente em List, Tuple |
| `map(f, col)` | `col.map(f)` | ✓ (renomear — ver Renomeações pendentes) |
| `filter(f, col)` | `col.filter(f)` | ✓ (renomear — ver Renomeações pendentes) |

#### Banir (validator)

| Builtin | Motivo |
|---|---|
| `print` | ✓ bloqueado — use `obj.print()` |
| `len(x)` | ✓ bloqueado — use `x.len()` |
| `abs(x)` | ✓ bloqueado — use `x.abs()` |
| `range(n)` | ✓ reescrito → `Interval` via RangeTransformer |
| `hash(x)` | ✓ bloqueado — use `x.hash()` |
| `id(x)` | ✓ bloqueado — use `x.id()` |
| `all(col)` | ✓ bloqueado — use `col.all(block)` |
| `any(col)` | ✓ bloqueado — use `col.any(block)` |
| `min(a, b)` / `max(a, b)` | ✓ bloqueado — use `a.min(b)` / `a.max(b)` |
| `isinstance(x, T)` | ✓ bloqueado — use `x.is_instance(T)` |
| `hasattr(x, s)` | ✓ bloqueado — use `x.has_attr(s)` |
| `callable(x)` | ✓ bloqueado — use `x.callable()` |
| `divmod(a, b)` | ✓ bloqueado — use `a.divmod(b)` |
| `pow(a, b)` | ✓ bloqueado — use `a.pow(b)` |
| `bin(n)` / `hex(n)` / `oct(n)` | ✓ bloqueado — use `n.bin()` / `n.hex()` / `n.oct()` |
| `chr(n)` / `ord(c)` | ✓ bloqueado — use `n.chr()` / `c.ord()` |
| `input` | ✓ bloqueado — I/O sem substituto POOP |
| `open` | ✓ bloqueado — I/O sem substituto POOP |
| `exec` / `eval` / `compile` | ✓ bloqueado — metaprogramação |
| `breakpoint` | ✓ bloqueado — debug Python-específico |
| `exit` / `quit` | ✓ bloqueado — controle de processo |
| `globals` / `locals` / `vars` / `dir` | ✓ bloqueado — use instâncias |
| `setattr` / `delattr` | ✓ bloqueado — use métodos da classe |
| `iter` / `next` / `aiter` / `anext` | ✓ bloqueado — use `col.for_each(block)` |
| `enumerate` / `zip` | ✓ bloqueado — use `col.map(block)` / `col.reduce(init, block)` |
| `slice` | ✓ bloqueado — use `obj.at(index)` |
| `format` | ✓ bloqueado — use `obj.format(spec)` |
| `ascii` | Python-específico |

#### Permitir / Decidir depois

| Builtin | Observação |
|---|---|
| `super` | necessário para herança |
| `property` / `classmethod` / `staticmethod` | definição de classe |
| `getattr` | usado internamente por `responds_to` |
| `list` / `dict` / `set` / `tuple` | serão substituídos pelos tipos POOP |
| `int` / `float` / `str` / `bool` | construtores cobertos por transformers |
| `complex` | substituído por `Complex` — ver Próximos tipos |
| `frozenset` | substituído por `FrozenSet` — ver Próximos tipos |
| `bytes` / `bytearray` / `memoryview` | substituídos por `Bytes`/`ByteArray`/`MemoryView` — ver Próximos tipos |
| `issubclass` | avaliar junto com `isinstance` |
| `repr` | delega para `__repr__` → `__str__` |
| `sum` | usar `reduce(0, block)` — banir quando transformer existir |

### Bugs / inconsistências

- ~~**`Interval.detect` retorna `None` nativo**~~ ✓ corrigido.
- ~~**`Object.class_name()` retorna `str` nativo**~~ ✓ corrigido.
- **Funções built-in** (`len`, `isinstance`, `hasattr`, `callable`) vazam tipos Python nativos para dentro do modelo POOP.
- ~~**`Str.split()` retorna `list` Python**~~ ✓ corrigido — retorna `List` POOP.
- ~~**`Str.join()` aceita `list[Str]` Python**~~ ✓ corrigido — aceita `List` POOP.
- ~~**`__repr__` ausente em Int, Float, Str, Interval, List, Tuple, NoneClass**~~ — corrigido: `__repr__ = __str__` presente em todos os tipos.

### Validators ausentes

- ~~**[ALTA PRIORIDADE] `no_subscript`**~~: implementado — bloqueia `obj[key]`, fatiamento `obj[1:3]` permitido por ora (ver item abaixo).
- **`no_slice`**: fatiamento `obj[1:3]` tem aparência de operador mas ainda não tem substituto definido — candidato: `obj.from_to(start, stop)`. Ativar após decidir o nome e implementar o método.
- **`slice` como classe Python**: `slice` é uma classe built-in (`slice(1, 3, 2)` cria um objeto com `.start`, `.stop`, `.step`). Vale pensar se POOP deveria ter um tipo `Slice` próprio, ou se o fatiamento deve simplesmente ser banido sem substituto de objeto. O `no_slice` atual bloqueia apenas a chamada `slice(...)`, não o uso do tipo em anotações ou `isinstance`.
- **[MÉDIA PRIORIDADE] ~~`no_comprehension`~~**: implementado — bloqueia `ast.ListComp`, `ast.SetComp`, `ast.DictComp`, `ast.GeneratorExp`. Substitutos: `col.map(block)`, `col.filter(block)` (após renomear).
- **[MÉDIA PRIORIDADE] `no_augmented_assign`**: `x += 1`, `x -= 1` etc. não são bloqueados — `ast.AugAssign`. Construto muito frequente; a ausência de bloqueio cria uma exceção implícita ao modelo de mensagens.
- **`no_import`**: `import os` dentro de código POOP não é bloqueado — decidir se deve ser banido ou restrito.
- **`no_raise`** e **`no_assert`**: bloqueados por `Error` — os validators não podem ser ativados antes do tipo `Error` existir (ver seção Próximos tipos).
- **`no_bytes`**: `bytes(...)`, `bytearray(...)`, `memoryview(...)` — aguardando implementação de `Bytes`/`ByteArray`/`MemoryView` (ver Próximos tipos).

### Métodos faltando em tipos existentes

- **`List.sorted()` / `List.reversed()`**: retornam nova cópia ordenada/invertida. `Interval` tem `reversed()`; `List` e `Tuple` não têm.
- **`Tuple.sorted()` / `Tuple.reversed()`**: idem.
- **`List.as_tuple()` / `Tuple.as_list()`**: conversão entre tipos de coleção.
- **`Interval.as_list()` / `Interval.as_tuple()`**: materializa o intervalo em coleção.
- ~~**`Int.times(block)`**~~: removido — `times` e `timesRepeat:` são nomes Smalltalk sem equivalente em `int` Python.
- ~~**`Int.divmod(other)` / `Float.divmod(other)` → `Tuple`**~~: implementado.

### Renomeações pendentes (nomes Smalltalk → nomes Python)

Nenhuma pendente.

### Arquitetura / DX

- **REPL**: loop interativo — `poop` sem argumentos abre o REPL.
- **Mensagens de erro mais ricas**: `ValidationError` poderia sugerir o equivalente POOP (ex.: `"use x.not_() instead of 'not x'"`).

### Exemplos de código

- Expandir `examples/` com coleções: `List`, `Tuple`, `Interval` com `map`/`filter`/`filter_false`.

### ~~CLI como entry point instalável~~ ✓ (concluído)


## Decisões em aberto

- **Dunders expostos como métodos regulares**: todo dunder relevante de um tipo POOP ganha um alias com o nome Python sem underscores — `__len__` → `len()`, `__abs__` → `abs()`, `__contains__` → `contains()`, `__iter__` → `iter()`, `__hash__` → `hash()`, etc. A regra é: remover os underscores, manter o nome Python — não traduzir para Smalltalk. Nomes Smalltalk (`size()`, `identity_hash()`, etc.) não são implementados.
- **`isEmpty` não será implementado em `Str`**: usar `obj == ''` — chama `Str.__eq__` e retorna `Boolean` POOP.
- **`List.join` / `Tuple.join` não serão implementados**: `list` Python não tem `join` — o idioma correto é `Str(sep).join(lista)`, que já existe.
- **`Transcript` removido**: era um remanescente Smalltalk sem equivalente Python. O idioma POOP correto é o objeto receber a mensagem: `obj.print()`. `Object.print()` retorna `self` para cascatas; `List`/`Tuple` sobrescrevem com parâmetro `sep`. `"".print()` substitui `Transcript.nl()`.
- **`as_string()` / `printString` não serão implementados**: usar `str(obj)` — chama `__str__` de cada tipo POOP.
- **Lambdas** (`ast.Lambda`): análogos aos blocos Smalltalk — **permitidos**.
- **Compreensões** (`ast.ListComp`, `ast.SetComp`, `ast.DictComp`, `ast.GeneratorExp`): contêm iteração implícita — avaliar se devem ser banidas junto com loops.
- **Atribuição aumentada / múltipla**: avaliar consistência com o modelo de objetos.
- **`import`** (`ast.Import`, `ast.ImportFrom`): avaliar se deve ser banido ou restrito a imports de módulos POOP.
