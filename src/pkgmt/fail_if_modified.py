import subprocess
import argparse
import sys


def check_modified(base_branch, exclude_path, debug=False):
    # https://stackoverflow.com/questions/4380945
    cmd = f"git diff --exit-code {base_branch}... -- ."

    for path in exclude_path:
        cmd += f" ':^{path}'"

    if debug:
        print(f"cmd: {cmd}")
    try:
        subprocess.check_output(cmd, shell=True)
        return 0
    except subprocess.CalledProcessError as err:
        if debug:
            print(
                f"Path has been modified with respect to '{base_branch}'\n"
                f"Excluding paths: {exclude_path}"
            )
            print(f"Return code: {err.returncode}")
            print(f"Output: {err.output}")
        return 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Check if a branch has modified" "anything excluding some path/dir"
    )
    parser.add_argument(
        "-b", "--base-branch", default="main", help="Base branch to compare against"
    )
    parser.add_argument(
        "-e",
        "--exclude-path",
        default=["doc"],
        nargs="+",
        help="Path to exclude from git diff." "Can be used multiple times eg: -e p1 p2",
    )
    parser.add_argument("--debug", action="store_true", help="Print debug info")

    args = parser.parse_args()
    returncode = check_modified(args.base_branch, args.exclude_path, debug=args.debug)
    sys.exit(returncode)
