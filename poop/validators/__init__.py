from poop.validators.base import Validator
from poop.validators.no_if import NoIfValidator

DEFAULT_VALIDATORS: list[Validator] = [NoIfValidator()]

__all__ = ["DEFAULT_VALIDATORS", "Validator"]
