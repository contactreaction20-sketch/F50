# FUTURE-50

FUTURE-50 is a local-first, modular autonomous personal AI operating system architecture.

This repository contains the initial repository structure, a minimum working Python core,
a model router abstraction, a permission and autonomy framework, memory and knowledge
interfaces, and a simple command-line entry point.

## Repository structure

The project folders intentionally mirror the requested layered architecture:

- app/
- core/
- cognition/
- models/
- agents/
- memory/
- knowledge/
- world_model/
- skills/
- coding/
- tools/
- computer_use/
- research/
- self_improvement/
- evolution/
- sandbox/
- evaluation/
- security/
- permissions/
- plugins/
- database/
- interface/
- scheduler/
- monitoring/
- logs/
- backups/
- experiments/
- tests/
- workspace/
- documentation/

## Minimum working core

The first implementation is intentionally simple and dependency-free:

- a model abstraction interface;
- a local model router that maps task types to model roles;
- a minimal chat and orchestration engine;
- in-memory memory and knowledge components;
- permission/security stubs and a default local-only safety posture;
- a CLI entry point for a chat loop.

## Run

```bash
python -m future50
```

## Testing

```bash
python -m pytest
```
