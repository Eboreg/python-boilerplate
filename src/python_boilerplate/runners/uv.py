from python_boilerplate.runners import Runner


class UvRunner(Runner):
    NAME = "uv"

    def init_uv(self):
        args = [
            "uv",
            "init",
            "--name",
            self.project_name,
            "--package",
            "--description",
            self.description,
            "--no-readme",
        ]
        if self.no_git:
            args.extend(["--vcs", "none"])
        self.run_in_project_dir(args)
        self.log(f"Ran uv init in {self.project_root_path}")

    def create_venv(self):
        self.run_in_project_dir(["uv", "venv", "--clear", ".venv"])
        self.log(f"Created virtual environment in {self.project_root_path / '.venv'}")

    def run_uv_add(self):
        if dependencies := self.get_dependencies():
            self.run_in_project_dir(["uv", "add", *dependencies])
            self.log("Added dependencies")
        if dev_dependencies := self.get_dev_dependencies():
            self.run_in_project_dir(["uv", "add", "--dev", *dev_dependencies])
            self.log("Added dev dependencies")

    def run_uv_sync(self):
        self.run_in_project_dir(["uv", "sync"])
        self.log("Ran uv sync")

    def create_project_dir(self):
        super().create_project_dir()
        # Remove pyproject.toml so `uv init` won't complain
        (self.project_root_path / "pyproject.toml").unlink(missing_ok=True)

    def run(self):
        self.pre_run()
        self.create_project_dir()
        self.init_uv()
        self.write_readme()
        self.copy_base_files()
        self.create_venv()
        self.run_uv_add()
        self.write_pyproject_toml()
        self.run_uv_sync()
        self.post_run()
