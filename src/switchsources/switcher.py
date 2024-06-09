import abc
import os
import re
import shutil
import subprocess
import xml.etree.ElementTree as ET

from rich import print


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
    def switch(self, source: str):
        pass

    @abc.abstractmethod
    def recover(self) -> str:
        pass


class PipSwitcher(BaseSwitcher):
    def check(self) -> str:
        return subprocess.run("pip config get global.index-url", shell=True, check=True, stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE).stdout.decode('utf-8')

    def switch(self, source: str):
        try:
            subprocess.run(f"pip config set global.index-url {source}", shell=True, check=True, stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE)
            print(f"Switched to {source}")
        except subprocess.CalledProcessError:
            print(f"Failed to switch to {source}")

    def recover(self) -> str:
        return subprocess.run("pip config unset global.index-url", shell=True, check=True, stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE).stdout.decode('utf-8')


def _get_maven_settings_path():
    home_dir = os.path.expanduser("~")
    return os.path.join(home_dir, ".m2", "settings.xml")


def _get_mvn_install_location():
    output = subprocess.check_output(['mvn', '-v']).decode('utf-8')
    match = re.search(r'Maven home: (.*)', output)
    if match:
        return match.group(1)
    else:
        return None


def _create_new_mvn_settings():
    mvn_home = _get_mvn_install_location()
    src = os.path.join(mvn_home, 'conf', 'settings.xml')
    print('mvn src settings.xml:', src)
    dest = _get_maven_settings_path()
    print('mvn dest settings.xml: ', dest)
    shutil.copy2(src, dest)


class MavenSwitcher(BaseSwitcher):
    def __init__(self, name):
        super().__init__(name)
        self.mirror_id = 'switchsources-mirror'
        self.namespace = {'mvn': 'http://maven.apache.org/SETTINGS/1.2.0'}
        ET.register_namespace('', "http://maven.apache.org/SETTINGS/1.2.0")
        ET.register_namespace('xsi', "http://www.w3.org/2001/XMLSchema-instance")
        ET.register_namespace('schemaLocation',
                              "http://maven.apache.org/SETTINGS/1.2.0 http://maven.apache.org/xsd/settings-1.2.0.xsd")

    def check(self) -> str:
        path = _get_maven_settings_path()
        print(path)
        return self._check_maven_repository(path)

    def switch(self, source: str):
        path = _get_maven_settings_path()
        self._change_maven_repository(path, source)
        print(f"Switched to {source}")

    def recover(self) -> str:
        path = _get_maven_settings_path()
        self._del_maven_repository(path)
        return "Recovered to default maven repository"

    def _check_maven_repository(self, settings_file):
        tree = ET.parse(settings_file)
        root = tree.getroot()
        mirrors = root.find('mvn:mirrors', namespaces=self.namespace)
        if mirrors is None:
            return None
        for mirror in mirrors:
            if mirror.find('mvn:id', namespaces=self.namespace).text == self.mirror_id:
                return mirror.find('mvn:url', namespaces=self.namespace).text
        return None

    def _del_maven_repository(self, settings_file):
        tree = ET.parse(settings_file)
        root = tree.getroot()
        mirrors = root.find('mvn:mirrors', namespaces=self.namespace)
        if mirrors is None:
            return
        for mirror in mirrors:
            if mirror.find('id').text == self.mirror_id:
                mirrors.remove(mirror)
        tree.write(settings_file)

    def _change_maven_repository(self, settings_file, new_mirror_url):
        if not os.path.exists(settings_file):
            print("settings.xml not found, creating a new one")
            _create_new_mvn_settings()
        # 解析XML文件
        tree = ET.parse(settings_file)
        root = tree.getroot()

        # 找到mirrors标签
        mirrors = root.find('mvn:mirrors', namespaces=self.namespace)

        # 如果mirrors标签不存在，创建一个
        if mirrors is None:
            print("mirrors tag is missing, creating a new one")
            mirrors = ET.SubElement(root, 'mirrors')

        # 创建新的mirror标签
        mirror = ET.SubElement(mirrors, 'mirror')
        ET.SubElement(mirror, 'id').text = self.mirror_id
        ET.SubElement(mirror, 'url').text = new_mirror_url
        ET.SubElement(mirror, 'mirrorOf').text = '*'

        # 保存修改后的XML文件
        tree.write(settings_file, encoding='utf-8')
