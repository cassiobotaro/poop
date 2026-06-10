# Proposals

### 170. `http.HTTPStatus` / `http.HTTPMethod` members are raw CPython enum objects — every read path leaks

- **Where:** `poop/types/http.py:327-328` (`Http.HTTPStatus` / `Http.HTTPMethod` re-export `_http.HTTPStatus` / `_http.HTTPMethod` unwrapped), `poop/types/http.py:29-42` (the `_missing_` patch that makes POOP `Int`/`Str` arguments resolve to members — proof that member lookup is an intended user path, not an internal token)
- **Leak:** the two enums are bound into the user namespace as the raw CPython
  classes, so every value that comes out of them is a bare Python object: the
  member itself (`HTTPStatus.OK`) answers no POOP message; `.value` is a raw
  `int`, `.phrase` / `.description` raw `str`; member equality answers a raw
  `bool`, so the one branching idiom POOP offers —
  `(status == HTTPStatus.OK).if_true(...)` — crashes, making status dispatch
  impossible. The module even patches `_missing_` so `HTTPStatus(Int(200))`
  resolves — and then hands back the raw member, so the supported POOP-side
  construction path leaks too. Distinct from entry 144 (POOP enum-family
  *user classes* leak operator results — those members at least carry
  `name_str`/`value_object`) and from entry 149's constants sweep (which
  excluded `enum.STRICT`-style *argument tokens*; `HTTPStatus` members are
  read as user-facing values, not passed back into wrapper calls).
- **Evidence:** e2e (`uv run python main.py ...`), each line crashing
  independently:

  ```python
  http.HTTPStatus.OK.print()
  # poop: 'HTTPStatus' object has no attribute 'print'   (Python: HTTPStatus.OK)
  http.HTTPStatus.OK.phrase.print()
  # poop: 'str' object has no attribute 'print'          (Python: OK)
  http.HTTPStatus(200).value.print()
  # poop: 'int' object has no attribute 'print'          (Python: 200)
  (http.HTTPStatus.OK == http.HTTPStatus.OK).if_true(lambda: "ok".print())
  # poop: 'bool' object has no attribute 'if_true'       (Python: True branch)
  http.HTTPMethod.GET.print()
  # poop: 'HTTPMethod' object has no attribute 'print'   (Python: HTTPMethod.GET)
  ```

  Probes of the sibling namespaces show this is the only raw-enum door of its
  kind on the surface: `signal`/`socket`/`re`/`ssl` expose their flag values
  as POOP `Int` constants (`signal.Signals` / `ssl.TLSVersion` are simply
  absent), so `http` is the lone namespace handing whole raw enum classes to
  user code as values.
- **Proposed fix:** rebuild both enums over the POOP enum-family bases from
  `poop/types/enum.py` instead of re-exporting CPython's: at import time
  construct a POOP `IntEnum` (`HTTPStatus`) and POOP `StrEnum`-shaped class
  (`HTTPMethod`) from `[(m.name, m.value) for m in _http.HTTPStatus]` (the
  *internal* functional call can pass raw names, dodging entry 124), attach
  `phrase` / `description` properties answering `Str` (backed by a lookup
  table built from the CPython members), and keep the `_missing_` unwrap so
  `HTTPStatus(Int(200))` still resolves — now to a POOP member. Combined with
  entry 144's operator bridging on `_PoopEnumMixin`, member equality then
  answers a POOP `Boolean` and status dispatch works. `HTTPClient` call sites
  that feed `_http` internals must unwrap via `member.value_object()._value`
  (or accept both classes) at the boundary.
