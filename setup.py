from setuptools import find_packages, setup
import os
import shutil
import sys
from eyetracker import __version__

packages = find_packages()

# def install_simplecv():
#     """ Installs the newest version of SimpleCV from Github """
#     print("Installing the newest version of SimpleCV")
#     simplecv_zip = "https://github.com/sightmachine/SimpleCV/archive/master.zip"
#     import urllib
#     import zipfile
#     urllib.urlretrieve(simplecv_zip, "simplecv130.zip")
#     path = os.getcwd() + "/SimpleCV-master"
#     with zipfile.ZipFile("simplecv130.zip", 'r') as myzip:
#         myzip.extractall()
#     olddir = os.getcwd()
#     os.chdir(path)
#     os.system("python setup.py install")
#     os.chdir(olddir)
#     try:
#         os.remove("simplecv130.zip")
#         shutil.rmtree(path, ignore_errors=False, onerror=handleRemoveReadonly)
#     except Exception as e:
#         print("Couldn't delete temporary files:", type(e), e)
#
# def handleRemoveReadonly(func, path, exc):
#     excvalue = exc[1]
#     if func in (os.rmdir, os.remove) and excvalue.errno == errno.EACCES:
#         os.chmod(path, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)  # 0777
#         func(path)
#     else:
#         raise
#
# install_simplecv()

setup(name="eyetracker",
      version=__version__,
      description="AIBS Eyetracker Package",
      author="derricw",
      author_email="derricw@alleninstitute.org",
      url="http://stash.corp.alleninstitute.org/projects/ENG/repos/eyetracker/browse",
      packages=packages,
      requires=[], #['cv2', 'numpy', 'pyqtgraph', 'PyQt4', 'SimpleCV'],
      include_package_data=True,
      package_data={
          "": ['*.png', '*.ico', '*.jpeg', '*.jpg' '*.ui'],
      },
      scripts=['post_install.py']
      )
