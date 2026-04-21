from poop.validators.base import Validator
from poop.validators.no_abs import NoAbsValidator
from poop.validators.no_all import NoAllValidator
from poop.validators.no_any import NoAnyValidator
from poop.validators.no_bin import NoBinValidator
from poop.validators.no_breakpoint import NoBreakpointValidator
from poop.validators.no_callable import NoCallableValidator
from poop.validators.no_chr import NoChrValidator
from poop.validators.no_divmod import NoDivmodValidator
from poop.validators.no_enumerate import NoEnumerateValidator
from poop.validators.no_exec import NoExecValidator
from poop.validators.no_exit import NoExitValidator
from poop.validators.no_format import NoFormatValidator
from poop.validators.no_free_functions import NoFreeFunctionsValidator
from poop.validators.no_global import NoGlobalValidator
from poop.validators.no_hasattr import NoHasattrValidator
from poop.validators.no_hash import NoHashValidator
from poop.validators.no_id import NoIdValidator
from poop.validators.no_if import NoIfValidator
from poop.validators.no_input import NoInputValidator
from poop.validators.no_introspection import NoIntrospectionValidator
from poop.validators.no_invert import NoInvertValidator
from poop.validators.no_is import NoIsValidator
from poop.validators.no_isinstance import NoIsinstanceValidator
from poop.validators.no_iter import NoIterValidator
from poop.validators.no_len import NoLenValidator
from poop.validators.no_loops import NoLoopsValidator
from poop.validators.no_match import NoMatchValidator
from poop.validators.no_max import NoMaxValidator
from poop.validators.no_min import NoMinValidator
from poop.validators.no_not import NoNotValidator
from poop.validators.no_open import NoOpenValidator
from poop.validators.no_pow import NoPowValidator
from poop.validators.no_print import NoPrintValidator
from poop.validators.no_setattr import NoSetattrValidator
from poop.validators.no_slice import NoSliceValidator
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
    NoMaxValidator(),
    NoBinValidator(),
    NoBreakpointValidator(),
    NoChrValidator(),
    NoDivmodValidator(),
    NoEnumerateValidator(),
    NoExecValidator(),
    NoExitValidator(),
    NoFormatValidator(),
    NoHasattrValidator(),
    NoInputValidator(),
    NoIntrospectionValidator(),
    NoIterValidator(),
    NoOpenValidator(),
    NoPowValidator(),
    NoSetattrValidator(),
    NoSliceValidator(),
]

__all__ = ["DEFAULT_VALIDATORS", "Validator"]
