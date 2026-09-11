# Context Engine

The context engine is implemented in `future50/cognition/context.py`.

For each message it:

1. Detects multiple intents.
2. Resolves `this`, `that`, `previous`, and `continue` against structured turns.
3. Scores prior turns by token overlap, topic, importance, and recency.
4. Limits injected context to the most relevant turns.
5. Emits confidence and unresolved-reference metadata.
6. Persists user and assistant turns after a response.

The web server invokes this engine for both buffered and streaming chat paths. It does not expose hidden chain-of-thought; only intent/confidence metadata is available for observability.
