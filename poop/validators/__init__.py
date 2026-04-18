from poop.validators.base import Validator
from poop.validators.no_free_functions import NoFreeFunctionsValidator
from poop.validators.no_if import NoIfValidator
from poop.validators.no_loops import NoLoopsValidator

DEFAULT_VALIDATORS: list[Validator] = [
    NoIfValidator(),
    NoLoopsValidator(),
    NoFreeFunctionsValidator(),
]

__all__ = ["DEFAULT_VALIDATORS", "Validator"]
