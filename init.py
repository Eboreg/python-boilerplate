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


def create_dir(path: Path, force: bool = False) -> Path:
    if path.exists():
        if not path.is_dir():
            print(f"Path {path} exists and is not a directory; aborting.")
            sys.exit(1)
        if not force:
            print(f"Path {path} already exists, aborting. (Use --force to use it anyway)")
            sys.exit(1)
        print(f"Path {path} already exists, using it anyway because --force.")
    else:
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
    with root_path.joinpath("README.md").open("wt", encoding="utf8") as readme:
        readme.write(f"# {project_name}")
        if description:
            readme.write(f"\n{description}")
    print("Copied base files.")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("project_name")
    parser.add_argument("directory", help="Project root dir (default: cwd/project_name)", nargs="?")
    parser.add_argument("-d", "--description", nargs="?", default="")
    parser.add_argument("-ng", "--no-git", help="Don't run git init.", action="store_true")
    parser.add_argument("-f", "--force", help="Continue even if destination directory exists.", action="store_true")

    args = parser.parse_args()

    if not re.match(r"^[a-zA-Z0-9\-_]+$", args.project_name):
        print("Project name can only contain alphanumeric characters, hyphens, and underscores.")
        sys.exit(1)

    if args.directory:
        root_path = Path(args.directory)
    else:
        root_path = Path(args.project_name)

    choice = input(f"Create project {args.project_name} in {root_path}? [Y/n] ")
    if choice.lower() == "n":
        sys.exit(0)

    create_dir(path=root_path, force=args.force)
    print(f"Using path `{root_path.absolute()}`.")
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
