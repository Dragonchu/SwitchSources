import abc
import subprocess
from rich import print


class BaseSwitcher(abc.ABC):
    def __init__(self, name):
        self.name = name

    @abc.abstractmethod
    def check(self):
        pass

    @abc.abstractmethod
    def switch(self):
        pass

    @abc.abstractmethod
    def recover(self):
        pass

class PipSwitcher(BaseSwitcher):
    def check(self):
        return subprocess.run("pip config get global.index-url", shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    def switch(self, source: str):
        try:
            subprocess.run(f"pip config set global.index-url {source}", shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            print(f"Switched to {source}")
        except subprocess.CalledProcessError:
            print(f"Failed to switch to {source}")

    def recover(self):
        return subprocess.run("pip config unset global.index-url", shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

def switcher_factory(name):
    if name == 'pip':
        return PipSwitcher(name)
    # 添加更多的if条件来处理其他的工具
    else:
        raise ValueError(f"Unknown switcher: {name}")