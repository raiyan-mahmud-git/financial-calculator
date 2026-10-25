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

---

## Phase 3: Modern Streamlit Web Interface (`views/` & `ui/`)

### 5-Line Summary
- **What changed:** Created modular Streamlit pages (`home`, `mortgage`, `retirement`, `growth`, `doubling`, `logarithms`, `scientific`, `ph`) using `st.navigation` and reusable UI components.
- **Why:** Replaced blocking CLI prompts with interactive metric cards, Plotly charts, side-by-side scenario comparators, and CSV export.
- **Key Concept to Learn:** **Declarative Multipage Architecture** — structuring web applications via `st.navigation` and `st.Page` provides clear routing, independent page modules, and clean execution boundaries.

---

## Phase 4: Streamlit Best Practices & Rerun Safety

### 5-Line Summary
- **What changed:** Implemented state persistence via `st.session_state["currency"]`, synced scenario states with `st.query_params`, and configured responsive dark-theme defaults.
- **Why:** Prevents state loss across widget reruns, avoids repetitive unmemoized computations, and empowers users to share bookmarked scenario links.
- **Key Concept to Learn:** **Streamlit Execution Model & State Synchronization** — Streamlit reruns scripts top-to-bottom on widget interactions; combining `session_state` with `query_params` bridges transient in-memory widget state with shareable web URLs.

---

## Phase 5: Headless UI Testing & Production Deployment

### 5-Line Summary
- **What changed:** Implemented automated headless UI testing using `streamlit.testing.v1.AppTest`, configured GitHub Actions CI matrix for Python 3.10-3.13, and added Cloud deployment guide.
- **Why:** Ensures the user interface cannot regress or throw unhandled exceptions in production, guaranteeing smooth 1-click deployment on Streamlit Community Cloud.
- **Key Concept to Learn:** **Headless Integration Testing with AppTest** — testing real Streamlit execution paths without launching a browser catches layout collisions, state race conditions, and widget typing bugs before shipping.
