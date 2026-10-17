[private]
default:
    @just --list --unsorted

build_script := "scripts/build.py"

[group("cv")]
[doc("Check that every variant composes in every locale.")]
check:
    python {{build_script}} check

[group("cv")]
[doc("Render a variant of the CV in a locale.")]
render variant="general" locale="en":
    python {{build_script}} render {{variant}} {{locale}}

[group("cv")]
[doc("Render every variant of the CV in every locale.")]
render-all:
    python {{build_script}} render-all

alias c := check
alias r := render
alias ra := render-all
