"""Formatting and input parsing utilities for financial and mathematical values."""

from __future__ import annotations

from fincalc.errors import InvalidInputError

CURRENCY_SYMBOLS: dict[str, str] = {
    "USD": "$",
    "EUR": "€",
    "GBP": "£",
    "BDT": "৳",
    "JPY": "¥",
    "CAD": "CA$",
    "AUD": "AU$",
    "INR": "₹",
}


def parse_rate(val: str | float) -> float:
    """Parse an interest or growth rate into a standard decimal fraction.

    Accepts:
        - Percent string: '5%', '5.5%' -> 0.05, 0.055
        - Numeric or string integer/float > 1.0: '5', 5, 7.25 -> 0.05, 0.0725
        - Decimal rate <= 1.0: 0.05, '0.05', 0.0 -> 0.05, 0.05, 0.0

    Rejects:
        - Rates below -100% (-1.0)
        - Rates above 10,000% (100.0)
        - Non-numeric strings

    Args:
        val: The input rate as a string or number.

    Returns:
        float: The rate as a decimal (e.g. 0.05 for 5%).

    Raises:
        InvalidInputError: If the input cannot be parsed or is out of reasonable bounds.
    """
    if val is None:
        raise InvalidInputError("Rate cannot be None.")

    if isinstance(val, (int, float)):
        num = float(val)

        rate = num / 100.0 if abs(num) > 1.0 else num
    elif isinstance(val, str):
        clean = val.strip()
        if not clean:
            raise InvalidInputError("Rate string cannot be empty.")
        has_percent = clean.endswith("%")
        if has_percent:
            clean = clean[:-1].strip()

        try:
            num = float(clean)
        except ValueError as err:
            raise InvalidInputError(f"Cannot parse rate '{val}' as a valid number.") from err

        rate = num / 100.0 if has_percent or abs(num) > 1.0 else num
    else:
        raise InvalidInputError(f"Unsupported type for rate: {type(val).__name__}")

    if rate < -1.0:
        raise InvalidInputError(f"Rate cannot be less than -100% (got {rate * 100:.2f}%).")
    if rate > 100.0:
        raise InvalidInputError(f"Rate cannot exceed 10,000% (got {rate * 100:.2f}%).")

    return rate


def format_currency(amount: float, currency: str = "USD", decimals: int = 2) -> str:
    """Format a monetary amount with currency symbol and thousands separator.

    Args:
        amount: The monetary value to format.
        currency: The 3-letter currency code (e.g., 'USD', 'EUR', 'BDT').
        decimals: Number of decimal places to include (default: 2).

    Returns:
        str: Formatted currency string, e.g. '$1,234.56' or '৳10,000.00'.
    """
    sym = CURRENCY_SYMBOLS.get(currency.upper(), f"{currency} ")
    is_neg = amount < 0
    abs_amt = abs(amount)

    formatted_num = f"{abs_amt:,.0f}" if decimals == 0 else f"{abs_amt:,.{decimals}f}"

    if is_neg:
        return f"-{sym}{formatted_num}"
    return f"{sym}{formatted_num}"


def format_percent(rate: float, decimals: int = 2) -> str:
    """Format a decimal rate as a percentage string.

    Args:
        rate: Decimal rate (e.g. 0.05 for 5%).
        decimals: Decimal places for display.

    Returns:
        str: Formatted percent string, e.g. '5.00%'.
    """
    pct = rate * 100.0
    return f"{pct:.{decimals}f}%"
