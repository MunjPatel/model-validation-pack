# Model Validation Pack

**Roles:** Model Validation / Risk Quant (primary)  
**Model under review:** `02_credit_risk_engine`

## Source

Federal Reserve / OCC Supervisory Guidance on Model Risk Management (SR 11-7):  
https://www.federalreserve.gov/boarddocs/srletters/2011/sr1107.pdf

Note: US agencies have been updating MRM guidance; this pack uses the classic three-pillar structure (conceptual soundness, monitoring, outcomes analysis) as the teaching scaffold.

## Run

```bash
python 02_credit_risk_engine/scripts/run_mvp.py   # prerequisite
python 03_model_validation_pack/scripts/run_mvp.py
streamlit run 03_model_validation_pack/app/dashboard.py
```



1. Push this repo to GitHub (already done if you cloned from MunjPatel/model-validation-pack).
2. Go to https://share.streamlit.io/ → **New app**
3. Select repo `MunjPatel/model-validation-pack`, branch `main`
4. Main file path: `app/dashboard.py`
5. Python version 3.11+ recommended → Deploy

The app reads artifacts under `outputs/`. Re-run `scripts/run_mvp.py` locally if you need to refresh them before pushing.

## Live dashboard

[https://model-validation-pack.streamlit.app/](https://model-validation-pack.streamlit.app/)

