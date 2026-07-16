{
  lib,
  python3,
  fetchPypi,
  pytestCheckHook,
}:

python3.pkgs.buildPythonApplication rec {
  pname = "workspace-docs-portal";
  version = "0.1.0";
  pyproject = true;

  src = lib.cleanSource ./.;

  nativeBuildInputs = with python3.pkgs; [
    setuptools
  ];

  propagatedBuildInputs = with python3.pkgs; [
    mcp
    mkdocs
    mkdocs-material
    pymdown-extensions
  ];

  nativeCheckInputs = with python3.pkgs; [
    pytestCheckHook
  ];

  pythonImportsCheck = [ "docs_server" ];

  preCheck = ''
    export PYTHONPATH="$PWD/src:$PYTHONPATH"
  '';

  meta = with lib; {
    description = "Configurable Python documentation server with MkDocs and FastMCP for AI agent access";
    homepage = "https://github.com/workspace-docs-portal";
    license = licenses.mit;
    maintainers = [];
    platforms = platforms.unix;
  };
}
