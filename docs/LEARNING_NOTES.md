# Learning Notes & Architecture Decisions

This document tracks our design decisions, core concepts, and educational summaries across each phase of developing **Financial Calculator**.

---

## Phase 0: Audit & Architecture Blueprint

### 5-Line Summary
- **What changed:** Audited the original Google Colab notebook, cataloged all bugs/edge cases, initialized repository hygiene (.gitignore, LICENSE), and drafted the system roadmap.
- **Why:** Production engineering begins with understanding legacy shortcomings (silent errors, lossy formatting, mixed concerns) before writing modern application code.
- **Key Concept to Learn:** **Separation of Concerns (SoC)** — mathematical business logic (`fincalc/core.py`) must remain pure, deterministic, and decoupled from input/output frameworks (CLI or Streamlit) to enable robust automated unit testing.

---

## Phase 1: Pure Core Library Implementation (`fincalc/`)

### 5-Line Summary
- **What changed:** Built `fincalc/core.py`, `fincalc/errors.py`, and `fincalc/formatting.py` with typed, documented, pure functions covering all financial calculations and formatting.
- **Why:** Replaces legacy brittle Colab logic with robust algorithms that handle zero rates, inflation, amortization schedules, and multi-variable logarithm solving.
- **Key Concept to Learn:** **Defensive Programming & Custom Exception Hierarchies** — rather than returning polymorphic error strings that poison calculations, use a structured exception hierarchy (`FinCalcError` -> `InvalidInputError`, `CalculationError`) to cleanly communicate domain failures.

---

## Phase 2: Comprehensive Test Suite (`tests/`)

### 5-Line Summary
- **What changed:** Implemented 55 unit tests in `tests/test_core.py` and `tests/test_formatting.py` testing normal values, edge cases, zero rates, round-trips, and invalid inputs.
- **Why:** Verified mathematical correctness independently against known benchmark numbers ($200,000 mortgage at 6% over 30 years = \$1,199.10/mo; $12,534.55 annuity).
- **Key Concept to Learn:** **Property & Boundary Testing** — verify invariants like loan balances terminating at exactly \$0.00 and bidirectional transformations (`to_scientific` <-> `from_scientific`) round-tripping losslessly.
