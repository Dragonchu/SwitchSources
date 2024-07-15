import subprocess
import time

import inquirer
import requests
import typer
from rich import print
from rich.console import Console
from ping3 import ping
from rich.table import Table
from rich.text import Text

import switchsources.switcher as switcher
from switchsources.config import source_config

app = typer.Typer()


def run_command(command):
    return subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


@app.command()
def ls():
    soft_worms = Table(show_header=False, show_lines=True)
    for k, v in enumerate(source_config.get_config()):
        soft_worms.add_row(v)
    print(soft_worms)


@app.command()
def show(name: str):
    soft_worms = Table(show_header=False, header_style='bold', show_lines=True)
    sources = source_config.get_config()[name]
    for v in sources:
        soft_worms.add_row(v)
    print(soft_worms)


@app.command()
def switch(name: str):
    cur_switcher = switcher.switcher_factory(name)
    sources = source_config.get_config()[name]
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


@app.command()
def add(name: str, source: str):
    if name not in source_config.get_config():
        source_config.get_config()[name] = []
    source_config.get_config()[name].append(source)
    print(source_config.get_config())
    source_config.save_config()


@app.command()
def remove(name: str):
    del source_config.get_config()[name]
    source_config.save_config()


@app.command()
def rs(name: str):
    sources = source_config.get_config()
    questions = [
        inquirer.List('source',
                      message="Select Source",
                      choices=sources[name],
                      carousel=True
                      ),
    ]
    answers = inquirer.prompt(questions)
    source_config.get_config()[name].remove(answers['source'])
    source_config.save_config()


@app.command()
def speed(name: str):
    sources = source_config.get_config()[name]
    console = Console()
    table = Table(title="URL Latency Test Result")
    table.add_column("Host", justify="left", style="cyan", no_wrap=True)
    table.add_column("Latency (s)", justify="right", style="green")
    for source in sources:
        try:
            # Send a ping request to the host
            latency = ping(source)
            if latency is not None:
                # Display the result in a friendly format
                table.add_row(source, f"{latency:.4f}")
            else:
                # Handle unreachable host
                error_text = Text(f"Failed to reach {source}: Host is unreachable", style="bold red")
                console.print(error_text)
        except Exception as e:
            # Handle any exceptions (e.g., invalid host)
            error_text = Text(f"An error occurred: {str(e)}", style="bold red")
            console.print(error_text)
    console.print(table)


def main():
    app()


if __name__ == '__main__':
    main()
