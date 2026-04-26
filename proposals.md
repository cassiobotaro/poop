# Proposals — POOP code review

Review feita por Claude (Opus 4.7) considerando `INFECTIONS.md` e o pipeline `parse → validate → transform → execute`. Cada item indica caminho, linhas relevantes e uma sugestão concreta. Itens estão agrupados por intenção: refatoração, bug/inconsistência, alinhamento filosófico e novas funcionalidades.

---

## 1. Refatoração — duplicação massiva nos validators

**O que existe hoje.** Existem ~35 validators em `poop/validators/` com o mesmo esqueleto:

```python
class No<X>Validator:
    def validate(self, tree: ast.Module) -> None:
        _No<X>Visitor().visit(tree)

class _No<X>Visitor(ast.NodeVisitor):
    def visit_Call(self, node: ast.Call) -> None:
        if isinstance(node.func, ast.Name) and node.func.id == "<x>":
            raise ValidationError(
                "<x>() is forbidden — use <substitute>",
                lineno=node.lineno, col_offset=node.col_offset,
            )
        self.generic_visit(node)
```

A única coisa que muda entre `no_abs.py`, `no_all.py`, `no_any.py`, `no_callable.py`, `no_dir.py`, `no_format.py`, `no_getattr.py`, `no_hasattr.py`, `no_hash.py`, `no_id.py`, `no_input.py`, `no_isinstance.py`, `no_issubclass.py`, `no_len.py`, `no_open.py`, `no_pow.py`, `no_print.py`, `no_repr.py`, `no_reversed.py`, `no_slice.py`, `no_sorted.py`, `no_sum.py`, `no_breakpoint.py`, `no_ascii.py`, `no_divmod.py`, `no_format.py` é o nome da função e a mensagem de erro. `no_bin.py`, `no_chr.py`, `no_enumerate.py`, `no_exec.py`, `no_exit.py`, `no_introspection.py`, `no_iter.py`, `no_setattr.py` adicionam apenas um `frozenset` de nomes.

**Proposta.** Introduzir um helper único:

```python
# poop/validators/_call_name.py
import ast
from collections.abc import Iterable
from poop.errors import ValidationError


def make_call_name_validator(
    *,
    forbidden: Iterable[str],
    message: str,  # template, recebe {name}
) -> type:
    names = frozenset(forbidden)

    class _Visitor(ast.NodeVisitor):
        def visit_Call(self, node: ast.Call) -> None:
            if isinstance(node.func, ast.Name) and node.func.id in names:
                raise ValidationError(
                    message.format(name=node.func.id),
                    lineno=node.lineno,
                    col_offset=node.col_offset,
                )
            self.generic_visit(node)

    class _Validator:
        def validate(self, tree: ast.Module) -> None:
            _Visitor().visit(tree)

    return _Validator
```

Cada `no_*.py` que hoje tem ~20 linhas vira ~3:

```python
NoLenValidator = make_call_name_validator(
    forbidden={"len"},
    message="{name}() is forbidden — use obj.len() instead",
)
```

**Ganhos.** Reduz ~700 linhas para ~150. Garante mensagens de erro com formato consistente. Diminui o atrito de adicionar uma nova "infecção". Mantém a API pública intacta (`No<X>Validator()`).

**Riscos.** Perde-se a docstring de classe granular — mitigável passando `__doc__` no factory. Stack trace de erros aponta para o helper em vez do arquivo específico — irrelevante porque a mensagem de erro já contém o nome do builtin proibido.

Aplicar a mesma ideia para validators que disparam em `ast.UnaryOp` (`no_not`, `no_unary_plus`, `no_invert`, `no_unary_minus` parcialmente) e `ast.Compare` (`no_is`, `no_in`).

---

## 2. Refatoração — duplicação igualmente grande nos transformers

Todos os transformers seguem o mesmo padrão:

```python
class XTransformer:
    BINDINGS: ClassVar[dict[str, object]] = {...}

    def transform(self, tree: ast.Module) -> ast.Module:
        tree = _XRewriter().visit(tree)
        ast.fix_missing_locations(tree)
        return tree
```

**Proposta.** Mover `transform()` para uma classe-base mínima:

```python
class _BaseTransformer:
    rewriter: type[ast.NodeTransformer]
    BINDINGS: ClassVar[dict[str, object]] = {}

    def transform(self, tree: ast.Module) -> ast.Module:
        tree = self.rewriter().visit(tree)
        ast.fix_missing_locations(tree)
        return tree
```

E cada transformer concreto declara apenas `rewriter = _XRewriter` e `BINDINGS`. Remove ~50 linhas de boilerplate e centraliza o `fix_missing_locations`, que hoje é repetido 16 vezes (e fácil de esquecer ao criar um novo transformer).

A API pública continua sendo o `Transformer` Protocol em `transformers/base.py`.

---

## 3. Refatoração — duplicação nos métodos de coleção (List, Tuple, Set, FrozenSet, Interval, Bytes, ByteArray, MemoryView, Dict)

Os métodos `do`, `map`, `filter`, `filter_false`, `find`, `reduce`, `sum`, `all`, `any` aparecem com implementação quase idêntica em **9 tipos**. Exemplos:

- `List.do`, `Tuple.do`, `Set.do`, `FrozenSet.do`, `Bytes.do`, `ByteArray.do`, `MemoryView.do`, `Interval.do` — todos fazem `deque(map(block, items), maxlen=0)` (Bytes/ByteArray/MemoryView envolvem cada item num `Int`).
- `List.all`, `Tuple.all`, `Set.all`, `FrozenSet.all`, `Interval.all` — todos fazem `true if builtins_all(bool(block(x)) for x in items) else false`.
- `find` aparece em todos (mesmo loop, mesmo retorno `none`).

**Proposta.** Introduzir um mixin `Iterable` interno:

```python
class _IterableMixin:
    """Mixin para tipos POOP que expõem __iter__. Concentra do/map/filter/etc."""

    def do(self, block):
        deque(map(block, self), maxlen=0)
        return self  # opcional, ver item 11

    def all(self, block):
        from poop.types.boolean import false, true
        return true if builtins_all(bool(block(x)) for x in self) else false

    def any(self, block):
        from poop.types.boolean import false, true
        return true if builtins_any(bool(block(x)) for x in self) else false

    def find(self, block):
        from poop.types.none import none
        for item in self:
            if bool(block(item)):
                return item
        return none

    def reduce(self, init, block):
        return reduce(block, self, init)

    def sum(self):
        from poop.types.int import Int
        items = list(self)
        if not items:
            return Int(0)  # ver item 5: hoje retorna 0 nativo
        return reduce(lambda a, b: a + b, items)
```

`map`/`filter` precisam saber o tipo de retorno (List → List, Set → Set, Interval → List, Bytes → List). Pode ser via método-fábrica `_collect(items) -> "concrete type"`.

**Ganhos.** Cada coleção fica ~60 linhas mais enxuta. Bug fixes em `find`/`all`/`any` se aplicam num único lugar. Reduz a chance de cada coleção evoluir de forma divergente.

---

## 4. Bug — `Dict.pop` / `Dict.setdefault` retornam tipos não validados

`poop/types/dict.py:91-101`:

```python
def pop(self, key: Object) -> Object:
    return self._data.pop(key)

def setdefault(self, key: Object, default: Object) -> Object:
    return self._data.setdefault(key, default)
```

`pop` levanta `KeyError` Python diretamente — sem chance de o usuário tratar via `Try(...).except_(KeyError, ...)` de forma idiomática (porque `KeyError.raise_` está no transformer, mas nada chama isso aqui — o exception nativo *é* compatível com `Try.except_`, então OK). Contudo, `pop(missing_key)` deveria, alinhado ao resto do `Dict` (`.at` retorna `none` para chave ausente), retornar `none` ou aceitar um default explícito. Hoje a inconsistência é: `at(missing) → none`, mas `pop(missing) → KeyError`. Decidir o contrato e documentar.

`setdefault` retorna o valor inserido — se o usuário passa um Python nativo, ele entra no `_data` e é retornado sem virar POOP. Adicionar verificação ou converter.

---

## 5. Bug — `__eq__` com tipos numéricos heterogêneos sempre retorna `false`

`Int(1) == Float(1.0)` → `false`. `Int(1) == Complex(1+0j)` → `false`. Em Python nativo, todos seriam `True`.

Isso pode ser **decisão de design** (tipos POOP são opacos uns aos outros) e parece consistente com a filosofia "everything is an object, including type" — mas não está documentado em `INFECTIONS.md`. Sugiro documentar explicitamente em INFECTIONS:

> **Comparações entre tipos numéricos POOP são heterogeneamente desiguais**: `Int(1) == Float(1.0) → false`. Para comparar valor numérico independente de tipo, converta primeiro: `i.float() == f`.

Caso contrário, é um buraco de surpresa que pode comer 30 minutos de debug do usuário.

---

## 6. Inconsistência — `do(block)` retorna `None` em vez de `self`

Ver `INFECTIONS.md` linha 483: *"Returning `self` enables cascades: `x.print().print()`."* Esse princípio é aplicado em `Object.print`, mas `do` (em todos os tipos) retorna `None`:

```python
def do(self, block: Callable[[Object], Any]) -> None:
    deque(map(block, self._items), maxlen=0)
```

Em Smalltalk, todo método retorna `self` por padrão (a menos que use `^value`). O princípio "retornar `self` para encadeamento" deveria valer para `do`, `clear`, `reverse`, `extend` etc. Hoje a maioria já retorna `self` — `do` é a exceção visível. Sugiro:

```python
def do(self, block) -> Self:
    deque(map(block, self), maxlen=0)
    return self
```

Permite `numbers.do(lambda x: x.print()).map(lambda x: x.times(Int(2))).print()`.

---

## 7. Inconsistência — `BINDINGS` montado depois da classe em `Try` e `With`

`poop/types/try_.py:71` e `poop/types/with_.py:51`:

```python
class Try(Object):
    BINDINGS: ClassVar[dict[str, object]] = {}
    ...
Try.BINDINGS = {"Try": Try}
```

Esse padrão é necessário porque o nome da classe não existe dentro do corpo dela. **Mas todos os outros transformers seguem outra convenção** — eles definem `BINDINGS` apontando para classes ou funções já importadas:

```python
class IntTransformer:
    BINDINGS: ClassVar[dict[str, object]] = {
        "_poop_int": Int,
        ...
    }
```

A diferença ficaria menos visível movendo `Try.BINDINGS` para um arquivo separado (ex.: `poop/transformers/try_.py`) que importa `Try` e expõe `BINDINGS`, alinhando-se ao resto do projeto. Hoje `Try` e `With` são tipos *e* "transformers" ao mesmo tempo, o que é coerente filosoficamente mas quebra o padrão de organização.

---

## 8. Inconsistência — `With` não está em `poop/types/__init__.py`

`poop/types/__init__.py` exporta todos os tipos POOP exceto `With`. Ou inclui `With` (consistência) ou retira `Try` para alinhar — `Try` está exposto, `With` não, sem motivo aparente.

---

## 9. Filosofia — `Object.is_instance(type_: type)` recebe tipo Python cru

`poop/types/object.py:59`:

```python
def is_instance(self, type_: type) -> Boolean:
```

O argumento é uma `type` Python — não há tipo POOP correspondente para "classe". Isso é coerente com `ExcType` em `Try` e contextos `With`, mas contradiz o princípio "todo tipo básico tem um equivalente POOP". Documentar a tradeoff em INFECTIONS (semelhante ao que já está feito para `Try`).

---

## 10. Filosofia — operadores binários `+`, `-`, `*`, `/`, `<<`, `>>`, `&`, `|`, `^` continuam permitidos

`Int.__add__`, `Int.__lshift__` etc. são *aliases* para mensagens (`add(other)`, `bit_shift_left(other)`). Mas `INFECTIONS.md` argumenta que `-x` "looks like an operator" e por isso é proibido. **Por que `a + b` é OK e `-a` não é?**

- `a + b` é `BinOp(Add)` — mesma família de "operadores que parecem procedurais".
- `-a` é `UnaryOp(USub)` — bloqueado em favor de `a.negated()`.

A justificativa em `INFECTIONS.md` para `+=` (linha 398) não cobre operadores binários simples. Há duas saídas coerentes:

1. **Documentar explicitamente** que operadores binários infixos ficam permitidos por ergonomia (mesma decisão de Smalltalk com `+`, `*` etc.). Adicionar à seção "Explicitly allowed".
2. **Bloquear todos** e exigir `a.add(b)`, `a.lt(b)` etc. — alinhado ao princípio mas drasticamente menos legível.

A opção 1 é claramente preferível, mas precisa estar em INFECTIONS para não ficar como inconsistência percebida.

Análogo: `==`, `!=`, `<`, `<=`, `>`, `>=` são `Compare` ASTs e estão permitidos — mesmo princípio.

---

## 11. Filosofia — `__getitem__` em `List`/`Tuple`/`Str`/`Bytes` está implementado mas é "morto" para POOP

Como `no_subscript` proíbe `obj[key]`, todos os `__getitem__` em tipos POOP são código que só funciona se chamado de Python externo (ex.: testes). Manter por compatibilidade Python é razoável, mas vale **um comentário no topo de cada `__getitem__`** explicando que ele é alcançável apenas via interop, não via POOP. Senão um futuro contributor pode achar que pode usar `[]` em código POOP.

Alternativa mais radical: remover os `__getitem__` (e `__contains__`, `__iter__` ficam por causa do `for` interno em transformers). Mas isso quebra interop, então melhor documentar.

---

## 12. Filosofia — `Str.__repr__ = __str__` esconde aspas em REPL

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

## 13. Filosofia — REPL imprime resultado mas não armazena `_`

CPython REPL armazena o último valor avaliado em `_`. Ao escrever uma expressão simples, o REPL POOP imprime o resultado (via commit `1488677`), mas não popula `_` no namespace. Adicionar isso eleva muito a usabilidade em sessão interativa:

```python
# poop/repl.py — após execução
if isinstance(last_node, ast.Expr):
    self._ns["_"] = last_value
```

Requer um pouco de cooperação no executor (`mode="single"` já imprime via `displayhook`).

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

`poop/types/boolean.py:132-152` e `212-232`. As duas implementações de `while_true` (e `while_false`) são **idênticas**. Movê-las para a base `Boolean` elimina ~40 linhas duplicadas. O receiver não altera o comportamento (ver item 19), portanto:

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

## 16. Performance — `from poop.types.boolean import false, true` em todo método

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

## 17. Performance / ergonomia — `singletons` para Int(0), Int(1), Str("")

Cada `Int(0)` aloca um novo objeto. Isso é custo desprezível para Python normal, mas em código POOP que faz `numbers.sum()` sobre coleção vazia, ou contadores em loops, há alocações repetidas. Smalltalk tradicionalmente faz cache de inteiros pequenos (semelhante a CPython com -5..256). Proposta: cache de `Int(-5)..Int(256)` no módulo `int.py`, retornado por `_poop_int(n)` quando aplicável.

Custo: pequena complexidade no factory. Ganho: alocação reduzida em hot loops.

---

## 18. Refatoração — `poop/transformers/dict.py:_poop_dict_from` tem ramos quase idênticos para Tuple/List

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

## 19. Funcionalidade nova — `Transcript`

Smalltalk tem `Transcript` como objeto global de saída. POOP hoje usa `obj.print()`. **Proposta**: adicionar um objeto `Transcript` no namespace padrão com `show`, `show_cr` (newline), `clear`. Não substitui `obj.print()` — coexiste. Útil para programas que fazem muito output de tipos diferentes:

```python
Transcript.show("hello").show_cr().show(x).show_cr()
```

Permite cascade sem que cada objeto saiba como se imprimir junto a outros. Já é mencionado em `INFECTIONS.md` linha 18 ("Transcript.show calls str(obj)") mas não encontrei a implementação no código atual — provavelmente foi removida ou nunca implementada.

---

## 20. Funcionalidade nova — `Block` como tipo de primeira classe

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

Resolve o item 19 (`while_true` mora no objeto certo). Ergonomia depende de transformer que reescreva `lambda: ...` para `Block(lambda: ...)` — não trivial, pode ser opt-in via `block(lambda: ...)`.

---

## 21. Funcionalidade nova — `Symbol` (Smalltalk imutável e único)

`Symbol("foo")` é canonical e singleton em Smalltalk — `#foo == #foo` é sempre `true`. POOP poderia adicionar `Symbol` para chaves de Dict, mensagens passadas a `perform`, etc. Reduz alocações e ajuda a transmitir intenção. A implementação Python: cache em `Symbol("name")` que retorna a mesma instância para o mesmo nome.

---

## 22. Funcionalidade nova — `Object.respond_to(message: Str) -> Boolean`

Existe `has_attr` (atalho de `hasattr`). Smalltalk tem `respondsTo:` que verifica se o objeto responde àquela mensagem (basicamente o mesmo que `hasattr` mais `callable`). Adicionar:

```python
def respond_to(self, name: Str) -> Boolean:
    attr = getattr(self, name._value, None)
    return true if callable(attr) else false
```

Útil para duck typing sem `try/except AttributeError`.

---

## 23. Funcionalidade nova — `Object.perform(message_name, *args)`

Smalltalk: `obj perform: #foo with: 1 with: 2`. Equivalente a `getattr(obj, name)(*args)`. Hoje POOP tem `get_attr` mas não há atalho para "envia mensagem por nome". Proposta:

```python
def perform(self, name: Str, *args: Object) -> Object:
    method = getattr(self, name._value)
    return method(*args)
```

---

## 24. Funcionalidade nova — `times` em Int

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

## 26. Funcionalidade nova — `--validators-only` / `--transformers-only` / `--explain` no CLI

`poop/cli.py` aceita apenas o arquivo. Para depuração, seria útil:

- `poop --validators-only file.py` → roda só validators, mostra todos os erros (não para no primeiro). Hoje cada validator levanta na primeira ocorrência.
- `poop --transformers-only file.py` → mostra a árvore AST após transformers (ast.dump).
- `poop --explain file.py` → para cada construção bloqueada, mostra a regra que disparou e o substituto sugerido. Útil para onboarding.

---

## 27. Funcionalidade nova — fail-fast vs collect-all em Validator

Hoje cada validator lança `ValidationError` no primeiro problema. Programas grandes recebem feedback um erro por vez. **Proposta**: `Validator.validate` poderia retornar `list[ValidationError]` em vez de levantar, e o `Interpreter` decide o que fazer (printar todos, ou levantar o primeiro). Isso quebra a API atual — pode ser opt-in via `Interpreter(collect_all=True)`.

---

## 28. Funcionalidade nova — `ast.AsyncFunctionDef` está bloqueado mas `async`/`await` não têm validator próprio

`no_free_functions` bloqueia `AsyncFunctionDef` no top-level, mas dentro de classes, `async def` métodos seriam aceitos. Idem `await expr`, `async for`, `async with` — `async for`/`async with` têm validator (`no_loops`, `no_with`), mas `await` não. Em uma linguagem que não tem `Future` nem event loop POOP, `async`/`await` não fazem sentido. Adicionar `no_async`:

```python
class _NoAsyncVisitor(ast.NodeVisitor):
    def visit_AsyncFunctionDef(self, node):
        raise ValidationError("async functions are forbidden — POOP has no event loop", ...)

    def visit_Await(self, node):
        raise ValidationError("await is forbidden — POOP has no async runtime", ...)
```

---

## 29. Funcionalidade nova — `Number` mixin para `Int` + `Float` + `Complex`

Hoje as três classes duplicam `negated`, `__add__`, `__sub__`, etc. com tipos diferentes. Uma classe-base `Number` com hooks `_wrap(value)` por subclasse reduz ~150 linhas e abre porta para coerções `Int + Float → Float`, etc.

---

## 33. Filosofia — `properties` (`@property`) em tipos POOP contradizem "everything is a message"

`Int.real`, `Int.imag`, `Float.real`, `Complex.real`, `Interval.start` etc. são `@property`. Quem escreve `interval.start` está acessando um atributo, não enviando uma mensagem. Em Smalltalk, `start` seria um getter sem parens (mensagem unária). Em Python, sem parens vira atributo.

`INFECTIONS.md` (linha 408) diz que `@property` decorator é permitido como definição de classe, mas o **uso** (`obj.foo` sem parens) viola "object recebendo mensagem". Mais coerente: virar método (`interval.start()`).

Hoje há um leve mix:
- `Int.real` → property
- `Int.bit_count()` → método
- `Interval.start` → property
- `Interval.first()` → método (retorna a mesma coisa que `start`)

Padronizar tudo em métodos (com parens) é mais coerente.

---

## 35. Documentação — `INFECTIONS.md` `Object.print` na seção Object não documenta o `flush`

Linha 481: `obj.print(end="")`. A implementação aceita `flush: bool = False`. Pequeno, mas um leitor pode pensar que `flush` não é suportado.

---

## Resumo executivo

**Bugs reais a corrigir.** Nenhum — todos foram corrigidos.

**Refatorações de alto impacto.** 1 (factory de validators), 2 (base de transformers), 3 (mixin de coleção iterável), 15 (while_* na base de Boolean), 29 (Number mixin).

**Decisões filosóficas a documentar em INFECTIONS.md.** 5 (eq heterogêneo), 9 (`is_instance` com tipo cru), 10 (operadores binários permitidos), 14 (while_true e o receiver irrelevante), 30 (properties).

**Funcionalidades novas com bom retorno por esforço.** 19 (Transcript), 20 (Block), 22 (respond_to), 23 (perform), 24 (Int.times), 28 (no_async).
