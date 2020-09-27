import os
from distutils.dir_util import copy_tree, remove_tree
from shutil import copyfile

if not os.path.exists('build') or not os.path.isdir('build'):
    os.mkdir('build')

try:
    copy_tree('img', 'build/img')
    copy_tree('Modules', 'build/Modules')
    copyfile('config.json', 'build/config.json')

    os.system('pyinstaller --onefile app.py')

    copyfile('dist/app.exe', 'build/app.exe')
    remove_tree('dist')
    remove_tree('build/app')
    os.remove('app.spec')
except:
    pass
