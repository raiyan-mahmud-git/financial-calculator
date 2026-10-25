# Financial & Mathematical Formulas Reference

This document provides mathematical formulations, domain constraints, and derivations for all operations implemented in the `fincalc` library.

---

## 1. Compound Interest

### Discrete Compounding
When interest is compounded $n$ times per year over $t$ years:

$$A = P \left(1 + \frac{r}{n}\right)^{nt}$$

- **$P$**: Principal lump sum ($P \ge 0$)
- **$r$**: Nominal annual interest rate as a decimal ($r \ge 0$)
- **$n$**: Compounding frequency per year ($n \ge 1$, e.g., $12$ for monthly, $4$ for quarterly, $365$ for daily)
- **$t$**: Investment duration in years ($t \ge 0$)
- **$A$**: Accumulated future value

**Zero-rate limit ($r \to 0$):**
$$\lim_{r \to 0} P \left(1 + \frac{r}{n}\right)^{nt} = P$$

---

## 2. Continuous Growth & Compounding

When compounding occurs continuously ($n \to \infty$):

$$A = \lim_{n \to \infty} P \left(1 + \frac{r}{n}\right)^{nt} = P \cdot e^{rt}$$

- **$e$**: Euler's number ($\approx 2.718281828459$)

---

## 3. Percent Increase & Decrease

### Exponential Increase
$$A = P (1 + r)^t$$

### Exponential Depreciation / Decay
$$A = P (1 - r)^t \quad (0 \le r \le 1)$$

---

## 4. Annuity Future Value

An annuity is a sequence of equal cash payments made at regular intervals.

### Discrete Compounding (Ordinary Annuity)
Payments $P$ made at the **end** of each period with periodic interest rate $i = r/n$ across $N = n \cdot t$ periods:

$$FV = P \left[\frac{(1 + i)^N - 1}{i}\right] = P \left[\frac{\left(1 + \frac{r}{n}\right)^{nt} - 1}{\frac{r}{n}}\right]$$

### Annuity Due
Payments made at the **beginning** of each period earn an extra period of interest:

$$FV_{\text{due}} = FV_{\text{ordinary}} \cdot (1 + i)$$

### Continuous Compounding
If payments occur as a continuous cash flow rate $R = P \cdot n$ (total annual payment):

$$FV_{\text{cont}} = \int_0^t R e^{r(t - s)} \, ds = R \left[\frac{e^{rt} - 1}{r}\right]$$

**Zero-rate limit ($r \to 0$):**
In all cases, total accumulated value is simply the sum of payments:
$$FV = P \cdot n \cdot t$$

---

## 5. Fixed-Rate Mortgage & Amortization

### Periodic Monthly Payment ($PMT$)
For a principal loan $P$, monthly interest rate $i = r/12$, and total monthly payments $N = 12 \cdot t$:

$$PMT = P \left[\frac{i(1 + i)^N}{(1 + i)^N - 1}\right]$$

**Zero-rate limit ($r = 0$):**
$$PMT = \frac{P}{N}$$

### Month-by-Month Amortization
For each payment month $m$:
1. **Interest charge:** $I_m = \text{Balance}_{m-1} \cdot i$
2. **Scheduled Principal:** $Principal_m = PMT - I_m$
3. **Extra Principal:** Added directly to principal reduction:
   $$\text{Total Principal Paid}_m = Principal_m + \text{Extra}$$
4. **New Balance:** $\text{Balance}_m = \text{Balance}_{m-1} - \text{Total Principal Paid}_m$

---

## 6. Retirement Wealth Projection

Models three critical real-world dynamics:
1. **Initial Wealth:** Starting seed balance $P_0$.
2. **Contribution Escalation:** Monthly deposits grow annually by career raise rate $g$:
   $$C_y = C_0 \cdot (1 + g)^{y-1}$$
3. **Inflation Discounting (Real Purchasing Power):**
   $$\text{Real Balance}_y = \frac{\text{Nominal Balance}_y}{(1 + r_{\text{inf}})^y}$$

---

## 7. Doubling Time & Target Time

### Doubling Time ($A = 2P$)
- **Continuous:** $t = \frac{\ln(2)}{r}$
- **Annual Discrete:** $(1 + r)^t = 2 \implies t = \frac{\ln(2)}{\ln(1 + r)}$
- **Rule of 72 (Mental Shortcut):** $t \approx \frac{72}{r \times 100}$

### Time to Arbitrary Target ($A = T$)
$$t_{\text{discrete}} = \frac{\ln(T / P)}{\ln(1 + r)}, \quad t_{\text{continuous}} = \frac{\ln(T / P)}{r}$$

---

## 8. Logarithmic Relationships

General logarithm identity:
$$\log_b(x) = y \iff b^y = x$$

Domain constraints:
- Base $b > 0$ and $b \neq 1$
- Result $x > 0$

Solvers:
- Given $(b, y) \implies x = b^y$
- Given $(b, x) \implies y = \frac{\ln(x)}{\ln(b)}$
- Given $(x, y) \implies b = x^{1 / y}$

---

## 9. Scientific Notation

Standard base-10 scientific form:
$$x = m \times 10^e$$
where $1 \le |m| < 10$ and $e \in \mathbb{Z}$.

---

## 10. pH Scale

$$pH = -\log_{10}([H^+])$$
$$pOH = 14.0 - pH$$

Classification:
- $pH < 7.0$: **Acidic**
- $pH = 7.0$: **Neutral**
- $pH > 7.0$: **Basic / Alkaline**
