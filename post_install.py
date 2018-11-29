import importlib
import os
from win32com.client import Dispatch
import sys
import time


dependency_folder = r"\\aibsdata\mpe\_Projects\EyeTracking\Software\dependencies"
dependency_list = {
    'cv2': "opencv-python-2.4.9.win-amd64-py2.7.exe",
    'PIL': "",
    'numpy': "",
    'pymba': "",
    'pyqtgraph': "pyqtgraph-0.9.8.win-amd64.exe",
    'PyQt4': "",
    }


def check_dependencies(dependency_list):
    for dp, location in dependency_list.iteritems():
        try:
            print("Checking:", dp)
            i = importlib.import_module(dp)
        except Exception as e:
            print "Couldn't import %s: %s" % (dp, e)
            if location:
                print "Attempting to install %s" % dp
                path = os.path.join(dependency_folder, dependency_list[dp])
                try:
                    os.system(path)
                except Exception as e:
                    print "Couldn't install %s: %s" % (dp, e)


def create_shortcut(source, icon):
    import getpass
    user = getpass.getuser()
    #userhome = os.path.expanduser('~')
    #desktop = os.path.join(userhome, 'Desktop')
    desktop = "C:/Users/%s/Desktop" % user
    wdir = os.path.dirname(source)
    filename = os.path.basename(source).split('.')[0]+".lnk"
    path = os.path.join(desktop, filename)

    shell = Dispatch("WScript.Shell")
    shortcut = shell.CreateShortCut(path)
    shortcut.Targetpath = source
    shortcut.WorkingDirectory = wdir
    shortcut.IconLocation = icon
    shortcut.save()

if __name__ == '__main__':

    import site

    try:
        [sitepackages] = [dirname for dirname in site.getsitepackages() if
                          "site-packages" in dirname]
        package_path = os.path.join(sitepackages, "eyetracker")

        #Create gui shortcut
        gui_path = os.path.join(package_path,
                                "eyetrackergui.py")
        icon_path = os.path.join(os.path.dirname(gui_path),
                                 "res/eye.ico")
        create_shortcut(gui_path, icon_path)

        #check dependencies
        check_dependencies(dependency_list)
    except Exception, e:
        print "Post-install script failed:", e
        time.sleep(10)