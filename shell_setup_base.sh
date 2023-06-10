#!/bin/bash
export PATH="/usr/local/opt/python@3.7/bin:$PATH"
export PATH="/opt/homebrew/opt/node@16/bin:$PATH"

export CLICOLOR=1
export LSCOLORS=ExFxBxDxCxegedabagacad

alias bf="source $HOME/dotfiles/scripts/black_flake8.sh"
alias sa="source venv/bin/activate"
alias python3="python"
alias make-venv="deactivate && conda activate py310 && python -m venv venv && conda deactivate && source venv/bin/activate && python -m pip install --upgrade pip wheel pip-tools"