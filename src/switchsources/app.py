import os
import subprocess

import inquirer
import typer
from rich import print
from rich.table import Table

import switchsources.switcher as switcher
from switchsources.config import Config

app = typer.Typer()

current_script_path = os.path.realpath(__file__)
current_dir = os.path.dirname(current_script_path)
config_path = os.path.join(current_dir, '../../config.json')

config = Config(config_path).get_config()


def run_command(command):
    return subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


@app.command()
def ls():
    soft_worms = Table(show_header=False, show_lines=True)
    for k, v in enumerate(config):
        soft_worms.add_row(v)
    print(soft_worms)


@app.command()
def show(name: str):
    soft_worms = Table(show_header=False, header_style='bold', show_lines=True)
    sources = config[name]
    for v in sources:
        soft_worms.add_row(v)
    print(soft_worms)


@app.command()
def switch(name: str):
    cur_switcher = switcher.switcher_factory(name)
    sources = config[name]
    questions = [
        inquirer.List('source',
                      message="Select Source",
                      choices=sources,
                      carousel=True
                      ),
    ]
    answers = inquirer.prompt(questions)
    cur_switcher.switch(answers['source'])


@app.command()
def check(name: str):
    cur_switcher = switcher.switcher_factory(name)
    res = cur_switcher.check()
    print(res)


@app.command()
def recover(name: str):
    cur_switcher = switcher.switcher_factory(name)
    res = cur_switcher.recover()
    print(res)


def main():
    app()


if __name__ == '__main__':
    main()
