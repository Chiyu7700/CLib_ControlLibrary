<div align="center">
<h1 align="center">Clib Control Library</h1>
<p align="center">
  <a href="https://www.autodesk.com/products/maya/overview"><img src="https://img.shields.io/badge/Maya-2024-blue?logo=autodesk&logoColor=white" ></a>
  <a href="https://www.autodesk.com/products/maya/overview"><img src="https://img.shields.io/badge/Maya-2025-blue?logo=autodesk&logoColor=white" alt="Maya2025"></a>
  <a href="https://pypi.org/project/PySide6/"><img src="https://img.shields.io/badge/PySide-Qt%20for%20Python-green?logo=qt&logoColor=whitee" alt="PySide"></a>
  <a href="https://www.jetbrains.com/pycharm/"><img src="https://img.shields.io/badge/Built%20with-PyCharm-yellow?logo=jetbrains&logoColor=white" alt="PyCharm"></a>
</p>
<br>
  
<h3>Installation</h3>


-----

Copy the 📁`Clib` folder (either in the maya2024 or maya 2025 folders depending on the maya version you're using) to your Documents/maya/scripts directory

After copying, your folder structure should look like this:  
`Documents/maya/scripts/CLib/`

then launch Maya and drag and drop the `clib_shelf_installer.py` file to your maya viewport
Enjoy


-----

### Table of Contents
* [About](#About)
* [Instructions](#Instructions)


-----

### About

My main objeective was to create a tool that could help streamline the control/curve creation process when rigging in Maya. I tried my best to tailor the UI design and functionality of the tool towards simplicity and ease of use.


</div>

>  [!Note]
> My underlying goal with this tool was to further learn and practice Python and UI design in PySide2 and QT, I'm quite certain not everything is perfect but I'm really happy with how its turned out, . I developed it primarily in Maya 2024 and PySide2 although I have tried to make a Maya 2025, Pyside6 version, I noticed a few of the visual elements dont appear as intended but the difference is negligible.
> 
. 
---
<div align="center">
  
### Instructions

I've done my best to make sure the tool itself feels pretty intuitive but if anything is confusing please don't hesitate to refer to the explained features below:


![image](https://github.com/user-attachments/assets/99d2c77a-4377-4638-b665-d70ca38cb412)

CLib comes with 18 preset Curves, these and all user created curves are displayed on the left hand side of the tool while the panel on the right has menus for curve customization.

The panel on the right includes 2 menus, the first and default menu where most visuals of the stored curves can be customized before being created, and the second attribute menu where you can specify the name of the control before you create it and specify whether you'd like it to be created with
an offset/NPO group above it.

You can alternate between the two menus using the buttons at the two buttons at the top
![CLib_Swapmenus](https://github.com/user-attachments/assets/6e73ac19-9971-4d49-b5f8-6157f9b8992c)




