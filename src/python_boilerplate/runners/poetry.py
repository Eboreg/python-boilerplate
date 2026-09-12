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
        self.log(f"Ran poetry init in {self.project_root_path}")

    def sync_poetry(self):
        self.run_in_project_dir(["poetry", "sync"])
        self.log("Ran poetry sync")

    def run(self):
        self.pre_run()
        self.create_project_dir()
        self.write_readme()
        self.create_src_dir()
        self.copy_base_files()
        if not self.no_git:
            self.init_git()
        self.init_poetry()
        self.write_pyproject_toml()
        self.sync_poetry()
        self.post_run()
