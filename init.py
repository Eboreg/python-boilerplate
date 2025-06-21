#!/usr/bin/env python3

import argparse
import re
import shutil
import subprocess
from os import chdir
from pathlib import Path
import venv


class Runner:
    base_filenames = [".flake8", ".gitignore", "LICENSE", ".editorconfig"]
    description: str
    project_name_camelcase: str
    project_name: str
    project_python_path: Path
    project_root_path: Path
    source_path = Path(__file__).parent.absolute()

    def __init__(self, project_path: str | Path, project_name: str, description: str = ""):
        if not re.match(r"^[a-zA-Z0-9\-_]+$", project_name):
            raise ValueError("Project name can only contain alphanumeric characters, hyphens, and underscores.")

        if isinstance(project_path, str):
            project_path = Path(project_path)

        self.project_root_path = project_path.absolute()
        self.project_name = project_name
        self.project_name_camelcase = self.project_name.replace("-", "_")
        self.project_python_path = self.project_root_path / "src" / self.project_name_camelcase
        self.description = description

    def _1_create_project_dir(self, force: bool = False):
        if self.project_root_path.exists():
            if not self.project_root_path.is_dir():
                raise ValueError(f"Path {self.project_root_path} exists and is not a directory; aborting.")
            if not force:
                raise ValueError(f"Path {self.project_root_path} already exists, aborting (use --force to use it anyway).")
            print(f" * Path {self.project_root_path} already exists, using it anyway because --force.")
        else:
            self.project_root_path.mkdir(parents=True)
            print(f"* Created project directory: {self.project_root_path}.")

    def _2_copy_base_files(self):
        for filename in self.base_filenames:
            shutil.copy(self.source_path.joinpath(filename), self.project_root_path.joinpath(filename))

        print("* Copied base files: " + ", ".join(self.base_filenames) + ".")

    def _2_write_readme(self):
        with self.project_root_path.joinpath("README.md").open("wt", encoding="utf8") as readme:
            readme.write(f"# {self.project_name}")
            if self.description:
                readme.write(f"\n{self.description}")

        print("* Wrote README.md.")

    def _2_create_src_dir(self):
        self.project_python_path.mkdir(parents=True, exist_ok=True)
        package_init_py = self.project_python_path / "__init__.py"
        package_init_py.touch()

        print(f"* Created source directory: {self.project_python_path}.")

    def _2_init_git(self):
        chdir(self.project_root_path)
        subprocess.run("git init", shell=True, check=True)
        print("* Ran git init.")

    def _update_pyproject_toml(self):
        with self.project_root_path.joinpath("pyproject.toml").open("at", encoding="utf8") as outfile:
            with self.source_path.joinpath("pyproject.base.toml").open("rt", encoding="utf8") as infile:
                outfile.write("\n")
                outfile.writelines(infile.readlines())

    def run(self, force: bool = False, no_git: bool = False):
        self._1_create_project_dir(force=force)
        self._2_write_readme()
        self._2_create_src_dir()
        self._2_copy_base_files()
        if not no_git:
            self._2_init_git()


class SetuptoolsRunner(Runner):
    def _2_copy_pyproject_toml(self):
        with self.project_root_path.joinpath("pyproject.toml").open("wt", encoding="utf8") as outfile:
            with self.source_path.joinpath("pyproject.setuptools.toml").open("rt", encoding="utf8") as infile:
                for line in infile:
                    outfile.write(
                        line.replace("{{project_name}}", self.project_name)
                            .replace("{{description}}", self.description)
                    )

        self._update_pyproject_toml()

        print("* Wrote pyproject.toml.")

    def _2_create_venv(self):
        chdir(self.project_root_path)
        venv.create(".venv", with_pip=True)
        print(f"* Created virtual environment in `{self.project_root_path / '.venv'}`.")

    def _3_run_pip_install(self):
        chdir(self.project_root_path)
        subprocess.run(". .venv/bin/activate && pip install -e .[dev]", shell=True, check=True)
        print("* Ran pip install.")

    def run(self, force: bool = False, no_git: bool = False):
        super().run(force, no_git)
        self._2_copy_pyproject_toml()
        self._2_create_venv()
        self._3_run_pip_install()


class PoetryRunner(Runner):
    base_filenames = [".flake8", ".gitignore", "LICENSE", ".editorconfig", "poetry.toml"]

    def _3_init_poetry(self):
        dev_dependencies = ["flake8", "ipdb", "ipython", "isort", "pylint"]
        chdir(self.project_root_path)

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
        self._update_pyproject_toml()
        print("* Updated pyproject.toml.")

    def _4_sync_poetry(self):
        chdir(self.project_root_path)
        subprocess.call(["poetry", "sync"])

    def run(self, force: bool = False, no_git: bool = False):
        super().run(force, no_git)
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
    parser.add_argument("-bs", "--build-system", choices=["poetry", "setuptools"], default="poetry")

    args = parser.parse_args()
    runner_class = PoetryRunner if args.build_system == "poetry" else SetuptoolsRunner

    runner = runner_class(
        project_path=args.directory if args.directory else args.project_name,
        project_name=args.project_name,
        description=args.description,
    )

    prompt = f"Create project {runner.project_name} in {runner.project_root_path} using {args.build_system}? [Y/n] "
    if input(prompt).lower() != "n":
        runner.run(force=args.force, no_git=args.no_git)


if __name__ == "__main__":
    main()
