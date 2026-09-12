import venv
from os import chdir

from python_boilerplate.runners import Runner


class SetuptoolsRunner(Runner):
    NAME = "setuptools"

    def create_venv(self):
        chdir(self.project_root_path)
        venv.create(".venv", with_pip=True)
        print(f"* Created virtual environment in `{self.project_root_path / '.venv'}`.")

    def run_pip_install(self):
        self.run_in_project_dir(". .venv/bin/activate && pip install -e .[dev]", shell=True, check=True)
        print("* Ran pip install.")

    def run(self, force: bool = False, no_git: bool = False):
        self.create_project_dir(force=force)
        self.write_readme()
        self.create_src_dir()
        self.copy_base_files()
        if not no_git:
            self.init_git()
        self.update_pyproject_toml()
        self.create_venv()
        self.run_pip_install()
