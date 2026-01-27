# dotfiles

My base dotfiles.

## Requirements

If not already, set zsh as your login shell:

```bash
chsh -s $(which zsh)
```

1. Make a manual backup of any existing `~/.zshrc` if desired.
2. Install oh-my-zsh with `sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"`
3. You will also need `conda`. For mac, `brew install miniconda` works well (using homebrew).
4. Set up plugin etc. with `source setup.sh`. A backup of any existing `~/.zshrc` will be placed in `~/.zshrc.backup`.
5. If you do not already have a `~/.gitconfig`, you can set up a basic one that includes
the `.gitconfig` file in this repo via `source setup_gitconfig.sh`. If you already have
a `~/.gitconfig`, you can just add an `include` line like in `top_level_gitconfig`.
6. If you do not already have a `~/.claude/CLAUDE.md`, you can set up a basic one that
includes the `CLAUDE_personal.md` file in this repo via `source setup_claude.sh`.
If you already have a `~/.claude/CLAUDE.md`, you can just add an import line like in `claude/CLAUDE_top_level.md`.

## Claude Code Skills

This repo includes custom Claude Code skills in `claude/skills/`. The `setup_claude.sh` script
automatically symlinks these to `~/.claude/skills/`, making them available globally.

Skills can be invoked in two ways:

- **Explicitly** by typing the slash command (e.g., `/rebase-chain`)
- **Automatically** by Claude when it detects the skill is relevant to your conversation

### Available Skills

- `/rebase-chain` - Help rebase chained feature branches using `git rebase --onto`

### Manual Setup (if not using setup_claude.sh)

If you already have Claude Code configured and just want to add the skills:

```bash
# If ~/.claude/skills doesn't exist yet:
ln -s ~/dotfiles/claude/skills ~/.claude/skills

# If it already exists and you want to replace it:
mv ~/.claude/skills ~/.claude/skills.backup
ln -s ~/dotfiles/claude/skills ~/.claude/skills
```

No additional installation is required - Claude Code automatically discovers skills in `~/.claude/skills/`.
After symlinking, the skills are immediately available.

## Usage

Add include lines and `source` lines to corresponding base files referencing
the files here, along with any more specific files.

For github ssh (at least on linux):

```bash
for ip in $(for i in $(seq -f "140.82.%g.%%g" 112 127); do seq -f $i 1 254; done); do ssh-keygen -R $ip; done
```

From <https://github.com/orgs/community/discussions/27405>

## SSH

To store keys, make sure ssh-agent running on startup (via a command like `ssh-agent zsh`),
then add your key (e.g., `ssh-add ~/.ssh/id_....`). This will allow you to automatically
store your ssh key and not have to enter it all the time!

## Development

### Pre-commit Hooks (prek)

This repo uses [prek](https://github.com/j178/prek) for pre-commit hooks. To set up:

1. Install prek:
   - macOS: `brew install j178/tap/prek`
   - Other: See [installation docs](https://prek.j178.dev/installation/)
2. Install the hooks: `prek install`
3. (Optional) Run on all files: `prek run --all-files`
