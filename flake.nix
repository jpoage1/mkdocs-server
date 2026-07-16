{
  description = "Workspace Documentation Portal — MkDocs + FastMCP server";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = {
    self,
    nixpkgs,
    flake-utils,
  }:
    flake-utils.lib.eachDefaultSystem (system: let
      pkgs = import nixpkgs {inherit system;};
      docs-server = pkgs.python3.pkgs.callPackage ./package.nix {};
    in {
      packages = {
        inherit docs-server;
        default = docs-server;
      };

      devShells.default = pkgs.mkShell {
        inputsFrom = [docs-server];
        packages = with pkgs; [
          python3
          uv
        ];
      };
    });
}
