#!/bin/bash

# set up .gitconfig file
if [[ -f "~/.gitconfig" ]] then
    mv ~/.gitconfig ~/.gitconfig.backup
fi
cp ~/dotfiles/top_level_gitconfig ~/.gitconfig