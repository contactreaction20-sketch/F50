# Self-Coding

`future50/integration/runtime.py` contains the executable coding loop: write failing code, run tests, recover, apply a fix, retest, and audit the outcome. This is a verified isolated capability.

It is not automatically invoked by web chat. Connecting it requires explicit task detection, workspace/permission confirmation, checkpointing, and a user-visible status stream.
