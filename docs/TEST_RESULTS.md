# TEST_RESULTS

Fresh verification command:

```powershell
cd /d c:\F50
python -m pytest -q
```

Evidence:

```text
30 passed in 74.90s (0:01:14)
```

## Passed tests

- `Future50Chat.generate` returns assistant role and answer text.
- Provider path and model route tests.
- Core permission, autonomy, and system tests.
- GUI object and send-log regression tests.

## Known limitations

- There is no Git repository metadata in this workspace, so version control status is unknown.
- Android and Windows device tests cannot be verified without explicit device authorization and device bridge.
- Full semantic RAG/vector document and multi-device tests remain partial or optional.
