{pkgs, ...}: let
  # Space Grotesk and Space Mono are not packaged in nixpkgs, so they are fetched from their upstream sources.
  spaceGrotesk = pkgs.fetchzip {
    url = "https://github.com/floriankarsten/space-grotesk/releases/download/2.0.0/SpaceGrotesk-2.0.0.zip";
    hash = "sha256-niwd5E3rJdGmoyIFdNcK5M9A9P2rCbpsyZCl7CDv7I8=";
    stripRoot = false;
  };
  spaceMono = style: hash:
    pkgs.fetchurl {
      url = "https://raw.githubusercontent.com/google/fonts/47d54ca1ebb14fd864695f1d39dc734f39017c33/ofl/spacemono/SpaceMono-${style}.ttf";
      inherit hash;
    };

  # The fonts of the designs that RenderCV does not bundle, gathered in one folder.
  fonts = pkgs.runCommand "cv-fonts" {} ''
    mkdir -p $out
    cp ${spaceGrotesk}/SpaceGrotesk-2.0.0/otf/*.otf $out/
    cp ${spaceMono "Regular" "sha256-lYN+GCuu6tqDNo93SNsoNX8KG3XGuE/3Blte35M8jhg="} $out/SpaceMono-Regular.ttf
    cp ${spaceMono "Bold" "sha256-QF5z1Br7flkG784gajJq9clW844lXzVCHCYOhh5ZnFk="} $out/SpaceMono-Bold.ttf
    cp ${spaceMono "Italic" "sha256-7KJkyGkKkf6DfRmmut8tiJYWEMTIqvyxllJhkqnyWMU="} $out/SpaceMono-Italic.ttf
    cp ${spaceMono "BoldItalic" "sha256-zcyV7d7jEoealyhJTllfWRyxWfPydtebxYZz3sflcTg="} $out/SpaceMono-BoldItalic.ttf
    cp ${pkgs.fira-sans}/share/fonts/opentype/FiraSans-*.otf $out/
  '';
in {
  env = {
    GREET = "Mario's CV Development Environment";
    # Read by the build script, which makes these fonts available to RenderCV.
    CV_FONTS = "${fonts}";
  };

  packages = with pkgs; [
    just
    git
    sops
    rendercv
  ];

  languages.python = {
    enable = true;
    package = pkgs.python3.withPackages (ps: [
      ps.pyyaml
    ]);
  };

  git-hooks = {
    hooks = {
      convco = {
        enable = true;
        description = "Run convco to check commit messages follow Conventional Commits";
      };

      markdownlint = {
        enable = true;
        description = "Run markdownlint to check Markdown files";
        settings.configuration = {
          MD013.line_length = 120;
        };
      };

      alejandra = {
        enable = true;
        description = "Run the Alejandra formatter on Nix files";
      };

      yamllint = {
        enable = true;
        description = "Run yamllint to check YAML files";
      };

      ruff = {
        enable = true;
        description = "Run the Ruff linter on Python files";
      };

      ruff-format = {
        enable = true;
        description = "Run the Ruff formatter on Python files";
      };
    };
  };

  files = {
    ".yamllint.yaml".yaml = {
      extends = "default";
      # Encrypted values written by sops do not fit the line length limit.
      ignore = "secrets/";
      rules = {
        line-length.max = 120;
        # GitHub workflows use `on` as a key, which YAML 1.1 would read as a boolean.
        truthy.check-keys = false;
      };
    };
  };

  enterShell = ''
    echo $GREET
  '';
}
