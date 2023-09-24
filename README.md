# dotfiles
My base dotfiles.

# Requirements
If not already, set zsh as your login shell:
```
chsh -s $(which zsh)
```

1. Make a manual backup of any existing `~/.zshrc` if desired.
2. Install oh-my-zsh with `sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"`
3. Set up plugin etc. with `source setup.sh`. A backup of any existing `~/.zshrc` will be placed in `~/.zshrc.backup`.

# Usage
Add include lines and `source` lines to corresponding base files referencing
the files here, along with any more specific files

For github ssh (at least on linux): 

```
for ip in $(for i in $(seq -f "140.82.%g.%%g" 112 127); do seq -f $i 1 254; done); do ssh-keygen -R $ip; done
```
from https://github.com/orgs/community/discussions/27405

## SSH
To store keys, make sure ssh-agent running on startup (via a command like `ssh-agent zsh`),
then add your key (e.g., `ssh-add ~/.ssh/id_....`). This will allow you to automatically
store your ssh key and not have to enter it all the time!