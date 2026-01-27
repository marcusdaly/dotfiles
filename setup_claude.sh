#!/bin/bash

# Ensure ~/.claude directory exists
mkdir -p ~/.claude

# Set up ~/.claude/CLAUDE.md file
if [[ -f ~/.claude/CLAUDE.md ]]; then
    timestamp=$(date +%Y%m%d_%H%M%S)
    mv ~/.claude/CLAUDE.md ~/.claude/CLAUDE.md.backup.$timestamp
    echo "Created backup: ~/.claude/CLAUDE.md.backup.$timestamp"
fi
cp ~/dotfiles/claude/CLAUDE_top_level.md ~/.claude/CLAUDE.md

# Set up ~/.claude/skills symlink
if [[ -L ~/.claude/skills ]]; then
    echo "~/.claude/skills symlink already exists, skipping"
elif [[ -d ~/.claude/skills ]]; then
    timestamp=$(date +%Y%m%d_%H%M%S)
    mv ~/.claude/skills ~/.claude/skills.backup.$timestamp
    echo "Created backup: ~/.claude/skills.backup.$timestamp"
    ln -s ~/dotfiles/claude/skills ~/.claude/skills
    echo "Created symlink: ~/.claude/skills -> ~/dotfiles/claude/skills"
else
    ln -s ~/dotfiles/claude/skills ~/.claude/skills
    echo "Created symlink: ~/.claude/skills -> ~/dotfiles/claude/skills"
fi