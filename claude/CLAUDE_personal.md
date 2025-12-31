# General Guidance
## Style/Linting
- When fixing linting errors, prefer fixing the root cause of type errors rather than using comments to ignore them, unless there is a strong reason to do otherwise.
- Please do not use single-letter variable names. Instead, favor using somewhat human-readable variable names.

## ML Model Pipelines
- Try to avoid ad-hoc data processing and evaluation. Reproducible scripts and ideally pipelines are much better long term.

## Python Environment
- When configured in the project, please use `uv` for a python environment and dependency management.

## Plan Mode
- Feel free to enter plan mode whenever you deem appropriate!