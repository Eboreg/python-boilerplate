#!/usr/bin/env python3

import argparse
import re
import shutil
import subprocess
import sys
import venv
from os import chdir
from pathlib import Path


srcpath = Path(__file__).parent


def create_project_dir(root_path: Path, force: bool = False) -> Path:
    if root_path.exists():
        if force:
            print(f"Path {root_path} already exists, using it anyway because --force.")
        else:
            print(f"Path {root_path} already exists, aborting.")
            sys.exit(1)
    else:
        root_path.mkdir()
        print(f"Created project directory: {root_path}")
    return root_path


def create_src_dir(root_path: Path, project_name: str):
    project_name = project_name.replace("-", "_")
    package_path = root_path / "src" / project_name
    src_init_py = root_path / "src" / "__init__.py"
    package_init_py = package_path / "__init__.py"
    package_path.mkdir(parents=True, exist_ok=True)
    package_init_py.touch()
    with src_init_py.open("wt") as f:
        f.write("__version__ = \"0.1.0\"\n")
    print(f"Created source directory: {package_path}")


def copy_pyproject_toml(root_path: Path, project_name: str, description: str):
    with root_path.joinpath("pyproject.toml").open("wt", encoding="utf8") as outfile:
        with srcpath.joinpath("pyproject.toml").open("rt", encoding="utf8") as infile:
            section = ""
            for line in infile:
                if line.startswith("[") and line.strip().endswith("]"):
                    section = line.strip("[]\n")
                if section == "project" and re.match(r"^name *=.*", line):
                    outfile.write(f"name = \"{project_name}\"\n")
                elif section == "project" and re.match(r"^description *=.*", line):
                    outfile.write(f"description = \"{description}\"\n")
                else:
                    outfile.write(line)
    print("Wrote pyproject.toml.")


def copy_base_files(root_path: Path, project_name: str, description: str):
    copy_pyproject_toml(root_path=root_path, project_name=project_name, description=description)
    for filename in (".flake8", ".gitignore", "LICENSE"):
        shutil.copy(srcpath.joinpath(filename).absolute(), root_path.joinpath(filename).absolute())
    print("Copied base files.")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("root", help="Root directory of the project")
    parser.add_argument("-n", "--name", help="Project name (will be inferred from dirname if omitted).")
    parser.add_argument("-d", "--description", nargs="?", default="")
    parser.add_argument("-ng", "--no-git", help="Don't run git init.", action="store_true")
    parser.add_argument("-f", "--force", help="Continue even if destination directory exists.", action="store_true")

    args = parser.parse_args()
    root_path = Path(args.root).absolute()
    project_name = args.name or root_path.stem

    if not re.match(r"^[a-zA-Z0-9\-_]+$", project_name):
        print("Project name can only contain alphanumeric characters, hyphens, and underscores.")
        sys.exit(1)

    choice = input(f"Create project {project_name} in {root_path}? [Y/n] ")
    if choice.lower() == "n":
        sys.exit(0)

    create_project_dir(root_path=root_path, force=args.force)
    copy_base_files(root_path=root_path, project_name=project_name, description=args.description)
    create_src_dir(root_path=root_path, project_name=project_name)
    chdir(root_path)

    venv.create(".venv", with_pip=True)
    print("Created virtual environment in .venv.")

    subprocess.run(". .venv/bin/activate && pip install -e .[dev]", shell=True, check=True)
    if not args.no_git:
        subprocess.run("git init", shell=True, check=True)


if __name__ == "__main__":
    main()
