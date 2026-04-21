from poop.validators.base import Validator
from poop.validators.no_abs import NoAbsValidator
from poop.validators.no_all import NoAllValidator
from poop.validators.no_any import NoAnyValidator
from poop.validators.no_callable import NoCallableValidator
from poop.validators.no_free_functions import NoFreeFunctionsValidator
from poop.validators.no_global import NoGlobalValidator
from poop.validators.no_hash import NoHashValidator
from poop.validators.no_id import NoIdValidator
from poop.validators.no_if import NoIfValidator
from poop.validators.no_invert import NoInvertValidator
from poop.validators.no_is import NoIsValidator
from poop.validators.no_isinstance import NoIsinstanceValidator
from poop.validators.no_len import NoLenValidator
from poop.validators.no_loops import NoLoopsValidator
from poop.validators.no_match import NoMatchValidator
from poop.validators.no_min import NoMinValidator
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
    NoAbsValidator(),
    NoHashValidator(),
    NoIsinstanceValidator(),
    NoCallableValidator(),
    NoIdValidator(),
    NoAllValidator(),
    NoAnyValidator(),
    NoMinValidator(),
]

__all__ = ["DEFAULT_VALIDATORS", "Validator"]
