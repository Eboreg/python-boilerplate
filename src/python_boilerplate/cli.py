import argparse

from python_boilerplate.runners import PoetryRunner, Runner, SetuptoolsRunner, UvRunner
from python_boilerplate.tools import ALL_TOOLS, Tool


class Cli:
    default_runner: str = "uv"

    def add_arguments(self, parser: argparse.ArgumentParser):
        tools = self.get_tools()
        parser.add_argument("project_name")
        parser.add_argument("directory", help="Project root dir (default: cwd/project_name)", nargs="?")
        parser.add_argument("-d", "--description", nargs="?", default="")
        parser.add_argument("-ng", "--no-git", help="Don't run git init", action="store_true")
        parser.add_argument(
            "-f",
            "--force",
            help="Continue even if destination directory exists",
            action="store_true",
        )
        parser.add_argument(
            "-r",
            "--runner",
            choices=self.get_runner_classes(),
            default=self.default_runner,
            help=f"Default: {self.default_runner}",
        )
        parser.add_argument(
            "-t",
            "--tools",
            choices=[tool.name for tool in tools],
            default=[tool.name for tool in tools if tool.default],
            nargs="*",
            help=f"Default: {', '.join(tool.name for tool in tools if tool.default)}",
        )

    def get_runner_classes(self) -> dict[str, type[Runner]]:
        return {
            "poetry": PoetryRunner,
            "setuptools": SetuptoolsRunner,
            "uv": UvRunner,
        }

    def get_tools(self) -> list[Tool]:
        return ALL_TOOLS

    def run(self):
        parser = argparse.ArgumentParser()
        self.add_arguments(parser)
        args = parser.parse_args()
        runner_class: type[Runner] | None = None
        tools = [tool for tool in self.get_tools() if tool.name in args.tools]

        for key, value in self.get_runner_classes().items():
            if args.runner == key:
                runner_class = value
                break

        if runner_class is None:
            raise ValueError

        runner = runner_class(
            project_path=args.directory if args.directory else args.project_name,
            project_name=args.project_name,
            description=args.description,
            tools=tools,
        )

        prompt = f"Create project {runner.project_name} in {runner.project_root_path} using {args.runner}? [Y/n] "
        if input(prompt).lower() != "n":
            runner.run(force=args.force, no_git=args.no_git)


def main():
    cli = Cli()
    cli.run()


if __name__ == "__main__":
    main()
