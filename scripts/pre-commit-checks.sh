#!/usr/bin/env zsh

set -eo pipefail

SCRIPT_PATH=${0:a}

function markdown_fmt() {
  ( set -x; prettier --ignore-path .gitignore --prose-wrap=always --write ./**/*.md )
}

function nix_fmt() {
  ( set -x; nixfmt flake.nix )
}

function python_fmt() {
  ( set -x; ruff format )
}

function python_check() {
  ( set -x; ruff check )
}

function python_typecheck() {
  ( set -x; pyright )
}

function python_unit_tests() {
  ( set -x; pytest tests )
}

if [ "$#" -gt 0 ]; then
  "$@"
else
  parallel --line-buffer --halt now,fail=1 --tagstring '{}>' $SCRIPT_PATH ::: \
    markdown_fmt \
    nix_fmt \
    python_check \
    python_fmt \
    python_typecheck \
    python_unit_tests
fi
