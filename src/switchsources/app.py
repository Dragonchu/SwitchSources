import json
import subprocess
import os
import typer
from rich import print
from rich.table import Table


def run_command(command):
    return subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

def switch_sources():
    return run_command('pip --version')

def main():
    # 获取当前脚本文件的绝对路径
    current_script_path = os.path.realpath(__file__)
    # 获取当前脚本所在目录
    current_dir = os.path.dirname(current_script_path)
    # 构建config.json的绝对路径
    config_path = os.path.join(current_dir, '../../config.json')

    # 确保路径正确
    print(f"Trying to load config from: {config_path}")
    
    # 使用绝对路径读取config.json
    with open(config_path, 'r') as config_file:
        config = json.load(config_file)
        cur_os = config['mac']
        for v in cur_os:
            print(f"{v}")
        software = cur_os['pip']
        switch_command = software['switch']['sh']
        source = software['switch']['sources'][0]
        print(f"Switching sources to {source}")
        result = run_command(switch_command+' '+source)
        print(result.stdout.decode('utf-8'))


app = typer.Typer()

@app.command()
def list():
    current_script_path = os.path.realpath(__file__)
    current_dir = os.path.dirname(current_script_path)
    config_path = os.path.join(current_dir, '../../config.json')
    soft_worms = []
    soft_worms = Table(show_header=False, header_style='bold',show_lines=True)
    with open(config_path, 'r') as config_file:
        config = json.load(config_file)
        cur_os = config['mac']
        for v in cur_os:
            soft_worms.add_row(v)
    print(soft_worms)

@app.command()
def show(name: str):
    current_script_path = os.path.realpath(__file__)
    current_dir = os.path.dirname(current_script_path)
    config_path = os.path.join(current_dir, '../../config.json')
    soft_worms = []
    soft_worms = Table(show_header=False, header_style='bold',show_lines=True)
    with open(config_path, 'r') as config_file:
        config = json.load(config_file)
        cur_os = config['mac']
        software = cur_os[name]["switch"]["sources"]
        for v in software:
            soft_worms.add_row(v)
    print(soft_worms)

if __name__ == '__main__':
    app()