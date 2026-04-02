import subprocess
from os import chdir

from python_boilerplate.runners import Runner
from python_boilerplate.tools import IPDB, IPYTHON, RUFF


class UvRunner(Runner):
    ASSETS_SUBDIR = "uv"
    TOOLS = [RUFF, IPDB, IPYTHON]

    def init_uv(self, no_git: bool):
        chdir(self.project_root_path)
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
        subprocess.call(args)
        print(f"* Ran uv init in {self.project_root_path}.")

    def create_venv(self):
        chdir(self.project_root_path)
        subprocess.call(["uv", "venv", "--clear", ".venv"])
        print(f"* Created virtual environment in `{self.project_root_path / '.venv'}`.")

    def run_uv_add(self):
        chdir(self.project_root_path)
        dev_dependencies = [tool.dev_dependency for tool in self.TOOLS]
        subprocess.call(["uv", "add", "--dev", *dev_dependencies])
        print("* Added dev dependencies.")

    def run_uv_sync(self):
        chdir(self.project_root_path)
        subprocess.call(["uv", "sync"])
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
        self.update_pyproject_toml()
        self.run_uv_sync()
