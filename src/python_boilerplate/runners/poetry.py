import subprocess
from os import chdir

from python_boilerplate.runners import Runner


class PoetryRunner(Runner):
    ASSETS_SUBDIR = "poetry"
    BASE_FILENAMES = [".gitignore", "LICENSE", ".editorconfig", "poetry.toml"]

    def init_poetry(self):
        chdir(self.project_root_path)
        dev_dependencies = [tool.dev_dependency for tool in self.TOOLS]

        # Will only create a pyproject.toml and nothing more
        subprocess.call(
            [
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
            ]
        )
        print(f"Ran poetry init in {self.project_root_path}.")

    def sync_poetry(self):
        chdir(self.project_root_path)
        subprocess.call(["poetry", "sync"])
        print("Ran poetry sync.")

    def run(self, force: bool = False, no_git: bool = False):
        self.create_project_dir(force=force)
        self.write_readme()
        self.create_src_dir()
        self.copy_base_files()
        if not no_git:
            self.init_git()
        self.init_poetry()
        self.update_pyproject_toml()
        self.sync_poetry()
