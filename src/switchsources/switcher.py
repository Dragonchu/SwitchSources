import abc
import subprocess
import os
from rich import print
import xml.etree.ElementTree as ET
import re
import shutil

def switcher_factory(name):
    if name == 'pip':
        return PipSwitcher(name)
    # 添加更多的if条件来处理其他的工具
    elif name == 'maven':
        return MavenSwitcher(name)
    else:
        raise ValueError(f"Unknown switcher: {name}")

class BaseSwitcher(abc.ABC):
    def __init__(self, name):
        self.name = name

    @abc.abstractmethod
    def check(self) -> str:
        pass

    @abc.abstractmethod
    def switch(self):
        pass

    @abc.abstractmethod
    def recover(self) -> str:
        pass

class PipSwitcher(BaseSwitcher):
    def check(self) -> str:
        return subprocess.run("pip config get global.index-url", shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout.decode('utf-8')

    def switch(self, source: str):
        try:
            subprocess.run(f"pip config set global.index-url {source}", shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            print(f"Switched to {source}")
        except subprocess.CalledProcessError:
            print(f"Failed to switch to {source}")

    def recover(self) -> str:
        return subprocess.run("pip config unset global.index-url", shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout.decode('utf-8')

class MavenSwitcher(BaseSwitcher):
    def __init__(self, name):
        super().__init__(name)
        self.mirror_id = 'switchsources-mirror'

    def check(self) -> str:
        path = self._get_maven_settings_path()
        print(path)
        return self._check_maven_repository(path)
    
    def switch(self, source: str):
        path = self._get_maven_settings_path()
        self._change_maven_repository(path, source)
        print(f"Switched to {source}")
    
    def recover(self) -> str:
        path = self._get_maven_settings_path()
        self._del_maven_repository(path)
        return "Recovered to default maven repository"
    
    def _check_maven_repository(self, settings_file):
        tree = ET.parse(settings_file)
        root = tree.getroot()
        mirrors = root.find('mirrors')
        if mirrors is None:
            return None
        for mirror in mirrors:
            if mirror.find('id').text == self.mirror_id:
                return mirror.find('url').text
        return None

    def _del_maven_repository(self, settings_file):
        tree = ET.parse(settings_file)
        root = tree.getroot()
        mirrors = root.find('mirrors')
        if mirrors is None:
            return
        for mirror in mirrors:
            if mirror.find('id').text == self.mirror_id:
                mirrors.remove(mirror)
        tree.write(settings_file, encoding='utf-8')

    def _get_maven_settings_path(self):
        home_dir = os.path.expanduser("~")
        return os.path.join(home_dir, ".m2", "settings.xml")

    def _change_maven_repository(self, settings_file, new_mirror_url):
        if not os.path.exists(settings_file):
            self._create_new_mvn_settings()
        # 解析XML文件
        tree = ET.parse(settings_file)
        root = tree.getroot()

        # 找到mirrors标签
        mirrors = root.find('mirrors')

        # 如果mirrors标签不存在，创建一个
        if mirrors is None:
            mirrors = ET.SubElement(root, 'mirrors')

        # 创建新的mirror标签
        mirror = ET.SubElement(mirrors, 'mirror')
        ET.SubElement(mirror, 'id').text = self.mirror_id
        ET.SubElement(mirror, 'url').text = new_mirror_url
        ET.SubElement(mirror, 'mirrorOf').text = '*'

        # 保存修改后的XML文件
        tree.write(settings_file, encoding='utf-8')

    def _get_mvn_install_location(self):
        output = subprocess.check_output(['mvn', '-v']).decode('utf-8')
        match = re.search(r'Maven home: (.*)', output)
        if match:
            return match.group(1)
        else:
            return None
    
    def _create_new_mvn_settings(self):
        mvn_home = self._get_mvn_install_location()
        src = os.path.join(mvn_home, 'conf', 'settings.xml')
        dest = self._get_maven_settings_path()
        shutil.copy2(src, dest)
