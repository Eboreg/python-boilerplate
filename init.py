#!/usr/bin/env python3

from os import chdir
import shutil
from pathlib import Path
import re
import subprocess
import sys
import argparse
import venv

srcpath = Path(__file__).parent


def create_project_dir(dirname: str, parent: str) -> Path:
    path = Path(parent).joinpath(dirname)
    if path.exists():
        print("Path already exists, aborting.")
        sys.exit(1)
    path.mkdir()
    print(f"Created project directory: {path}")
    return path


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
    parser.add_argument("project_name")
    parser.add_argument("parent", help="Parent directory of the project")
    parser.add_argument("-d", "--description", nargs="?", default="")
    parser.add_argument("-ng", "--no-git", help="Don't run git init.", action="store_true")

    args = parser.parse_args()

    if not re.match(r"^[a-zA-Z0-9\-_]+$", args.project_name):
        print("Project name can only contain alphanumeric characters, hyphens, and underscores.")
        sys.exit(1)

    root_path = create_project_dir(args.project_name, args.parent)
    copy_base_files(root_path=root_path, project_name=args.project_name, description=args.description)
    create_src_dir(root_path=root_path, project_name=args.project_name)
    chdir(root_path)

    venv.create(".venv", with_pip=True)
    print("Created virtual environment in .venv.")

    subprocess.run(". .venv/bin/activate && pip install -e .[dev]", shell=True, check=True)
    if not args.no_git:
        subprocess.run("git init", shell=True, check=True)


if __name__ == "__main__":
    main()
