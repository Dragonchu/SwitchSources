import json
import subprocess
import os
import typer
from rich import print
from rich.table import Table
from config import Config
import inquirer
import platform

app = typer.Typer()


current_script_path = os.path.realpath(__file__)
current_dir = os.path.dirname(current_script_path)
config_path = os.path.join(current_dir, '../../config.json')

config = Config(config_path)
cur_platform = platform.system()
cur_platform_config = config.get_config(cur_platform)


def run_command(command):
    return subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


@app.command()
def list():
    soft_worms = []
    soft_worms = Table(show_header=False, show_lines=True)
    for v in cur_platform_config:
        soft_worms.add_row(v)
    print(soft_worms)


@app.command()
def show(name: str):
    soft_worms = []
    soft_worms = Table(show_header=False, header_style='bold',show_lines=True)
    software = cur_platform_config[name]["switch"]["sources"]
    for v in software:
        soft_worms.add_row(v)
    print(soft_worms)

@app.command()
def switch(name: str):
    command = cur_platform_config[name]["switch"]["sh"]
    sources = cur_platform_config[name]["switch"]["sources"]
    questions = [
        inquirer.List('source',
                      message="Select Source",
                      choices=sources,
                      carousel=True
                  ),
    ]
    answers = inquirer.prompt(questions)
    res = run_command(f"{command} {answers['source']}")
    print(res.stdout.decode('utf-8'))
    print(f"Switched to {answers['source']}")


@app.command()
def check(name: str):
    command = cur_platform_config[name]["check"]["sh"]
    res = run_command(f"{command}")
    print(res.stdout.decode('utf-8'))

@app.command()
def recover(name: str):
    command = cur_platform_config[name]["recover"]["sh"]
    res = run_command(f"{command}")
    print(res.stdout.decode('utf-8'))

if __name__ == '__main__':
    app()