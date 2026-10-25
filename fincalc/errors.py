"""Custom exception hierarchy for the Financial Calculator library.

Using custom typed exceptions ensures that mathematical edge cases, invalid
user inputs, or arithmetic impossibilities are reported cleanly to calling code
(such as the Streamlit UI or unit tests) without returning ambiguous error strings
or raising unhandled internal crashes.
"""


class FinCalcError(Exception):
    """Base exception for all financial calculator errors."""


class InvalidInputError(FinCalcError, ValueError):
    """Raised when an input parameter is outside the valid domain.

    Examples:
        - Negative interest rates where not allowed
        - Negative loan principal or duration
        - Logarithm base <= 0 or == 1
        - Hydrogen concentration <= 0 for pH
    """


class CalculationError(FinCalcError, ArithmeticError):
    """Raised when an arithmetic or numerical computation fails or diverges.

    Examples:
        - Division by zero in cash flow formulas
        - Non-converging amortization calculations
    """
