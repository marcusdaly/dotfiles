#!/bin/bash
# set up oh-my-zsh plugin
PLUGIN_NAME=$HOME/dotfiles/zsh_config/zsh_custom/plugins/zsh-syntax-highlighting
if [[ ! -d "$PLUGIN_NAME" ]]; then
    git clone https://github.com/zsh-users/zsh-syntax-highlighting.git "$PLUGIN_NAME"
fi

# set up .zshrc file
if [[ -f "$HOME/.zshrc" ]]; then
    mv "$HOME"/.zshrc "$HOME"/.zshrc.backup
fi
cp "$HOME"/dotfiles/zsh_config/top_level_zshrc.sh "$HOME"/.zshrc

# set up .condarc file
if [[ -f "$HOME/.condarc" ]]; then
    mv "$HOME"/.condarc "$HOME"/.condarc.backup
fi
cp "$HOME"/dotfiles/.condarc "$HOME"/.condarc

# set up conda
conda init zsh