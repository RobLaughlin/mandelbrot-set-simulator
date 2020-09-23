import os
from distutils.dir_util import copy_tree, remove_tree
from shutil import copyfile

if not os.path.exists('build') or not os.path.isdir('build'):
    os.mkdir('build')

copy_tree('img', 'build/img')
copy_tree('Modules', 'build/Modules')
copy_tree('AppConfig', 'build/Appconfig')
copyfile('config.json', 'build/config.json')

os.system('pyinstaller --onefile main.py')
copyfile('dist/main.exe', 'build/main.exe')
remove_tree('dist')
os.remove('main.spec')
