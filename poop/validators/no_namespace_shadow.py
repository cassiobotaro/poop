from poop.transformers import DEFAULT_NAMESPACE
from poop.validators._shadow import ShadowValidator


class NoNamespaceShadowValidator(ShadowValidator):
    # Pull the set of user-facing entry points from DEFAULT_NAMESPACE so the
    # protected list stays in sync with whatever the transformers register.
    protected = frozenset(n for n in DEFAULT_NAMESPACE if not n.startswith("_poop_"))
    message = (
        "{name!r} is a POOP namespace binding; reassigning it shadows the "
        "runtime entry point"
    )
