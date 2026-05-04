# Propostas de Melhoria

Lista priorizada de melhorias verificadas no código com referências `file:line` reais. Categorias: **bug**, **decisão em aberto**.

Princípio em jogo (`INFECTIONS.md:16`): *"Activate validator only when the substitute exists — blocking without offering an alternative only breaks code without teaching anything."*

---

## Alta prioridade

### 1. Implementar `Object.format(spec)` — substituto faltante para `format()` (bug)

**Local:** `poop/types/object.py` (adicionar método); `poop/validators/no_format.py:5`; `INFECTIONS.md:271-275`.

O validator `no_format` rejeita `format(x, spec)` e a documentação promete o substituto `obj.format(spec)`, mas o método não existe em `Object`. É o único caso em todo o conjunto de validators ativos onde o contrato validator↔substituto está rompido.

**Implementação esperada** (segue o padrão de `repr`/`ascii`/`get_attr`):

```python
def format(self, spec: Str) -> Str:
    from poop.types.string import Str
    return Str(builtins.format(self, spec._value))
```

**Testes em `tests/test_types/test_object.py`:**
- `Int(42).format(Str("x"))` → `Str("2a")`
- `Float(3.14159).format(Str(".2f"))` → `Str("3.14")`
- `Str("abc").format(Str(">5"))` → `Str("  abc")`
- spec inválido propaga `ValueError` do builtin

**Esforço:** pequeno (~5 linhas + 4 testes). **Impacto:** fecha a única lacuna validator↔substituto.

---

## Decisões em aberto — substituto existe com nome diferente

Itens onde o substituto funciona, mas o nome do método não espelha o builtin. Implementar é opcional — depende de priorizar nomes espelhados vs. API enxuta.

### 2. `slice()` → adicionar alias `.slice(start, stop, step)`?

**Local hoje:** `poop/types/list.py:42`, `poop/types/tuple.py:37`, `poop/types/string.py:50`, `poop/types/bytes.py:36`, `poop/types/byte_array.py:30`, `poop/types/range.py:32` — todos expõem `copy_from_to(start, stop, step)`. Documentado em `INFECTIONS.md:281`.

**Decisão:** manter só `copy_from_to`, ou adicionar `.slice(...)` como alias para alinhar com o nome do builtin?

### 3. `enumerate(col)` → `col.enumerate()`?

**Local sugerido:** `poop/types/_iterable_mixin.py` (cobriria `List`, `Tuple`, `Set`, `Range`, `Bytes`, `ByteArray` numa única implementação).

**Hoje:** `INFECTIONS.md:287` aponta `col.map(block)` / `col.reduce(init, block)` com índice manual.

**Comportamento esperado:** retornar `List` de `Tuple(Int(index), item)`.

**Decisão:** implementar `_IterableMixin.enumerate()` ou manter substituto indireto?

### 4. `zip(a, b)` → `a.zip(other)`?

**Local sugerido:** `poop/types/_iterable_mixin.py` aceitando outra coleção.

**Comportamento esperado:** retornar `List` de `Tuple(item_a, item_b)`, parando no menor.

**Decisão:** implementar ou manter substituto indireto via `map`/`reduce`?

### 5. `iter(col)` / `next(it)` → tipo `Iterator` first-class?

**Hoje:** iteração apenas via `col.do(block)` (`INFECTIONS.md:294`).

**Implementação:** invasiva — requer novo tipo `Iterator` em `poop/types/` + transformer correspondente em `poop/transformers/` (assim como `Block` tem o seu).

**Decisão:** introduzir iterator first-class, ou manter o modelo Smalltalk puro (apenas `do`)?

---

## Decisões em aberto — reavaliar "intencional"

Itens hoje categorizados como "sem substituto possível" (`INFECTIONS.md:299-345`), mas que merecem revisão.

### 6. `setattr(obj, name, val)` → `obj.set_attr(name, val)`?

**Assimetria atual:** `Object` expõe `get_attr` (`poop/types/object.py:84`) e `has_attr` (`poop/types/object.py:87`) mas não há `set_attr`. `INFECTIONS.md:299-304` diz apenas "use class methods", o que já não é a regra para `getattr`/`hasattr`.

**Decisão:** completar o trio com `set_attr` (e `del_attr` simétrico, item 7)?

### 7. `delattr(obj, name)` → `obj.del_attr(name)`?

Par do item 6. Mesma justificativa de simetria.

### 8. `vars(obj)` → `obj.vars()` retornando `Dict`?

**Hoje:** englobado em `no_introspection` (`poop/validators/no_introspection.py`, `INFECTIONS.md:312`) junto com `globals()`/`locals()`.

**Distinção importante:** `vars(obj)` numa instância retorna `__dict__` — isso é **estado da instância**, não escopo léxico. POOP usa `__slots__`, então o substituto natural seria iterar os slots e produzir `Dict[Str, Object]`.

`globals()`/`locals()` continuam sem substituto (são escopo léxico real).

**Decisão:** separar `vars` de `no_introspection` e dar um substituto `obj.vars()` em `Object`?

### 9. `input(prompt)` → introduzir tipo `Console` / `Stdin`?

**Hoje:** `INFECTIONS.md:343-345` declara "interactive I/O — no POOP equivalent".

**Observação:** Smalltalk *modela* I/O interativo (`Transcript`, etc.). Substituto natural: objeto POOP `Console` com `Console.read_line(prompt: Str) -> Str`.

**Escopo:** grande — novo subsistema de I/O.

**Decisão:** vale o investimento ou mantém banido?

### 10. `open(path)` → tipo `Path` POOP inspirado em `pathlib`?

**Hoje:** `INFECTIONS.md:349-351` declara "file I/O — no POOP equivalent".

**Observação importante:** o `pathlib` da stdlib já é **orientado a objetos** — `Path("foo.txt").read_text()`, `Path("dir").iterdir()`, `Path("a").exists()`. A API casa naturalmente com o modelo de mensagens do POOP, dispensando um "subsistema novo" pensado do zero.

**Modelagens possíveis:**
- **(a) Wrapper sobre `pathlib.Path`** — `Path` POOP envolve `pathlib.Path` e expõe métodos como `read_text() -> Str`, `read_lines() -> List[Str]`, `write_text(content: Str) -> Path`, `exists() -> Boolean`, `iterdir() -> List[Path]`. Mais barato, leveraging pathlib testado.
- **(b) `Str.open(mode)` retornando `File` POOP** — alternativa originalmente proposta, mais próxima do builtin `open()` mas exige desenhar do zero o ciclo de vida (`close`, context manager via `With`).

**Recomendação:** (a). Pathlib já fez o trabalho de "OO-ificar" I/O de filesystem; POOP herda isso quase de graça. Para o `open()` em si, basta `Path("foo").read_text()` / `write_text()` cobrir a maior parte dos usos sem precisar de file handles abertos.

**Local sugerido:** `poop/types/path.py` (novo) + transformer em `poop/transformers/path.py` para interceptar `open(...)` rewriting para `Path(...).read_text()` quando o padrão for óbvio (ou simplesmente deixar o usuário escrever `Path("foo").read_text()` diretamente).

**Escopo:** menor que reimplementar I/O do zero — wrapper sobre `pathlib` + métodos delegando.

**Decisão:** adotar a abordagem (a) com `pathlib` como base, ou desenhar `File` do zero, ou manter banido?

---

## Decisões em aberto — semântica da linguagem

### 11. Avaliação de operadores binários no estilo Smalltalk (esquerda-para-direita, sem precedência)?

**Hoje:** Python avalia `3 + 1 * 2` como `3 + (1 * 2) = 5` (precedência: `*` antes de `+`). POOP herda isso pois o parser é o do Python (`poop/parser.py` → `ast.parse`).

**Em Smalltalk:** mensagens binárias são avaliadas **esquerda-para-direita sem precedência**. `3 + 1 * 2` lê-se "envia `+ 1` para `3`, depois `* 2` para o resultado" → `(3 + 1) * 2 = 8`. É consequência direta do princípio "tudo é mensagem para um objeto".

**Tensão de princípios em POOP:**
- `INFECTIONS.md:8` — "Everything is an object and every operation is message passing".
- `INFECTIONS.md` (Active types) — "Binary infix operators (`+`, `-`, `*`, `/`, `<<`, `>>`, `&`, `|`, `^`, `==`, `!=`, `<`, `<=`, `>`, `>=`)" são **explicitamente permitidos**.

Se cada `+`, `*`, etc. é mensagem (`__add__`, `__mul__`), então o "agrupamento" via precedência Python é uma decisão artificial — o leitor humano espera message-passing puro.

**Implementação possível:** novo transformer em `poop/transformers/binop_left_assoc.py` que reescreve `ast.BinOp` para ser left-associative ignorando precedência:

```python
class _LeftAssocRewriter(ast.NodeTransformer):
    def visit_BinOp(self, node: ast.BinOp) -> ast.AST:
        # Junta cadeias de BinOp em pós-ordem reagrupando esquerda-para-direita
        # exceto onde houver parênteses explícitos (já refletidos na árvore).
        ...
```

Detalhe: parênteses explícitos no código fonte (`3 + (1 * 2)`) viram subárvores aninhadas e devem ser preservados — o transformer só reordena cadeias planas.

**Trade-offs:**
- **Pró:** consistência com o princípio "tudo é mensagem"; código POOP fica mais previsível pra quem lê como diálogo de objetos; alinha com Smalltalk-isms já adotados (`do:`, `if_true:`).
- **Contra:** quebra a expectativa de qualquer programador Python que olhe o código; expressões matemáticas precisam parênteses explícitos para semântica usual (`3 + (1 * 2)`); ferramentas estáticas (ty, IDE inspections) avaliam com precedência Python e poderiam mostrar resultados diferentes do runtime; muito "infectivo" — afeta toda expressão aritmética em todos os exemplos.
- **Mitigação parcial:** validator opcional que pede parênteses em qualquer cadeia mista de operadores diferentes, forçando o autor a explicitar — mas isso é poluição sintática.

**Casos a considerar:**
- Comparações encadeadas (`a < b < c`) — Python já tem semântica especial; preservar ou rejeitar?
- Operadores unários (`-x`) — já banidos via `no_unary_minus`, então não interferem.
- Atribuição aumentada (`x += y * z`) — o RHS sofre o mesmo reordenamento?

**Esforço:** médio (transformer + testes + atualização de exemplos que dependem de precedência implícita). **Impacto:** mudança semântica observável em todo programa POOP com operadores misturados; alinha a linguagem com seu princípio fundador.

**Decisão:** adotar avaliação esquerda-para-direita estilo Smalltalk, ou manter precedência Python por pragmatismo?

---

## Decisões em aberto — documentação

### 12. Site de documentação com MkDocs?

**Hoje:** documentação espalhada em `README.md` (visão geral), `INFECTIONS.md` (catálogo de validators/transformers/types — 90+ seções), `CLAUDE.md` (guia interno) e `proposals.md` (este backlog). Sem navegação, sem busca, sem versionamento publicado.

**Proposta:** adotar [MkDocs](https://www.mkdocs.org/) com tema [Material](https://squidpalm.github.io/mkdocs-material/) para gerar site estático navegável.

**Estrutura sugerida em `docs/`:**
- `index.md` — landing page (extraído de `README.md`)
- `getting-started.md` — instalar, rodar primeiro programa POOP
- `principles.md` — princípios da linguagem (extraído de `INFECTIONS.md` "Principles")
- `infections/validators.md` — um item por validator (gerado/extraído de `INFECTIONS.md`)
- `infections/transformers.md` — idem para transformers
- `types/` — uma página por tipo POOP (`Object`, `Int`, `Str`, etc.) com seus métodos
- `examples.md` — apontador para `examples/`
- `contributing.md` — workflow, commits atômicos, princípios de design

**Setup mínimo:**
- `mkdocs.yml` no root (config + nav)
- `mkdocs` + `mkdocs-material` em `[dependency-groups.dev]` no `pyproject.toml`
- `uv run mkdocs serve` para preview local; `uv run mkdocs build` para gerar `site/`
- Opcional: GitHub Pages via Action (`mkdocs gh-deploy`).

**Bônus considerados:**
- `mkdocstrings[python]` para gerar API reference automaticamente a partir de docstrings dos tipos POOP — alinha com a regra "every relevant dunder gets an alias com nome Python" e expõe a API rica.
- Plugin `mkdocs-autorefs` para links cruzados entre páginas.

**Trade-offs:**
- **Manter** `INFECTIONS.md` como single-source-of-truth e gerar páginas a partir dele (script de extração) — evita duplicação, mas exige tooling.
- **Migrar** o conteúdo para arquivos separados em `docs/` — mais limpo no final, mas exige atualizar o workflow ("Após cada infection, atualizar `docs/infections/...`" em vez de `INFECTIONS.md`).

**Esforço:** médio (setup ~1h; migração de conteúdo dependendo da escolha de SSOT). **Impacto:** descoberta da linguagem POOP por novos usuários melhora drasticamente; busca textual no site; histórico publicado.

**Decisão:** adotar MkDocs? Se sim, qual SSOT — `INFECTIONS.md` extraído ou `docs/` migrado?

---

## Permanecem banidos (sem proposta)

Genuinamente sem substituto possível dentro do modelo POOP:

- `exec`/`eval`/`compile` — metaprogramação, contraria o princípio estático.
- `exit`/`quit` — controle de processo, fora do modelo de objetos.
- `breakpoint` — handshake de debugger, não é operação de domínio.
- `globals()`/`locals()` — introspecção de escopo léxico (estado de instância já é acessível).
- `del` — statement, não builtin function.
