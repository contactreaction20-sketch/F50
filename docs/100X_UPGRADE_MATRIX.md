# FUTURE-50 100X Upgrade Matrix

Status values are evidence-based: `VERIFIED`, `PARTIAL`, `DISCONNECTED`, `MISSING`, `BLOCKED_EXTERNAL`, or `OPTIONAL`.

| Capability | Status | Evidence / boundary |
|---|---|---|
| Local model/provider | VERIFIED | Ollama provider has generate and streaming paths. |
| Web chat transport | VERIFIED | `/api/chat` and `/api/chat/stream` serve live responses. |
| Structured conversation context | VERIFIED | `ContextManager` ranks turns and persists JSON sessions. |
| Intent detection | VERIFIED | Executable routing checks cover code, research, strategy, and general lanes. |
| Reference resolution | VERIFIED | `this`, `previous`, and `continue` resolve against session turns; low-confidence references remain visible. |
| Multi-agent routing | VERIFIED | `MultiAgentTeam` selects specialist lane and lead model. |
| Long-term memory | PARTIAL | Bounded JSON conversation memory works; typed project/task/user preference memory is not yet unified. |
| RAG | PARTIAL / DISCONNECTED | Local RAG is tested but only awaits cognitive task integration. |
| Tool catalog | PARTIAL | Tool registry exists; web chat does not yet select or execute tools. |
| Permission enforcement | PARTIAL | Permission API exists, but legacy registry/runtime enforcement requires hardening. |
| Task lifecycle | PARTIAL | Scheduler/runtime task APIs exist; web task service is not connected. |
| Verification/self-check | PARTIAL | Coding loop verifies tests; ordinary chat has no answer verifier yet. |
| Self-coding | PARTIAL | Existing coding loop is executable in focused tests but not web-invoked. |
| Self-modification | PARTIAL | Checkpoint/accept/rollback exist; autonomous proposal loop is absent. |
| Learning/failure lessons | MISSING | No connected experience extraction and reuse layer yet. |
| Hardware-aware routing | BLOCKED_EXTERNAL | Hardware/model inventory and unload policy are not connected to web routing. |
| Device control | BLOCKED_EXTERNAL | Real device bridge/authorization is unavailable. |
| Observability events | PARTIAL | Audit exists for runtime paths; cognitive web events need a unified event sink. |

## Baseline Rule

This matrix does not claim a complete 100X system. Each upgrade must connect runtime invocation and executable evidence before its status changes to `VERIFIED`.
