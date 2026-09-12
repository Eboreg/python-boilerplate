from python_boilerplate.runners import Runner


class PoetryRunner(Runner):
    NAME = "poetry"

    def init_poetry(self):
        # Will only create a pyproject.toml and nothing more
        self.run_in_project_dir(
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
                *[f"--dev-dependency='{dep}'" for dep in self.get_dev_dependencies()],
                *[f"--dependency='{dep}'" for dep in self.get_dependencies()],
            ]
        )
        print(f"Ran poetry init in {self.project_root_path}.")

    def sync_poetry(self):
        self.run_in_project_dir(["poetry", "sync"])
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
