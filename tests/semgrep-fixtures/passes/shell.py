import subprocess


def convert(filename):
    subprocess.run(["convert", filename, "out.png"], check=True)


def list_tmp():
    subprocess.run("ls -la /tmp", shell=True)
