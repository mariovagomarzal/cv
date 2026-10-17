# Mario's CV

The source of my CV. See it at [cv.mariovagomarzal.com][cv], in each of its versions and languages.

## How it works

The CV is written once as data and rendered with [RenderCV][rendercv] in every combination of:

- **Variants**, such as the general CV and a shorter academic one, each with its own sections and design.
- **Locales**, with every text translated in place, so that no locale can fall out of sync with the others.
- **Visibility**: the public CVs leave out personal data, which the private ones add from secrets encrypted with
  [sops][sops].

Variants and locales are plain data files, so adding one needs no code changes. The public CVs are published with a
small viewer, built from the same data, whenever the main branch changes.

## Repository structure

- `content.yaml`: the content of every variant, in every locale. Its header explains how it is written.
- `variants/`: one file per variant, choosing its design, its sections and how the website names it.
- `locales/`: one file per locale, with the RenderCV locale and the website's interface texts.
- `designs/`: the RenderCV design of each variant, with optional Typst code and template overrides.
- `secrets/`: the personal data of the private CVs, encrypted with sops for the keys in `.sops.yaml`.
- `settings.yaml`: the RenderCV settings, shared by all the CVs.
- `scripts/build.py`: composes the RenderCV input of each CV, renders it and builds the website.
- `site/`: the viewer of the website and the script that draws its logo.
- `output/` and `dist/`: the rendered CVs and the built website (not tracked by Git).

## Development environment

The development environment is set up using Nix and [Devenv][devenv]. Run the following command to enter the development
environment:

```bash
devenv shell
```

Run `just` to see the available commands or check the `justfile` for more details. In short, `just check` validates
every combination, `just render <variant> <locale>` and `just render-all` render the CVs (pass `--private` for the
private ones, which needs a key to decrypt the secrets), and `just site` and `just serve` build and preview the
website.

## Conventions

This project follows the [Conventional Commits][conventional-commits] specification for commit messages. There are no
strict rules for branching in this repository.

## License

The code in this repository is licensed under the [MIT License](LICENSE). The content of the CV (`content.yaml`, the
files in `secrets/` and the rendered CVs) is personal and is not covered by that license: all rights reserved.

<!-- External links -->

[cv]: https://cv.mariovagomarzal.com
[rendercv]: https://rendercv.com
[sops]: https://getsops.io
[devenv]: https://devenv.sh
[conventional-commits]: https://www.conventionalcommits.org/en/v1.0.0/
