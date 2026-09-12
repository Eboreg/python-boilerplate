from python_boilerplate.runners import Runner


class UvRunner(Runner):
    NAME = "uv"

    def init_uv(self, no_git: bool):
        args = [
            "uv",
            "init",
            "--name",
            self.project_name,
            "--package",
            "--description",
            self.description,
        ]
        if no_git:
            args.extend(["--vcs", "none"])
        self.run_in_project_dir(args)
        print(f"* Ran uv init in {self.project_root_path}.")

    def create_venv(self):
        self.run_in_project_dir(["uv", "venv", "--clear", ".venv"])
        print(f"* Created virtual environment in `{self.project_root_path / '.venv'}`.")

    def run_uv_add(self):
        if dependencies := self.get_dependencies():
            self.run_in_project_dir(["uv", "add", *dependencies])
            print("* Added dependencies.")

    def run_uv_add_dev(self):
        if dev_dependencies := self.get_dev_dependencies():
            self.run_in_project_dir(["uv", "add", "--dev", *dev_dependencies])
            print("* Added dev dependencies.")

    def run_uv_sync(self):
        self.run_in_project_dir(["uv", "sync"])
        print("* Ran uv sync.")

    def create_project_dir(self, force: bool = False):
        super().create_project_dir(force)
        # Remove pyproject.toml so `uv init` won't complain
        (self.project_root_path / "pyproject.toml").unlink(missing_ok=True)

    def run(self, force: bool = False, no_git: bool = False):
        self.create_project_dir(force=force)
        self.init_uv(no_git=no_git)
        self.write_readme()
        self.copy_base_files()
        self.create_venv()
        self.run_uv_add()
        self.run_uv_add_dev()
        self.update_pyproject_toml()
        self.run_uv_sync()
