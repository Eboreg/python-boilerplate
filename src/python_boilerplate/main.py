import argparse

from python_boilerplate.runners import PoetryRunner, SetuptoolsRunner, UvRunner


def main():
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
        "-bs",
        "--build-system",
        choices=["uv", "poetry", "setuptools"],
        default="uv",
        help="Default: uv",
    )

    args = parser.parse_args()

    if args.build_system == "poetry":
        runner_class = PoetryRunner
    elif args.build_system == "setuptools":
        runner_class = SetuptoolsRunner
    elif args.build_system == "uv":
        runner_class = UvRunner
    else:
        raise ValueError

    runner = runner_class(
        project_path=args.directory if args.directory else args.project_name,
        project_name=args.project_name,
        description=args.description,
    )

    prompt = f"Create project {runner.project_name} in {runner.project_root_path} using {args.build_system}? [Y/n] "
    if input(prompt).lower() != "n":
        runner.run(force=args.force, no_git=args.no_git)


if __name__ == "__main__":
    main()
