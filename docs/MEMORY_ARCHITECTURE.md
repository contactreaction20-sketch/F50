# Memory Architecture

`ContextManager` is the connected conversational memory boundary.

- Working/session memory: `ContextTurn` records in the active session.
- Conversation memory: bounded recent turns with role, timestamp, topic, source, and importance.
- Durable storage: atomic JSON persistence at `memory/cognitive_sessions.json`.
- Retrieval: token overlap, recency, importance, and topic scoring.
- Reference resolution: current subject, previous subject, and active task.
- Confidence: unresolved references lower the snapshot confidence instead of becoming facts.

The existing `InMemoryMemory` remains a lower-level adapter and is not falsely marked as the web runtime memory. Typed project, preference, lesson, and tool-result stores remain follow-up work.
