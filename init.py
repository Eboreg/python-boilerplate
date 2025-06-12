#!/usr/bin/env python3

import argparse
import re
import shutil
import subprocess
import venv
from os import chdir
from pathlib import Path


class Runner:
    source_path = Path(__file__).parent
    root_path: Path
    project_name: str
    description: str

    def __init__(self, root_path: str | Path, project_name: str, description: str = ""):
        if not re.match(r"^[a-zA-Z0-9\-_]+$", project_name):
            raise ValueError("Project name can only contain alphanumeric characters, hyphens, and underscores.")

        if isinstance(root_path, str):
            root_path = Path(root_path)

        self.root_path = root_path.absolute()
        self.project_name = project_name
        self.description = description

    def create_project_dir(self, force: bool = False):
        if self.root_path.exists():
            if not self.root_path.is_dir():
                raise ValueError(f"Path {self.root_path} exists and is not a directory; aborting.")
            if not force:
                raise ValueError(f"Path {self.root_path} already exists, aborting (use --force to use it anyway).")
            print(f" * Path {self.root_path.absolute()} already exists, using it anyway because --force.")
        else:
            self.root_path.mkdir()
            print(f"* Created project directory: {self.root_path.absolute()}.")

    def copy_base_files(self):
        filenames = [".flake8", ".gitignore", "LICENSE", ".editorconfig"]

        for filename in filenames:
            shutil.copy(self.source_path.joinpath(filename).absolute(), self.root_path.joinpath(filename).absolute())

        print("* Copied base files: " + ", ".join(filenames) + ".")

    def copy_pyproject_toml(self):
        with self.root_path.joinpath("pyproject.toml").open("wt", encoding="utf8") as outfile:
            with self.source_path.joinpath("pyproject.toml").open("rt", encoding="utf8") as infile:
                section = ""

                for line in infile:
                    if line.startswith("[") and line.strip().endswith("]"):
                        section = line.strip("[]\n")

                    if section == "project" and re.match(r"^name *=.*", line):
                        outfile.write(f"name = \"{self.project_name}\"\n")
                    elif section == "project" and re.match(r"^description *=.*", line):
                        outfile.write(f"description = \"{self.description}\"\n")
                    else:
                        outfile.write(line)

        print("* Wrote pyproject.toml.")

    def create_src_dir(self):
        project_name = self.project_name.replace("-", "_")
        package_path = self.root_path / "src" / project_name
        src_init_py = self.root_path / "src" / "__init__.py"
        package_init_py = package_path / "__init__.py"
        package_path.mkdir(parents=True, exist_ok=True)
        package_init_py.touch()

        with src_init_py.open("wt") as f:
            f.write("__version__ = \"0.1.0\"\n")

        print(f"* Created source directory: {package_path}.")

    def create_venv(self):
        chdir(self.root_path)
        venv.create(".venv", with_pip=True)
        print("* Created virtual environment in .venv.")

    def install_requirements(self, no_git: bool = False):
        chdir(self.root_path)
        subprocess.run(". .venv/bin/activate && pip install -e .[dev]", shell=True, check=True)
        print("* Installed requirements.")

        if not no_git:
            subprocess.run("git init", shell=True, check=True)
            print("* Ran git init.")

    def write_readme(self):
        with self.root_path.joinpath("README.md").open("wt", encoding="utf8") as readme:
            readme.write(f"# {self.project_name}")
            if self.description:
                readme.write(f"\n{self.description}")

        print("* Wrote README.md.")

    def run(self, force: bool = False, no_git: bool = False):
        self.create_project_dir(force=force)
        self.copy_base_files()
        self.copy_pyproject_toml()
        self.write_readme()
        self.create_src_dir()
        self.create_venv()
        self.install_requirements(no_git=no_git)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("project_name")
    parser.add_argument("directory", help="Project root dir (default: cwd/project_name)", nargs="?")
    parser.add_argument("-d", "--description", nargs="?", default="")
    parser.add_argument("-ng", "--no-git", help="Don't run git init.", action="store_true")
    parser.add_argument("-f", "--force", help="Continue even if destination directory exists.", action="store_true")

    args = parser.parse_args()

    runner = Runner(
        root_path=args.directory if args.directory else args.project_name,
        project_name=args.project_name,
        description=args.description,
    )

    if input(f"Create project {runner.project_name} in {runner.root_path}? [Y/n] ").lower() != "n":
        runner.run(force=args.force, no_git=args.no_git)


if __name__ == "__main__":
    main()
