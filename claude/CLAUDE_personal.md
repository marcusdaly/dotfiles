# General Guidance
## Style/Linting
- When fixing linting errors, prefer fixing the root cause of type errors rather than using comments to ignore them, unless there is a strong reason to do otherwise.
- Please do not use single-letter variable names. Instead, favor using somewhat human-readable variable names.
- Please make imports at the top of files without strong reasoning otherwise.
- When making changes to not-yet-deployed branches, please favor a cleaner implementation over backwards compatbility.
- Favor explicit errors and avoid fallbacks and warnings if something unexpected is observed.

## Best Practices working around Code
- When adding, updating, or deleting code, please be cognizant that nearby documentation (e.g. READMEs) or deployment files (e.g. Dockerfiles) may reference the code being changed! Make sure to check and update these files accordingly.

## ML Model Pipelines
- Try to avoid ad-hoc data processing and evaluation. Reproducible scripts and ideally pipelines are much better long term.

## Python Environment
- When configured in the project, please use `uv` for a python environment and dependency management.

## Plan Mode
- Feel free to enter plan mode whenever you deem appropriate!