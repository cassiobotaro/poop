from poop.validators.base import Validator
from poop.validators.no_abs import NoAbsValidator
from poop.validators.no_all import NoAllValidator
from poop.validators.no_and_or import NoAndOrValidator
from poop.validators.no_any import NoAnyValidator
from poop.validators.no_ascii import NoAsciiValidator
from poop.validators.no_assert import NoAssertValidator
from poop.validators.no_async import NoAsyncValidator
from poop.validators.no_bin import NoBinValidator
from poop.validators.no_breakpoint import NoBreakpointValidator
from poop.validators.no_builtin_shadow import NoBuiltinShadowValidator
from poop.validators.no_callable import NoCallableValidator
from poop.validators.no_chr import NoChrValidator
from poop.validators.no_comprehension import NoComprehensionValidator
from poop.validators.no_del import NoDelValidator
from poop.validators.no_dir import NoDirValidator
from poop.validators.no_divmod import NoDivmodValidator
from poop.validators.no_dunder_attribute import NoDunderAttributeValidator
from poop.validators.no_dunder_name import NoDunderNameValidator
from poop.validators.no_exec import NoExecValidator
from poop.validators.no_exit import NoExitValidator
from poop.validators.no_filter import NoFilterValidator
from poop.validators.no_format import NoFormatValidator
from poop.validators.no_free_functions import NoFreeFunctionsValidator
from poop.validators.no_fstring import NoFstringValidator
from poop.validators.no_getattr import NoGetattrValidator
from poop.validators.no_global import NoGlobalValidator
from poop.validators.no_hasattr import NoHasattrValidator
from poop.validators.no_hash import NoHashValidator
from poop.validators.no_help import NoHelpValidator
from poop.validators.no_id import NoIdValidator
from poop.validators.no_if import NoIfValidator
from poop.validators.no_import import NoImportValidator
from poop.validators.no_in import NoInValidator
from poop.validators.no_input import NoInputValidator
from poop.validators.no_introspection import NoIntrospectionValidator
from poop.validators.no_invert import NoInvertValidator
from poop.validators.no_is import NoIsValidator
from poop.validators.no_isinstance import NoIsinstanceValidator
from poop.validators.no_issubclass import NoIssubclassValidator
from poop.validators.no_iter import NoIterValidator
from poop.validators.no_len import NoLenValidator
from poop.validators.no_loops import NoLoopsValidator
from poop.validators.no_map import NoMapValidator
from poop.validators.no_match import NoMatchValidator
from poop.validators.no_max import NoMaxValidator
from poop.validators.no_min import NoMinValidator
from poop.validators.no_namespace_shadow import NoNamespaceShadowValidator
from poop.validators.no_not import NoNotValidator
from poop.validators.no_open import NoOpenValidator
from poop.validators.no_poop_prefix import NoPoopPrefixValidator
from poop.validators.no_pow import NoPowValidator
from poop.validators.no_print import NoPrintValidator
from poop.validators.no_raise import NoRaiseValidator
from poop.validators.no_repr import NoReprValidator
from poop.validators.no_reversed import NoReversedValidator
from poop.validators.no_round import NoRoundValidator
from poop.validators.no_setattr import NoSetattrValidator
from poop.validators.no_sorted import NoSortedValidator
from poop.validators.no_subscript import NoSubscriptValidator
from poop.validators.no_sum import NoSumValidator
from poop.validators.no_try import NoTryValidator
from poop.validators.no_type import NoTypeValidator
from poop.validators.no_type_alias import NoTypeAliasValidator
from poop.validators.no_unary_minus import NoUnaryMinusValidator
from poop.validators.no_unary_plus import NoUnaryPlusValidator
from poop.validators.no_walrus import NoWalrusValidator
from poop.validators.no_with import NoWithValidator
from poop.validators.no_yield import NoYieldValidator

DEFAULT_VALIDATORS: list[Validator] = [
    NoIfValidator(),
    # Ahead of the async-flavoured symptom checks (no_loops' AsyncFor,
    # no_with's AsyncWith, no_free_functions' async branch) so the root
    # cause wins: fixing an `async for` inside a method that is itself
    # about to be rejected is wasted effort.
    NoAsyncValidator(),
    NoLoopsValidator(),
    NoComprehensionValidator(),
    NoFreeFunctionsValidator(),
    NoPrintValidator(),
    NoAssertValidator(),
    NoRaiseValidator(),
    NoTryValidator(),
    NoTypeAliasValidator(),
    NoWithValidator(),
    NoNotValidator(),
    NoAndOrValidator(),
    NoUnaryMinusValidator(),
    NoUnaryPlusValidator(),
    NoInvertValidator(),
    NoIsValidator(),
    NoInValidator(),
    NoGlobalValidator(),
    NoYieldValidator(),
    NoWalrusValidator(),
    NoMatchValidator(),
    NoFstringValidator(),
    NoLenValidator(),
    NoAbsValidator(),
    NoHashValidator(),
    NoIsinstanceValidator(),
    NoIssubclassValidator(),
    NoCallableValidator(),
    NoIdValidator(),
    NoAsciiValidator(),
    NoAllValidator(),
    NoAnyValidator(),
    NoMinValidator(),
    NoMaxValidator(),
    NoMapValidator(),
    NoFilterValidator(),
    NoRoundValidator(),
    NoBinValidator(),
    NoBreakpointValidator(),
    NoHelpValidator(),
    NoChrValidator(),
    NoDivmodValidator(),
    NoDunderAttributeValidator(),
    NoDunderNameValidator(),
    NoExecValidator(),
    NoExitValidator(),
    NoFormatValidator(),
    NoGetattrValidator(),
    NoHasattrValidator(),
    NoInputValidator(),
    NoDirValidator(),
    NoTypeValidator(),
    NoIntrospectionValidator(),
    NoIterValidator(),
    NoOpenValidator(),
    NoPowValidator(),
    NoReprValidator(),
    NoSetattrValidator(),
    NoSortedValidator(),
    NoReversedValidator(),
    NoSubscriptValidator(),
    NoSumValidator(),
    NoDelValidator(),
    NoImportValidator(),
    NoPoopPrefixValidator(),
    NoNamespaceShadowValidator(),
    NoBuiltinShadowValidator(),
]

__all__ = ["DEFAULT_VALIDATORS", "Validator"]
