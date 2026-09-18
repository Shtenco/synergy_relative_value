# API examples — SYNERGY Relative Value

`POST /enterprise/v1/relative-value/analyze` — roles **researcher, trader**.

```json
{"x":[100,101,102,103,104,105,106,107,108,109],"y":[50,50.5,51,51.5,52,52.5,53,53.5,54,54.5],"x_now":110,"y_now":55.2,"expected_carry_bps":15,"volatility":0.12,"corr_hedge":0.9}
```

Expected: `alpha`, `beta`, `zscore`, `carry_score`, `request_id`. Canonical schema: `/docs`.