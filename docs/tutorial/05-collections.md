# Lesson 5 — Collections

**Goal:** wield POOP lists, dicts, and sets the way they want to be
wielded — fluent chains of methods.

## What's new

`list`, `dict`, `set`, and `tuple` literals all become POOP types. The
extra ingredient on top of [Lesson 3](03-iteration.md) is **chaining**:
each iteration method returns a new collection, so you can pipe them
together top-to-bottom.

```python
items.filter(...).map(...).sorted().do(...)
```

That's a complete program: pick the items you want, transform each,
sort, then run a side effect. No intermediate variables.

A second piece: `dict` and `set` have their own message vocabulary.
`dict.at(key)` replaces `d[key]`, `dict.includes_key(k)` replaces
`k in d`, `set.intersection(other)` is what you'd reach for if you
were using `set & other`.

## Walk-through

A small product catalog. Save to `pipeline.py`:

```python
class ProductCatalog:
    def run(self):
        products = [
            ("Apple", 120, True),
            ("Laptop", 3500, True),
            ("Banana", 80, False),
            ("Headset", 450, True),
            ("Phone", 2200, True),
            ("Cable", 30, False),
        ]

        products.filter(
            lambda p: p.at(2)
        ).filter_false(
            lambda p: p.at(1) > 1000
        ).map(
            lambda p: p.at(0) + " $" + p.at(1).repr()
        ).do(
            lambda line: line.print()
        )


ProductCatalog().run()
```

Two new things in there:

- `p.at(0)` instead of `p[0]`. POOP forbids the `[]` subscript syntax;
  the underlying operation is a method call.
- `filter_false` — keeps items where the predicate returns *falsy*,
  the complement of `filter`. Useful when negating the predicate would
  read awkwardly.

The pipeline reads as: keep available products → drop expensive ones →
format each → print.

Set operations are similarly fluent. From `examples/common_interests.py`:

```python
alice = {"python", "music", "hiking", "coffee"}
bob   = {"rust",   "music", "gaming", "coffee"}

alice.intersection(bob).do(lambda x: x.print())
# music
# coffee
```

`union`, `difference`, `issubset`, `issuperset` are all there.

For aggregations across a whole collection:

```python
data = range(1, 11).map(lambda i: i * i)   # [1, 4, 9, ..., 100]
data.sum().print()       # 385
data.sorted().at(0).print()  # 1   (min)
(data.sum() / data.len()).print()   # 38.5  (mean)
```

Note `data.sum() / data.len()` — POOP arithmetic just works because
`Int` and `Float` know how to divide each other.

## Try it

Given the products list above, print the **total price** of items that
are in stock (`p.at(2) is True`). Solution should be one fluent chain
ending in `.sum()` and `.print()`.

## Anchor example

[`examples/pipeline.py`](https://github.com/cassiobotaro/poop/blob/main/examples/pipeline.py) — the catalog example, ready to run.
[`examples/statistics.py`](https://github.com/cassiobotaro/poop/blob/main/examples/statistics.py) — sum, mean, min, max, and median over the squares 1²…10².

## Reference

- [Python vs POOP — Builtins](../python-vs-poop/builtins.md) for
  `at`, `slice`, `includes`, `sorted`, `reversed`, `reduce`, and the
  rest of the collection vocabulary.
- [Next lesson — Errors →](06-errors.md)
