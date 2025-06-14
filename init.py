#!/usr/bin/env python3

import argparse
import re
import shutil
import subprocess
from os import chdir
from pathlib import Path


class Runner:
    source_path = Path(__file__).parent
    project_path: Path
    project_name: str
    description: str

    def __init__(self, project_path: str | Path, project_name: str, description: str = ""):
        if not re.match(r"^[a-zA-Z0-9\-_]+$", project_name):
            raise ValueError("Project name can only contain alphanumeric characters, hyphens, and underscores.")

        if isinstance(project_path, str):
            project_path = Path(project_path)

        self.project_path = project_path.absolute()
        self.project_name = project_name
        self.description = description

    def _1_create_project_dir(self, force: bool = False):
        if self.project_path.exists():
            if not self.project_path.is_dir():
                raise ValueError(f"Path {self.project_path} exists and is not a directory; aborting.")
            if not force:
                raise ValueError(f"Path {self.project_path} already exists, aborting (use --force to use it anyway).")
            print(f" * Path {self.project_path.absolute()} already exists, using it anyway because --force.")
        else:
            self.project_path.mkdir()
            print(f"* Created project directory: {self.project_path.absolute()}.")

    def _2_copy_base_files(self):
        filenames = [".flake8", ".gitignore", "LICENSE", ".editorconfig", "poetry.toml"]

        for filename in filenames:
            shutil.copy(
                self.source_path.joinpath(filename).absolute(),
                self.project_path.joinpath(filename).absolute(),
            )

        print("* Copied base files: " + ", ".join(filenames) + ".")

    def _2_write_readme(self):
        with self.project_path.joinpath("README.md").open("wt", encoding="utf8") as readme:
            readme.write(f"# {self.project_name}")
            if self.description:
                readme.write(f"\n{self.description}")

        print("* Wrote README.md.")

    def _2_create_src_dir(self):
        package_path = self.project_path / "src" / self.project_name.replace("-", "_")
        package_path.mkdir(parents=True, exist_ok=True)
        package_init_py = package_path / "__init__.py"
        package_init_py.touch()

        print(f"* Created source directory: {package_path}.")

    def _2_init_git(self):
        chdir(self.project_path)
        subprocess.run("git init", shell=True, check=True)
        print("* Ran git init.")

    def _3_init_poetry(self):
        dev_dependencies = ["flake8", "ipdb", "ipython", "isort", "pylint"]
        chdir(self.project_path)
        subprocess.call([
            "poetry",
            "init",
            "--name",
            self.project_name,
            "--description",
            self.description,
            "--author",
            "Robert Huselius <robert@huseli.us>",
            "--python",
            ">=3.11,<4.0",
            "--license",
            "GPL-3.0-or-later",
            "--no-interaction",
            *[f"--dev-dependency={dep}" for dep in dev_dependencies],
        ])

    def _4_update_pyproject_toml(self):
        chdir(self.project_path)

        with self.project_path.joinpath("pyproject.toml").open("at", encoding="utf8") as outfile:
            with self.source_path.joinpath("pyproject.toml").open("rt", encoding="utf8") as infile:
                outfile.write("")
                for line in infile:
                    outfile.write(line)

        print("* Updated pyproject.toml.")

    def _4_sync_poetry(self):
        chdir(self.project_path)
        subprocess.call(["poetry", "sync"])

    def run(self, force: bool = False, no_git: bool = False):
        self._1_create_project_dir(force=force)
        self._2_copy_base_files()
        self._2_write_readme()
        self._2_create_src_dir()
        if not no_git:
            self._2_init_git()
        self._3_init_poetry()
        self._4_update_pyproject_toml()
        self._4_sync_poetry()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("project_name")
    parser.add_argument("directory", help="Project root dir (default: cwd/project_name)", nargs="?")
    parser.add_argument("-d", "--description", nargs="?", default="")
    parser.add_argument("-ng", "--no-git", help="Don't run git init.", action="store_true")
    parser.add_argument("-f", "--force", help="Continue even if destination directory exists.", action="store_true")

    args = parser.parse_args()

    runner = Runner(
        project_path=args.directory if args.directory else args.project_name,
        project_name=args.project_name,
        description=args.description,
    )

    if input(f"Create project {runner.project_name} in {runner.project_path}? [Y/n] ").lower() != "n":
        runner.run(force=args.force, no_git=args.no_git)


if __name__ == "__main__":
    main()
