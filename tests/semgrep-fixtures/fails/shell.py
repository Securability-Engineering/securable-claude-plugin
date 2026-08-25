import subprocess


def convert(filename):
    subprocess.run("convert " + filename + " out.png", shell=True)
