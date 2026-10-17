# Mario's CV

Read the README for what this repository is and how it is organized, and explore the files for the details if needed.

## Development environment

The development environment is set up using Nix and Devenv. Run every command inside `devenv shell`, which provides
the tools and the fonts the build needs, and run `just` to see the available commands.

## Conventions

- Commit messages follow the Conventional Commits specification, checked by convco.
- This repository is public. Before adding any sensitive data (a phone number, a photo, an address, etc.), ask the
  user whether it should be a secret encrypted with sops in `secrets/` instead.
