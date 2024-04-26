{
  description = "richexif - Wrapper around ExifTool to display metadata with Rich";

  outputs = {
    self,
    nixpkgs,
    flake-utils,
    git-hooks,
    ...
  }: (flake-utils.lib.eachDefaultSystem (
    system: let
      pkgs = import nixpkgs {inherit system;};

      pythonDeps = with pkgs.python3Packages; [
        pyexiftool
        rich
        typer
        typing-extensions
      ];

      pythonPackage = with pkgs.python3.pkgs;
        buildPythonApplication {
          pname = "richexif";
          version = "0-unstable-2024-04-26";
          src = self;
          format = "pyproject";

          nativeBuildInputs = with pkgs; [
            poetry-core
          ];

          propagatedBuildInputs = pythonDeps;

          pythonImportsCheck = [
            "richexif"
          ];
        };
    in {
      packages.default = pythonPackage;

      devShells.default = pkgs.mkShell {
        inherit (self.checks.${system}.pre-commit-check) shellHook;
        packages = with pkgs; [
          poetry
          ruff
          (python3.withPackages (_: pythonDeps))
        ];
      };

      checks = {
        pre-commit-check = git-hooks.lib.${system}.run {
          src = "./.";
          excludes = ["flake\.lock"];
          hooks = {
            alejandra.enable = true;
            commitizen.enable = true;
            deadnix.enable = true;
            editorconfig-checker.enable = true;
            markdownlint.enable = true;
            poetry-check.enable = true;
            poetry-lock.enable = true;
            prettier.enable = true;
            ruff.enable = true;
            statix.enable = true;
            typos.enable = true;
          };
        };
      };
    }
  ));

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs";
    flake-utils.url = "github:numtide/flake-utils";
    git-hooks = {
      url = "github:cachix/git-hooks.nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };
}
