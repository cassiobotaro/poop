# Proposals — POOP code review

Review feita por Claude (Opus 4.7) considerando `INFECTIONS.md` e o pipeline `parse → validate → transform → execute`. Cada item indica caminho, linhas relevantes e uma sugestão concreta. Itens estão agrupados por intenção: refatoração, bug/inconsistência, alinhamento filosófico e novas funcionalidades.

---
## 1. Filosofia — `Str.__repr__ = __str__` esconde aspas em REPL

`Str("hello").__repr__()` retorna `"hello"` em vez de `"'hello'"`. No REPL POOP atual:

```
>>> "hello"
hello
```

Sem distinguir do output de `print`. Em CPython:

```
>>> "hello"
'hello'
```

`INFECTIONS.md` (linha 17) decreta que `__repr__` delega a `__str__`, mas isso degrada a experiência do REPL. Sugestões:

1. Manter `__str__ = self._value` e definir `__repr__ = f"'{self._value}'"` (apenas para `Str`). Documenta como exceção justificada.
2. Adicionar `displayhook` customizado no executor REPL que, ao mostrar `Str`, envolve em aspas.

---

## 2. Filosofia — REPL imprime resultado mas não armazena `_`

CPython REPL armazena o último valor avaliado em `_`. Ao escrever uma expressão simples, o REPL POOP imprime o resultado (via commit `1488677`), mas não popula `_` no namespace. Adicionar isso eleva muito a usabilidade em sessão interativa:

```python
# poop/repl.py — após execução
if isinstance(last_node, ast.Expr):
    self._ns["_"] = last_value
```

Requer um pouco de cooperação no executor (`mode="single"` já imprime via `displayhook`).

---

## 3. Filosofia — `Boolean.while_true(cond_block, body_block)` é uma mensagem para o objeto errado

Em Smalltalk, `whileTrue:` é mensagem para um **block**, não para o booleano: `[cond] whileTrue: [body]`. O receiver é o block que retorna o booleano, não um bool literal.

POOP escolheu colocar `while_true` em `Boolean` (`true.while_true(cond, body)` ou `false.while_true(cond, body)` — funciona igual em ambos), o que **torna o receiver irrelevante**. Não há um valor de `true` ou `false` que mude o comportamento.

Alternativas:

1. Aceitar que receiver é decorativo e renomear para algo neutro: `loop(cond, body)` em algum lugar (mas onde?).
2. Definir `while_true` em `Object` (qualquer objeto pode disparar). Idiomático: `none.while_true(...)` ou `none.repeat(...)`. Pelo menos para de fingir que o booleano importa.
3. Fazer `Block` ser um tipo de primeira classe (envelope para callable) — proposta abaixo.

Hoje, ler `true.while_true(lambda: x < 10, lambda: x.print())` é confuso porque o `true` no início é decorativo.

---

## 4. Filosofia — duplicação `_TrueClass.while_true` vs `_FalseClass.while_true`

`poop/types/boolean.py:132-152` e `212-232`. As duas implementações de `while_true` (e `while_false`) são **idênticas**. Movê-las para a base `Boolean` elimina ~40 linhas duplicadas. O receiver não altera o comportamento (ver item 17), portanto:

```python
class Boolean(Object, ABC):
    def while_true(self, cond_block, body_block) -> NoneClass:
        from poop.types.none import none
        while bool(cond_block()):
            body_block()
        return none

    def while_false(self, cond_block, body_block) -> NoneClass:
        from poop.types.none import none
        while not bool(cond_block()):
            body_block()
        return none
```

Igualmente, `_TrueClass.if_true_if_false`/`if_false_if_true` poderiam compartilhar lógica com base de despacho `__bool__`, mas é mais legível mantê-los polimórficos.

---

## 5. Performance — `from poop.types.boolean import false, true` em todo método

Cada método que retorna Boolean importa `false, true` no body. Isso é necessário por causa do ciclo `Object → Boolean → Object`. Mas os imports lazy são executados a cada chamada — não é grande custo (Python cacheia o módulo), mas o ruído visual é considerável.

**Proposta.** Criar `poop/types/_boolean_constants.py` que importa diretamente de `boolean.py`. Não — o ciclo continua. Solução melhor: usar `TYPE_CHECKING` para a anotação e injetar `true`/`false` via `setattr` do módulo após criação:

```python
# poop/types/object.py
true: "Boolean | None" = None
false: "Boolean | None" = None

def _set_booleans(t, f):
    global true, false
    true, false = t, f
```

Chamado em `poop/types/boolean.py` no fim:

```python
from poop.types.object import _set_booleans
_set_booleans(true, false)
```

Reduz ruído e elimina ~80 imports lazy. Uma alternativa mais leve: **module-level cache** em cada arquivo:

```python
# topo de list.py, tuple.py etc.
_true: "Boolean | None" = None
_false: "Boolean | None" = None

def _bools():
    global _true, _false
    if _true is None:
        from poop.types.boolean import false, true
        _true, _false = true, false
    return _true, _false
```

E usar `t, f = _bools()` no body. Funciona, mas o real ganho é estético.

---

## 6. Performance / ergonomia — `singletons` para Int(0), Int(1), Str("")

Cada `Int(0)` aloca um novo objeto. Isso é custo desprezível para Python normal, mas em código POOP que faz `numbers.sum()` sobre coleção vazia, ou contadores em loops, há alocações repetidas. Smalltalk tradicionalmente faz cache de inteiros pequenos (semelhante a CPython com -5..256). Proposta: cache de `Int(-5)..Int(256)` no módulo `int.py`, retornado por `_poop_int(n)` quando aplicável.

Custo: pequena complexidade no factory. Ganho: alocação reduzida em hot loops.

---

## 7. Refatoração — `poop/transformers/dict.py:_poop_dict_from` tem ramos quase idênticos para Tuple/List

```python
if isinstance(item, Tuple):
    if len(item._items) != 2:
        raise TypeError(...)
    d._data[item._items[0]] = item._items[1]
elif isinstance(item, List):
    if len(item._items) != 2:
        raise TypeError(...)
    d._data[item._items[0]] = item._items[1]
```

Unificar:

```python
if isinstance(item, (Tuple, List)):
    items = item._items
    if len(items) != 2:
        raise TypeError(f"dict entry must have exactly 2 elements, got {len(items)}")
    d._data[items[0]] = items[1]
else:
    raise TypeError(f"cannot use {type(item).__name__} as dict entry")
```

---

## 8. Funcionalidade nova — `Transcript`

Smalltalk tem `Transcript` como objeto global de saída. POOP hoje usa `obj.print()`. **Proposta**: adicionar um objeto `Transcript` no namespace padrão com `show`, `show_cr` (newline), `clear`. Não substitui `obj.print()` — coexiste. Útil para programas que fazem muito output de tipos diferentes:

```python
Transcript.show("hello").show_cr().show(x).show_cr()
```

Permite cascade sem que cada objeto saiba como se imprimir junto a outros. Já é mencionado em `INFECTIONS.md` linha 18 ("Transcript.show calls str(obj)") mas não encontrei a implementação no código atual — provavelmente foi removida ou nunca implementada.

---

## 9. Funcionalidade nova — `Block` como tipo de primeira classe

Hoje "block" = `lambda` Python. Smalltalk tem blocks com mensagens próprias: `[1+2] value`, `[:x | x*2] value: 5`, `[cond] whileTrue: [body]`.

**Proposta.** Criar `poop/types/block.py`:

```python
class Block(Object):
    def __init__(self, fn):
        self._fn = fn

    def value(self, *args):
        return self._fn(*args)

    def while_true(self, body):
        while bool(self._fn()):
            body.value()
        return none

    def while_false(self, body):
        while not bool(self._fn()):
            body.value()
        return none

    def repeat(self):  # infinite loop
        while True:
            self._fn()
```

Resolve o item 17 (`while_true` mora no objeto certo). Ergonomia depende de transformer que reescreva `lambda: ...` para `Block(lambda: ...)` — não trivial, pode ser opt-in via `block(lambda: ...)`.

---

## 10. Funcionalidade nova — `Symbol` (Smalltalk imutável e único)

`Symbol("foo")` é canonical e singleton em Smalltalk — `#foo == #foo` é sempre `true`. POOP poderia adicionar `Symbol` para chaves de Dict, mensagens passadas a `perform`, etc. Reduz alocações e ajuda a transmitir intenção. A implementação Python: cache em `Symbol("name")` que retorna a mesma instância para o mesmo nome.

---

## 11. Funcionalidade nova — `Object.respond_to(message: Str) -> Boolean`

Existe `has_attr` (atalho de `hasattr`). Smalltalk tem `respondsTo:` que verifica se o objeto responde àquela mensagem (basicamente o mesmo que `hasattr` mais `callable`). Adicionar:

```python
def respond_to(self, name: Str) -> Boolean:
    attr = getattr(self, name._value, None)
    return true if callable(attr) else false
```

Útil para duck typing sem `try/except AttributeError`.

---

## 12. Funcionalidade nova — `Object.perform(message_name, *args)`

Smalltalk: `obj perform: #foo with: 1 with: 2`. Equivalente a `getattr(obj, name)(*args)`. Hoje POOP tem `get_attr` mas não há atalho para "envia mensagem por nome". Proposta:

```python
def perform(self, name: Str, *args: Object) -> Object:
    method = getattr(self, name._value)
    return method(*args)
```

---

## 13. Funcionalidade nova — `times` em Int

Smalltalk: `5 timesRepeat: [Transcript show: 'hi']`. Equivalente em POOP:

```python
class Int(Object):
    def times(self, block: Callable[[], Any]) -> Int:
        for _ in range(self._value):
            block()
        return self
```

Útil porque hoje a única forma é `Int(0).to_(Int(4)).do(lambda i: ...)`, mais verboso.

---

## 14. Funcionalidade nova — `--validators-only` / `--transformers-only` / `--explain` no CLI

`poop/cli.py` aceita apenas o arquivo. Para depuração, seria útil:

- `poop --validators-only file.py` → roda só validators, mostra todos os erros (não para no primeiro). Hoje cada validator levanta na primeira ocorrência.
- `poop --transformers-only file.py` → mostra a árvore AST após transformers (ast.dump).
- `poop --explain file.py` → para cada construção bloqueada, mostra a regra que disparou e o substituto sugerido. Útil para onboarding.

---

## 15. Funcionalidade nova — fail-fast vs collect-all em Validator

Hoje cada validator lança `ValidationError` no primeiro problema. Programas grandes recebem feedback um erro por vez. **Proposta**: `Validator.validate` poderia retornar `list[ValidationError]` em vez de levantar, e o `Interpreter` decide o que fazer (printar todos, ou levantar o primeiro). Isso quebra a API atual — pode ser opt-in via `Interpreter(collect_all=True)`.

---

## 16. Funcionalidade nova — `ast.AsyncFunctionDef` está bloqueado mas `async`/`await` não têm validator próprio

`no_free_functions` bloqueia `AsyncFunctionDef` no top-level, mas dentro de classes, `async def` métodos seriam aceitos. Idem `await expr`, `async for`, `async with` — `async for`/`async with` têm validator (`no_loops`, `no_with`), mas `await` não. Em uma linguagem que não tem `Future` nem event loop POOP, `async`/`await` não fazem sentido. Adicionar `no_async`:

```python
class _NoAsyncVisitor(ast.NodeVisitor):
    def visit_AsyncFunctionDef(self, node):
        raise ValidationError("async functions are forbidden — POOP has no event loop", ...)

    def visit_Await(self, node):
        raise ValidationError("await is forbidden — POOP has no async runtime", ...)
```

---

## 17. Funcionalidade nova — `Number` mixin para `Int` + `Float` + `Complex`

Hoje as três classes duplicam `negated`, `__add__`, `__sub__`, etc. com tipos diferentes. Uma classe-base `Number` com hooks `_wrap(value)` por subclasse reduz ~150 linhas e abre porta para coerções `Int + Float → Float`, etc.

---

## 18. Filosofia — `properties` (`@property`) em tipos POOP contradizem "everything is a message"

`Int.real`, `Int.imag`, `Float.real`, `Complex.real`, `Interval.start` etc. são `@property`. Quem escreve `interval.start` está acessando um atributo, não enviando uma mensagem. Em Smalltalk, `start` seria um getter sem parens (mensagem unária). Em Python, sem parens vira atributo.

`INFECTIONS.md` (linha 408) diz que `@property` decorator é permitido como definição de classe, mas o **uso** (`obj.foo` sem parens) viola "object recebendo mensagem". Mais coerente: virar método (`interval.start()`).

Hoje há um leve mix:
- `Int.real` → property
- `Int.bit_count()` → método
- `Interval.start` → property
- `Interval.first()` → método (retorna a mesma coisa que `start`)

Padronizar tudo em métodos (com parens) é mais coerente.

---

## 19. Consistência — `__str__` e `__repr__` devem seguir a convenção Python em todos os tipos

Em Python, `__repr__` deve retornar uma representação que idealmente permita recriar o objeto (`eval(repr(x)) == x`), enquanto `__str__` retorna a forma legível para humanos. Hoje POOP define `__repr__ = __str__` na base `Object`, o que faz todos os tipos perderem a distinção — visível no REPL (item 1 trata `Str` especificamente, mas o problema é geral).

Exemplos do comportamento atual vs. esperado:

| Tipo | `str(x)` atual | `repr(x)` atual | `repr(x)` esperado |
|---|---|---|---|
| `Str("hello")` | `hello` | `hello` | `'hello'` |
| `Int(42)` | `42` | `42` | `42` (ok) |
| `List(Int(1), Int(2))` | `[1, 2]` | `[1, 2]` | `[1, 2]` (ok) |
| `none` | `None` | `None` | `None` (ok) |
| `true` | `True` | `True` | `True` (ok) |

O único tipo onde a distinção importa de verdade é `Str` — `repr` deve envolver em aspas simples, como CPython. Para os demais tipos numéricos e coleções, `str` e `repr` já coincidem com a convenção Python, então `__repr__ = __str__` está correto.

**Proposta concreta:** definir `__repr__` em `Str` para retornar `f"'{self._value}'"` (ou escapar aspas simples internas), mantendo `__repr__ = __str__` nos demais tipos.

---

## Resumo executivo

**Bugs corrigidos.** Nenhum pendente — todos foram resolvidos. (Dict.pop, Interval.includes, sum() return type, etc.).

**Refatorações de alto impacto completadas.** ✅ 7 (while_* na base de Boolean), 17 (Number mixin).

**Decisões filosóficas a documentar em INFECTIONS.md.** 1 (`is_instance` com tipo cru), 2 (operadores binários permitidos), 3 (while_true e o receiver irrelevante), 18 (properties).

**Funcionalidades novas com bom retorno por esforço.** 8 (Transcript), 9 (Block), 11 (respond_to), 12 (perform), 13 (Int.times), 16 (no_async).

**Consistência com convenção Python.** 1 (`Str.__repr__` esconde aspas no REPL), 19 (`__str__`/`__repr__` para todos os tipos).
