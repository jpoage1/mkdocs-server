{
  lib,
  python,
  makeWrapper,
}:
python.pkgs.buildPythonApplication rec {
  pname = "workspace-docs-portal";
  version = "0.1.0";
  pyproject = true;

  src = lib.cleanSource ./.;

  nativeBuildInputs =
    (with python.pkgs; [
      setuptools
    ])
    ++ [makeWrapper];

  propagatedBuildInputs = with python.pkgs; [
    mcp
    mkdocs
    mkdocs-material
    pymdown-extensions
  ];

  nativeCheckInputs = with python.pkgs; [
    pytestCheckHook
  ];

  pythonImportsCheck = ["docs_server"];

  preCheck = ''
    export PYTHONPATH="$PWD/src:$PYTHONPATH"
  '';

  # docs-server's own console_scripts (docs-scanner, docs-mcp-server) don't
  # include a bare `mkdocs` binary - the systemd unit
  # (nix-config/modules/systemd/mkdocs-server.service.nix) needs one to run
  # the static docs site on :8000, separate from the stdio-only MCP server.
  # Wrap mkdocs' own binary with PYTHONPATH covering both our extra deps
  # (mkdocs-material, pymdown-extensions - mkdocs.yml's theme needs them but
  # mkdocs itself doesn't depend on them) and $out's own site-packages,
  # since mkdocs.yml's hooks entry (src/docs_server/hooks/discover_docs.py)
  # imports `docs_server` itself.
  postFixup = ''
    makeWrapper ${python.pkgs.mkdocs}/bin/mkdocs $out/bin/mkdocs \
      --set PYTHONPATH "$out/${python.sitePackages}:${python.pkgs.makePythonPath propagatedBuildInputs}"
  '';

  meta = with lib; {
    description = "Configurable Python documentation server with MkDocs and FastMCP for AI agent access";
    homepage = "https://github.com/workspace-docs-portal";
    license = licenses.mit;
    maintainers = [];
    platforms = platforms.unix;
  };
}
