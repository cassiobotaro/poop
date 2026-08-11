# Proposals

Open design backlog. Closing convention: see [`CONTRIBUTING.md`](CONTRIBUTING.md#closing-a-proposal).

Numbering continues from the closed set, so a `proposal N` in a code comment
keeps pointing at one entry and never at two.

### 42. Every exception mirror lists three of CPython's own attributes

`INFECTIONS.md` records the same failure one class over: "`PoopMeta` derives
from `ABCMeta`, and inherited two *public* names with it: `type.mro` and
`ABCMeta.register`… unreachable by reading and reachable by typing." Both are
`class_side` refusals now. The mirrors inherit from `BaseException` and picked
up three more the same way, and this time `dir` does list them:

```
>>> :methods ValueError
ValueError understands 28 messages:
add_note   args   …   raise_   …   with_traceback
```

All 17 mirrors carry `args`, `add_note` and `with_traceback`; `AttributeError`
adds `obj` and `StopIteration` adds `value` — 55 sites. They are not messages
POOP designed, and what they answer says so:

```
ValueError.args              # a raw Python tuple, silently
ValueError.with_traceback    # a raw method descriptor, silently
ValueError.add_note("x")     # descriptor 'add_note' for 'BaseException'
                             #   objects doesn't apply to a 'str' object
```

The refusal names `BaseException` — a class outside `MIRRORS` that no program
can spell — and a `'str' object` the program never mentioned.

The instance side already gets this right, which is what makes it a
disagreement rather than a gap: the `Error` a handler is given refuses all
three (`ValueError does not understand #args`), and its own `dir` lists
neither. So the class advertises three names the error object refuses.

**Fix.** `class_side_refusal` on `PoopExcMeta` for the three, in the shape
`mro` and `register` already use — `#args is Python's; a class answers
#message` for the one with a substitute, and the `_refuse_native` sentence for
the two without. `__dir__` then drops them by the rule it already applies to
refusing descriptors, and `AttributeError.obj` / `StopIteration.value` come
with them: both are attributes of the *exception instance* in CPython, so
neither means anything on the class. A test asserting that no mirror's `dir`
holds a name `Error` refuses would keep the two sides in step, which is the
shape that found this.

---

### 43. A method does not equal itself

A method read off an object is a block now, which is what makes
`"abc".upper.print()` answer. Each read builds a fresh wrapper, and `Object`
compares by identity, so the same method on the same receiver is not equal to
itself:

```
s = "abc"
(s.upper == s.upper).print()          # False   (CPython: True)
(s.upper.is_identical(s.upper)).print()  # False
(s.upper.hash() == s.upper.hash()).print()  # False
```

CPython defines this deliberately — a bound method compares by `__self__` and
`__func__`, and hashes to match — precisely so a program can ask "is this the
same callback?". A block literal is the other case and POOP already agrees
with Python there: `b = lambda: 1` then `b == b` is true because it is one
object, and two separately written lambdas are not equal in either language.

The shape a reader hits is a registry: storing `obj.on_change` and later asking
whether the same method is already registered answers no, every time. Nothing
warns; the program simply registers it twice.

**Fix.** `_MethodBlock` answers `__eq__` / `__hash__` from the pair it wraps —
the receiver and the underlying function, which is exactly what CPython's
bound method compares — so two reads of one method agree and two different
methods do not. `Block` itself keeps identity: it wraps a lambda, and two
lambdas with the same body are different blocks in Smalltalk as in Python.
`is_identical` stays as it is and will still answer false, which is honest —
those really are two objects, and `INFECTIONS.md` already documents that pair
disagreeing by design for classes.

---

### 44. Eight of the eighteen constructors still answer CPython's call machinery

`poop/transformers/_arity.py` exists for this and its docstring closes with a
claim: "So the call path is **complete** now: every `<builtin>(...)` reaches
the converter whatever its arity, and the converter refuses in POOP's
vocabulary." Ten constructors do. Eight do not:

```
float(5, 5)          # float() takes from 0 to 1 positional arguments but 2 …
bool(5, 5)           # bool() takes from 0 to 1 positional arguments but 2 …
int(1, 2, 3)         # int() takes from 0 to 2 positional arguments but 3 …
range(1, 2, 3, 4)    # range() takes from 1 to 3 positional arguments but 4 …
enumerate([1], 1, 2) # enumerate() takes from 1 to 2 positional arguments …
zip([1], nope=1)     # zip() got an unexpected keyword argument 'nope'
object(5)            # object() takes no arguments
slice(1, 2, 3, 4)    # slice.__init__() takes from 1 to 4 positional …
```

Each names the builtin spelt as a **call** and says "positional argument",
which the wording sweep bans outright as describing a block as a Python
function. The last is the sharpest: it names `__init__`, a dunder
`no_dunder_attribute` refuses — and it is the *same sentence shape* the module
quotes as the reason it was written (`str.__init__() takes 2 positional
arguments but 3 were given`, "from a construct the program spelled without a
dunder anywhere"). One constructor over, the leak was never closed.

The keyword half leaks on all eight too (`float(nope=1)`, `object(nope=1)`),
where `list`, `set` and their siblings answer `list takes no keyword arguments
— it is built from at most one collection`.

**Fix.** `refuse_extra_arguments` at the head of each of the eight converters,
which is one call apiece and the sentence the other ten already read. Three
need a little more than the arity: `object` takes none at all (`object is built
from nothing — write Object() for a bare object`), `zip` legitimately takes any
number of iterables and only its `strict` keyword is real, and `slice` has no
`_poop_slice_from` factory at all — `Slice(start, stop, step)` *is* the call,
as proposal 9 recorded, so it needs the guard in `__init__` or a factory like
its siblings'. The sweep that would have caught this is mechanical and cheap:
every bare constructor name, called with five arguments and with an unknown
keyword, must answer a sentence carrying none of `_FORBIDDEN`'s patterns —
which is how the eight were counted.

---

### 45. A block refuses a keyword by counting it, and the count comes out right

`Block.__call__` rewords CPython's arity failure, and `_arity_message` is
handed `len(args) + len(kwargs)`. A keyword the block does not take is
therefore reported as a *count* mismatch — and the count matches:

```
(lambda x: x)(nope=1)        # block expects 1 argument, got 1
(lambda x, y: x)(1, nope=2)  # block expects 2 arguments, got 2
```

A sentence that states two equal numbers and refuses anyway teaches nothing,
and the actual fault — a keyword name the block has no parameter for — is never
mentioned. CPython says `<lambda>() got an unexpected keyword argument 'nope'`,
which POOP is right to reword (`<lambda>` is banned by the sweep) but wrong to
collapse.

It is reachable from ordinary POOP: every block a program writes goes through
`Block.__call__`, and `.do(item=x)` is an easy slip when the block's parameter
has a name in the reader's head.

**Fix.** `__call__` separates the two failures before rewording. A keyword the
block does not accept answers `block does not take a keyword argument 'nope'`,
naming it; the count message keeps `len(args)` alone, so `expects 1, got 1`
becomes unrepresentable. `_accepted` already reads the signature and can report
the accepted keyword names, so a block that *does* take one by keyword
(`lambda x=1: x` called as `b(x=2)`) keeps working — it does today and must
keep doing so.

---

### 46. A message defined on a mixin says its receiver is `object`

`_cloak`'s docstring names this exact leak and fixes half of it: `[1, 2].map()`
used to blame `_IterableMixin.map()`, "a private name `_reject_private` exists
to keep out of user code", so the mixins are cloaked. The name they were given
is `object`:

```
[1, 2].append()   # list.append() missing 1 required positional argument: 'obj'
[1, 2].map()      # object.map() missing 1 required positional argument: 'block'
Object().map(…)   # object does not understand #map
```

The wrong-arity shape is exempt from the wording sweep, and `_cloak`'s
docstring gives the reason: "it only renames the callee". That reason holds
where the rename is true. Here it is not — `object` is a name a program can
write, `object` does not answer `map`, and the reader can check it in one line
and be told the opposite of what the refusal just said. Six mixins are cloaked
this way, so it covers `map`, `filter`, `do`, `reduce`, `all`, `any`, `find`,
`len` on the views, `next` on the iterators, and `Object`'s own protocol as
seen from any receiver.

The class side no longer has this problem — a class names itself when it
refuses an instance message — which leaves the instance side as the only place
POOP still reports a receiver the program did not send to.

**Fix.** Two candidates, and the item exists to choose between them. Cloaking
the mixins as a name no class claims (`collection`, `iterator`) stops the
sentence being falsifiable but names something that does not exist. Binding the
selector alone — `__qualname__ = "map"` — reads as `map() missing 1 required
positional argument`, which names the *forbidden builtin*, so that one is out.
The honest third is to stop leaning on CPython here: give the mixin's messages
the same arity guard the argument kinds already have, so `[1, 2].map()` answers
`#map expects a block, got nothing` from the receiver that was sent it. That is
one guard on `_IterableMixin` rather than one per message, and it would let the
sweep drop its wrong-arity exemption for this family — the exemption's own
justification is what this item shows to be false.

---

### 47. `set_attr` on a builtin class is refused; the assignment is not

Proposal 2 closed one spelling of this and its record says what it was for:
"`class_()` hands the class out — so `"abc".class_().del_attr("upper")` removed
`upper` from every string in the program". `_reject_builtin` refuses a write to
a class the program did not define, keyed on `__module__`. It is called from
`set_attr` and `del_attr`, and from nowhere else. The plain assignment is the
undotted twin `mro` was for `__mro__`:

```
"abc".class_().set_attr("shout", block)   # str is a POOP builtin — its
                                          #   messages cannot be changed
Object.shout = lambda self: self.repr() + "!"
(5).shout().print()      # 5!
"abc".shout().print()    # 'abc'!
[1, 2].shout().print()   # [1, 2]!
```

One intent, two spellings, and the refused one is the sanctioned one. The root
is reachable by name on purpose — `INFECTIONS.md`: "The root is the one
exception user code can name directly… the binding stays `_poop_object`" — so
`Object.foo = 5` writes on the real root and every object in the language
answers `#foo` from then on. That is exactly the encapsulation the `__slots__`
decision exists to hold: a `Str` that "holds no state of its own" now holds
whatever was hung on the root.

The other receivers are polluted rather than hijacked, because a bare builtin
name binds the *alias*: `int.foo = 5` sticks to `_poop_int_cls`, so `int.foo`
reads back and `int.dir()` lists it, while `(5).foo` is still not understood.
That makes the sibling case worse, not better:

```
str.upper = lambda self: "HACKED"
"abc".upper().print()    # ABC
```

Accepted, and does nothing at all — the reader is neither obeyed nor told why.
The mirrors take it too (`ValueError.foo = 5`).

Two names *are* refused, which shows the guard exists and is simply not
reached: `Object.print = …` and `int.name = 5` answer `#print is answered by
every class — it cannot be rebound`, because `class_side.__set__` is a data
descriptor and gets consulted. Every name outside that set falls through.

**Fix.** `PoopMeta.__setattr__` calls `_reject_builtin(cls)` before delegating,
which is the same guard `set_attr` already runs and puts the two spellings on
one sentence — `class_side.__set__` keeps its own wording, since "answered by
every class" says something truer about those names than "is a POOP builtin"
does. A `class C(Object)` a program wrote is untouched: `C.foo = 5` is how a
class holds shared state, and `__module__` is `__poop__` there. `del` needs no
twin — `no_del` bans the statement outright.

The silently-ineffective half closes with it: `str.upper = …` starts answering
the same refusal instead of writing to an alias nobody reads. A test that every
bare builtin name refuses both spellings, and that a user class accepts both,
is the sweep this item is: `set_attr` was tested per receiver and the
assignment was never tested at all.

---

### 48. Storing on a value leaks the `__dict__` sentence proposal 3 removed

Proposal 3's record quotes the sentence it closed word for word:
`"abc".del_attr("zzz")` answered `'str' object has no attribute 'zzz' and no
__dict__ for setting new attributes`, "naming the dunder `_reject_dunder` will
not even let a program spell". `set_attr` and `del_attr` compose POOP's
sentence for it now. The assignment does not:

```
"abc".set_attr("x", 5)   # str is a value — it holds no state of its own;
                         #   only an object of a class you defined can be given one
"abc".x = 5              # 'str' object has no attribute 'x' and no __dict__
                         #   for setting new attributes
```

Every value receiver leaks it — `Str`, `List`, `Dict`, `Int`, `Boolean` and the
rest, 15 of them — and the leak carries three things at once: a dunder, the
quoted CPython class spelling `'str' object`, and advice about a `__dict__` the
reader cannot inspect because `no_dunder_attribute` refuses the name.

It is the same pairing as item 47 one level down: the message spelling is
guarded, the assignment is the undotted twin. `obj.x = 5` is also the *more*
natural first attempt — a reader coming from Python writes it before they know
`set_attr` exists, so the leaked sentence is the first thing the `__slots__`
decision ever says to them.

**Fix.** `Object.__setattr__` catches the `AttributeError` and raises the
sentence `set_attr` already composes, which is one place and no new wording.
The cost is bounded in a way `__getattribute__`'s is not: a wrapper writes its
payload once in `__init__` and never again, so this runs on user-class stores
and nothing else hot.

Out of scope deliberately: `C()._p = 5` on a user class succeeds while
`C().set_attr("_p", 5)` is refused as private. That pair should *not* be
levelled — `self._balance = balance` inside a method is how a POOP object
holds its own state (`examples/patterns/execute_around.py` is built on it), and
nothing at the assignment site can tell the object writing its own slot from a
caller reaching into someone else's. `set_attr` is reflection and can refuse;
the assignment cannot.

---

### 49. `_value` is refused through `get_attr` and handed over by writing it

The two guarded spellings of reaching into an object are closed. The third,
which is the one a reader would actually type, is open — and what it answers is
a naked Python primitive:

```
"abc".get_attr("_value")   # _value is private — POOP objects do not expose
                           #   their internals
"abc"._value               # 'abc', a Python str
"abc"._value.print()       # 'str' object has no attribute 'print'
[1, 2]._items              # a Python list
{"a": 1}._data             # a Python dict
```

That contradicts the language's first principle twice over. `INFECTIONS.md`
says "no naked Python primitive ever reaches runtime" and "Python native types
must not leak into POOP code"; this hands one out on request. And the object
that comes back answers nothing, in CPython's vocabulary — `'str' object has no
attribute 'print'` is precisely the sentence `does_not_understand` exists to
replace, reachable from a two-token expression.

The blind spot is visible in the code that works around it.
`_selectors.is_message` explains that the REPL completer used to offer
`x._value` and calls that "the encapsulation leak taught by the tool meant to
teach the language" — the completer stopped *offering* the spelling, and the
spelling still works. And `examples/patterns/memento.py` opens by showing
`saved = editor._content` as the procedural Python that POOP exists to
prevent — `# poking at internals`, in the example's own comment. The language
teaches the rule in an example and does not enforce it.

`no_dunder_attribute` is the shape of the answer and shows it is enforceable
syntactically: it refuses `.__class__` at parse time on any receiver, and names
the substitute.

**Fix.** A `no_private_attribute` validator refusing an `ast.Attribute` whose
name starts with a single `_`, naming `obj.get_attr(name)` — which refuses it
too, but by *saying so*, which is the whole point of a substitute. Three
receivers stay legal, because an object reaching its own state is not reaching
into anything: `self`, `cls`, and the enclosing class by its own name. The last
is not hypothetical — it is one site, `Transaction._commit` in
`examples/patterns/execute_around.py`, where a `@staticmethod` has no `cls` to
write. A sweep over `examples/` reports that single case and nothing else, so
the rule costs one allowance and no rewrites.

The mangled `_poop_*` half is already covered by `no_poop_prefix`, which
reserves those names; this is the same reservation for the single-underscore
internals every wrapper declares in `__slots__`. It belongs with items 47 and
48: three spellings of one act, guarded through the message and open through
the syntax.

---

### 50. `*` is the one operator still worded by CPython, on 95 sites

`+` and `*` are the two operators a sequence answers, and they are worded by
different languages:

```
([1, 2] + "a")   # list does not understand #+ with a str
([1, 2] * "a")   # can't multiply sequence by non-int of type 'str'
```

The second names "sequence" — a Python protocol, not a receiver — quotes the
class the CPython way (`'str'`), and describes the operator as a type-level
protocol rather than a message, which is the family the wording sweep bans
under `operator-as-protocol`. It is not a corner: five wrappers answer `*`
(`Str`, `List`, `Tuple`, `Bytes`, `ByteArray`) against fourteen operand kinds,
and a sweep of every operator across every pair reports this one message shape
and no other — 95 sites, 12 spellings, one operator.

`_repeat.py` documents the decision and calls it the opposite of what it is:
the operand is "unwrapped to its underlying value (or passed through) so the
wrapped sequence's `__mul__` raises CPython's **faithful** `can't multiply
sequence by non-int` `TypeError` for non-integers". Faithful to CPython is what
proposal 10 spent a whole item overturning — "the wrapper naming the Python
method it happens to call".

`__add__` shows the machinery is already there and costs nothing: it answers
`NotImplemented` for a foreign operand with the comment `# foreign operand ->
faithful TypeError`, CPython raises `unsupported operand type(s) for +`, and
`_message.poop_message` rewrites that shape into `binary_refusal`'s sentence.
`*` never reaches it, because `_repeat_count` lets the *inner* multiplication
raise a shape `poop_message` does not match.

The sweep missed it for a reason worth fixing too: operators are covered only
by the `_FAILING` program list, which carries `("a" + 1)` and `([1] + 1)` and
no `*`.

**Fix.** `__mul__` and `__rmul__` guard the operand the way `__add__` guards
its own — a non-integral one answers `NotImplemented` — and the existing
rewriting produces `list does not understand #* with a str` with no new
wording. Both halves are needed: leaving `__rmul__` open sends `[1] * "a"`
straight back into `Str.__rmul__` and out through the same leak. `Boolean`
keeps folding to 1/0, which is what `_repeat_count` is really for and the one
part of it that must stay. The operator matrix — every operator over every
pair, run against the `_FORBIDDEN` patterns — belongs in the sweep beside the
program list, since that is what found this and it would have found it on day
one.

---

### 51. A spread into a literal names the builtin it is not

`[*x]`, `(*x,)` and `{*x}` are literals with a spread. Given something that
cannot be spread, all three answer in terms of a constructor call the program
did not write:

```
[*5]     # list() argument after * must be an iterable, not int
(*5,)    # tuple() argument after * must be an iterable, not int
{*5}     # set() argument after * must be an iterable, not int
{**5}    # cannot ** -unpack int into a dict display
```

`list()`, `tuple()` and `set()` are messages spelt as calls, which is the
pattern the wording sweep bans; they name a construct that is not in the
program at all, since the reader wrote brackets; and `[*5]` in POOP is not even
routed through the `list` converter, so the name is doubly not the one that
ran. The dict form is worse in a smaller way — `** -unpack` has a stray space
and "dict display" is Python's grammar vocabulary for a construct POOP calls a
literal.

The block form is already right and shows the target: `f(*5)` answers `<block>
argument after * must be an iterable, not int`, naming the receiver in POOP's
spelling.

**Fix.** The literal transformers already rewrite these nodes, so each can
resolve its spread through one helper that refuses with `a list literal can
only spread a collection, got an int` — the receiver named as what the reader
wrote (a literal), the operand named by its POOP class through the cloak, and
no call anywhere. `{**x}` takes the mapping twin. This is the last family of
CPython-worded failures reachable from a literal, which is what makes it worth
the four call sites rather than a note in the sweep's exemptions.

---

### 52. The wording sweep is blind to CPython's other sentence shape

`tests/test_no_python_wording.py` already sends **every public message on every
wrapper with wrong-typed arguments** — proposal 10 built that half precisely so
a leak could not survive by not being on a list. It runs over the sites below
every time the suite runs, and passes, because `_FORBIDDEN`'s six patterns look
for calls, dunders, operators-as-protocols, subscripts, blocks-as-functions and
generators. CPython has a seventh shape they do not name:

    <thing> is required, not 'X'   /   argument should be … not 'X'

Nothing in it is a call, a dunder or an operator, so it passes. About forty
receiver/message sites answer in it, and they are not scattered — they are the
guards `Str` has and its byte twins never got:

```
"abc".count(5)     # #count expects a str, got an int
b"abc".count(5.5)  # argument should be integer or bytes-like object, not 'float'
"abc".strip(5)     # strip arg must be None or str
b"abc".strip(5)    # a bytes-like object is required, not 'int'
```

`argument should be integer or bytes-like object` covers `count`, `find`,
`index`, `rfind` and `rindex` on both byte wrappers — the same five messages
`_needle` was written for and wired into `Str` alone, which is proposal 6's
item reopening on the receiver next door. `a bytes-like object is required`
covers eleven more: `includes`, `strip` and its two halves, `partition`,
`rpartition`, `removeprefix`, `removesuffix`, `split`, `rsplit` and `join`.

`Str` is not clean either. Three of its own leak the same way, and one of them
is the sharpest sentence in the family:

```
"abc".includes(5)  # 'in <string>' requires string as left operand, not int
```

`includes` is the substitute `no_in` points at, and its refusal quotes the
banned operator in its Python spelling. `partition` / `rpartition` answer `must
be str, not function` — a sentence with no subject at all — and `strip` /
`lstrip` / `rstrip` name the message as a bare word (`strip arg must be…`).

Two singletons round it out, both naming something POOP bans:
`memoryview(b"ab").hex(5)` answers `object of type 'int' has no len()` — the
banned builtin spelt as a call — and `(2.5).fromhex(5)` answers `bad argument
type for built-in operation`, while the two `fromhex` twins on the byte
wrappers already answer `#fromhex expects a str, got an int`.

**Fix.** Two commits, and the order matters. The pattern first: `_FORBIDDEN`
grows `a CPython argument report` (`is required, not '`, `argument should be`,
`must be None or`, `expected a \w+-like object`, `has no len\(\)`, `bad
argument type for built-in`) and the suite goes red on every site above, which
is the only way to know the list is complete. Then the guards: `_needle` moves
to `_argument.py` beside `text_like` and `a_bound` — its sentence is already
receiver-independent — and the byte wrappers route their search family and
their affix/strip/partition arguments through it, exactly as `_affix.py`
already shares `startswith`/`endswith` across all three. `Str.includes` and
`MemoryView.hex` take `text_like` and the separator guard `Bytes.hex` already
has; `Float.fromhex` takes the one its twins use.

A cross-receiver assertion belongs with them, since that is what surfaced this:
one message, one wrong argument, sent to every receiver that answers it — the
sentences must agree in shape. `count` answers three different shapes today.

---

### 53. Two constructs check that their block is a block; forty-odd do not

`_require_block` was written for one sentence, quoted in its own docstring:
CPython answers `'int' object is not callable`, which is "true of every POOP
object, and silent about what was expected". `Try` and `With` route their four
block arguments through it. Every other message that takes a block reaches the
deferred call instead, and the language has about forty of them.

Sending a non-block splits three ways, and all three are wrong:

```
[1, 2].do(5)            # 'int' object is not callable
[1, 2].sorted(key=5)    # 'int' object is not callable
True.if_true(5)         # 'int' object is not callable
[1, 2].map(5)           # accepted; nothing happens
[1, 2].filter(5)        # accepted; nothing happens
True.if_false(5)        # accepted; nothing happens
```

Seventeen leak the sentence. Five **accept in silence** because the receiver is
lazy — `map`, `filter` and `filter_false` answer a view and call nothing until
it is walked, so the failure surfaces somewhere else entirely, or never, if the
view is never iterated.

The third group is the worst, because whether a wrong argument is reported at
all depends on the receiver's *value*: `True.if_true(5)` refuses and
`True.if_false(5)` says nothing; `False` swaps them. `and_` refuses and `or_`
does not, on the same receiver. `(5).if_none(5)` is quiet and
`(5).if_not_none(5)` is not. A program can ship a mistake that only reports on
the branch it does not usually take.

`_require_block`'s docstring already makes the argument this item is: "resolve
what you need before running anything, so the failure lands where the mistake
was written rather than after a deferred block has had side effects." Two
proposals applied it to `Try` and `With`; nothing carried it to the collection
protocol, where blocks are what POOP replaced every control structure *with*.

**Fix.** `_require_block` at the head of each block-taking message, which is
one line apiece and the sentence two constructs already answer. The roles are
worth spelling per family rather than generically: `#do expects a block, got an
int — write .do(lambda item: …)` for the iteration protocol, `key must be a
block` for the four `sorted`/`sort`/`min`/`max` sites, and the `if_*` family
naming its own branch. `_IterableMixin` carries most of them in one place, so
the sweep is nine methods there, four on `Boolean`, two on `Block`, two on
`Object` plus the `NoneClass`/`PoopMeta` twins, and the `key` slot on the six
receivers that spell `sorted`/`min`/`max` themselves.

The lazy three cannot be left to the deferred call *at all* — that is the
half no wording change reaches, since there is no message to reword when the
program simply gets a `Map` that will fail later. A mechanical test belongs
with it: every message whose signature names a `Callable` parameter, given a
non-block, must answer a sentence carrying the words `must be a block`. That
enumeration is derivable from the signatures — 58 parameters across 18 modules
today — so a new block-taking message cannot ship unguarded.

---

### 54. `obj.format(spec)` is a no-op on the receiver most likely to be formatted

`no_format` bans `format(x, spec)` and its table names one substitute:
`x.format(spec)`. It works on every receiver but one, and the exception is
`Str`:

```
(5).format(">6")     # '     5'
(2.5).format(".2f")  # '2.50'
"ab".format(">6")    # 'ab'
"ab".format("d")     # 'ab'
"ab".format("+")     # 'ab'
```

Nothing is raised. `Str.format` is POOP's *template* surface — the
`"{}".format(x)` method proposal 24 worded five failures for — so a spec
handed to it is read as an argument for placeholders the string does not have,
and `str.format` discards extra positional arguments. The reader follows the
ban's advice and gets their string back unchanged, three times out of three,
with no way to tell it did not work. CPython refuses two of those three
(`Unknown format code 'd' for object of type 'str'`, `Sign not allowed in
string format specifier`), so even the faithful behaviour would be louder than
this.

One selector, two meanings, decided by the receiver — the shape
`Range.stop()`'s docstring calls out and resolves the other way ("One selector,
two meanings, decided by the receiver" is written there as the thing being
fixed). Here the meaning a *validator* points at is the one that loses.

**Fix.** Two spellings are available and the item exists to choose. Either
`Str.format` keeps the template meaning and `no_format`'s substitute column
gains the exception — pointing `Str` at `"{:spec}".format(text)`, which is what
actually works — or `Str.format` disambiguates on its argument: one `Str`
argument that parses as a *format spec* and no placeholders in the receiver
means the `Object.format` meaning, anything else means the template. The second
reads better at the call site and is what a reader expects from the ban, but it
decides by inspection, which is the kind of rule proposal 9 refused elsewhere
("a value whose class and contents disagree").

The first is smaller and honest, and it comes with a test worth having either
way: every receiver named by a validator's Substitute column must actually
answer that substitute — `no_format` is the one row where following the table
silently does nothing, and nothing in the suite reads that table.

---

### 55. `hash()` answers CPython's bare sentence; the two sites that store agree already

`no_hash` bans `hash(x)` and names `obj.hash()`. The substitute's own failure
is CPython's, on nine receivers, while the two places that reach the *same*
condition compose POOP's:

```
{[1]}                # cannot use 'list' as a set element (unhashable type: 'list')
{}.at_put([1], 2)    # cannot use 'list' as a dict key (unhashable type: 'list')
[1, 2].hash()        # unhashable type: 'list'
```

The composed sentence quotes CPython's in parentheses on purpose — `_cloak`'s
docstring records why, Python 3.14 having put both spellings in one line — so
the wording is written, tested and one call away. `hash` does not use it.

Nine receivers answer the bare form: `List`, `Dict`, `Set`, `ByteArray`, the
three dict views, a `Tuple` holding any of them, and — in a variant of its own
— a writable `MemoryView`, which answers `cannot hash writable memoryview
object`, the only sentence in the language that says *object* where POOP says
receiver.

Nothing in it names a construct the sweep's patterns look for, which is the
same blind spot item 52 is about: `unhashable type: 'list'` has no call, no
dunder, no operator. It says "type" where POOP says class, quotes the class the
CPython way, and — the part a reader actually needs — says neither why nor what
to do instead.

**Fix.** `Object.hash` catches the `TypeError` and composes the sentence the
storage sites already share, from the same helper: `list cannot be hashed — a
mutable object has no place as a set element or a dict key`, keeping CPython's
parenthetical for the reason the other two keep it. The `MemoryView` variant
takes the same treatment with its own reason (`a memoryview over a bytearray
cannot be hashed — the bytes behind it can still change`), since "writable" is
a buffer-protocol word and `INFECTIONS.md` keeps that vocabulary out
deliberately.

The dict views are worth a look while there: they are unhashable in CPython
too, and `INFECTIONS.md` records `__hash__ = None` on all three as deliberate,
so only the sentence changes.

---

### 56. A caught error is transparent to every message about its class but one

`Error.class_`'s docstring states the rule: "Transparent identity: answer the
wrapped exception's class. An `Error` stands in for the exception it caught, so
`e.class_()` and the `class_name()` built on it answer that exception's class
— mirroring Python's `except IndexError as e`, where `type(e)` is `IndexError`,
not some wrapper." `kind`, `class_`, `class_name` and `__str__` all keep it.
`is_instance` does not:

```
Try(lambda: ValueError.raise_("m")).except_(ValueError, lambda e:
    e.class_name().print()          # ValueError
).run()

Try(lambda: ValueError.raise_("m")).except_(ValueError, lambda e:
    e.is_instance(ValueError).print()   # False
).run()
```

The handler fired *because* the error is a `ValueError`, and the receiver
inside it says it is not one. `e.is_instance(Exception)` is false too, and
`e.is_instance(Object)` is true — so the answer is not merely wrong, it is
about the wrapper, which is the one object the docstring says an `Error` must
never be.

It costs a program the natural shape for a multi-way handler. Catching
`Exception` once and dispatching inside — `e.is_instance(ValueError).if_true(…)`
— is how POOP spells what Python spells with several `except` clauses, since
`if` is banned and `except_` chaining requires knowing the kinds up front. That
shape silently takes no branch. A user's own subclass makes it plainer:
`MyErr.raise_(…)` caught as `ValueError` answers false to
`e.is_instance(MyErr)`, about the exact class the program defined and raised.

`is_instance` is also the substitute `no_isinstance` names, so this is a
validator pointing at a message that answers the wrong thing on one receiver —
the same shape as item 54, a different receiver.

**Fix.** `Error.is_instance` delegates through `kind()` the way `class_` does,
which is one method beside the three that already do it — `isinstance` on the
wrapped exception, with `unalias` applied to the argument as `Object.is_instance`
already applies it. Its twin `not_identical`-style pairing needs no change:
`is_identical` asks identity and those really are two objects, which
`INFECTIONS.md` already documents as a deliberate disagreement for classes.

`is_subclass` deserves a look in the same commit — it is a class-side message,
so `e.is_subclass(…)` is not the spelling in question, but `e.class_().
is_subclass(Exception)` already answers `true` and should keep doing so. A test
that every message an `Error` answers about its class agrees with `kind()`
would close the family rather than this one member: that sweep is what found
it, and `is_instance` was its only survivor.

---

### 57. A `Range` is the one receiver where a boolean stops being a number

`_index.py` opens with the rule and the reason: "`bool` is an `int` subclass in
CPython, so `[10, 20][True]` is `20`… POOP's `Boolean` is not an `Int`
subclass — the two rungs of the tower are separate classes — so every message
that takes an index names both." `Range` obeys it when it is built and when it
is indexed, and drops it when it is searched:

```
range(True, 5).print()                  # range(1, 5)     — __init__ folds
range(1, 6, 2).at(True).print()         # 3               — at folds
range(1, 6, 2).includes(True).print()   # False           (CPython: True)
range(1, 6, 2).count(True).print()      # 0               (CPython: 1)
range(1, 6, 2).index(True)              # range has no element equal to True
```

Three messages of one class disagreeing with two others of the same class is
already the shape, but the sentence `index` composes is what makes it a
contradiction rather than a gap. The language answers all three of these:

```
(True == 1).print()                     # True
range(1, 6, 2).includes(1).print()      # True
range(1, 6, 2).includes(True).print()   # False
```

So a collection is said to hold `1`, and to hold nothing equal to a value it
agrees is equal to `1`. `index`'s refusal states it outright — *range has no
element equal to True* — about a range whose first element is `1`.

Every other receiver folds, which is what isolates this to one class:

```
[1, 3, 5].includes(True).print()        # True
(1, 3, 5).count(True).print()           # 1
{1, 3}.includes(True).print()           # True
{1: "x"}.at(True).print()               # x
"ab".at(True).print()                   # b
```

They fold because they hold POOP objects, so the comparison is
`Int(1) == true`, and `_num_value` has the `Boolean` branch that folds it to
`1`. `Range` is the only wrapper in the language that stores raw Python
numbers — `_range()` builds a real `range` — so the comparison is `1 == true`
between a raw `int` and a POOP object. `int.__eq__` answers `NotImplemented`,
the reflected side reaches `_num_value`, which has no branch for a raw `int`
and answers `_NOT_NUMERIC`, and `__eq__` returns `false`. Both directions
decline, so the two are unequal — while the same two spelt in POOP are equal.

The split is visible in three lines of `range.py`: `__init__` and `at` unwrap
through `_index`, which names both rungs; `includes`, `count` and `index`
unwrap through `_faithful`, which reads `_value` — and `Boolean` is the one
wrapper in the language that has no `_value`, so `_faithful` hands the wrapper
back untouched and it crosses into the raw `range` as a POOP object.

**Fix.** The three search messages fold through the index rung the way their
own constructor already does. `_index` itself is not the helper — it refuses a
non-index, and `includes`/`count` must answer `false`/`0` for a foreign value
as they do today rather than raise — so this is `_faithful` plus the `Boolean`
fold, one function beside it in `_unwrap.py`. It belongs there and not in
`range.py` because the cause is general: `Boolean` is the one wrapper with no
`_value`, so any future site that unwraps an argument and then relies on
*equality* rather than on `__index__` will lose the same way. The `__index__`
sites are all safe today and stay untouched, which is why `at`, `center`,
`ljust`, `zfill`, `split`'s maxsplit and `replace`'s count all already work.

Widening `_num_value` to accept a raw `int`/`float` would fix it a level down
and is the wrong call: it would change equality for every numeric wrapper to
accommodate one class's internals, when the honest reading is that raw Python
numbers exist in exactly one place and should be converted at that boundary.

The sweep that found this is worth keeping: for every receiver answering
`includes`, `count` or `index`, the answer for `True` must equal the answer for
`1` and the answer for `False` must equal the answer for `0`. It is one loop,
it covers a rule `_index.py` already states in prose, and `Range` is its only
failure.

---

### 58. A caught error refuses three messages its own class answers

Proposal 56 found `is_instance` disagreeing with `kind()`. The other direction
is open too, and it is louder, because the REPL prints both halves:

```
>>> :methods ValueError
ValueError understands 28 messages:
add_note  dir   …  name  …  raise_  …  superclass  with_traceback

Try(lambda: ValueError.raise_("m")).except_(ValueError, lambda e:
    e.raise_()
).run()          # ValueError does not understand #raise_ —
                 #   try :methods to list its messages
```

`e.name()` and `e.superclass()` answer the same sentence. All three are
messages `ValueError` genuinely answers — `raise_` on `PoopExcMeta`, `name` and
`superclass` on `PoopMeta` — so the refusal names a receiver, in the reader's
own vocabulary, that does not refuse. (`args`, `add_note` and `with_traceback`
refuse here too; those are proposal 42's, and the two items agree once the
class side refuses them as well.)

`Error.does_not_understand`'s own body is the proof. It composes the label like
this:

```python
label = str(self.kind().name())
```

It sends `#name` to the class, successfully, and uses the answer to write a
sentence saying that class does not understand `#name`.

The cost is a re-raise. `raise_`'s docstring in `poop/types/exceptions.py`
records exactly this failure as the reason it was made a real class-side
message: "`e.kind()` inside a handler all answered `ValueError does not
understand #raise_`. The last made a *re-raise* inexpressible, since `Try`
swallows a matched exception and `raise` is banned." What that bought is
`e.kind().raise_(e.message())`, which constructs a **new** exception — the
original's identity, its notes and its traceback are gone, and the handler that
wanted to log and rethrow silently rethrows something else. The direct
spelling, the one a reader writes first, still answers the sentence the
docstring quotes as the bug.

POOP has a sentence for the opposite direction and not for this one.
`PoopMeta` refuses an instance message sent to a class with `#upper asks an
instance; send it to one`, and a second shape for the class-about-its-class
family (`#name asks an instance about its class; a class answers #name`).
Nothing words an instance sent a *class* message, so it falls through to
`does_not_understand` — the one wording that is false here.

**Fix.** Two parts, and they are separable.

`Error.raise_()` re-raises the wrapped exception itself. That is one method
over `self._exception`, it is what `raise` spells in Python and what `no_raise`
has no substitute for inside a handler, and it keeps identity, notes and
traceback that the `kind()` spelling drops. It makes the natural spelling work
rather than merely reword its refusal, which is the same call proposal 56 makes
for `is_instance`.

`name` and `superclass` stay class-side, because an `Error` is an instance and
those ask a class. `does_not_understand` checks whether `kind()` answers the
name and, when it does, composes the mirror of the sentence `PoopMeta` already
uses: `#superclass asks a class; send it to #kind()`. The label stays truthful
— the kind really is `ValueError` — and the reader is pointed at the receiver
that answers instead of being told a class refuses a message it lists.

The test is the one proposal 56 asks for, widened by a clause: every public
name `:methods <Kind>` lists must either be answered by an `Error` of that
kind, or be refused by a sentence that does not claim the kind refuses it.
Nothing in the suite reads `:methods`' own output against the object it
describes, which is why the class and the handler have been able to disagree
about six names.

---

### 59. Recursion is the substitute for every loop, and it runs out six times sooner than Python's

`INFECTIONS.md` says why `RecursionError` is mirrored at all: "recursion is
POOP's substitute for every loop, which makes it the most reachable of the
lot." The class is mirrored, the failure is catchable, and the budget it runs
against was never looked at. A message that sends itself runs 164 levels deep.
The same recursion written as a Python function runs 998:

```
class Counter(Object):
    def count(self, n):
        return (n <= 0).if_true_if_false(lambda: 0, lambda: self.count(n - 1) + 1)

Counter().count(164).print()   # 164
Counter().count(165).print()   # RecursionError: maximum recursion depth exceeded
```

Both run under the same `sys.getrecursionlimit()` of `1000` — nothing in POOP
calls `setrecursionlimit`. The difference is that one POOP step is six Python
frames, and the traceback names them:

```
block.py    __call__            #  Block.__call__      — the lambda wrapper
<string>    <lambda>            #  the reader's block
block.py    __call__            #  _MethodBlock.__call__ — reading self.count
<string>    count               #  the reader's method
block.py    __call__            #  _MethodBlock.__call__ — reading if_true_if_false
boolean.py  if_true_if_false    #  the branch
```

Two of the six are the program. Four are POOP getting out of its own way, and
the reader is charged for all six.

Two of those four are recent. `_MethodBlock` is the "a method read off an
object is a block, whichever way it was read" feature — the one that made
`"abc".upper.print()` answer. Bypassing the wrap and re-measuring the same
program gives **247** instead of 164, so that feature cost a third of the
language's recursion ceiling and nothing recorded the price. That is not an
argument for undoing it; it is an argument for having the number written down
next to it.

The scope is worth stating precisely, because half of it is fine.
`Block.while_true` and `while_false` are real Python `while` loops, so
loop-shaped code has no ceiling at all and `collatz.py` is safe at any input.
What this bites is *structural* recursion, where the depth follows the data
rather than a counter — `examples/patterns/interpreter.py`, whose header says
"the tree dispatches recursively", and the Composite shape next to it. A
Python program walking a 200-deep tree is unremarkable; the POOP translation
of it stops.

And the sentence a reader gets is CPython's:

```
poop: RecursionError: maximum recursion depth exceeded
  3 |         return (n <= 0).if_true_if_false(lambda: 0, lambda: self.count(n - 1) + 1)
```

It names no receiver, offers no substitute, and — the part that actually
misleads — implies the reader wrote 1000 levels of recursion when they wrote
164. It is the same blind spot as items 52 and 55: nothing in it is a call, a
dunder or an operator, so the wording sweep cannot see it.

**Fix.** Raise the limit once, at the entry point, sized from the frame cost.
Six frames per user-visible send means a limit of `6000` buys a POOP program
roughly the thousand levels a Python program already gets, which is the honest
target — a language should not be an order of magnitude shallower than the one
it is built on, least of all the language that banned `for`. One call in
`poop/executor.py` covers the CLI and the REPL, since both reach the runtime
through it.

It is safe to raise on 3.14, which is worth checking rather than assuming, so
it was: at a limit of `10000` the program above reaches depth 1000, and at 1500
it stops on CPython's own C-stack guard —

```
RecursionError: Stack overflow (used 8148 kB) while calling a Python object
```

— a catchable `RecursionError`, not a crash. So the ceiling moves and the
floor underneath it holds. A test asserting exactly that belongs with the
change: a program recursing past the new limit answers a `RecursionError` a
`Try` can catch.

The sentence is the second half and is separable. `RecursionError` is already
in `MIRRORS`, so the reword goes in `poop_message` beside the others: name the
ceiling as POOP's, and point at the substitute that fits the shape — `while_true`
/ `while_false` for a loop the reader wrote as recursion, and the iteration
protocol for a walk over a collection. Neither is discoverable from
`maximum recursion depth exceeded`, and both are what a reader who hit this
actually needs.

Recording the frame cost belongs with the method-as-block entry in
`INFECTIONS.md` rather than in code. It is the one number that turns "a method
is a block" from a free convenience into a trade with a stated price, and it is
the number that will move again the next time a wrapper joins the send path.

---

### 60. The caret counts characters; the reader's terminal counts columns

`_caret_column` states the rule it was written for, and states it in the form
that decides this item too: a tab "is one character wide to `len` and eight to
the reader." It handles two conversions in a documented order — the UTF-8 byte
offset `ast` reports, then the tab expansion — and both are right. A third case
has the same shape and is unhandled: a CJK ideograph is one character wide to
`len` and **two** to the reader.

```
r = "日本語" + (1 if True else 2)
             ^                        # caret printed at column 13
                  ^                   # the `1` sits at column 16
```

Three ideographs, three columns short. The project's own mascot does it too:

```
r = "💩💩" + (1 if True else 2)
            ^                         # column 12; the `1` is at column 14
```

The other direction exists as well, and is worse because nothing about the
source looks unusual. A decomposed `á` is `a` followed by U+0301 — legal Python
source, what several input methods and macOS filenames produce, and visually
identical to the precomposed form. It is two characters to `len` and one column
to the reader, so the caret runs *past* its target:

```
r = "áéí" + (1 if True else 2)        # decomposed
                ^                     # caret at column 16; the `1` is at 13
```

Precomposed accents are fine, which is what makes this quiet: `"áéíóú"` typed
normally lands the caret exactly right, so the failure needs a wide character
or a combining mark to appear at all, and then it is off by one column per
character with no indication that anything moved.

It reaches both front ends. `format_error` and `render_error` are shared by
`cli.py` and the REPL, so a file run from the shell and the same line typed at
`>>>` are both mispointed, and `--validators-only` — the mode whose whole
output is carets — is mispointed once per error.

**Fix.** `_caret_column` measures display width instead of `len`, which is the
same substitution the tab expansion already makes one line above it and needs
no new dependency: `unicodedata.east_asian_width(c) in ("W", "F")` counts two,
`unicodedata.combining(c)` counts zero, everything else counts one. The two
existing conversions keep their order and their reasons; this is a third step
in the same pipeline, and the docstring's sentence extends to cover it without
being rewritten.

Where to stop is the real decision, and it should be stopped deliberately
rather than by accident. Grapheme clusters are unbounded — a ZWJ emoji family
is seven code points and one column, flag sequences are two and two, and
terminals disagree with each other about several of them. `unicodedata` has a
stable answer for the East Asian and combining cases and no answer for the
rest, so the fix takes those two and leaves ZWJ sequences approximate. That is
a real improvement over counting characters and an honest place to stop; the
alternative is a `wcwidth` dependency for a caret, which is not a trade this
project would make.

The test is the shape the tab fix already used: a source line with a wide
character before the offending node, asserting the caret's printed column
equals the target's display column. It is one assertion per case and it would
have failed the day the byte-offset conversion landed, since that commit is
where the function started claiming to measure what the reader sees.

---

### 61. One formatting failure, two vocabularies, chosen by which spelling the reader used

`_template_refusal`'s docstring states what it is for: `Unknown format code 'd'
for object of type 'str'` "names a 'format code' and an 'object of type' — the
type-level protocol `_message.py` rewrites everywhere else." It is wired into
`Str.format` and nowhere else, so the same failure answers in two languages
depending on which of POOP's two formatting spellings reached it:

```
"{0:d}".format(2.5)   # a float cannot be formatted with 'd'
(2.5).format("d")     # Unknown format code 'd' for object of type 'float'

"{0:s}".format(5)     # an int cannot be formatted with 's'
(5).format("s")       # Unknown format code 's' for object of type 'int'
```

Same value, same code, same failure. The one that leaks is the one a validator
sends the reader to: `no_format` bans `format(x, spec)` and its Substitute
column names `x.format(spec)`. So a reader who obeys the ban gets CPython's
sentence, and a reader who writes the template they were not pointed at gets
POOP's.

A second shape leaks on **both** spellings, which is why this is not simply a
missing call:

```
"{0:zzz}".format(5)   # Invalid format specifier 'zzz' for object of type 'int'
(5).format("zzz")     # Invalid format specifier 'zzz' for object of type 'int'
```

`_template_refusal` matches `_UNKNOWN_CODE` and rewords that one; everything
else falls through its final line, which replaces `format string` with
`template` and leaves a sentence containing neither untouched. `Invalid format
specifier` contains neither. Sweeping the spec codes across the receivers gives
17 sites: 8 in the `Unknown format code` shape, which the template spelling
already words and the message spelling does not, and 9 in the `Invalid format
specifier` shape, which neither words.

`Object.format` shows the gap in one method. It already catches `TypeError`
and composes POOP's sentence for it — the comment there walks through two
earlier leaks it closed — and the `ValueError` beside it passes through
untouched. The method knows the wording rule and applies it to one of the two
exceptions CPython raises from the same call.

Nothing in the sweep can see either shape. `object of type 'int'` has no call,
no dunder and no operator in it, which is the same blind spot items 52 and 55
are about; this is the third family found through it, and the first where POOP
has already written the correct sentence and simply does not reach it.

**Fix.** `Object.format` grows an `except ValueError` beside the `except
TypeError` it has, routed through `_template_refusal`. That is one clause, no
new wording, and it closes the 8 `Unknown format code` sites by making both
spellings answer the sentence `Str.format` composes today. The helper is
already receiver-independent — it reads the class name out of CPython's text
rather than out of the receiver — so it moves next to the other shared argument
helpers without changing behaviour, the way item 52 proposes moving `_needle`.

`Invalid format specifier` needs the wording written, since it does not exist
yet in either path: `'zzz' is not a format spec an int understands` keeps the
receiver named in POOP's spelling and drops "object of type" for the same
reason the sibling shape did. It goes in `_template_refusal` next to the
`_UNKNOWN_CODE` branch, so both spellings pick it up at once.

The assertion is a cross-spelling one, which is what surfaced this: for every
receiver and every rejected spec, `x.format(spec)` and `"{0:spec}".format(x)`
must answer the *same sentence*. It is the "one failure, every way it can be
spelt" shape item 52 asks for on arguments, applied to the one message POOP
offers under two syntaxes — and no test today compares the two paths against
each other at all.

Item 54 is adjacent and separate: it decides what `Str.format` should *mean*
when handed a spec, which is a question about the receiver POOP excludes here.
This item is about how the failure reads on the fifteen receivers where the
meaning was never in doubt.
