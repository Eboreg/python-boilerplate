import re
import shutil
import subprocess
from abc import ABC, abstractmethod
from os import chdir
from pathlib import Path
from typing import ClassVar

import tomlkit
import tomlkit.items
import tomlkit.toml_document
from tomlkit.toml_file import TOMLFile

from python_boilerplate.tools import FLAKE8, IPDB, IPYTHON, ISORT, MYPY, PYLINT, Tool


class Runner(ABC):
    ASSETS_PATH = (Path(__file__) / "../../assets").resolve().absolute()
    ASSETS_SUBDIR: ClassVar[str]
    BASE_FILENAMES = [".gitignore", "LICENSE", ".editorconfig"]
    TOOLS: ClassVar[list[Tool]] = [FLAKE8, IPDB, IPYTHON, ISORT, MYPY, PYLINT]

    description: str
    project_name: str
    project_python_path: Path
    project_root_path: Path

    def __init__(self, project_path: str | Path, project_name: str, description: str = ""):
        if not re.match(r"^[a-zA-Z0-9\-_]+$", project_name):
            raise ValueError("Project name can only contain alphanumeric characters, hyphens, and underscores.")

        if isinstance(project_path, str):
            project_path = Path(project_path)

        self.project_root_path = project_path.absolute()
        self.project_name = project_name
        self.project_python_path = self.project_root_path / "src" / self.project_name.replace("-", "_")
        self.description = description

    def create_project_dir(self, force: bool = False):
        if self.project_root_path.exists():
            if not self.project_root_path.is_dir():
                raise ValueError(f"Path {self.project_root_path} exists and is not a directory; aborting.")
            if not force:
                raise ValueError(
                    f"Path {self.project_root_path} already exists, aborting (use --force to use it anyway)."
                )
            print(f" * Path {self.project_root_path} already exists, using it anyway because --force.")
        else:
            self.project_root_path.mkdir(parents=True)
            print(f"* Created project directory: {self.project_root_path}.")

    def copy_base_files(self):
        filenames = [
            *self.BASE_FILENAMES,
            *[filename for tool in self.TOOLS for filename in tool.assets],
        ]
        for filename in filenames:
            shutil.copy(self.get_asset(filename), self.project_root_path / filename)

        print("* Copied base files: " + ", ".join(filenames) + ".")

    def write_readme(self):
        with self.project_root_path.joinpath("README.md").open("wt", encoding="utf8") as readme:
            readme.write(f"# {self.project_name}")
            if self.description:
                readme.write(f"\n{self.description}")

        print("* Wrote README.md.")

    def create_src_dir(self):
        self.project_python_path.mkdir(parents=True, exist_ok=True)
        package_init_py = self.project_python_path / "__init__.py"
        package_init_py.touch()

        print(f"* Created source directory: {self.project_python_path}.")

    def get_asset(self, filename: str, check_subdir: bool = True) -> Path:
        if check_subdir:
            path = self.ASSETS_PATH / self.ASSETS_SUBDIR / filename
            if path.is_file():
                return path
        return self.ASSETS_PATH / filename

    def init_git(self):
        chdir(self.project_root_path)
        subprocess.run("git init", shell=True, check=True)
        print("* Ran git init.")

    def merge_pyproject_tables(
        self,
        source: tomlkit.items.Table | tomlkit.toml_document.TOMLDocument,
        target: tomlkit.items.Table | tomlkit.toml_document.TOMLDocument,
        path: list[str] | None = None,
    ):
        path = path or []
        if len(path) == 2 and path[0] == "tool":
            if path[1] not in [tool.pyproject_key for tool in self.TOOLS]:
                return
        for key, base_value in source.items():
            if isinstance(base_value, tomlkit.items.Table):
                project_value = target.get(key)
                if not isinstance(project_value, tomlkit.items.Table):
                    target[key] = {}
                    project_value = target[key]
                assert isinstance(project_value, tomlkit.items.Table)
                self.merge_pyproject_tables(base_value, project_value, path + [key])
                if len(project_value) == 0:
                    del target[key]
            else:
                target[key] = base_value

    def update_pyproject_toml(self):
        base_toml_path = self.get_asset("pyproject.template.toml", check_subdir=False)
        runner_toml_path = self.get_asset("pyproject.template.toml")
        project_toml_path = self.project_root_path / "pyproject.toml"
        project_toml_file = TOMLFile(project_toml_path)
        project_toml = project_toml_file.read()
        base_toml = TOMLFile(base_toml_path).read()

        if base_toml_path != runner_toml_path:
            runner_toml = TOMLFile(runner_toml_path).read()
            self.merge_pyproject_tables(runner_toml, base_toml)

        self.merge_pyproject_tables(base_toml, project_toml)
        project_toml_file.write(project_toml)

        with project_toml_path.open("rt") as f:
            toml_string = f.read()
        toml_string = toml_string.replace("{{project_name}}", self.project_name).replace(
            "{{description}}", self.description
        )
        with project_toml_path.open("wt") as f:
            f.write(toml_string)

        print("* Updated pyproject.toml.")

    @abstractmethod
    def run(self, force: bool = False, no_git: bool = False):
        raise NotImplementedError()
