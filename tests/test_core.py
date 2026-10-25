"""Comprehensive unit tests for the core financial mathematics library."""

import math

import pytest

from fincalc.core import (
    amortization_schedule,
    annuity_future_value,
    compound_interest,
    continuous_growth,
    doubling_time,
    from_scientific,
    mortgage_payment,
    percent_decrease,
    percent_increase,
    ph_from_concentration,
    retirement_projection,
    solve_log,
    time_to_reach_target,
    to_scientific,
)
from fincalc.errors import InvalidInputError


class TestCompoundInterest:
    """Tests for compound interest and growth calculations."""

    def test_compound_interest_monthly(self):
        # 1000 at 5% for 10 years compounded monthly: 1000 * (1 + 0.05/12)^120
        expected = 1000.0 * ((1.0 + 0.05 / 12) ** 120)
        result = compound_interest(1000.0, 0.05, 10, compounds_per_year=12)
        assert result == pytest.approx(expected, rel=1e-9)
        assert result == pytest.approx(1647.009498, abs=1e-3)

    def test_compound_interest_annual(self):
        # 1000 at 5% for 10 years compounded annually: 1000 * (1.05)^10
        expected = 1000.0 * (1.05**10)
        assert compound_interest(
            1000.0, 0.05, 10, compounds_per_year=1
        ) == pytest.approx(expected, rel=1e-9)

    def test_compound_interest_zero_rate(self):
        assert compound_interest(1500.0, 0.0, 10, compounds_per_year=12) == 1500.0

    def test_compound_interest_zero_years(self):
        assert compound_interest(2500.0, 0.08, 0, compounds_per_year=12) == 2500.0

    def test_compound_interest_invalid_inputs(self):
        with pytest.raises(InvalidInputError, match="Principal cannot be negative"):
            compound_interest(-100.0, 0.05, 5)
        with pytest.raises(InvalidInputError, match="Years cannot be negative"):
            compound_interest(100.0, 0.05, -1)
        with pytest.raises(
            InvalidInputError, match="Compounds per year must be at least 1"
        ):
            compound_interest(100.0, 0.05, 5, compounds_per_year=0)


class TestContinuousGrowth:
    """Tests for continuous compounding."""

    def test_continuous_growth_standard(self):
        # 1000 * e^(0.05 * 10) = 1000 * e^0.5
        expected = 1000.0 * math.exp(0.5)
        assert continuous_growth(1000.0, 0.05, 10) == pytest.approx(expected, rel=1e-9)
        assert continuous_growth(1000.0, 0.05, 10) == pytest.approx(
            1648.721271, abs=1e-4
        )

    def test_continuous_growth_zero_rate(self):
        assert continuous_growth(2000.0, 0.0, 5) == 2000.0

    def test_continuous_growth_invalid_inputs(self):
        with pytest.raises(InvalidInputError, match="Principal cannot be negative"):
            continuous_growth(-50.0, 0.05, 10)
        with pytest.raises(InvalidInputError, match="Years cannot be negative"):
            continuous_growth(50.0, 0.05, -2)


class TestPercentChanges:
    """Tests for exponential increase and decrease."""

    def test_percent_increase(self):
        # 100 * (1 + 0.10)^2 = 121
        assert percent_increase(100.0, 0.10, 2) == pytest.approx(121.0)
        assert percent_increase(100.0, 0.0, 5) == pytest.approx(100.0)

    def test_percent_increase_invalid(self):
        with pytest.raises(
            InvalidInputError, match="Initial amount cannot be negative"
        ):
            percent_increase(-10.0, 0.05, 1)
        with pytest.raises(InvalidInputError, match="Rate cannot be less than -100%"):
            percent_increase(10.0, -1.2, 1)
        with pytest.raises(InvalidInputError, match="Time cannot be negative"):
            percent_increase(10.0, 0.05, -1)

    def test_percent_decrease(self):
        # 100 * (1 - 0.10)^2 = 81
        assert percent_decrease(100.0, 0.10, 2) == pytest.approx(81.0)
        assert percent_decrease(100.0, 0.0, 5) == pytest.approx(100.0)

    def test_percent_decrease_invalid(self):
        with pytest.raises(
            InvalidInputError, match="Decay rate must be between 0.0 and 1.0"
        ):
            percent_decrease(100.0, 1.5, 2)
        with pytest.raises(
            InvalidInputError, match="Decay rate must be between 0.0 and 1.0"
        ):
            percent_decrease(100.0, -0.1, 2)


class TestAnnuityFutureValue:
    """Tests for annuity future values."""

    def test_hand_verified_notebook_annuity(self):
        # From the Colab notebook: payment 300, rate 0.10, 3 years, monthly compounding
        # Expected: 12534.546327077787
        res = annuity_future_value(
            300.0, 0.10, 3, compounds_per_year=12, annuity_due=False
        )
        assert res == pytest.approx(12534.546327077787, rel=1e-9)

    def test_annuity_due_factor(self):
        # Annuity due receives 1 additional compounding period of interest
        ord_fv = annuity_future_value(
            300.0, 0.10, 3, compounds_per_year=12, annuity_due=False
        )
        due_fv = annuity_future_value(
            300.0, 0.10, 3, compounds_per_year=12, annuity_due=True
        )
        assert due_fv == pytest.approx(ord_fv * (1.0 + 0.10 / 12), rel=1e-9)

    def test_continuous_annuity(self):
        # Continuous cash flow of 300/month = 3600/year at 10% for 3 years
        # 3600 * (e^(0.3) - 1) / 0.10
        expected = 3600.0 * (math.exp(0.3) - 1.0) / 0.10
        res = annuity_future_value(
            300.0, 0.10, 3, compounds_per_year=12, continuous=True
        )
        assert res == pytest.approx(expected, rel=1e-9)
        # Continuous compounding produces slightly more than monthly discrete compounding
        ord_fv = annuity_future_value(
            300.0, 0.10, 3, compounds_per_year=12, continuous=False
        )
        assert res > ord_fv

    def test_annuity_zero_rate(self):
        # With zero interest, total FV is simply payments * total periods
        assert annuity_future_value(300.0, 0.0, 3, compounds_per_year=12) == 300.0 * 36
        assert (
            annuity_future_value(300.0, 0.0, 3, compounds_per_year=12, continuous=True)
            == 300.0 * 36
        )

    def test_annuity_invalid(self):
        with pytest.raises(
            InvalidInputError, match="Payment amount cannot be negative"
        ):
            annuity_future_value(-50.0, 0.05, 5)
        with pytest.raises(InvalidInputError, match="Years cannot be negative"):
            annuity_future_value(50.0, 0.05, -5)


class TestRetirementProjection:
    """Tests for multi-year retirement simulations."""

    def test_zero_rate_matches_deposits(self):
        # Starting 5000, 200/month, 0% return, 5 years -> 5000 + (200 * 60) = 17,000
        res = retirement_projection(
            starting_balance=5000.0,
            monthly_contribution=200.0,
            annual_rate=0.0,
            years=5,
            annual_contribution_increase=0.0,
            inflation_rate=0.0,
        )
        assert res.final_nominal_balance == pytest.approx(17000.0)
        assert res.total_contributions == pytest.approx(17000.0)
        assert res.total_interest == pytest.approx(0.0)
        assert res.final_real_balance == pytest.approx(17000.0)
        assert len(res.schedule) == 5

    def test_standard_retirement_growth(self):
        res = retirement_projection(
            starting_balance=10000.0,
            monthly_contribution=500.0,
            annual_rate=0.07,
            years=10,
            annual_contribution_increase=0.0,
            inflation_rate=0.025,
        )
        assert res.final_nominal_balance > res.total_contributions
        assert res.total_interest > 0
        assert res.final_real_balance < res.final_nominal_balance
        assert len(res.schedule) == 10

        # Verify annual schedule continuity
        for i in range(1, len(res.schedule)):
            assert res.schedule[i].starting_balance == pytest.approx(
                res.schedule[i - 1].ending_nominal_balance
            )

    def test_annual_contribution_increase(self):
        # 5% annual raise in contributions increases total deposited
        base = retirement_projection(
            monthly_contribution=500, annual_rate=0.05, years=5
        )
        elevated = retirement_projection(
            monthly_contribution=500,
            annual_rate=0.05,
            years=5,
            annual_contribution_increase=0.05,
        )
        assert elevated.total_contributions > base.total_contributions
        assert elevated.final_nominal_balance > base.final_nominal_balance

    def test_retirement_invalid_inputs(self):
        with pytest.raises(
            InvalidInputError, match="Starting balance cannot be negative"
        ):
            retirement_projection(starting_balance=-10)
        with pytest.raises(
            InvalidInputError, match="Monthly contribution cannot be negative"
        ):
            retirement_projection(monthly_contribution=-5)
        with pytest.raises(InvalidInputError, match="Years must be at least 1"):
            retirement_projection(years=0)


class TestMortgageAndAmortization:
    """Tests for mortgage payments and amortization schedules."""

    def test_hand_verified_mortgage_payment(self):
        # Hand-verified from prompt: $200,000 at 6% over 30 years = 1199.10/month
        pmt = mortgage_payment(200000.0, 0.06, 30)
        assert round(pmt, 2) == 1199.10
        assert pmt == pytest.approx(1199.101104, abs=1e-3)

    def test_zero_rate_mortgage(self):
        # $120,000 over 10 years at 0% = $120,000 / 120 = $1,000/month
        assert mortgage_payment(120000.0, 0.0, 10) == pytest.approx(1000.0)

    def test_mortgage_invalid_inputs(self):
        with pytest.raises(
            InvalidInputError, match="Loan principal must be strictly positive"
        ):
            mortgage_payment(0.0, 0.05, 30)
        with pytest.raises(
            InvalidInputError, match="Annual interest rate cannot be negative"
        ):
            mortgage_payment(200000.0, -0.01, 30)
        with pytest.raises(
            InvalidInputError, match="Loan duration must be strictly positive"
        ):
            mortgage_payment(200000.0, 0.05, 0)

    def test_amortization_schedule_balances_to_zero(self):
        # Crucial check: schedule balance must end at exactly ~0
        sched = amortization_schedule(200000.0, 0.06, 30)
        assert sched.payoff_months == 360
        last_rec = sched.schedule[-1]
        assert last_rec.ending_balance == pytest.approx(0.0, abs=1e-5)

        # Sum of all principal paid must equal starting principal
        total_principal_paid = sum(r.principal_paid for r in sched.schedule)
        assert total_principal_paid == pytest.approx(200000.0, abs=1e-4)

        # Total paid must equal principal + interest
        assert sched.total_paid == pytest.approx(
            sched.total_principal + sched.total_interest
        )

    def test_amortization_with_extra_monthly_payment(self):
        # Adding $200/month extra payment saves interest and shortens payoff time
        regular = amortization_schedule(200000.0, 0.06, 30, extra_monthly_payment=0.0)
        accelerated = amortization_schedule(
            200000.0, 0.06, 30, extra_monthly_payment=200.0
        )

        assert accelerated.payoff_months < regular.payoff_months
        assert accelerated.total_interest < regular.total_interest
        assert (
            accelerated.months_saved
            == regular.payoff_months - accelerated.payoff_months
        )
        assert accelerated.interest_saved == pytest.approx(
            regular.total_interest - accelerated.total_interest
        )
        assert accelerated.schedule[-1].ending_balance == pytest.approx(0.0, abs=1e-5)


class TestDoublingAndTargetTime:
    """Tests for doubling time and target time formulas."""

    def test_doubling_time_continuous(self):
        # t = ln(2) / 0.07 ~ 9.9021
        assert doubling_time(0.07, method="continuous") == pytest.approx(
            math.log(2) / 0.07, rel=1e-9
        )

    def test_doubling_time_annual(self):
        # t = ln(2) / ln(1.07) ~ 10.2448
        assert doubling_time(0.07, method="annual") == pytest.approx(
            math.log(2) / math.log(1.07), rel=1e-9
        )

    def test_doubling_time_rule_of_72(self):
        # 72 / 7 ~ 10.2857
        assert doubling_time(0.07, method="rule_of_72") == pytest.approx(
            72.0 / 7.0, rel=1e-9
        )

    def test_doubling_time_invalid_rate(self):
        with pytest.raises(InvalidInputError, match="strictly positive"):
            doubling_time(0.0)
        with pytest.raises(InvalidInputError, match="strictly positive"):
            doubling_time(-0.05)

    def test_time_to_reach_target(self):
        # 1000 to 2000 at 7% continuous should match doubling_time(0.07, 'continuous')
        t_cont = time_to_reach_target(1000.0, 2000.0, 0.07, continuous=True)
        assert t_cont == pytest.approx(doubling_time(0.07, "continuous"))

        # Target equal to principal
        assert time_to_reach_target(1000.0, 1000.0, 0.05) == 0.0

        # Target less than principal
        with pytest.raises(
            InvalidInputError, match="greater than or equal to principal"
        ):
            time_to_reach_target(1000.0, 500.0, 0.05)


class TestSolveLog:
    """Tests for solving logarithmic equations."""

    def test_solve_for_x(self):
        # log_2(x) = 4 -> x = 2^4 = 16
        assert solve_log(base=2, exponent=4) == pytest.approx(16.0)
        # log_10(x) = 3 -> x = 1000
        assert solve_log(base=10, exponent=3) == pytest.approx(1000.0)

    def test_solve_for_exponent(self):
        # log_2(16) = y -> y = 4
        assert solve_log(base=2, x=16) == pytest.approx(4.0)
        # log_10(1000) = 3
        assert solve_log(base=10, x=1000) == pytest.approx(3.0)

    def test_solve_for_base(self):
        # b^4 = 16 -> b = 16^(1/4) = 2
        assert solve_log(x=16, exponent=4) == pytest.approx(2.0)
        # b^3 = 27 -> b = 3
        assert solve_log(x=27, exponent=3) == pytest.approx(3.0)

    def test_solve_log_domain_errors(self):
        with pytest.raises(InvalidInputError, match="Logarithm base must be positive"):
            solve_log(base=-2, exponent=4)
        with pytest.raises(InvalidInputError, match="Logarithm base cannot be 1.0"):
            solve_log(base=1.0, exponent=4)
        with pytest.raises(InvalidInputError, match="Argument x must be positive"):
            solve_log(base=2, x=-16)
        with pytest.raises(InvalidInputError, match="Exactly two"):
            solve_log(base=2)  # Only 1 provided
        with pytest.raises(InvalidInputError, match="Exactly two"):
            solve_log(base=2, x=16, exponent=4)  # All 3 provided


class TestScientificNotation:
    """Tests for scientific notation conversion and round trips."""

    def test_prompt_156_billion_fix(self):
        # Hand-verified bug in notebook: 156000000000 previously returned 1.56e+00
        # Now must output "1.56 x 10^11"
        assert to_scientific(156000000000) == "1.56 x 10^11"

    def test_small_number(self):
        # Notebook step 17: 0.000000000413 -> 4.13 x 10^-10
        assert to_scientific(0.000000000413) == "4.13 x 10^-10"

    def test_zero(self):
        assert to_scientific(0) == "0.00 x 10^0"
        assert to_scientific(0.0, precision=4) == "0.0000 x 10^0"

    def test_negatives(self):
        assert to_scientific(-156000000000) == "-1.56 x 10^11"
        assert to_scientific(-0.0005) == "-5.00 x 10^-4"

    def test_rounding_edge_9_999(self):
        # 9.999 rounded to 2 decimals rounds to 10.00 -> 1.00 x 10^1
        assert to_scientific(9.999, precision=2) == "1.00 x 10^1"

    def test_float_log10_quirks(self):
        # 1000.0 can suffer from log10(1000) = 2.9999999999999996 in naive code
        assert to_scientific(1000.0) == "1.00 x 10^3"

    def test_from_scientific_formats(self):
        # Test various representations
        assert from_scientific("1.56e11") == pytest.approx(156000000000.0)
        assert from_scientific("1.56 x 10^11") == pytest.approx(156000000000.0)
        assert from_scientific("1.56*10^11") == pytest.approx(156000000000.0)
        assert from_scientific("1.56 * 10^11") == pytest.approx(156000000000.0)
        assert from_scientific("1.56 × 10^11") == pytest.approx(156000000000.0)
        assert from_scientific("-4.13 x 10^-10") == pytest.approx(-0.000000000413)

    def test_round_trip(self):
        # Round trip test: number -> to_scientific -> from_scientific
        numbers = [156000000000, 0.000000000413, 1000.0, -42000, 9.999, 1.23e-15]
        for num in numbers:
            sci = to_scientific(num, precision=4)
            parsed = from_scientific(sci)
            assert parsed == pytest.approx(num, rel=1e-3)

    def test_invalid_scientific_string(self):
        with pytest.raises(InvalidInputError, match="Cannot parse scientific notation"):
            from_scientific("invalid string")
        with pytest.raises(InvalidInputError, match="cannot be empty"):
            from_scientific("   ")


class TestPHFromConcentration:
    """Tests for pH calculation."""

    def test_ph_calculations(self):
        # Step 21 in notebook: concentration 0.007 -> pH = -log10(0.007) ~ 2.15
        res = ph_from_concentration(0.007)
        assert res.ph == pytest.approx(-math.log10(0.007), rel=1e-9)
        assert round(res.ph, 2) == 2.15
        assert res.classification == "Acidic"
        assert res.poh == pytest.approx(14.0 - res.ph)

    def test_ph_neutral_and_alkaline(self):
        neutral = ph_from_concentration(1e-7)
        assert neutral.ph == pytest.approx(7.0)
        assert neutral.classification == "Neutral"

        alkaline = ph_from_concentration(1e-11)
        assert alkaline.ph == pytest.approx(11.0)
        assert alkaline.classification == "Basic (Alkaline)"

    def test_ph_invalid(self):
        with pytest.raises(InvalidInputError, match="strictly positive"):
            ph_from_concentration(0.0)
        with pytest.raises(InvalidInputError, match="strictly positive"):
            ph_from_concentration(-1e-5)
