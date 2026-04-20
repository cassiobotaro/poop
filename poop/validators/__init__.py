from poop.validators.base import Validator
from poop.validators.no_free_functions import NoFreeFunctionsValidator
from poop.validators.no_global import NoGlobalValidator
from poop.validators.no_if import NoIfValidator
from poop.validators.no_invert import NoInvertValidator
from poop.validators.no_is import NoIsValidator
from poop.validators.no_len import NoLenValidator
from poop.validators.no_loops import NoLoopsValidator
from poop.validators.no_match import NoMatchValidator
from poop.validators.no_not import NoNotValidator
from poop.validators.no_print import NoPrintValidator
from poop.validators.no_try import NoTryValidator
from poop.validators.no_unary_minus import NoUnaryMinusValidator
from poop.validators.no_walrus import NoWalrusValidator
from poop.validators.no_yield import NoYieldValidator

DEFAULT_VALIDATORS: list[Validator] = [
    NoIfValidator(),
    NoLoopsValidator(),
    NoFreeFunctionsValidator(),
    NoPrintValidator(),
    NoTryValidator(),
    NoNotValidator(),
    NoUnaryMinusValidator(),
    NoInvertValidator(),
    NoIsValidator(),
    NoGlobalValidator(),
    NoYieldValidator(),
    NoWalrusValidator(),
    NoMatchValidator(),
    NoLenValidator(),
]

__all__ = ["DEFAULT_VALIDATORS", "Validator"]
