from poop.validators.base import Validator
from poop.validators.no_free_functions import NoFreeFunctionsValidator
from poop.validators.no_if import NoIfValidator
from poop.validators.no_loops import NoLoopsValidator
from poop.validators.no_print import NoPrintValidator

DEFAULT_VALIDATORS: list[Validator] = [
    NoIfValidator(),
    NoLoopsValidator(),
    NoFreeFunctionsValidator(),
    NoPrintValidator(),
]

__all__ = ["DEFAULT_VALIDATORS", "Validator"]
