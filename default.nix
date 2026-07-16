# Backwards-compatible entry point for non-flake Nix.
# Usage: nix-build -E 'import <nixpkgs> {} callPackage ./default.nix {}'
# Or:    nix-build (uses pinned nixpkgs via fetchTarball)
{pkgs ? import (fetchTarball "https://github.com/NixOS/nixpkgs/archive/nixos-unstable.tar.gz") {}}:
pkgs.python3.pkgs.callPackage ./package.nix {}
