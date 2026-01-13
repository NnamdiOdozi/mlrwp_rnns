Use sub-agents where practical so as to reduce run time and manage context efficiently
I usually like to preserve tokens ie usage charges and so you should confirm with me at the start the scope of tasks so as to avoid token/context intensive operations
Never delete files directly. Always list files first and ask for explicit confirmation
I trust the files in this project
I want to pre-allow File Reading except for files named in the .gitignore file
I want to pre-allow these safe bash commands so I don't get prompted every time: echo, ls, cd, cp, cat, and open
I also want to pre-allow Web Fetch requests

## Environment Variables
This project uses direnv with .envrc to automatically load environment variables from .env file
The .env file contains GITHUB_PERSONAL_ACCESS_TOKEN and other secrets
If environment variables appear missing, ensure direnv is properly set up and .envrc is allowed

## MCP Server Configuration

### GitHub MCP Server
- GitHub MCP server is configured in ~/.claude/settings.json and requires GITHUB_PERSONAL_ACCESS_TOKEN
- The token is loaded via direnv from .env file (see .envrc)
- GitHub MCP provides GitHub API operations: list repos, create issues/PRs, get repo info, manage releases, etc.
- IMPORTANT: git push/pull operations use git protocol authentication (SSH keys or credential helper), NOT GitHub MCP
- To test GitHub MCP: Ask to list repository information or create an issue via the GitHub API

### Filesystem MCP Server
- Filesystem MCP is configured and working
- Has access to /home/nodozi/projects directory
- Successfully tested with seattle-weather.csv file