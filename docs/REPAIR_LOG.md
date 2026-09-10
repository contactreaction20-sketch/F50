# REPAIR_LOG

## Baseline

The original workspace included an Ollama provider, a Tkinter GUI, and a model router. The main broken area was the old route phrase and missing same-language provider state.

## Repairs performed

1. Removed static route phrase style from model inference branch.
2. Added same-language detection for Hindi/Hinglish prompt handling in the local provider adapter.
3. Added model registry and manager scaffolding under `future50/inference`.
4. Made GUI send path asynchronous only when a root Tk object exists.
5. Updated regression tests and GUI test monkeypatch to make them deterministic and non-environmental.

## Repair evidence

Fresh verification command:

```powershell
cd /d c:\F50
python -m pytest -q
```

Observed result:

```text
30 passed in 74.90s (0:01:14)
```
