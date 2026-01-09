# General Guidance
## Style/Linting
- When fixing linting errors, prefer fixing the root cause of type errors rather than using comments to ignore them, unless there is a strong reason to do otherwise.
- Please do not use single-letter variable names. Instead, favor using somewhat human-readable variable names.
- Please make imports at the top of files without strong reasoning otherwise.
- When making changes to not-yet-deployed branches, please favor a cleaner implementation over backwards compatbility.
- Favor explicit errors and avoid fallbacks and warnings if something unexpected is observed.
- Avoid redundant comments. If a section of code is very readable and short, there is no need to have a dedicated comment for each of these sections explaining what the code does.
- Please only use `assert` statements in tests, instead favoring raising appropriate, informative error types when e.g. an input parameter is of an unexpected value or type.

## Best Practices working around Code
- When adding, updating, or deleting code, please be cognizant that nearby documentation (e.g. READMEs) or deployment files (e.g. Dockerfiles) may reference the code being changed! Make sure to check and update these files accordingly.
- Before considering a task complete, please run any formatting/type-checking tools present in the repository we're working in. often, this will look like `uv run ruff check` and `uv run pyright`.

## ML Model Pipelines
- Try to avoid ad-hoc data processing and evaluation. Reproducible scripts and ideally pipelines are much better long term.

## Python Environment
- When configured in the project, please use `uv` for a python environment and dependency management.

## Plan Mode
- Feel free to enter plan mode whenever you deem appropriate!