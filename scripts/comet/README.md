# comet-check

CLI tool to query Comet ML experiments from the terminal.

## Setup

1. Get your Comet API key from <https://www.comet.com> -> Settings -> Developer Information -> API Key
2. Add to `~/.secrets.env`:

   ```bash
   export COMET_API_KEY="your-api-key-here"
   export COMET_WORKSPACE="your-workspace"
   ```

3. Install dependencies:

   ```bash
   cd ~/dotfiles/scripts/comet && uv sync
   ```

4. The `comet` alias (defined in `~/dotfiles/zsh_config/.zshrc`) provides convenient access.

## Usage

```bash
comet list <project>                # Recent experiments with loss
comet metrics <key> [metric...]     # Latest metrics
comet text <key>                    # Qualitative generations
comet compare <key1> <key2>         # Compare experiments
comet url <key>                     # Print experiment URL
```

Requires `COMET_API_KEY` and `COMET_WORKSPACE` environment variables.
