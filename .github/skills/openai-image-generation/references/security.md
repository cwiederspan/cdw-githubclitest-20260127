# Security Notes

- Set `OPENAI_API_KEY` in your shell environment.
- Do not commit keys to the repo.
- Prefer per-session keys with least privilege where possible.

Examples:

## Bash / zsh
export OPENAI_API_KEY="***"

## PowerShell
$env:OPENAI_API_KEY="***"
