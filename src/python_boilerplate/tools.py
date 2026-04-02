class Tool:
    def __init__(
        self,
        name: str,
        dev_dependency: str | None = None,
        pyproject_key: str | None = None,
        assets: list[str] | None = None,
    ):
        self.name = name
        self.dev_dependency = dev_dependency or name
        self.pyproject_key = pyproject_key or name
        self.assets = assets or []


FLAKE8 = Tool("flake8", assets=[".flake8"])
IPDB = Tool("ipdb")
IPYTHON = Tool("ipython")
ISORT = Tool("isort")
MYPY = Tool("mypy")
PYLINT = Tool("pylint")
RUFF = Tool("ruff")
