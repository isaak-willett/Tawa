import subprocess

def pull_version_from_pyproject():
    proc_output = subprocess.run("grep -Rnw Tawa/pyproject.toml -e 'version'", shell=True, capture_output=True)
    # drop new line chats at end, split on " char
    stdout = str(proc_output.stdout)[:-3]
    # breaks up to three pieces because two " chars, take val at idx 1
    pieces = stdout.split('"')
    return pieces[1]
