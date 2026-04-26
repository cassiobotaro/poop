# Proposals — POOP code review

Review feita por Claude (Opus 4.7) considerando `INFECTIONS.md` e o pipeline `parse → validate → transform → execute`. Cada item indica caminho, linhas relevantes e uma sugestão concreta. Itens estão agrupados por intenção: refatoração, bug/inconsistência, alinhamento filosófico e novas funcionalidades.

---
## 1. Refatoração — `poop/transformers/dict.py:_poop_dict_from` tem ramos quase idênticos para Tuple/List

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

## 2. Funcionalidade nova — `Transcript`

Smalltalk tem `Transcript` como objeto global de saída. POOP hoje usa `obj.print()`. **Proposta**: adicionar um objeto `Transcript` no namespace padrão com `show`, `show_cr` (newline), `clear`. Não substitui `obj.print()` — coexiste. Útil para programas que fazem muito output de tipos diferentes:

```python
Transcript.show("hello").show_cr().show(x).show_cr()
```

Permite cascade sem que cada objeto saiba como se imprimir junto a outros. Já é mencionado em `INFECTIONS.md` linha 18 ("Transcript.show calls str(obj)") mas não encontrei a implementação no código atual — provavelmente foi removida ou nunca implementada.

---

## 3. Funcionalidade nova — `Block` como tipo de primeira classe

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

## 4. Funcionalidade nova — `Symbol` (Smalltalk imutável e único)

`Symbol("foo")` é canonical e singleton em Smalltalk — `#foo == #foo` é sempre `true`. POOP poderia adicionar `Symbol` para chaves de Dict, mensagens passadas a `perform`, etc. Reduz alocações e ajuda a transmitir intenção. A implementação Python: cache em `Symbol("name")` que retorna a mesma instância para o mesmo nome.

---

## 5. Funcionalidade nova — `Object.respond_to(message: Str) -> Boolean`

Existe `has_attr` (atalho de `hasattr`). Smalltalk tem `respondsTo:` que verifica se o objeto responde àquela mensagem (basicamente o mesmo que `hasattr` mais `callable`). Adicionar:

```python
def respond_to(self, name: Str) -> Boolean:
    attr = getattr(self, name._value, None)
    return true if callable(attr) else false
```

Útil para duck typing sem `try/except AttributeError`.

---

## 6. Funcionalidade nova — `Object.perform(message_name, *args)`

Smalltalk: `obj perform: #foo with: 1 with: 2`. Equivalente a `getattr(obj, name)(*args)`. Hoje POOP tem `get_attr` mas não há atalho para "envia mensagem por nome". Proposta:

```python
def perform(self, name: Str, *args: Object) -> Object:
    method = getattr(self, name._value)
    return method(*args)
```

---

## 7. Funcionalidade nova — `times` em Int

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

## 8. Funcionalidade nova — `--validators-only` / `--transformers-only` / `--explain` no CLI

`poop/cli.py` aceita apenas o arquivo. Para depuração, seria útil:

- `poop --validators-only file.py` → roda só validators, mostra todos os erros (não para no primeiro). Hoje cada validator levanta na primeira ocorrência.
- `poop --transformers-only file.py` → mostra a árvore AST após transformers (ast.dump).
- `poop --explain file.py` → para cada construção bloqueada, mostra a regra que disparou e o substituto sugerido. Útil para onboarding.

---

## 9. Funcionalidade nova — fail-fast vs collect-all em Validator

Hoje cada validator lança `ValidationError` no primeiro problema. Programas grandes recebem feedback um erro por vez. **Proposta**: `Validator.validate` poderia retornar `list[ValidationError]` em vez de levantar, e o `Interpreter` decide o que fazer (printar todos, ou levantar o primeiro). Isso quebra a API atual — pode ser opt-in via `Interpreter(collect_all=True)`.

---

## 10. Funcionalidade nova — `ast.AsyncFunctionDef` está bloqueado mas `async`/`await` não têm validator próprio

`no_free_functions` bloqueia `AsyncFunctionDef` no top-level, mas dentro de classes, `async def` métodos seriam aceitos. Idem `await expr`, `async for`, `async with` — `async for`/`async with` têm validator (`no_loops`, `no_with`), mas `await` não. Em uma linguagem que não tem `Future` nem event loop POOP, `async`/`await` não fazem sentido. Adicionar `no_async`:

```python
class _NoAsyncVisitor(ast.NodeVisitor):
    def visit_AsyncFunctionDef(self, node):
        raise ValidationError("async functions are forbidden — POOP has no event loop", ...)

    def visit_Await(self, node):
        raise ValidationError("await is forbidden — POOP has no async runtime", ...)
```

---

## 11. Funcionalidade nova — `Number` mixin para `Int` + `Float` + `Complex`

Hoje as três classes duplicam `negated`, `__add__`, `__sub__`, etc. com tipos diferentes. Uma classe-base `Number` com hooks `_wrap(value)` por subclasse reduz ~150 linhas e abre porta para coerções `Int + Float → Float`, etc.

---

## 12. Filosofia — `properties` (`@property`) em tipos POOP contradizem "everything is a message"

`Int.real`, `Int.imag`, `Float.real`, `Complex.real`, `Interval.start` etc. são `@property`. Quem escreve `interval.start` está acessando um atributo, não enviando uma mensagem. Em Smalltalk, `start` seria um getter sem parens (mensagem unária). Em Python, sem parens vira atributo.

`INFECTIONS.md` (linha 408) diz que `@property` decorator é permitido como definição de classe, mas o **uso** (`obj.foo` sem parens) viola "object recebendo mensagem". Mais coerente: virar método (`interval.start()`).

Hoje há um leve mix:
- `Int.real` → property
- `Int.bit_count()` → método
- `Interval.start` → property
- `Interval.first()` → método (retorna a mesma coisa que `start`)

Padronizar tudo em métodos (com parens) é mais coerente.

---

## 13. Renomeação — `Interval` → `Range`

`poop/types/interval.py` expõe o tipo como `Interval`, mas o conceito é idêntico ao `range` do Python e ao `Range` de outras linguagens. Em POOP, o tipo é criado via `Int.to_(limit)` e representa uma sequência inteira — semanticamente um intervalo, mas o nome `Range` é mais reconhecível e alinhado com o vocabulário do domínio.

Impacto da renomeação:

- `poop/types/interval.py` → `poop/types/range.py`; classe `Interval` → `Range`
- `poop/transformers/range.py` — já usa o nome `Range` internamente (`RangeTransformer`); ajustar imports
- `poop/types/__init__.py` — exportar `Range` em vez de (ou além de) `Interval`
- Todos os arquivos que importam `Interval`: `list.py`, `tuple.py`, `set.py`, `frozen_set.py`, `int.py`, `dict.py`, testes
- `INFECTIONS.md` — ocorrências de "Interval"
- Manter `Interval` como alias depreciado é opcional; dado que não há interop externo, pode-se renomear diretamente

---

## 14. Filosofia — `Boolean.while_true(cond_block, body_block)` é uma mensagem para o objeto errado

Em Smalltalk, `whileTrue:` é mensagem para um **block**, não para o booleano: `[cond] whileTrue: [body]`. O receiver é o block que retorna o booleano, não um bool literal.

POOP escolheu colocar `while_true` em `Boolean` (`true.while_true(cond, body)` ou `false.while_true(cond, body)` — funciona igual em ambos), o que **torna o receiver irrelevante**. Não há um valor de `true` ou `false` que mude o comportamento.

Alternativas:

1. Aceitar que receiver é decorativo e renomear para algo neutro: `loop(cond, body)` em algum lugar (mas onde?).
2. Definir `while_true` em `Object` (qualquer objeto pode disparar). Idiomático: `none.while_true(...)` ou `none.repeat(...)`. Pelo menos para de fingir que o booleano importa.
3. Fazer `Block` ser um tipo de primeira classe (envelope para callable) — proposta abaixo.

Hoje, ler `true.while_true(lambda: x < 10, lambda: x.print())` é confuso porque o `true` no início é decorativo.

---

## 15. Filosofia — duplicação `_TrueClass.while_true` vs `_FalseClass.while_true`

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

## Resumo executivo

**Bugs corrigidos.** Nenhum pendente — todos foram resolvidos. (Dict.pop, Interval.includes, sum() return type, etc.).

**Refatorações de alto impacto completadas.** ✅ 1 (while_* na base de Boolean), 11 (Number mixin).

**Decisões filosóficas a documentar em INFECTIONS.md.** 17 (while_true e o receiver irrelevante), 12 (properties).

**Funcionalidades novas com bom retorno por esforço.** 2 (Transcript), 3 (Block), 5 (respond_to), 6 (perform), 7 (Int.times), 10 (no_async).

**Renomeações.** 13 (`Interval` → `Range`).
