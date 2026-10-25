"""Custom exception hierarchy for the Financial Calculator library.

"""


class FinCalcError(Exception):
    """Base exception for all financial calculator errors."""


class InvalidInputError(FinCalcError, ValueError):
    """when an input parameter is outside the valid domain.

    """


class CalculationError(FinCalcError, ArithmeticError):
    """when an arithmetic or numerical computation fails or diverges.

    """
