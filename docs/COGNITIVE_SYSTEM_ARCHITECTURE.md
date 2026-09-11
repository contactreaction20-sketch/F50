# FUTURE-50 Cognitive System Architecture

## Runtime Flow

```text
User -> Web API -> ContextManager -> MultiAgentTeam -> ModelRouter
     -> LocalOllamaProvider (streaming) -> ContextManager memory update
```

The web runtime is the current authoritative conversational path. It preserves a browser session id, selects relevant structured turns, classifies intent, resolves common references, routes to a specialist lane, streams the answer, and persists the bounded context store at `memory/cognitive_sessions.json`.

## Connected Components

- **Context:** `future50/cognition/context.py` owns structured turns, ranking, intent, reference resolution, persistence, and confidence.
- **Agent routing:** `future50/agents/team.py` selects a lead model and specialist lane without adding extra model calls for simple messages.
- **Model transport:** `future50/inference/providers.py` streams Ollama output and keeps the selected local model warm.
- **Web integration:** `future50/web/server.py` invokes context and team routing for `/api/chat` and `/api/chat/stream`.
- **Existing runtime:** scheduler, tools, permissions, audit, recovery, coding, RAG, and self-modification remain available through their existing package APIs but are not yet invoked by ordinary web chat.

## Evidence Boundary

A component is marked verified only when a test or runtime smoke check invokes it. File existence alone is not evidence. The web chat currently has executable evidence for context persistence, intent routing, specialist routing, and streaming transport. Tool-loop and self-modification evidence remains in their existing focused tests and is not claimed as web-chat behavior.

## Next Integration Boundaries

1. Add a cognitive task service that can choose retrieval, tool use, or direct response.
2. Connect relevant local RAG retrieval only for research/document intents.
3. Expose task state and concise status events without exposing hidden reasoning.
4. Add verification and learning records after tool-backed tasks.
