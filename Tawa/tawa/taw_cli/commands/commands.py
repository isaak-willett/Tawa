import subprocess


def lint():
    subprocess.run("ruff check .", shell=True, check=True)

def format():
    subprocess.run("black .", shell=True, check=True)
