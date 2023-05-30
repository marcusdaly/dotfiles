#!/bin/bash
# set up oh-my-zsh plugin
PLUGIN_NAME=~/dotfiles/zsh_config/zsh_custom/plugins/zsh-syntax-highlighting
if [[ ! -d "$PLUGIN_NAME" ]] then
    git clone https://github.com/zsh-users/zsh-syntax-highlighting.git $PLUGIN_NAME
fi

# set up .zshrc file
if [[ -f "~/.zshrc" ]] then
    mv ~/.zshrc ~/.zshrc.backup
fi
cp ~/dotfiles/zsh_config/top_level_zshrc ~/.zshrc