# Learning Notes & Architecture Decisions

This document tracks our design decisions, core concepts, and educational summaries across each phase of developing **Financial Calculator**.

---

## Phase 0: Audit & Architecture Blueprint

### 5-Line Summary
- **What changed:** Audited the original Google Colab notebook, cataloged all bugs/edge cases, initialized repository hygiene (.gitignore, LICENSE), and drafted the system roadmap.
- **Why:** Production engineering begins with understanding legacy shortcomings (silent errors, lossy formatting, mixed concerns) before writing modern application code.
- **Key Concept to Learn:** **Separation of Concerns (SoC)** — mathematical business logic (`fincalc/core.py`) must remain pure, deterministic, and decoupled from input/output frameworks (CLI or Streamlit) to enable robust automated unit testing.

### Detailed Audit Findings
1. **Scientific Notation String Formatting Bug:**
   - Legacy: `mantissa = number / (10**exponent); return f"{mantissa:.2e}"`.
   - Flaw: Applying `:.2e` to an already normalized mantissa completely discarded the computed base-10 exponent and outputted `1.56e+00` for `156,000,000,000`.
   - Fix: Format explicitly as `f"{mantissa:.{precision}f} x 10^{exponent}"` and support round-trip parsing of multiple notation formats (`1.56e11`, `1.56 x 10^11`, `1.56*10^11`). Account for IEEE 754 float log quirks (`math.log10(1000)`) and rounding rollover (e.g. `9.999` rounding to `10.00` shifts exponent by $+1$).

2. **Error Handling via Strings vs Typed Exceptions:**
   - Legacy: Returned strings like `"Rate must be positive to double"` or `"Invalid scientific notation string"` on error, corrupting downstream numeric arithmetic.
   - Fix: Implement a clean exception hierarchy (`FinCalcError`, `InvalidInputError`, `CalculationError`) in `fincalc/errors.py`.

3. **Annuity Semantic Discrepancy & Cash-flow Definitions:**
   - Legacy: Discrete branch interpreted `payment` as per-period installment ($P \times \frac{(1+r/n)^{nt}-1}{r/n}$), whereas continuous compounding interpreted `payment` as total annual flow rate ($P \times \frac{e^{rt}-1}{r}$). Passing a monthly payment produced a continuous value off by a factor of 12.
   - Fix: Harmonize parameter definitions. Standardize `payment` as per-compounding-period payment, allow annual payment rate specification, and support both Ordinary Annuity (end-of-period) and Annuity Due (start-of-period).

4. **Incomplete Logarithmic Solver:**
   - Legacy: Solved only for $x$ given base and exponent ($x = b^y$).
   - Fix: Generalize `solve_log` to solve for any unknown variable: $x$, base $b = x^{1/y}$, or exponent $y = \log_b(x)$ with rigorous domain validation ($b > 0, b \neq 1, x > 0$).

5. **Omission of Real-World Retirement Realities:**
   - Legacy: Simple recurring monthly deposits from $\$0$ at fixed rate.
   - Fix: Support starting balance, annual contribution escalation (career salary increases), and inflation adjustment to report purchasing power alongside nominal balances.

6. **Rate Parsing Fragility:**
   - Legacy: Accepted only raw decimal floats; crashed or gave unintended results on `"5%"` or `"5"`.
   - Fix: Add robust rate parsing and validation utilities in `fincalc/formatting.py`.

7. **Missing Financial/Math Utilities from Foundational Curriculum:**
   - Add pH scale calculation ($-\log_{10}[H^+]$), amortization schedule generator with extra monthly principal payments, discrete vs Rule of 72 doubling times, and target accumulation solvers.
