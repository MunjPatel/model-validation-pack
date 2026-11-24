from __future__ import annotations

from pathlib import Path

import pandas as pd


MEMO_TEMPLATE = """# Independent Model Validation Memo — Credit DD / PD Engine

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

{findings_table}

## 5. Findings summary

- **Critical/High:** {high_count} open items
- **Warn:** {warn_count}
- **Pass:** {pass_count}

## 6. Use limitations

Do not use absolute PDs for regulatory capital, pricing, or credit approval. Suitable for **methodology demonstration** and relative ranking experiments only until PIT debt and empirical PD mapping are implemented.

## 7. Recommendation

**Conditional acceptance for portfolio demonstration** with mandatory remediation of PIT debt and documentation of PD mapping limitations.
"""


def render_memo(findings: pd.DataFrame, path: Path) -> Path:
    table = findings.to_string(index=False)
    high = int(((findings["status"] == "FAIL") & (findings["severity"].isin(["Critical", "High"]))).sum())
    warn = int((findings["status"] == "WARN").sum())
    passed = int((findings["status"] == "PASS").sum())
    text = MEMO_TEMPLATE.format(
        findings_table=table,
        high_count=high,
        warn_count=warn,
        pass_count=passed,
    )
    path.write_text(text, encoding="utf-8")
    return path
