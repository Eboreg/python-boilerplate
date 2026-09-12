from __future__ import annotations

import functools
import re
import shutil
import subprocess
from abc import ABC, abstractmethod
from os import chdir
from pathlib import Path
from typing import TYPE_CHECKING, Any, ClassVar

from tomlkit import TOMLDocument
from tomlkit.toml_file import TOMLFile


if TYPE_CHECKING:
    from python_boilerplate.tools import Tool


class Runner(ABC):
    NAME: ClassVar[str]

    assets_paths: list[Path]
    description: str
    force: bool
    no_git: bool
    package_name: str
    project_name: str
    project_python_path: Path
    project_root_path: Path
    tools: list[Tool]

    def __init__(
        self,
        project_path: str | Path,
        project_name: str,
        description: str,
        tools: list[Tool],
        force: bool = False,
        no_git: bool = False,
    ):
        if not re.match(r"^[a-zA-Z0-9\-_]+$", project_name):
            raise ValueError("Project name can only contain alphanumeric characters, hyphens, and underscores.")

        if isinstance(project_path, str):
            project_path = Path(project_path)

        self.assets_paths = [(Path(__file__) / "../../assets").resolve()]
        self.force = force
        self.no_git = no_git
        self.project_root_path = project_path.resolve()
        self.project_name = project_name
        self.package_name = project_name.replace("-", "_")
        self.project_python_path = self.project_root_path / "src" / self.package_name
        self.description = description
        self.tools = tools

    def build_assets_paths(self, *names: str) -> list[Path]:
        paths: list[Path] = []
        for path in self.assets_paths:
            for name in names:
                paths.append(path / name)
        return [p for p in paths if p.exists()]

    def copy_base_files(self):
        for base_dir in self.build_assets_paths("runners/base"):
            shutil.copytree(base_dir, self.project_root_path, dirs_exist_ok=True)
            self.log(f"Copied base files from {base_dir} to {self.project_root_path}")

        for runner_dir in self.build_assets_paths(f"runners/{self.NAME}"):
            shutil.copytree(runner_dir, self.project_root_path, dirs_exist_ok=True)
            self.log(f"Copied {self.NAME} specific files from {runner_dir} to {self.project_root_path}")

        for tool in self.tools:
            for tool_dir in self.build_assets_paths(f"tools/{tool.name}"):
                shutil.copytree(tool_dir, self.project_root_path, dirs_exist_ok=True)
                self.log(f"Copied {tool.name} specific files from {tool_dir} to {self.project_root_path}")

    def create_project_dir(self):
        if self.project_root_path.exists():
            assert self.project_root_path.is_dir(), (
                f"Path {self.project_root_path} exists and is not a directory; aborting"
            )
            assert self.force, f"Path {self.project_root_path} already exists, aborting (use --force to use it anyway)"
            self.log(f"Path {self.project_root_path} already exists, using it anyway because --force")
        else:
            self.project_root_path.mkdir(parents=True)
            self.log(f"Created project directory: {self.project_root_path}")

    def create_src_dir(self):
        self.project_python_path.mkdir(parents=True, exist_ok=True)
        package_init_py = self.project_python_path / "__init__.py"
        package_init_py.touch()

        self.log(f"Created source directory: {self.project_python_path}")

    def do_string_replacements(self, s: str) -> str:
        for k, v in self.get_string_replacements().items():
            s = re.sub(rf"{{{{ *{k} *}}}}", v, s)
        return s

    def get_dependencies(self):
        return [tool.specifier for tool in self.tools if not tool.dev]

    def get_dev_dependencies(self):
        return [tool.specifier for tool in self.tools if tool.dev]

    def get_last_existing_assets_path(self, *parts: str):
        for assets_path in reversed(self.assets_paths):
            path = assets_path / "/".join(parts)
            if path.exists():
                return path
        return None

    def get_string_replacements(self) -> dict[str, str]:
        return {
            "description": self.description,
            "package_name": self.package_name,
            "project_name": self.project_name,
        }

    def init_git(self):
        self.run_in_project_dir("git init", shell=True, check=True)
        self.log("Ran git init")

    def log(self, message: str):
        suffix = "=" * (120 - len(message) - 5)
        print(f"=== {message} {suffix}")

    def merge_pyproject_tables(
        self,
        source: dict[str, Any],
        target: dict[str, Any],
        path: list[str] | None = None,
        tools: list[str] | None = None,
    ):
        path = path or []
        tools = tools or []

        if len(path) == 2 and path[0] == "tool" and path[1] not in tools:
            return

        for key, base_value in source.items():
            if isinstance(base_value, dict):
                project_value = target.setdefault(key, {})
                assert isinstance(project_value, dict)
                self.merge_pyproject_tables(base_value, project_value, path=path + [key], tools=tools)
                if len(project_value) == 0:
                    del target[key]
            else:
                target[key] = base_value

    def merge_pyprojects(self, source: TOMLDocument, target: TOMLDocument) -> TOMLDocument:
        self.merge_pyproject_tables(source, target, tools=[tool.pyproject_key for tool in self.tools])
        return target

    def post_run(self):
        pass

    def pre_run(self):
        pass

    def replace_pyproject_toml_placeholders(self, toml: dict[str, Any]):
        for k, v in toml.items():
            if isinstance(v, dict):
                self.replace_pyproject_toml_placeholders(v)
            elif isinstance(v, str):
                toml[k] = self.do_string_replacements(v)
            elif isinstance(v, list):
                for idx in range(len(v)):
                    if isinstance(v[idx], dict):
                        self.replace_pyproject_toml_placeholders(v[idx])
                    if isinstance(v[idx], str):
                        v[idx] = self.do_string_replacements(v[idx])

    def run_in_project_dir(
        self,
        args: str | list[str],
        shell: bool = False,
        check: bool = False,
    ) -> subprocess.CompletedProcess[bytes]:
        chdir(self.project_root_path)
        return subprocess.run(args, shell=shell, check=check)

    def update_pyproject_toml(self, toml: TOMLDocument):
        pass

    def write_pyproject_toml(self):
        project_toml_file = TOMLFile(self.project_root_path / "pyproject.toml")
        tomls = [
            *[
                TOMLFile(path).read()
                for path in self.build_assets_paths(
                    "templates/base/pyproject.toml",
                    f"templates/{self.NAME}/pyproject.toml",
                )
            ],
            project_toml_file.read(),
        ]
        toml = functools.reduce(lambda x, y: self.merge_pyprojects(x, y), tomls)

        self.update_pyproject_toml(toml)
        self.replace_pyproject_toml_placeholders(toml)
        project_toml_file.write(toml)

        self.log("Wrote pyproject.toml")

    def write_readme(self):
        with self.project_root_path.joinpath("README.md").open("wt", encoding="utf8") as readme:
            readme.write(f"# {self.project_name}")
            if self.description:
                readme.write(f"\n{self.description}")

        self.log("Wrote README.md")

    @abstractmethod
    def run(self):
        raise NotImplementedError()
