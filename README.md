# 💰 Financial Calculator & Modeling Suite

[![CI](https://github.com/raiyan-mahmud-git/financial-calculator/actions/workflows/ci.yml/badge.svg)](https://github.com/raiyan-mahmud-git/financial-calculator/actions/workflows/ci.yml)
[![Python Version](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-blue)](https://www.python.org/)
[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://financial-calculator.streamlit.app/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code Style: Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

A modern, production-grade financial and mathematical web application built with **Streamlit** and pure Python. Decoupled from legacy interactive notebook dependencies, this application offers deterministic, high-precision financial projections, interactive Plotly visualizations, scenario comparisons, and CSV export capabilities.

---

## ✨ Features

- **🏡 Mortgage & Loan Amortization:**
  - Standard periodic payments ($PMT$) across custom terms and rates.
  - Month-by-month interactive amortization schedule ending at balance \$0.00.
  - Accelerated payoff calculation: model extra monthly principal payments to measure interest saved and months saved.
  - One-click CSV download of complete amortization schedules.
  - Side-by-side scenario comparison (e.g., 30-year vs 15-year terms).

- **📈 Retirement Wealth Planner:**
  - Multi-decade wealth accumulation simulations with monthly compounding.
  - Realistic real-world inputs: starting nest egg, monthly savings, and annual career salary raises.
  - Inflation discounting to calculate real purchasing power in today's dollars.
  - Side-by-side asset allocation comparison (e.g., Conservative Fixed Income vs Growth Equities).

- **🌱 Compound Growth & Annuities:**
  - Discrete compounding ($n$ times per year: annual, semi-annual, quarterly, monthly, daily).
  - Continuous compounding ($P \cdot e^{rt}$).
  - Ordinary Annuities vs Annuity Due vs Continuous cash flow streams.
  - Exponential percent growth and asset depreciation.

- **⏱️ Doubling & Milestone Target Time:**
  - Investment doubling duration modeled via Continuous, Annual, and Rule of 72 methods.
  - Time-to-target goal calculator (growing from principal $P$ to goal $T$).

- **🧮 Logarithm Equation Solver:**
  - Full algebraic solver for $\log_b(x) = y \iff b^y = x$.
  - Solve for $x$, solve for exponent $y$, or solve for base $b$.
  - Interactive curve plotting showing inverse symmetries with coordinate callouts.

- **🔬 Scientific Notation Converter:**
  - Convert real numbers of any magnitude to normalized scientific notation ($m \times 10^e$).
  - Resilient to IEEE 754 float log quirks and rounding rollover edge cases ($9.999 \to 1.00 \times 10^1$).
  - Multi-format string parser supporting `1.56 x 10^11`, `1.56*10^11`, `1.56 × 10^11`, and `1.56e11`.

- **🧪 pH Scale & Acidity:**
  - Logarithmic acidity/alkalinity tool: $\text{pH} = -\log_{10}([H^+])$.
  - Calculates pH, pOH, and chemical classification (Acidic, Neutral, Alkaline).
  - Visual pH spectrum gauge with quick substance presets.

- **🌐 Global Usability & Architecture:**
  - Multi-currency selector (USD, EUR, GBP, BDT, JPY, CAD, AUD, INR) persisted in session state.
  - Shareable bookmarkable links: inputs auto-sync to URL query parameters (`st.query_params`).
  - Mathematical transparency: "How this is calculated" dropdowns on every view with LaTeX formulas.

---

## 🚀 Quickstart (Local Setup in 5 Commands)

```bash
# 1. Clone repository
git clone https://github.com/raiyan-mahmud-git/financial-calculator.git
cd financial-calculator

# 2. Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run test suite
pytest

# 5. Launch the Streamlit application
streamlit run app.py
```

The app will open automatically in your browser at `http://localhost:8501`.

---

## ☁️ Deployment Instructions (Streamlit Community Cloud)

You can deploy this application for free on **Streamlit Community Cloud** in under 3 minutes:

1. **Push your code to GitHub:**
   Ensure your latest code is pushed to your GitHub repository:
   ```bash
   git push origin main
   ```
2. **Sign in to Streamlit Cloud:**
   Go to [share.streamlit.io](https://share.streamlit.io/) and sign in with your GitHub account.
3. **Create a New App:**
   - Click the **"New app"** button.
   - **Repository:** `raiyan-mahmud-git/financial-calculator`
   - **Branch:** `main`
   - **Main file path:** `app.py`
   - **App URL:** (Choose your preferred custom subdomain, e.g. `raiyan-financial-calc`)
4. **Advanced Settings (Optional):**
   - Python Version: Select `3.11` or `3.12`.
5. **Deploy:**
   Click **"Deploy!"**. Streamlit will automatically install dependencies from `requirements.txt` and launch your live web application at a public URL!

---

## 📁 Project Architecture

```
financial-calculator/
├── app.py                     # Application entrypoint & st.navigation setup
├── fincalc/                   # Pure mathematical domain library (Zero UI dependencies)
│   ├── __init__.py            # Clean public API
│   ├── core.py                # Pure mathematical functions & dataclasses
│   ├── errors.py              # Typed custom exceptions (FinCalcError)
│   └── formatting.py          # Multi-currency & rate parsing utilities
├── views/                     # Streamlit page views
│   ├── home.py                # Dashboard overview & directory
│   ├── mortgage.py            # Loan amortization & extra payment accelerator
│   ├── retirement.py          # Long-term retirement wealth simulation
│   ├── growth.py              # Compounding frequencies & annuity streams
│   ├── doubling.py            # Doubling time & target accumulation solver
│   ├── logarithms.py          # Logarithmic & exponential equation solver
│   ├── scientific.py          # Standard form conversion & parsing
│   └── ph.py                  # Chemistry pH scale & concentration tool
├── ui/                        # Reusable interface presentation layer
│   ├── components.py          # Currency selector, query-param sync, formula expanders
│   └── charts.py              # Plotly visualizers (donut, amortization, curves)
├── tests/                     # Automated test suite (100% passing)
│   ├── test_core.py           # Mathematical correctness & edge-case unit tests
│   ├── test_formatting.py     # Multi-currency & rate parsing tests
│   └── test_app.py            # Headless Streamlit AppTest integration tests
├── docs/                      # Documentation
│   ├── FORMULAS.md            # Complete mathematical formulas & LaTeX derivations
│   └── LEARNING_NOTES.md      # Phase-by-phase design decisions & pedagogical summaries
├── .streamlit/
│   └── config.toml            # Modern dark/light theme & server settings
├── .github/workflows/
│   └── ci.yml                 # Matrix CI testing Python 3.10, 3.11, 3.12, 3.13
├── requirements.txt           # Pinned production dependencies
├── pyproject.toml             # Ruff and Pytest project configuration
├── LICENSE                    # MIT License
└── README.md                  # Project documentation
```

---

## 📖 Mathematical Reference & Documentation

- **Mathematical Formulations & Derivations:** See [docs/FORMULAS.md](docs/FORMULAS.md) for full LaTeX formulas, compounding limits, and continuous cash flow derivations.
- **Architectural Evolution & Educational Notes:** See [docs/LEARNING_NOTES.md](docs/LEARNING_NOTES.md) for detailed pedagogical notes documenting how legacy bugs were diagnosed and solved.

---

## 🧪 Running Tests & Quality Checks

Run the automated test suite:
```bash
pytest
```

Run the linter and code formatter:
```bash
ruff check .
ruff format --check .
```

---

## 📄 License

This project is licensed under the terms of the [MIT License](LICENSE).
