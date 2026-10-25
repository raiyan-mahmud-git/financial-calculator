"""Unit tests for formatting and parsing functions."""

import pytest

from fincalc.errors import InvalidInputError
from fincalc.formatting import format_currency, format_percent, parse_rate


class TestParseRate:
    """Test rate parsing for diverse human and numeric inputs."""

    def test_parse_percentage_string(self):
        assert parse_rate("5%") == pytest.approx(0.05)
        assert parse_rate("5.5%") == pytest.approx(0.055)
        assert parse_rate("0.25%") == pytest.approx(0.0025)
        assert parse_rate(" 10 % ") == pytest.approx(0.10)

    def test_parse_number_greater_than_one(self):
        assert parse_rate("5") == pytest.approx(0.05)
        assert parse_rate(5) == pytest.approx(0.05)
        assert parse_rate(7.5) == pytest.approx(0.075)
        assert parse_rate("12.5") == pytest.approx(0.125)

    def test_parse_decimal_rate(self):
        assert parse_rate(0.05) == pytest.approx(0.05)
        assert parse_rate("0.05") == pytest.approx(0.05)
        assert parse_rate(0.0) == pytest.approx(0.0)
        assert parse_rate("0") == pytest.approx(0.0)

    def test_parse_zero_and_negative_rates(self):
        assert parse_rate("-5%") == pytest.approx(-0.05)
        assert parse_rate(-0.02) == pytest.approx(-0.02)

    def test_invalid_rates(self):
        with pytest.raises(InvalidInputError, match="cannot be None"):
            parse_rate(None)  # type: ignore[arg-type]

        with pytest.raises(InvalidInputError, match="cannot be empty"):
            parse_rate("   ")

        with pytest.raises(InvalidInputError, match="Cannot parse rate"):
            parse_rate("five percent")

        with pytest.raises(InvalidInputError, match="less than -100%"):
            parse_rate("-150%")

        with pytest.raises(InvalidInputError, match="cannot exceed 10,000%"):
            parse_rate("15000%")


class TestFormatters:
    """Test string formatters for currency and percentages."""

    def test_format_currency_usd(self):
        assert format_currency(1234.56, "USD") == "$1,234.56"
        assert format_currency(0.0, "USD") == "$0.00"
        assert format_currency(-500.25, "USD") == "-$500.25"

    def test_format_currency_international(self):
        assert format_currency(1000000.0, "EUR") == "€1,000,000.00"
        assert format_currency(50000.0, "GBP") == "£50,000.00"
        assert format_currency(7500.50, "BDT") == "৳7,500.50"
        assert format_currency(1200.0, "JPY", decimals=0) == "¥1,200"

    def test_format_percent(self):
        assert format_percent(0.05) == "5.00%"
        assert format_percent(0.0725, decimals=2) == "7.25%"
        assert format_percent(0.07254, decimals=3) == "7.254%"
