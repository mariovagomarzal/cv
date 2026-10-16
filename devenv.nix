{pkgs, ...}: {
  env = {
    GREET = "Mario's CV Development Environment";
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
      rules.line-length.max = 120;
    };
  };

  enterShell = ''
    echo $GREET
  '';
}
