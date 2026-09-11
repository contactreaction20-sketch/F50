# Task Engine

The existing `TaskScheduler` and `AutonomousRuntime` provide task state, structured actions, audit records, emergency stop, and coding-loop boundaries. They are tested independently.

Status: `PARTIAL / DISCONNECTED` from ordinary web chat. The next safe integration is a cognitive task service that creates a scheduler task for explicit task/project requests, emits concise status events, and delegates permitted actions through `AutonomousRuntime`.
