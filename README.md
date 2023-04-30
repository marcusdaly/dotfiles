# dotfiles
My base dotfiles.

# Requirements
Set zsh as your login shell:
```
chsh -s $(which zsh)
```

# Usage
Add include lines and `source` lines to corresponding base files referencing
the files here, along with any more specific files

For github ssh (at least on linux): 

```
for ip in $(for i in $(seq -f "140.82.%g.%%g" 112 127); do seq -f $i 1 254; done); do ssh-keygen -R $ip; done
```
from https://github.com/orgs/community/discussions/27405