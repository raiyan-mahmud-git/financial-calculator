"""Core financial and mathematical computation library."""

from __future__ import annotations

import math
import re
from dataclasses import dataclass
from typing import Literal

from fincalc.errors import CalculationError, InvalidInputError


@dataclass(frozen=True)
class RetirementRecord:
    """Represents a single year's projection in a retirement timeline."""

    year: int
    starting_balance: float
    annual_contributions: float
    annual_interest: float
    ending_nominal_balance: float
    ending_real_balance: float
    cumulative_contributions: float
    cumulative_interest: float


@dataclass(frozen=True)
class RetirementResult:
    """Summary and year-by-year schedule for a retirement investment projection."""

    final_nominal_balance: float
    final_real_balance: float
    total_contributions: float
    total_interest: float
    schedule: list[RetirementRecord]


@dataclass(frozen=True)
class AmortizationRecord:
    """Monthly amortization record for a loan payment."""

    month: int
    beginning_balance: float
    payment: float
    principal_paid: float
    interest_paid: float
    ending_balance: float
    cumulative_interest: float


@dataclass(frozen=True)
class AmortizationResult:
    """Complete amortization analysis including schedule and payoff comparisons."""

    base_monthly_payment: float
    actual_monthly_payment: float
    total_principal: float
    total_interest: float
    total_paid: float
    payoff_months: int
    payoff_years: float
    interest_saved: float
    months_saved: int
    schedule: list[AmortizationRecord]


@dataclass(frozen=True)
class PHResult:
    """Results of a pH calculation from hydrogen ion concentration."""

    concentration: float
    ph: float
    poh: float
    classification: str


def compound_interest(
    principal: float,
    annual_rate: float,
    years: float,
    compounds_per_year: int = 1,
) -> float:
    r"""Calculate future value of a lump sum with compound interest.

    Formula:
        $$A = P \left(1 + \frac{r}{n}\right)^{nt}$$
        When $r = 0$: $A = P$

    Example:
        >>> compound_interest(1000.0, 0.05, 10, compounds_per_year=12)
        1647.00949769028

    Args:
        principal: Initial lump sum amount ($P \ge 0$).
        annual_rate: Nominal annual interest rate as a decimal (e.g. 0.05 for 5%).
        years: Number of years the investment grows ($t \ge 0$).
        compounds_per_year: Compounding frequency per year ($n \ge 1$).

    Returns:
        float: Future accumulated amount $A$.

    Raises:
        InvalidInputError: If principal < 0, years < 0, or compounds_per_year < 1.
    """
    if principal < 0:
        raise InvalidInputError("Principal cannot be negative.")
    if years < 0:
        raise InvalidInputError("Years cannot be negative.")
    if compounds_per_year < 1:
        raise InvalidInputError("Compounds per year must be at least 1.")

    if annual_rate == 0:
        return float(principal)

    # Periodic rate
    periodic_rate = annual_rate / compounds_per_year
    total_periods = compounds_per_year * years
    return principal * math.pow(1.0 + periodic_rate, total_periods)


def continuous_growth(
    principal: float,
    annual_rate: float,
    years: float,
) -> float:
    r"""Calculate future value with continuous compounding.

    Formula:
        $$A = P \cdot e^{rt}$$
        When $r = 0$: $A = P$

    Example:
        >>> continuous_growth(1000.0, 0.05, 10)
        1648.7212707001282

    Args:
        principal: Initial lump sum ($P \ge 0$).
        annual_rate: Continuous growth rate as a decimal.
        years: Time in years ($t \ge 0$).

    Returns:
        float: Future accumulated amount $A$.

    Raises:
        InvalidInputError: If principal < 0 or years < 0.
    """
    if principal < 0:
        raise InvalidInputError("Principal cannot be negative.")
    if years < 0:
        raise InvalidInputError("Years cannot be negative.")

    if annual_rate == 0:
        return float(principal)

    return principal * math.exp(annual_rate * years)


def percent_increase(
    initial: float,
    rate: float,
    time: float = 1.0,
) -> float:
    r"""Calculate the value after exponential percent increase.

    Formula:
        $$A = P (1 + r)^t$$

    Example:
        >>> percent_increase(100.0, 0.10, 2)
        121.00000000000001

    Args:
        initial: Starting value ($P \ge 0$).
        rate: Percentage growth rate per period ($r \ge -1.0$).
        time: Number of periods ($t \ge 0$).

    Returns:
        float: Increased amount $A$.
    """
    if initial < 0:
        raise InvalidInputError("Initial amount cannot be negative.")
    if rate < -1.0:
        raise InvalidInputError("Rate cannot be less than -100%.")
    if time < 0:
        raise InvalidInputError("Time cannot be negative.")

    if rate == 0:
        return float(initial)

    return initial * math.pow(1.0 + rate, time)


def percent_decrease(
    initial: float,
    rate: float,
    time: float = 1.0,
) -> float:
    r"""Calculate the value after exponential percent decrease (depreciation/decay).

    Formula:
        $$A = P (1 - r)^t$$

    Example:
        >>> percent_decrease(100.0, 0.10, 2)
        81.0

    Args:
        initial: Starting value ($P \ge 0$).
        rate: Percentage depreciation rate ($0 \le r \le 1.0$).
        time: Number of periods ($t \ge 0$).

    Returns:
        float: Decreased amount $A$.
    """
    if initial < 0:
        raise InvalidInputError("Initial amount cannot be negative.")
    if rate < 0 or rate > 1.0:
        raise InvalidInputError("Decay rate must be between 0.0 and 1.0 (0% to 100%).")
    if time < 0:
        raise InvalidInputError("Time cannot be negative.")

    if rate == 0:
        return float(initial)

    return initial * math.pow(1.0 - rate, time)


def annuity_future_value(
    payment: float,
    annual_rate: float,
    years: float,
    compounds_per_year: int = 12,
    annuity_due: bool = False,
    continuous: bool = False,
) -> float:
    r"""Calculate future value of a series of recurring equal payments (annuity).

    Formulas:
        Discrete Ordinary Annuity:
            $$FV = P \left[\frac{(1 + i)^N - 1}{i}\right]$$
            where $i = r / n$, $N = n \cdot t$.
        Discrete Annuity Due (payments made at beginning of period):
            $$FV_{\text{due}} = FV \cdot (1 + i)$$
        Continuous Compounding:
            Here the annual payment cash flow rate is $R = P \cdot n$.
            $$FV_{\text{cont}} = R \left[\frac{e^{rt} - 1}{r}\right]$$
        Zero-rate edge case ($r = 0$):
            $$FV = P \cdot n \cdot t$$

    Example:
        >>> annuity_future_value(300.0, 0.10, 3.0, compounds_per_year=12)
        12534.546327077787

    Args:
        payment: Recurring installment per compounding period ($P \ge 0$).
        annual_rate: Annual nominal interest rate (decimal).
        years: Investment duration in years ($t \ge 0$).
        compounds_per_year: Number of payment periods per year ($n \ge 1$).
        annuity_due: If True, payments occur at period start; if False, at period end.
        continuous: If True, treats cash flow as continuous compounding.

    Returns:
        float: Future value $FV$.
    """
    if payment < 0:
        raise InvalidInputError("Payment amount cannot be negative.")
    if years < 0:
        raise InvalidInputError("Years cannot be negative.")
    if compounds_per_year < 1:
        raise InvalidInputError("Compounds per year must be at least 1.")

    total_periods = compounds_per_year * years

    if annual_rate == 0:
        return float(payment * total_periods)

    if continuous:
        # Annual flow rate is payment * n
        annual_cash_flow = payment * compounds_per_year
        return annual_cash_flow * (math.exp(annual_rate * years) - 1.0) / annual_rate

    periodic_rate = annual_rate / compounds_per_year
    fv = payment * (math.pow(1.0 + periodic_rate, total_periods) - 1.0) / periodic_rate
    if annuity_due:
        fv *= 1.0 + periodic_rate
    return fv


def retirement_projection(
    starting_balance: float = 0.0,
    monthly_contribution: float = 0.0,
    annual_rate: float = 0.0,
    years: int = 30,
    annual_contribution_increase: float = 0.0,
    inflation_rate: float = 0.0,
) -> RetirementResult:
    r"""Simulate a comprehensive year-by-year retirement investment trajectory.

    Models:
        - Initial principal seed ($P_0$)
        - Monthly deposits with annual contribution growth (salary raises)
        - Monthly compounding interest
        - Real purchasing power adjustment via inflation indexation:
          $$\text{Real Balance}_y = \frac{\text{Nominal Balance}_y}{(1 + r_{\text{inf}})^y}$$

    Example:
        >>> res = retirement_projection(10000, 500, 0.07, 10)
        >>> round(res.final_nominal_balance, 2)
        105953.94

    Args:
        starting_balance: Initial account balance ($P_0 \ge 0$).
        monthly_contribution: Starting monthly deposit ($C \ge 0$).
        annual_rate: Expected nominal investment return (decimal).
        years: Investment horizon in whole years ($t \ge 1$).
        annual_contribution_increase: Annual percentage raise in contribution amount.
        inflation_rate: Expected annual inflation rate for real purchasing power.

    Returns:
        RetirementResult: Complete summary and year-by-year table.
    """
    if starting_balance < 0:
        raise InvalidInputError("Starting balance cannot be negative.")
    if monthly_contribution < 0:
        raise InvalidInputError("Monthly contribution cannot be negative.")
    if years < 1:
        raise InvalidInputError("Years must be at least 1.")
    if annual_contribution_increase < -1.0:
        raise InvalidInputError("Annual contribution increase cannot be less than -100%.")

    monthly_rate = annual_rate / 12.0
    current_balance = float(starting_balance)
    cumulative_contributions = float(starting_balance)
    cumulative_interest = 0.0
    schedule: list[RetirementRecord] = []

    for y in range(1, years + 1):
        year_start = current_balance
        # Monthly contribution escalates every year by contribution increase rate
        current_monthly_deposit = monthly_contribution * math.pow(
            1.0 + annual_contribution_increase, y - 1
        )
        annual_deposits = 0.0
        annual_interest = 0.0

        for _ in range(12):
            # Interest earned during month on existing balance
            month_interest = current_balance * monthly_rate
            current_balance += month_interest
            # Contribution added at end of month
            current_balance += current_monthly_deposit

            annual_interest += month_interest
            annual_deposits += current_monthly_deposit

        cumulative_contributions += annual_deposits
        cumulative_interest += annual_interest

        # Purchasing power discount
        real_balance = current_balance / math.pow(1.0 + inflation_rate, y)

        schedule.append(
            RetirementRecord(
                year=y,
                starting_balance=year_start,
                annual_contributions=annual_deposits,
                annual_interest=annual_interest,
                ending_nominal_balance=current_balance,
                ending_real_balance=real_balance,
                cumulative_contributions=cumulative_contributions,
                cumulative_interest=cumulative_interest,
            )
        )

    return RetirementResult(
        final_nominal_balance=current_balance,
        final_real_balance=schedule[-1].ending_real_balance,
        total_contributions=cumulative_contributions,
        total_interest=cumulative_interest,
        schedule=schedule,
    )


def mortgage_payment(
    principal: float,
    annual_rate: float,
    years: float,
    payments_per_year: int = 12,
) -> float:
    r"""Calculate periodic payment for a fixed-rate amortized loan.

    Formula:
        $$PMT = P \left[\frac{i (1 + i)^N}{(1 + i)^N - 1}\right]$$
        where $i = r / n$, $N = n \cdot t$.
        When $r = 0$: $PMT = P / N$.

    Example:
        >>> mortgage_payment(200000.0, 0.06, 30)
        1199.101104391694

    Args:
        principal: Total loan balance ($P > 0$).
        annual_rate: Nominal annual interest rate (decimal, $\ge 0$).
        years: Loan duration in years ($t > 0$).
        payments_per_year: Payment frequency per year (default: 12).

    Returns:
        float: Periodic payment amount $PMT$.
    """
    if principal <= 0:
        raise InvalidInputError("Loan principal must be strictly positive.")
    if annual_rate < 0:
        raise InvalidInputError("Annual interest rate cannot be negative.")
    if years <= 0:
        raise InvalidInputError("Loan duration must be strictly positive.")
    if payments_per_year < 1:
        raise InvalidInputError("Payments per year must be at least 1.")

    total_payments = payments_per_year * years
    if annual_rate == 0:
        return principal / total_payments

    periodic_rate = annual_rate / payments_per_year
    compounded = math.pow(1.0 + periodic_rate, total_payments)
    denominator = compounded - 1.0

    if denominator == 0:
        raise CalculationError("Amortization calculation resulted in zero denominator.")

    return principal * (periodic_rate * compounded) / denominator


def amortization_schedule(
    principal: float,
    annual_rate: float,
    years: int,
    extra_monthly_payment: float = 0.0,
    payments_per_year: int = 12,
) -> AmortizationResult:
    r"""Generate complete month-by-month loan amortization schedule.

    Tracks monthly interest vs principal breakdown and calculates exact savings
    (interest saved and payoff accelerated) when paying an extra amount monthly.

    Example:
        >>> res = amortization_schedule(200000, 0.06, 30, extra_monthly_payment=100)
        >>> res.months_saved > 0
        True

    Args:
        principal: Starting loan balance ($P > 0$).
        annual_rate: Annual interest rate as decimal ($\ge 0$).
        years: Original loan term in whole years ($\ge 1$).
        extra_monthly_payment: Additional payment applied directly to principal ($\ge 0$).
        payments_per_year: Payments per year (typically 12).

    Returns:
        AmortizationResult: Schedule, summary metrics, and payoff savings.
    """
    if extra_monthly_payment < 0:
        raise InvalidInputError("Extra monthly payment cannot be negative.")

    base_pmt = mortgage_payment(principal, annual_rate, years, payments_per_year)
    periodic_rate = annual_rate / payments_per_year

    # First, calculate baseline total interest without extra payments
    if extra_monthly_payment > 0:
        baseline = amortization_schedule(
            principal,
            annual_rate,
            years,
            extra_monthly_payment=0.0,
            payments_per_year=payments_per_year,
        )
        baseline_interest = baseline.total_interest
        baseline_months = baseline.payoff_months
    else:
        baseline_interest = None
        baseline_months = None

    balance = float(principal)
    cumulative_interest = 0.0
    total_paid = 0.0
    schedule: list[AmortizationRecord] = []
    month = 0
    max_months = years * payments_per_year * 2  # Guard against runaway loops

    while balance > 1e-7 and month < max_months:
        month += 1
        beg_balance = balance
        interest_charge = beg_balance * periodic_rate
        target_payment = base_pmt + extra_monthly_payment

        # Total amount required to retire loan this month
        full_payoff_needed = beg_balance + interest_charge

        if target_payment >= full_payoff_needed:
            actual_payment = full_payoff_needed
            principal_paid = beg_balance
            balance = 0.0
        else:
            actual_payment = target_payment
            principal_paid = actual_payment - interest_charge
            balance = beg_balance - principal_paid

        cumulative_interest += interest_charge
        total_paid += actual_payment

        schedule.append(
            AmortizationRecord(
                month=month,
                beginning_balance=beg_balance,
                payment=actual_payment,
                principal_paid=principal_paid,
                interest_paid=interest_charge,
                ending_balance=balance,
                cumulative_interest=cumulative_interest,
            )
        )

    payoff_months = month
    payoff_years = payoff_months / payments_per_year

    if baseline_interest is not None and baseline_months is not None:
        interest_saved = max(0.0, baseline_interest - cumulative_interest)
        months_saved = max(0, baseline_months - payoff_months)
    else:
        interest_saved = 0.0
        months_saved = 0

    return AmortizationResult(
        base_monthly_payment=base_pmt,
        actual_monthly_payment=base_pmt + extra_monthly_payment,
        total_principal=principal,
        total_interest=cumulative_interest,
        total_paid=total_paid,
        payoff_months=payoff_months,
        payoff_years=payoff_years,
        interest_saved=interest_saved,
        months_saved=months_saved,
        schedule=schedule,
    )


def doubling_time(
    rate: float,
    method: Literal["continuous", "annual", "rule_of_72"] = "continuous",
) -> float:
    r"""Calculate time (in years) required for an investment to double in value.

    Formulas:
        Continuous:
            $$t = \frac{\ln(2)}{r}$$
        Annual Discrete:
            $$(1 + r)^t = 2 \implies t = \frac{\ln(2)}{\ln(1 + r)}$$
        Rule of 72 (mental approximation):
            $$t \approx \frac{72}{r \times 100}$$

    Example:
        >>> round(doubling_time(0.07, method="continuous"), 2)
        9.9
        >>> round(doubling_time(0.07, method="rule_of_72"), 2)
        10.29

    Args:
        rate: Annual growth rate as decimal ($r > 0$).
        method: Compounding model ('continuous', 'annual', or 'rule_of_72').

    Returns:
        float: Years required to double.
    """
    if rate <= 0:
        raise InvalidInputError("Rate must be strictly positive to double.")

    if method == "continuous":
        return math.log(2.0) / rate
    elif method == "annual":
        return math.log(2.0) / math.log(1.0 + rate)
    elif method == "rule_of_72":
        return 72.0 / (rate * 100.0)
    else:
        raise InvalidInputError(f"Unknown doubling time method: '{method}'")


def time_to_reach_target(
    principal: float,
    target: float,
    annual_rate: float,
    continuous: bool = False,
) -> float:
    r"""Calculate the time in years required to grow from principal to target.

    Formulas:
        Discrete (annual):
            $$t = \frac{\ln(\text{target} / P)}{\ln(1 + r)}$$
        Continuous:
            $$t = \frac{\ln(\text{target} / P)}{r}$$

    Example:
        >>> round(time_to_reach_target(1000, 2000, 0.07, continuous=True), 2)
        9.9

    Args:
        principal: Initial lump sum ($P > 0$).
        target: Target amount ($T \ge P$).
        annual_rate: Annual growth rate as decimal ($r > 0$).
        continuous: If True, uses continuous compounding; else annual discrete.

    Returns:
        float: Years required.
    """
    if principal <= 0:
        raise InvalidInputError("Principal must be strictly positive.")
    if target < principal:
        raise InvalidInputError("Target must be greater than or equal to principal.")
    if target == principal:
        return 0.0
    if annual_rate <= 0:
        raise InvalidInputError("Annual rate must be strictly positive to grow to target.")

    ratio = target / principal
    if continuous:
        return math.log(ratio) / annual_rate
    return math.log(ratio) / math.log(1.0 + annual_rate)


def solve_log(
    base: float | None = None,
    x: float | None = None,
    exponent: float | None = None,
) -> float:
    r"""Solve the logarithmic relation $\log_b(x) = y \iff b^y = x$.

    Provide exactly two known arguments to solve for the third (None).

    Formulas:
        - Solve for $x$ (given base $b$ and exponent $y$):
          $$x = b^y$$
        - Solve for exponent $y$ (given base $b$ and $x$):
          $$y = \frac{\ln(x)}{\ln(b)}$$
        - Solve for base $b$ (given $x$ and exponent $y$):
          $$b = x^{1 / y}$$

    Examples:
        >>> solve_log(base=2, exponent=4)  # Solve for x
        16.0
        >>> solve_log(base=2, x=16)        # Solve for exponent
        4.0
        >>> solve_log(x=16, exponent=4)    # Solve for base
        2.0

    Args:
        base: The logarithm base ($b > 0, b \neq 1$).
        x: The argument / result ($x > 0$).
        exponent: The exponent / log value $y$.

    Returns:
        float: The calculated missing value.

    Raises:
        InvalidInputError: If inputs are invalid or domain restrictions violated.
    """
    provided = [arg for arg in (base, x, exponent) if arg is not None]
    if len(provided) != 2:
        raise InvalidInputError(
            f"Exactly two of (base, x, exponent) must be provided; received {len(provided)}."
        )

    # 1. Solve for x: b^y = x
    if x is None:
        assert base is not None and exponent is not None
        if base <= 0:
            raise InvalidInputError(f"Logarithm base must be positive (got {base}).")
        if math.isclose(base, 1.0):
            raise InvalidInputError("Logarithm base cannot be 1.0.")
        return math.pow(base, exponent)

    # 2. Solve for exponent y: log_b(x) = y
    if exponent is None:
        assert base is not None and x is not None
        if base <= 0:
            raise InvalidInputError(f"Logarithm base must be positive (got {base}).")
        if math.isclose(base, 1.0):
            raise InvalidInputError("Logarithm base cannot be 1.0.")
        if x <= 0:
            raise InvalidInputError(f"Argument x must be positive (got {x}).")
        return math.log(x) / math.log(base)

    # 3. Solve for base b: b = x^(1/y)
    assert base is None and x is not None and exponent is not None
    if x <= 0:
        raise InvalidInputError(f"Argument x must be positive (got {x}).")
    if exponent == 0:
        raise InvalidInputError("Cannot solve for base when exponent is 0.")
    calculated_base = math.pow(x, 1.0 / exponent)
    if math.isclose(calculated_base, 1.0) and not math.isclose(x, 1.0):
        raise InvalidInputError("Resulting base is 1.0, which cannot produce a non-1 value.")
    return calculated_base


def to_scientific(number: float, precision: int = 2) -> str:
    r"""Format a real number in standard scientific notation $m \times 10^e$.

    Accurately handles:
        - Numbers of any magnitude without losing the exponent (e.g. 156000000000 -> '1.56 x 10^11')
        - Rounding rollover (e.g. 9.999 with precision 2 becomes '1.00 x 10^1')
        - Zero -> '0.00 x 10^0'
        - Negative values -> '-1.56 x 10^11'
        - Float log10 precision quirks

    Example:
        >>> to_scientific(156000000000)
        '1.56 x 10^11'
        >>> to_scientific(0.000000000413)
        '4.13 x 10^-10'

    Args:
        number: The real number to format.
        precision: Number of decimal places in the mantissa.

    Returns:
        str: Scientific notation formatted as 'm x 10^e'.
    """
    if precision < 0:
        raise InvalidInputError("Precision must be non-negative.")

    if number == 0:
        zero_mantissa = f"{0.0:.{precision}f}"
        return f"{zero_mantissa} x 10^0"

    is_negative = number < 0
    abs_num = abs(number)

    # Python's built-in format string 'e' reliably performs exact IEEE 754 rounding
    # and exponent adjustment without math.log10 floating point precision quirks.
    raw_sci = f"{abs_num:.{precision}e}"  # e.g. '1.56e+11' or '1.00e+01'
    mantissa_str, exp_str = raw_sci.split("e")
    exponent = int(exp_str)

    sign = "-" if is_negative else ""
    return f"{sign}{mantissa_str} x 10^{exponent}"


def from_scientific(sci_str: str) -> float:
    r"""Parse a scientific notation string into a standard Python float.

    Supports multiple human and computer formats:
        - '1.56 x 10^11', '1.56x10^11'
        - '1.56 * 10^11', '1.56*10^11'
        - '1.56 × 10^11' (unicode multiplication)
        - '1.56e11', '1.56E+11', '1.56e-10'
        - Standard numeric strings: '12345.67', '-0.005'

    Example:
        >>> from_scientific("1.56 x 10^11")
        156000000000.0

    Args:
        sci_str: The string representation to parse.

    Returns:
        float: The parsed numeric value.

    Raises:
        InvalidInputError: If string cannot be parsed as valid scientific notation.
    """
    if not isinstance(sci_str, str):
        raise InvalidInputError(f"Expected string input, got {type(sci_str).__name__}.")

    clean = sci_str.strip()
    if not clean:
        raise InvalidInputError("Scientific notation string cannot be empty.")

    # Try standard Python float parsing first (handles '1.56e11', '-3.2', etc.)
    try:
        return float(clean)
    except ValueError:
        pass

    # Pattern for mantissa * 10^exponent with various multiplication symbols
    pattern = (
        r"^\s*([+-]?(?:\d+(?:\.\d*)?|\.\d+))\s*"
        r"(?:[xX*×]|\*)\s*10\s*(?:\^|\*\*)\s*([+-]?\d+)\s*$"
    )
    match = re.match(pattern, clean)
    if match:
        mantissa_str, exp_str = match.groups()
        try:
            mantissa = float(mantissa_str)
            exponent = int(exp_str)
            return mantissa * math.pow(10.0, exponent)
        except (ValueError, OverflowError) as err:
            raise InvalidInputError(f"Failed to parse numeric components of '{sci_str}'.") from err

    raise InvalidInputError(f"Cannot parse scientific notation string: '{sci_str}'")


def ph_from_concentration(hydrogen_concentration: float) -> PHResult:
    r"""Calculate pH and classify acidity/alkalinity from hydrogen ion concentration $[H^+]$.

    Formulas:
        $$\text{pH} = -\log_{10}([H^+])$$
        $$\text{pOH} = 14.0 - \text{pH}$$

    Classification:
        - $\text{pH} < 7.0$: Acidic
        - $\text{pH} = 7.0$: Neutral
        - $\text{pH} > 7.0$: Basic (Alkaline)

    Example:
        >>> res = ph_from_concentration(0.007)
        >>> round(res.ph, 2)
        2.15

    Args:
        hydrogen_concentration: $[H^+]$ concentration in mol/L (strictly $> 0$).

    Returns:
        PHResult: Named result with pH, pOH, and classification string.

    Raises:
        InvalidInputError: If concentration is $\le 0$.
    """
    if hydrogen_concentration <= 0:
        raise InvalidInputError(
            f"Hydrogen concentration must be strictly positive (got {hydrogen_concentration})."
        )

    ph = -math.log10(hydrogen_concentration)
    poh = 14.0 - ph

    if math.isclose(ph, 7.0, abs_tol=1e-5):
        classification = "Neutral"
    elif ph < 7.0:
        classification = "Acidic"
    else:
        classification = "Basic (Alkaline)"

    return PHResult(
        concentration=hydrogen_concentration,
        ph=ph,
        poh=poh,
        classification=classification,
    )
