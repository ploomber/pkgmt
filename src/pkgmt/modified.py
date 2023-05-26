import subprocess

def check_modified(base_branch, exclude_path, debug=False):
    # https://stackoverflow.com/questions/4380945
    cmd = f"git diff --exit-code {base_branch}... -- ."

    for path in exclude_path:
        cmd += f" :^{path}"

    if debug:
        print(f'cmd: {cmd}')
    try:
        subprocess.check_output(cmd, shell=True)
        return 0
    except subprocess.CalledProcessError as err:
        if debug:
            print(f"Path has been modified with respect to '{base_branch}'\n"
                  f"Excluding paths: {exclude_path}")
            print(f"Return code: {err.returncode}")
            print(f"Output: {err.output}")
        return 1