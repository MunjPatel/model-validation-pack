# Independent Model Validation Memo — Credit DD / PD Engine

**Framework:** SR 11-7 / OCC model risk management themes (conceptual soundness, ongoing monitoring, outcomes analysis).  
**Model under review:** `02_credit_risk_engine` Merton-style DD → PD mapping + migration loss simulator + IRB toy.  
**Validator posture:** Independent challenge (not model development ownership).

## 1. Model purpose

Rank relative default risk for a liquid public-firm demo universe; illustrate portfolio credit loss and IRB sensitivity education.

## 2. Conceptual soundness

| Component | Assessment |
|-----------|------------|
| Merton equity-as-call | Standard theory; assumptions (single debt, no coupons, constant rates) violated in practice |
| Asset vol inference | Iterative BS inversion — numerically fragile for deep ITM/OTM |
| PD = Φ(-DD) | **Not** an empirical EDF calibration; risk of mis-scaled absolute PDs |
| Debt input | **Illustrative constants** — material conceptual gap vs PIT capital structure |
| Migration matrix | Educational approximation — not agency-validated |

## 3. Ongoing monitoring (recommended)

- Track weekly max |ΔPD| by name
- Alert if PD bounds breached or DD–PD correlation breaks
- Recalibrate illustrative debt when 10-K/10-Q updates available
- Benchmark ranks vs leverage and vs agency ratings when accessible

## 4. Outcomes analysis

Automated challenge battery results:

test_id                               name severity status                                                                                   detail        metric
    T01                 PD bounds in [0,1]     Info   PASS                                                                          out_of_bounds=0  0.000000e+00
    T02 DD vs PD rank correlation negative     Info   PASS                                                                          spearman=-1.000 -1.000000e+00
    T03             IRB RW increases in PD     Info   PASS                                                             rw(0.1%)=0.297, rw(5%)=1.499  1.202004e+00
    T04          Max |ΔPD| below threshold   Medium   WARN                                                                        max_abs_dPD=0.211  2.114410e-01
    T05    Point-in-time debt (conceptual)     High   WARN Current MVP uses constant illustrative debt — flag as model limitation / incomplete PIT.           NaN
    T06               Loss tail above mean     Info   PASS                                                                mean=3777734, p99=7965500  7.965500e+06
    T07              Minimum name coverage     Info   PASS                                                                             n_tickers=10  1.000000e+01

## 5. Findings summary

- **Critical/High:** 0 open items
- **Warn:** 2
- **Pass:** 5

## 6. Use limitations

Do not use absolute PDs for regulatory capital, pricing, or credit approval. Suitable for **methodology demonstration** and relative ranking experiments only until PIT debt and empirical PD mapping are implemented.

## 7. Recommendation

**Conditional acceptance for portfolio demonstration** with mandatory remediation of PIT debt and documentation of PD mapping limitations.
