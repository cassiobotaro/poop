# Examples

Every program here runs with `uv run poop <path>`. POOP ships 44 programs across three subfolders, grouped by what they teach.

**Language basics** ([`basics/`](basics/))
- [`hello_world.py`](basics/hello_world.py) — the smallest POOP program
- [`greet.py`](basics/greet.py) — string input + concatenation
- [`fizzbuzz.py`](basics/fizzbuzz.py) — control flow via `if_true_if_false`
- [`leap_year.py`](basics/leap_year.py) — `and_` / `or_` / `not_`
- [`collatz.py`](basics/collatz.py) — while-style recursion
- [`grades.py`](basics/grades.py) — collection processing
- [`string_iteration.py`](basics/string_iteration.py) — a string is a collection too
- [`slicing.py`](basics/slicing.py) — `Slice` as a reusable value object
- [`bank_account.py`](basics/bank_account.py) — encapsulation

**Idiomatic POOP** ([`idiomatic/`](idiomatic/))
- [`pipeline.py`](idiomatic/pipeline.py) — `filter` / `filter_false` / `map` / `do` chain
- [`safe_config.py`](idiomatic/safe_config.py) — `if_none` / `if_not_none` cascade
- [`common_interests.py`](idiomatic/common_interests.py) — set operations
- [`statistics.py`](idiomatic/statistics.py) — number aggregation
- [`rpn_calculator.py`](idiomatic/rpn_calculator.py) — stack as a POOP `List`
- [`roman_numerals.py`](idiomatic/roman_numerals.py) — string mapping
- [`managed_resource.py`](idiomatic/managed_resource.py) — `With` and the `__exit__` protocol

**Classic OO patterns** (Sandi Metz / GoF) ([`patterns/`](patterns/))

*Creational*
- [`abstract_factory.py`](patterns/abstract_factory.py) — Abstract Factory
- [`builder.py`](patterns/builder.py) — Builder
- [`factory_method.py`](patterns/factory_method.py) — Factory Method
- [`prototype.py`](patterns/prototype.py) — Prototype (cloning a configured example)
- [`singleton.py`](patterns/singleton.py) — Singleton (class-side cached instance)

*Structural*
- [`adapter.py`](patterns/adapter.py) — Adapter
- [`bridge.py`](patterns/bridge.py) — Bridge
- [`tree.py`](patterns/tree.py) — Composite (replacing `isinstance`)
- [`decorators.py`](patterns/decorators.py) — Decorator (composition by delegation)
- [`facade.py`](patterns/facade.py) — Facade
- [`flyweight.py`](patterns/flyweight.py) — Flyweight (shared intrinsic state)
- [`proxy.py`](patterns/proxy.py) — Proxy (lazy-loading virtual proxy)

*Behavioral*
- [`chain_of_responsibility.py`](patterns/chain_of_responsibility.py) — Chain of Responsibility
- [`command.py`](patterns/command.py) — Command (with undo)
- [`interpreter.py`](patterns/interpreter.py) — Interpreter
- [`iterator.py`](patterns/iterator.py) — Iterator
- [`mediator.py`](patterns/mediator.py) — Mediator
- [`memento.py`](patterns/memento.py) — Memento
- [`observer.py`](patterns/observer.py) — Observer
- [`door.py`](patterns/door.py) — State
- [`discounts.py`](patterns/discounts.py) — Strategy
- [`template_method.py`](patterns/template_method.py) — Template Method
- [`visitor.py`](patterns/visitor.py) — Visitor

*Other OO patterns (Fowler / Beck / Evans / Metz)*
- [`null_customer.py`](patterns/null_customer.py) — Null Object
- [`payroll.py`](patterns/payroll.py) — polymorphism replacing `if employee.type == ...`
- [`specification.py`](patterns/specification.py) — Specification (composable rules replacing `and`/`or`/`not`)
- [`money.py`](patterns/money.py) — Money value object
- [`execute_around.py`](patterns/execute_around.py) — Execute Around Method
