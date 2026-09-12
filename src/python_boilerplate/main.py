import argparse

from python_boilerplate.runners import PoetryRunner, SetuptoolsRunner, UvRunner
from python_boilerplate.runners.base import Runner


def run_main(runner_classes: dict[str, type[Runner]], default_runner: str):
    parser = argparse.ArgumentParser()
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
        choices=runner_classes,
        default=default_runner,
        help=f"Default: {default_runner}",
    )

    args = parser.parse_args()
    runner_class: type[Runner] | None = None

    for key, value in runner_classes.items():
        if args.runner == key:
            runner_class = value
            break

    if runner_class is None:
        raise ValueError

    runner = runner_class(
        project_path=args.directory if args.directory else args.project_name,
        project_name=args.project_name,
        description=args.description,
    )

    prompt = f"Create project {runner.project_name} in {runner.project_root_path} using {args.build_system}? [Y/n] "
    if input(prompt).lower() != "n":
        runner.run(force=args.force, no_git=args.no_git)


def main():
    RUNNER_CLASSES = {
        "poetry": PoetryRunner,
        "setuptools": SetuptoolsRunner,
        "uv": UvRunner,
    }
    run_main(RUNNER_CLASSES, "uv")


if __name__ == "__main__":
    main()
