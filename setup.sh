#!/bin/bash
# install gh CLI if not present
if ! command -v gh >/dev/null 2>&1; then
    echo "Installing GitHub CLI (gh)..."
    (type -p wget >/dev/null || (sudo apt update && sudo apt-get install wget -y)) \
        && sudo mkdir -p -m 755 /etc/apt/keyrings \
        && out=$(mktemp) && wget -nv -O"$out" https://cli.github.com/packages/githubcli-archive-keyring.gpg \
        && cat "$out" | sudo tee /etc/apt/keyrings/githubcli-archive-keyring.gpg > /dev/null \
        && sudo chmod go+r /etc/apt/keyrings/githubcli-archive-keyring.gpg \
        && echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null \
        && sudo apt update \
        && sudo apt install gh -y
    echo "Run 'gh auth login' to authenticate."
else
    echo "gh CLI already installed: $(gh --version | head -1)"
fi

# set up oh-my-zsh plugin
PLUGIN_NAME=~/dotfiles/zsh_config/zsh_custom/plugins/zsh-syntax-highlighting
if [[ ! -d "$PLUGIN_NAME" ]]; then
    git clone https://github.com/zsh-users/zsh-syntax-highlighting.git "$PLUGIN_NAME"
fi

# set up .zshrc file
if [[ -f ~/.zshrc ]]; then
    mv ~/.zshrc ~/.zshrc.backup
fi
cp ~/dotfiles/zsh_config/top_level_zshrc ~/.zshrc

# set up .condarc file
if [[ -f ~/.condarc ]]; then
    mv ~/.condarc ~/.condarc.backup
fi
cp ~/dotfiles/.condarc ~/.condarc

# set up conda
conda init zsh