# Intelligence Benchmark

The current executable benchmark is `future50/tests/test_intelligence.py`.

Covered checks:

- durable fact retrieval after reload
- 20-turn continuity
- follow-up reference resolution
- adaptive specialist routing
- research-only RAG context selection

The current focused result is recorded by the test runner, not hard-coded here. Model answer quality, tool loops, project memory, contradiction detection, and long-running recovery remain future benchmark slices until connected to runtime.
