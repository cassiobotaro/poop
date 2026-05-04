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

### 2. `_poop_complex_from` silencia tipos inválidos com `0` (bug)

**Local:** `poop/transformers/complex.py:27-28`

```python
r = real._value if isinstance(real, (Int, Float)) else 0  # type: ignore[union-attr]
i = imag._value if isinstance(imag, (Int, Float)) else 0  # type: ignore[union-attr]
```

Se o usuário passar `complex(None, x)` ou outro tipo não suportado, o transformer silenciosamente converte para `0` em vez de erro. Comportamento divergente do `complex()` nativo do Python (que erra com `TypeError`).

**Correção:** levantar `TypeError` quando o tipo não for `Int`/`Float`/numérico nativo. Os dois `type: ignore` desaparecem porque o `else` deixa de existir.

**Esforço:** pequeno. **Impacto:** comportamento mais previsível, -2 ignores.

---

### 3. `# ty: ignore[unresolved-attribute]` nas lambdas com `.abs()` (type-ignore)

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

### 4. Boilerplate de comparação em `Int`/`Float`/`Str` (refactor)

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

### 5. Falta `Float.complex()` (architecture)

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

### 6. Cobertura de teste para `Tuple` como chave de `Dict` (test)

**Local:** `tests/test_types/test_tuple.py`, `tests/test_types/test_dict.py`

`Tuple.__hash__` existe (`poop/types/tuple.py:93`). Mas não vi teste validando que `Dict({Tuple(Int(1), Int(2)): Str("v")})` funciona — caso clássico de uso. Falha aqui seria embaraçosa.

**Correção:** adicionar teste cobrindo `Tuple` como chave de `Dict`. **Esforço:** trivial. **Impacto:** baixo, mas evita regressão.

---

### 7. Subtests do pytest 9 — não há ganho real (test/architecture)

**Local:** todos os tests

Avaliação anterior já feita: nenhum teste tem laços `for` com múltiplas asserções que se beneficiariam de `subtests`. Os 2 `parametrize` existentes já dão relatórios separados por valor. **Nenhuma ação recomendada.**

---

## Resumo executivo

| # | Categoria | Esforço | Impacto |
|---|---|---|---|
| 1 | `Complex` `NotImplemented` ignores | P | M |
| 2 | `_poop_complex_from` silencioso | P | M |
| 3 | `ty: ignore` `.abs()` | P-M | B |
| 4 | `_ComparableMixin` | M | B-M |
| 5 | `Float.complex()` ausente | P | B |
| 6 | Teste `Tuple` como chave de `Dict` | T | B |

Legenda: **T**rivial, **P**equeno, **M**édio · **B**aixo, **M**édio, **A**lto.

**Recomendação de ordem:** 6 → 2 → 1 → 5 → 4 → 3.
Item 6 é o único "quick win" trivial restante.
