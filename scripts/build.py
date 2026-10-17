"""Compose the CV variants from the shared content and render them with RenderCV.

Variants and locales are discovered from the files in `variants/` and `locales/`, so adding either needs no change
here. See `content.yaml` for how the content is written.

A design is a RenderCV design file in `designs/`, for what its options cannot express, optionally with:

- a Typst file of the same name, whose code runs before RenderCV's setup (so it can only style what RenderCV leaves
  alone, since RenderCV's own rules take precedence);
- a folder of the same name with RenderCV template overrides, as RenderCV looks for them in the theme folder.

The fonts the designs need are taken from
the folder in the `CV_FONTS` environment variable, which the development shell sets.

Private CVs also include the secrets in `secrets/cv.yaml`, encrypted with sops. That file mirrors the RenderCV input
(for example, `cv.phone`), follows the same rules as the content, and is merged over the public CV.
"""

import argparse
import functools
import itertools
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parent.parent
CONTENT_PATH = ROOT / "content.yaml"
SETTINGS_PATH = ROOT / "settings.yaml"
VARIANTS_DIR = ROOT / "variants"
LOCALES_DIR = ROOT / "locales"
SECRETS_PATH = ROOT / "secrets" / "cv.yaml"
BUILD_DIR = ROOT / "build"
OUTPUT_DIR = ROOT / "output"

# Keys that control how the content is composed and never reach RenderCV.
ONLY_KEY = "only"
EXCEPT_KEY = "except"
OVERRIDES_KEY = "overrides"


class BuildError(Exception):
    """An error in the sources that prevents composing a CV."""


def load_yaml(path: Path) -> Any:
    with path.open(encoding="utf-8") as file:
        return yaml.safe_load(file)


@functools.cache
def load_secrets() -> Any:
    """Decrypt the secrets with sops, once per run."""
    result = subprocess.run(["sops", "decrypt", str(SECRETS_PATH)], capture_output=True, text=True, check=False)
    if result.returncode != 0:
        raise BuildError(f"could not decrypt {SECRETS_PATH.relative_to(ROOT)}: {result.stderr.strip()}")
    return yaml.safe_load(result.stdout)


def deep_merge(base: dict[str, Any], extra: dict[str, Any]) -> dict[str, Any]:
    """Merge two mappings, recursively for the keys that hold mappings in both."""
    merged = dict(base)
    for key, value in extra.items():
        if isinstance(merged.get(key), dict) and isinstance(value, dict):
            merged[key] = deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged


def discover(directory: Path) -> list[str]:
    """Return the names of the YAML files in a directory, without extension."""
    return sorted(path.stem for path in directory.glob("*.yaml"))


class Resolver:
    """Resolve the content for one variant and one locale, collecting every error found."""

    def __init__(self, variants: list[str], locales: list[str], variant: str, locale: str) -> None:
        self.variants = variants
        self.locales = locales
        self.variant = variant
        self.locale = locale
        self.errors: list[str] = []

    def resolve(self, node: Any, path: str) -> Any:
        if isinstance(node, dict):
            return self._resolve_mapping(node, path)
        if isinstance(node, list):
            return [
                self.resolve(item, f"{path}[{index}]")
                for index, item in enumerate(node)
                if self._is_included(item, f"{path}[{index}]")
            ]
        return node

    def _resolve_mapping(self, node: dict[str, Any], path: str) -> Any:
        if node and set(node) <= set(self.locales):
            missing = [locale for locale in self.locales if locale not in node]
            if missing:
                self.errors.append(f"{path}: missing translations for {', '.join(missing)}")
                return None
            return self.resolve(node[self.locale], path)

        overrides = node.get(OVERRIDES_KEY, {})
        self._check_variants(list(overrides), f"{path}.{OVERRIDES_KEY}")
        merged = {**node, **overrides.get(self.variant, {})}
        return {
            key: self.resolve(value, f"{path}.{key}")
            for key, value in merged.items()
            if key not in (ONLY_KEY, EXCEPT_KEY, OVERRIDES_KEY)
        }

    def _is_included(self, item: Any, path: str) -> bool:
        if not isinstance(item, dict):
            return True
        only = item.get(ONLY_KEY)
        excluded = item.get(EXCEPT_KEY, [])
        self._check_variants([*(only or []), *excluded], path)
        if only is not None and self.variant not in only:
            return False
        return self.variant not in excluded

    def _check_variants(self, names: list[str], path: str) -> None:
        for name in names:
            if name not in self.variants:
                self.errors.append(f"{path}: unknown variant '{name}'")


def compose(variant: str, locale: str, private: bool) -> dict[str, Any]:
    """Build the RenderCV input for a variant in a locale, with the secrets if it is private."""
    variants = discover(VARIANTS_DIR)
    locales = discover(LOCALES_DIR)
    if variant not in variants:
        raise BuildError(f"unknown variant '{variant}' (available: {', '.join(variants)})")
    if locale not in locales:
        raise BuildError(f"unknown locale '{locale}' (available: {', '.join(locales)})")

    content = load_yaml(CONTENT_PATH)
    variant_config = load_yaml(VARIANTS_DIR / f"{variant}.yaml")
    resolver = Resolver(variants, locales, variant, locale)

    cv = resolver.resolve(content["cv"], "cv")
    cv["sections"] = {}
    for section_id in variant_config["sections"]:
        section = content["sections"].get(section_id)
        if section is None:
            resolver.errors.append(f"variants/{variant}.yaml: unknown section '{section_id}'")
            continue
        path = f"sections.{section_id}"
        title = resolver.resolve(section["title"], f"{path}.title")
        entries = resolver.resolve(section["entries"], f"{path}.entries")
        if entries:
            cv["sections"][title] = entries

    document = {
        "cv": cv,
        **load_yaml(ROOT / variant_config["design"]),
        **load_yaml(LOCALES_DIR / f"{locale}.yaml"),
        **load_yaml(SETTINGS_PATH),
    }
    if private:
        document = deep_merge(document, resolver.resolve(load_secrets(), "secrets"))

    if resolver.errors:
        raise BuildError(*resolver.errors)

    return document


def all_combinations() -> list[tuple[str, str]]:
    return list(itertools.product(discover(VARIANTS_DIR), discover(LOCALES_DIR)))


def prepare_build_folder(folder: Path, variant: str, locale: str) -> None:
    """Gather next to the RenderCV input the fonts and the template overrides that RenderCV looks for there."""
    fonts = os.environ.get("CV_FONTS")
    if not fonts:
        raise BuildError("CV_FONTS is not set, run the build inside the development shell")
    shutil.rmtree(folder, ignore_errors=True)
    folder.mkdir(parents=True)
    (folder / "fonts").symlink_to(fonts)

    design_path = ROOT / load_yaml(VARIANTS_DIR / f"{variant}.yaml")["design"]
    theme_folder = folder / load_yaml(design_path)["design"]["theme"]
    templates_folder = design_path.with_suffix("")
    if templates_folder.is_dir():
        shutil.copytree(templates_folder, theme_folder)
    if (theme_folder / "Preamble.j2.typ").exists():
        raise BuildError(f"{templates_folder.relative_to(ROOT)}: the preamble is generated, use the Typst file instead")

    # The preamble runs the design's Typst code, kept raw so that Jinja leaves it alone, and then RenderCV's own
    # preamble. RenderCV's locales have no Catalan, so the Typst language, which also sets the hyphenation rules, is
    # taken from the locale code instead.
    preamble = []
    typst_path = design_path.with_suffix(".typ")
    if typst_path.exists():
        preamble += ["{% raw %}", typst_path.read_text(encoding="utf-8"), "{% endraw %}"]
    preamble += [
        f'{{% with locale = {{"language_iso_639_1": "{locale}", "is_rtl": locale.is_rtl}} %}}',
        '{% include "typst/Preamble.j2.typ" %}',
        "{% endwith %}",
    ]
    theme_folder.mkdir(exist_ok=True)
    (theme_folder / "Preamble.j2.typ").write_text("\n".join(preamble) + "\n", encoding="utf-8")


def render(variant: str, locale: str, private: bool) -> None:
    # Private CVs go to their own folders, so they never replace the public ones.
    name = f"{variant}-{locale}" + ("-private" if private else "")
    document = compose(variant, locale, private)
    prepare_build_folder(BUILD_DIR / name, variant, locale)
    input_path = BUILD_DIR / name / "cv.yaml"
    with input_path.open("w", encoding="utf-8") as file:
        yaml.safe_dump(document, file, allow_unicode=True, sort_keys=False, width=120)
    subprocess.run(
        ["rendercv", "render", str(input_path), "--output-folder", str(OUTPUT_DIR / name)],
        check=True,
    )


def check(private: bool) -> None:
    # Most errors show up in several combinations, so each one is reported once with the combinations it affects.
    errors: dict[str, list[str]] = {}
    combinations = all_combinations()
    for variant, locale in combinations:
        try:
            compose(variant, locale, private)
        except BuildError as error:
            for message in error.args:
                errors.setdefault(message, []).append(f"{variant}/{locale}")
    if errors:
        raise BuildError(*(f"{message} (in {', '.join(names)})" for message, names in errors.items()))
    print(f"All {len(combinations)} combinations of variants and locales compose correctly.")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    options = argparse.ArgumentParser(add_help=False)
    options.add_argument("--private", action="store_true", help="include the secrets")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("check", parents=[options], help="check that every variant composes in every locale")
    render_parser = commands.add_parser("render", parents=[options], help="render a variant in a locale")
    render_parser.add_argument("variant")
    render_parser.add_argument("locale")
    commands.add_parser("render-all", parents=[options], help="render every variant in every locale")
    args = parser.parse_args()

    try:
        if args.command == "check":
            check(args.private)
        elif args.command == "render":
            render(args.variant, args.locale, args.private)
        else:
            for variant, locale in all_combinations():
                render(variant, locale, args.private)
    except BuildError as error:
        sys.exit("\n".join(f"error: {message}" for message in error.args))
    except subprocess.CalledProcessError as error:
        sys.exit(error.returncode)


if __name__ == "__main__":
    main()
