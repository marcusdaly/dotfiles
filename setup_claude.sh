#!/bin/bash

# set up ~/.claude/CLAUDE.md file
if [[ -f ~/.claude/CLAUDE.md ]]; then
    timestamp=$(date +%Y%m%d_%H%M%S)
    mv ~/.claude/CLAUDE.md ~/.claude/CLAUDE.md.backup.$timestamp
    echo "Created backup: ~/.claude/CLAUDE.md.backup.$timestamp"
fi
cp ~/dotfiles/claude/CLAUDE_top_level.md ~/.claude/CLAUDE.md