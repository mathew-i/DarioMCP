# Branch Setup Instructions

This repository has been set up with the following structure:

## Branches Created

1. **main** - Main branch containing stable releases
2. **develop** - Main development branch (primary branch for ongoing development)

## Folder Structure

The following folders have been created and committed:

- `setup/` - Setup and configuration files
- `tests/` - Test files and test suites
- `mcp/` - MCP (Model Context Protocol) related files

## Branch Structure

- The `main` branch contains the stable, production-ready code
- The `develop` branch is the main development branch where all feature development happens
- Both branches currently contain the initial commit with the folder structure

## Next Steps

To push these branches to the remote repository, the repository owner should:

```bash
git push origin main
git push origin develop
```

To set `develop` as the default branch in GitHub:
1. Go to repository Settings
2. Navigate to Branches
3. Set `develop` as the default branch
