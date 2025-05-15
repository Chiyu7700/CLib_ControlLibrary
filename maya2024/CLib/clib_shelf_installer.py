import maya.cmds as cmds
import maya.mel as mel
import os
import sys

scripts_dir = os.path.expanduser('~/maya/scripts')

if scripts_dir not in sys.path:
    sys.path.append(scripts_dir)

def install_clib_shelf_button():
    shelf_name = "Custom"
    shelf_tab = mel.eval('$gShelfTopLevel=$gShelfTopLevel') 
    label = "CLib"
    SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
    icon_dir = os.path.join(SCRIPT_DIR, "icons")
    icon_name = os.path.join(icon_dir, "logo.png")
    script = '''import CLib.main as CLib
from importlib import reload
reload(CLib)
CLib'''

    if not cmds.shelfLayout(shelf_name, exists=True):
        mel.eval(f'addNewShelfTab "{shelf_name}"')

    cmds.setParent(shelf_name)
    cmds.shelfButton(
        label="CLib",
        annotation="Launch CLib Control Studio",
        image=icon_name,
        imageOverlayLabel="CLib",
        overlayLabelColor=(1, 1, 1),  # White label text
        overlayLabelBackColor=(0, 0, 0, 0.5),
        command=script,
        sourceType="python"
    )

    print(f"[CLib Installer] Shelf button added to '{shelf_name}' shelf.")

    cmds.tabLayout(shelf_tab, edit=True, selectTab=shelf_name)

def onMayaDroppedPythonFile(*args):
    print('old me')
    install_clib_shelf_button()
