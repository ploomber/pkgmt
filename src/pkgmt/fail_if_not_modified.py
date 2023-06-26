import subprocess
import argparse
import sys


def check_modified(base_branch, include_path, debug=False):
    # https://stackoverflow.com/questions/4380945
    cmd = f"git diff --exit-code {base_branch}... -- "

    for path in include_path:
        try:
            subprocess.check_output(cmd + path, shell=True)
            if debug:
                print(f"{path} has not been modified with respect to '{base_branch}'")
            return 1
        except subprocess.CalledProcessError:
            pass
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Check if a branch has modified" "anything excluding some path/dir"
    )
    parser.add_argument(
        "-b", "--base-branch", default="main", help="Base branch to compare against"
    )
    parser.add_argument(
        "-i",
        "--include-path",
        default=["CHANGELOG.md"],
        nargs="+",
        help="Path to include in git diff. "
        "Will fail if anyone of the path is not modified."
        "Can be used multiple times eg: -i p1 p2",
    )
    parser.add_argument("--debug", action="store_true", help="Print debug info")

    args = parser.parse_args()
    returncode = check_modified(args.base_branch, args.include_path, debug=args.debug)
    sys.exit(returncode)
