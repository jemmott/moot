{
  description = "moot flake";

  inputs = {
    flake-utils.url = "github:numtide/flake-utils";
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-23.11";
    nixpkgs-unstable.url = "github:nixos/nixpkgs/nixos-unstable";
  };

  outputs = { self, flake-utils, nixpkgs, nixpkgs-unstable }@inputs :
    flake-utils.lib.eachDefaultSystem (system:
    let
      nixpkgs = inputs.nixpkgs.legacyPackages.${system};
      nixpkgs-unstable = inputs.nixpkgs-unstable.legacyPackages.${system};
    in
    {
      devShells.default = nixpkgs.mkShell {
        packages = [
          nixpkgs-unstable.python311
          nixpkgs-unstable.python311Packages.numpy
          nixpkgs-unstable.python311Packages.scipy
          (nixpkgs-unstable.python311Packages.opencv4.override {
            enableGtk2 = true;
          })
          nixpkgs-unstable.python311Packages.webcolors
          nixpkgs-unstable.python311Packages.pyaudio
        ];
        shellHook = ''
          python3 --version
        '';
      };
    });
}
