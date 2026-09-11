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

## Personal local use

GitHub stores the source code; it does not run this Python server. To use F50
personally on Windows, clone the repository, install it, set the three
environment variables shown in `.env.example`, and start the local web chat:

```powershell
git clone https://github.com/contactreaction20-sketch/F50.git
cd F50
python -m pip install .
$env:F50_MODEL_API_URL = "https://integrate.api.nvidia.com/v1"
$env:F50_MODEL_API_KEY = "your-new-nvidia-key"
$env:F50_MODEL_NAME = "google/gemma-4-31b-it"
python -m future50 --chat
```

Then open `http://127.0.0.1:8765`. Keep the API key only in your local
environment; do not put it in `.env.example` or commit it to GitHub.

For faster online inference, use the secure NVIDIA launcher after creating a
new NVIDIA API key at https://build.nvidia.com:

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\run_nvidia.ps1
```

The launcher reads the key as a hidden prompt and keeps it out of the source
tree. Do not use any key previously pasted into chat; revoke those keys first.

## Free cloud deployment

The included `render.yaml` deploys the web interface as a Render free web
service. In Render, choose **New Blueprint**, connect this repository, and
deploy. Render will install the package with `pip install .` and provide the
required `PORT` automatically.

The service health endpoint is:

```text
/api/health
```

For cloud inference, configure an OpenAI-compatible provider in Render:
`F50_MODEL_API_URL` should be the provider base URL (for example, an endpoint
ending in `/v1`), `F50_MODEL_API_KEY` is its secret key, and `F50_MODEL_NAME`
is the provider's model name. Without these variables, cloud deployments need
an Ollama server and model available to the service.

The default Blueprint target is NVIDIA's OpenAI-compatible API. Add a newly
rotated NVIDIA API key as `F50_MODEL_API_KEY` in Render. The default model is
`google/gemma-4-31b-it`; change `F50_MODEL_NAME` to another model
available to your NVIDIA account when needed. Never commit API keys to Git or
paste them into chat, issues, or public logs. Model provider safety controls
remain enabled by design.
