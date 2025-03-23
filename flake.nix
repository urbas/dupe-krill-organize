{
  description = "Interactively deduplicate your directories.";

  inputs.nixpkgs.url = "nixpkgs/nixpkgs-unstable";
  inputs.flake-utils.url = "github:numtide/flake-utils";
  inputs.dupe-krill-analyze.url = "github:urbas/dupe-krill-analyze";
  inputs.dupe-krill-analyze.inputs.nixpkgs.follows = "nixpkgs";
  inputs.dupe-krill-analyze.inputs.flake-utils.follows = "flake-utils";

  outputs =
    {
      self,
      nixpkgs,
      flake-utils,
      dupe-krill-analyze,
    }:
    flake-utils.lib.eachDefaultSystem (
      system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
        inherit (pkgs) python3 lib;
        pyproject = lib.importTOML ./pyproject.toml;

        runtimeBinDeps = with pkgs; [
          dupe-krill
          dupe-krill-analyze.packages.${system}.default
        ];

        pkg = python3.pkgs.buildPythonPackage rec {
          pname = pyproject.project.name;
          version = pyproject.project.version;
          format = "pyproject";
          src = self;

          nativeBuildInputs = with python3.pkgs; [
            hatchling
          ];

          propagatedBuildInputs =
            with python3.pkgs;
            [
              click
              textual
            ]
            ++ runtimeBinDeps;

          checkInputs = with python3.pkgs; [
            pytestCheckHook
          ];
        };

        editable-pkg = python3.pkgs.mkPythonEditablePackage {
          pname = pyproject.project.name;
          inherit (pyproject.project) scripts version;
          root = "$PWD";
        };

      in
      {
        apps.default.program = "${pkg}/bin/${pyproject.project.name}";
        apps.default.type = "app";

        packages.default = pkg;
        packages.${pyproject.project.name} = pkg;

        devShells.default = pkgs.mkShell {
          inputsFrom = [ pkg ];
          packages = with pkgs; [
            editable-pkg
            nixfmt-rfc-style
            nodePackages.prettier
            parallel
            pyright
            python3.pkgs.ipython
            ruff
          ];
        };
      }
    );
}
