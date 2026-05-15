from poop.types.random import _DEFAULT, Random

# Two bindings, mirroring Python's distinction between the
# `random` module and the `Random` class:
#   `random` (lowercase) → singleton instance acting as the
#            module-level API: random.random(), random.choice(xs), ...
#   `Random` (PascalCase) → the class itself, callable as a
#            constructor: r = Random(seed)
NAMESPACE: dict[str, object] = {
    "random": _DEFAULT,
    "Random": Random,
}
