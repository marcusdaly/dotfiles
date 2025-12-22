#!/bin/bash

# set up .gitconfig file
if [[ -f ~/.gitconfig ]]; then
    timestamp=$(date +%Y%m%d_%H%M%S)
    mv ~/.gitconfig ~/.gitconfig.backup.$timestamp
    echo "Created backup: ~/.gitconfig.backup.$timestamp"
fi
cp ~/dotfiles/top_level_gitconfig ~/.gitconfig