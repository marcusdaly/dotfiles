# General Guidance
## Style/Linting
- When fixing linting errors, prefer fixing the root cause of type errors rather than using comments to ignore them, unless there is a strong reason to do otherwise.
- Please do not use single-letter variable names. Instead, favor using somewhat human-readable variable names.
- Please keep import statements at the top of files whenever possible.
- When making changes to not-yet-deployed branches, please favor a cleaner implementation over backwards compatbility.
- Please avoid fallbacks and warnings if something unexpected is observed. Instead, raise explicit errors to increase visibility to the issue.
- Avoid redundant comments. If a section of code is very readable and short, there is no need to have a dedicated comment for each of these sections explaining what the code does.
- Please only use `assert` statements in tests, instead favoring raising appropriate, informative error types when e.g. an input parameter is of an unexpected value or type.
- When working with code that enumerates a list of items that code changes may update, please try to keep each item on its own line for cleaner diffs and better readability.

## Best Practices working around Code
- When adding, updating, or deleting code, please be cognizant that nearby documentation (e.g. READMEs) or deployment files (e.g. Dockerfiles) may reference the code being changed! Make sure to check and update these files accordingly.
- Before considering a task complete, please run any formatting, linting, type-checking, and testing tools present in the repository we're working in. Often, this will look like `uv run ruff check`, `uv run pyright`, and `uv run pytest`.

## Git - Resolving conflicts and rebasing
- When merging in chagnes from other branches, please keep in mind that often one branch was originally branched off of the other, but both branches have had changes since then, and the older one in particular often will have rebased on a main branch to pull in fresh changes. Please keep that in mind and maybe use `git rebase --onto` to focus on the relevant commits.
- Note that I often work in repos where the norm is to squash and merge into main. This means that the commit history may look much longer on the feature branch than it does on main
when trying to rebase on top of main.

## ML Model Pipelines
- Try to avoid ad-hoc data processing and evaluation. Reproducible scripts and ideally pipelines are much better long term.

## Python Environment
- When configured in the project, please use `uv` for a python environment and dependency management.

## Plan Mode
- Feel free to enter plan mode whenever you deem appropriate!