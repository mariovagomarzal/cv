"""Compose the CV variants from the shared content and render them with RenderCV.

Variants and locales are discovered from the files in `variants/` and `locales/`, so adding either needs no change
here. See `content.yaml` for how the content is written.
"""

import argparse
import itertools
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


def compose(variant: str, locale: str) -> dict[str, Any]:
    """Build the RenderCV input for a variant in a locale."""
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

    if resolver.errors:
        raise BuildError(*resolver.errors)

    return {
        "cv": cv,
        **load_yaml(ROOT / variant_config["design"]),
        **load_yaml(LOCALES_DIR / f"{locale}.yaml"),
        **load_yaml(SETTINGS_PATH),
    }


def all_combinations() -> list[tuple[str, str]]:
    return list(itertools.product(discover(VARIANTS_DIR), discover(LOCALES_DIR)))


def render(variant: str, locale: str) -> None:
    name = f"{variant}-{locale}"
    input_path = BUILD_DIR / name / "cv.yaml"
    input_path.parent.mkdir(parents=True, exist_ok=True)
    with input_path.open("w", encoding="utf-8") as file:
        yaml.safe_dump(compose(variant, locale), file, allow_unicode=True, sort_keys=False, width=120)
    subprocess.run(
        ["rendercv", "render", str(input_path), "--output-folder", str(OUTPUT_DIR / name)],
        check=True,
    )


def check() -> None:
    # Most errors show up in several combinations, so each one is reported once with the combinations it affects.
    errors: dict[str, list[str]] = {}
    combinations = all_combinations()
    for variant, locale in combinations:
        try:
            compose(variant, locale)
        except BuildError as error:
            for message in error.args:
                errors.setdefault(message, []).append(f"{variant}/{locale}")
    if errors:
        raise BuildError(*(f"{message} (in {', '.join(names)})" for message, names in errors.items()))
    print(f"All {len(combinations)} combinations of variants and locales compose correctly.")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("check", help="check that every variant composes in every locale")
    render_parser = commands.add_parser("render", help="render a variant in a locale")
    render_parser.add_argument("variant")
    render_parser.add_argument("locale")
    commands.add_parser("render-all", help="render every variant in every locale")
    args = parser.parse_args()

    try:
        if args.command == "check":
            check()
        elif args.command == "render":
            render(args.variant, args.locale)
        else:
            for variant, locale in all_combinations():
                render(variant, locale)
    except BuildError as error:
        sys.exit("\n".join(f"error: {message}" for message in error.args))
    except subprocess.CalledProcessError as error:
        sys.exit(error.returncode)


if __name__ == "__main__":
    main()
