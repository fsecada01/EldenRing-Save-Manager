import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path

# main variables, directories and settings
_main_dir = Path(os.environ.get("BASE_DIRECTORY"))
config_path = (_main_dir / "data/config.json").resolve()
save_dir = (_main_dir / "data/save-files/").resolve()
app_title = "Elden Ring Save Manager"
backupdir = (_main_dir / "data/backup/").resolve()
update_dir = (_main_dir / "data/updates/").resolve()
temp_dir = (_main_dir / "data/temp/").resolve()
post_update_file = (_main_dir / "data/post.update").resolve()
version = "v1.73"
v_num = 1.73  # Used for checking version for update
video_url = "https://youtu.be/LQxmFuq3dfg"
custom_search_tutorial_url = "https://youtu.be/li-ZiMXBmRk"
background_img = (_main_dir / "data/background.png").resolve()
icon_file = (_main_dir / "data/icon.ico").resolve()
bk_p = (-140, 20)  # Background image position
is_windows = any(platform.win32_ver()) or hasattr(sys, "getwindowsversion")


def open_folder_standard_explorer(path):
    """Note: os.startfile is only available on Win platform"""
    if platform.system() == "Windows":
        os.startfile(path.replace("/", "\\"))
    else:
        subprocess.Popen(["xdg-open", path])


def open_textfile_in_editor(path):
    if is_windows:
        subprocess.run(
            f"notepad {path}", shell=True, capture_output=True, text=True
        )
    else:
        subprocess.Popen(["xdg-open", path])


def force_close_process(process):
    if is_windows:
        comm = f"taskkill /IM {process} -F"
        subprocess.run(comm, shell=True, capture_output=True, text=True)
    else:
        comm = f"pkill {process}"
        os.system(comm)


def copy_folder(src, dest):
    """
    if is_windows: command = f"Xcopy {src} {dest} /E /H /C /I /Y".format(
    gamedir,saved,lst_box_choice) subprocess.run(comm, shell=True ,
    capture_output=True, text=True) else: shutil.copytree(src, dest,
    dirs_exist_ok=True)
    """
    shutil.copytree(src, dest, dirs_exist_ok=True)


def copy_file(src, dst):
    shutil.copy(src, dst)


def delete_folder(folder):
    if folder is None or not isinstance(folder, str) or len(folder) < 5:
        raise Exception("UNSAFE FOLDER DELETE OPERATION. QUIT")
    shutil.rmtree(folder)
