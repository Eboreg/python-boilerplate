class Tool:
    def __init__(
        self,
        name: str,
        dev: bool = True,
        default: bool = True,
        specifier: str | None = None,
        pyproject_key: str | None = None,
    ):
        self.name = name
        self.dev = dev
        self.default = default
        self.specifier = specifier or name
        self.pyproject_key = pyproject_key or name

    def __repr__(self):
        return f"Tool({self.name})"


FLAKE8 = Tool("flake8", default=False)
IPDB = Tool("ipdb")
IPYTHON = Tool("ipython")
ISORT = Tool("isort")
MYPY = Tool("mypy", default=False)
PYLINT = Tool("pylint", default=False)
RUFF = Tool("ruff")

ALL_TOOLS = [FLAKE8, IPDB, IPYTHON, ISORT, MYPY, PYLINT, RUFF]
