# 40. Programs are confined to a builtins allow-list

Date: 2026-07-25

## Status

Accepted

Amended by [78. A program's builtins hold __import__ for CPython's own imports](0078-a-program-s-builtins-hold-import-for-cpython-s-own-imports.md)

## Context

Validators and transformers cover the names someone thought to enumerate; `exec` hands a program everything else in CPython's builtins namespace. `OSError`, `BaseException`, `KeyboardInterrupt`, `copyright`, `NotImplemented` and `open`, with 56 of Python's 72 builtin exceptions among them, were naked natives one identifier away, answering `type object 'OSError' has no attribute 'print'` instead of `does not understand #print`. That contradicted `poop/types/exceptions.py`, which mirrors 17 exceptions on purpose: "a language with no files and no modules cannot reach the `OSError` subtree" (ADR 34).

`exec` injects `__builtins__` only when the globals dict lacks one. The executor is not the only caller that evaluates against a program's namespace: the REPL's `:methods` and its tab completion `eval` against the session namespace, and `eval` plants CPython's builtins exactly as `exec` does. One `:methods 1` before the first input made `OSError.print()` answer `type object 'OSError' has no attribute 'print'` for the rest of the session.

Once withheld, the names answered `name 'copyright' is not defined`, the sentence a misspelt variable gets, with nothing to say that POOP withheld the name. That was cheap while nobody reached for those names; Python 3.15 added two a programmer types on purpose (`frozendict`, `sentinel`, both wrapped since).

## Decision

A program runs against an allow-list of builtins, `_ALLOWED_BUILTINS` in `poop/executor.py`, and everything outside it answers a `NameError`. If Python needs an import to reach something, POOP does not offer it.

- The allow-list holds `__build_class__` (what the `class` statement calls), `__name__` (read while creating a class), `super` (without it inheritance breaks), and `classmethod` / `staticmethod` / `property` (class-definition machinery with no message-passing substitute, by the same argument as `super`). Each is scoped to the position it was argued for (ADR 18).
- `confine()` binds it, with `setdefault` rather than assignment, because the REPL reuses one namespace across inputs. `execute` calls it, and the REPL confines its namespace when it creates it, before anything evaluates against it.
- `withheld_builtin` (`poop/types/_message.py`) rewords a `NameError` whose name is in `builtins` and not in the allow-list: `'copyright' is a Python builtin POOP does not offer`, or `'OSError' is a Python exception POOP does not mirror` for the exception subtree. The set is derived from `builtins` minus `_ALLOWED_BUILTINS`, not tabulated. The sentence reaches the uncaught report and `e.print()` inside a `Try`, since both go through `poop_message`, and `:explain copyright` answers it too.

## Consequences

- The allow-list is a rule where the validators are a list. It closes the whole class of escapes, including names nobody enumerated.
- `no_dunder_name` and the builtin-call bans remain as the teaching half, refusing a program before it runs rather than at runtime.
- A misspelt variable keeps CPython's `name 'banana' is not defined`.
- The withheld-name sentence points at no substitute, because a name a validator bans never gets here (`x = len` is refused at parse time), so what is left is exactly the set with nothing to point at.
- Deriving the set from `builtins` keeps it current where a hand-kept list would fall behind, as the REPL's `:explain` topic list once did.
