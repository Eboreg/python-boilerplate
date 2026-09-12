import venv
from os import chdir

from tomlkit import TOMLDocument

from python_boilerplate.runners import Runner


class SetuptoolsRunner(Runner):
    NAME = "setuptools"

    def create_venv(self):
        chdir(self.project_root_path)
        venv.create(".venv", with_pip=True)
        self.log(f"Created virtual environment in {self.project_root_path / '.venv'}")

    def run_pip_install(self):
        self.run_in_project_dir(". .venv/bin/activate && pip install -e .[dev]", shell=True, check=True)
        self.log("Ran pip install")

    def run(self):
        self.pre_run()
        self.create_project_dir()
        self.write_readme()
        self.create_src_dir()
        self.copy_base_files()
        if not self.no_git:
            self.init_git()
        self.write_pyproject_toml()
        self.create_venv()
        self.run_pip_install()
        self.post_run()

    def update_pyproject_toml(self, toml: TOMLDocument):
        project = toml.setdefault("project", {})
        optional_dependencies = project.setdefault("optional-dependencies", {})
        optional_dependencies["dev"] = self.get_dev_dependencies()
        project["dependencies"] = self.get_dependencies()
