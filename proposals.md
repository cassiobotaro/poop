# Proposals — POOP code review

Review feita por Claude (Opus 4.7) considerando `INFECTIONS.md` e o pipeline `parse → validate → transform → execute`. Cada item indica caminho, linhas relevantes e uma sugestão concreta. Itens estão agrupados por intenção: refatoração, bug/inconsistência, alinhamento filosófico e novas funcionalidades.

---
## 1. Filosofia — `properties` (`@property`) em tipos POOP contradizem "everything is a message"

`Int.real`, `Int.imag`, `Float.real`, `Complex.real`, `Range.start` etc. são `@property`. Quem escreve `r.start` está acessando um atributo, não enviando uma mensagem. Em Smalltalk, `start` seria um getter sem parens (mensagem unária). Em Python, sem parens vira atributo.

`INFECTIONS.md` diz que `@property` decorator é permitido como definição de classe, mas o **uso** (`obj.foo` sem parens) viola "object recebendo mensagem". Mais coerente: virar método (`r.start()`).

Hoje há um leve mix:
- `Int.real` → property
- `Int.bit_count()` → método
- `Range.start` → property
- `Range.first()` → método (retorna a mesma coisa que `start`)

Padronizar tudo em métodos (com parens) é mais coerente.

---

## 2. Filosofia — `Boolean.while_true(cond_block, body_block)` é uma mensagem para o objeto errado

Em Smalltalk, `whileTrue:` é mensagem para um **block**, não para o booleano: `[cond] whileTrue: [body]`. O receiver é o block que retorna o booleano, não um bool literal.

POOP escolheu colocar `while_true` em `Boolean` (`true.while_true(cond, body)` ou `false.while_true(cond, body)` — funciona igual em ambos), o que **torna o receiver irrelevante**. Não há um valor de `true` ou `false` que mude o comportamento.

Alternativas:

1. Aceitar que receiver é decorativo e renomear para algo neutro: `loop(cond, body)` em algum lugar (mas onde?).
2. Definir `while_true` em `Object` (qualquer objeto pode disparar). Idiomático: `none.while_true(...)` ou `none.repeat(...)`. Pelo menos para de fingir que o booleano importa.
3. Fazer `Block` ser um tipo de primeira classe (envelope para callable) — proposta abaixo.

Hoje, ler `true.while_true(lambda: x < 10, lambda: x.print())` é confuso porque o `true` no início é decorativo.

---

## 3. Filosofia — duplicação `_TrueClass.while_true` vs `_FalseClass.while_true`

`poop/types/boolean.py:132-152` e `212-232`. As duas implementações de `while_true` (e `while_false`) são **idênticas**. Movê-las para a base `Boolean` elimina ~40 linhas duplicadas. O receiver não altera o comportamento (ver item 3), portanto:

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

## 4. Funcionalidade nova — `Block` como tipo de primeira classe

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

Resolve o item 3 (`while_true` mora no objeto certo). Ergonomia depende de transformer que reescreva `lambda: ...` para `Block(lambda: ...)` — não trivial, pode ser opt-in via `block(lambda: ...)`.

---

## Resumo executivo

**Bugs corrigidos.** Nenhum pendente — todos foram resolvidos. (Dict.pop, Range.includes, sum() return type, etc.).

**Refatorações de alto impacto.** 3 (while_* na base de Boolean).

**Decisões filosóficas a documentar em INFECTIONS.md.** 2 (while_true e o receiver irrelevante), 1 (properties).

**Funcionalidades novas com bom retorno por esforço.** 4 (Block).
