# REGRESSION_RESULTS

Fresh verification:

```powershell
cd /d c:\F50
python -m pytest -q
```

Observed:

```text
30 passed in 74.90s (0:01:14)
```

This confirms that the repaired model provider route, GUI message flow, and same-language system instruction support remain regression-safe under the repository test harness.
