[private]
default:
    @just --list --unsorted

build_script := "scripts/build.py"

[group("cv")]
[doc("Check that every variant composes in every locale. Pass --private to include the secrets.")]
check *args:
    python {{build_script}} check {{args}}

[group("cv")]
[doc("Render a variant of the CV in a locale. Pass --private to include the secrets.")]
render variant="general" locale="en" *args:
    python {{build_script}} render {{variant}} {{locale}} {{args}}

[group("cv")]
[doc("Render every variant of the CV in every locale. Pass --private to include the secrets.")]
render-all *args:
    python {{build_script}} render-all {{args}}

alias c := check
alias r := render
alias ra := render-all
