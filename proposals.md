# Propostas de Melhoria

Lista priorizada de melhorias verificadas no código com referências `file:line` reais. Categorias: **bug**, **refactor**, **type-ignore**, **architecture**, **test**.

---

## Alta prioridade

### 1. `Complex` retornando `NotImplemented` com 10 `type: ignore` (refactor/type-ignore)

**Local:** `poop/types/complex.py:54,60,66,72,78,84,90,96,102,108`

10 ocorrências de `return NotImplemented  # type: ignore[return-value]`. As assinaturas declaram `-> Complex` mas retornam `NotImplemented` (correto pelo protocolo Python para que `__radd__` etc. seja invocado).

**Correção:** mudar a assinatura para refletir a realidade. Opções:
- (a) `-> Complex | type[NotImplemented]` (verbosa mas precisa)
- (b) Remover `_coerce` retornando `None` e validar tipos na entrada com `TypeError` antes — mas isso quebra o protocolo de operadores binários do Python.
- (c) Mais limpo: usar `from typing import Any; -> Any` e documentar — perde-se precisão de tipo, mas elimina os 10 ignores.

**Recomendação:** (a). É o padrão correto, mesmo verboso. **Esforço:** pequeno. **Impacto:** elimina 10 supressões.

---

## Média prioridade

### 2. `# ty: ignore[unresolved-attribute]` nas lambdas com `.abs()` (type-ignore)

**Local:** `tests/test_types/test_list.py:207,336`, `tests/test_types/test_tuple.py:203`

Adicionado em commit recente (`0ba6ac9`). A causa raiz é a assinatura `Callable[[Object], Any]` em `sorted`/`sort`, e `Object` não tem `abs`.

**Correção alternativa:** anotar a lambda explicitamente — `lambda x: cast(Int, x).abs()` — ou usar `TypeVar` no parâmetro `key`:
```python
T = TypeVar("T", bound=Object)
def sorted(self, key: Callable[[T], Any] | None = None) -> List: ...
```
mas o caller perderia covariância. Avaliar se vale a complexidade extra para 3 ignores.

**Esforço:** pequeno-médio. **Impacto:** baixo (3 supressões).

---

## Baixa prioridade / oportunidades

### 3. Boilerplate de comparação em `Int`/`Float`/`Str` (refactor)

**Local:** `poop/types/int.py`, `poop/types/float.py`, `poop/types/string.py`

Os três tipos repetem o mesmo padrão para `__eq__`, `__ne__`, `__lt__`, `__le__`, `__gt__`, `__ge__`: `isinstance` check + retorno de singleton `true`/`false`. ~30 linhas de duplicação.

**Correção:** um `_ComparableMixin` semelhante ao `_IterableMixin`:
```python
class _ComparableMixin:
    @abstractmethod
    def _compare_value(self) -> Any: ...
    @abstractmethod
    def _compare_type(self) -> type: ...
    def __eq__(self, other): ...
```

**Esforço:** médio. **Impacto:** -90 linhas, manutenção mais simples ao adicionar novos tipos comparáveis. Mas o ROI é menor que o do `_IterableMixin` por que comparações são código simples.

---

### 4. Falta `Float.complex()` (architecture)

**Local:** `poop/types/float.py` (método ausente)

`Int` tem `.float()`. `Float` tem `.int()`. Nem `Int` nem `Float` têm `.complex()`. INFECTIONS.md:442 explicitamente recomenda conversões explícitas como caminho idiomático: *"To compare numeric values across types, convert explicitly first: `i.float() == f`, `f.int() == i`, `i.complex() == c`."* — então `complex()` deveria existir.

**Correção:** adicionar `complex()` em `Int` e `Float`:
```python
def complex(self) -> Complex:
    from poop.types.complex import Complex
    return Complex(complex(self._value))
```

**Esforço:** pequeno. **Impacto:** completa a API documentada.

---

### 5. Subtests do pytest 9 — não há ganho real (test/architecture)

**Local:** todos os tests

Avaliação anterior já feita: nenhum teste tem laços `for` com múltiplas asserções que se beneficiariam de `subtests`. Os 2 `parametrize` existentes já dão relatórios separados por valor. **Nenhuma ação recomendada.**

---

## Resumo executivo

| # | Categoria | Esforço | Impacto |
|---|---|---|---|
| 1 | `Complex` `NotImplemented` ignores | P | M |
| 2 | `ty: ignore` `.abs()` | P-M | B |
| 3 | `_ComparableMixin` | M | B-M |
| 4 | `Float.complex()` ausente | P | B |

Legenda: **T**rivial, **P**equeno, **M**édio · **B**aixo, **M**édio, **A**lto.

**Recomendação de ordem:** 1 → 4 → 3 → 2.
