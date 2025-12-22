#!/bin/bash

# set up ~/.claude/CLAUDE.md file
if [[ -f "~/.claude/CLAUDE.md" ]] then
    mv ~/.claude/CLAUDE.md ~/.claude/CLAUDE.md.backup
fi
cp ~/dotfiles/claude/CLAUDE_top_level.md ~/.claude/CLAUDE.md