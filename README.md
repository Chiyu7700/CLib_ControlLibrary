<h1 align="center">Clib Control Library</h1>
<p align="center">
  <a href="https://www.autodesk.com/products/maya/overview"><img src="https://img.shields.io/badge/Maya-2024-blue?logo=autodesk&logoColor=white" ></a>
  <a href="https://www.autodesk.com/products/maya/overview"><img src="https://img.shields.io/badge/Maya-2025-blue?logo=autodesk&logoColor=white" alt="Maya2025"></a>
  <a href="https://www.autodesk.com/products/maya/overview"><img src="https://img.shields.io/badge/Maya-2027-blue?logo=autodesk&logoColor=white" alt="Maya2027"></a>
  <a href="https://pypi.org/project/PySide6/"><img src="https://img.shields.io/badge/PySide-Qt%20for%20Python-green?logo=qt&logoColor=white" alt="PySide"></a>
  <a href="https://www.jetbrains.com/pycharm/"><img src="https://img.shields.io/badge/Built%20with-PyCharm-yellow?logo=jetbrains&logoColor=white" alt="PyCharm"></a>
</p>
<br>
  
<h2>Installation</h2>

-----

Copy the 📁`Clib` folder (either in the maya2024 or maya2025 folders depending on the maya version you're using) to your 
<br> 📁`Documents/maya/scripts` directory

After copying, your folder structure should look like this:  
`Documents/maya/scripts/CLib/`

In Maya drag and drop the `clib_shelf_installer.py` file to your maya viewport.
Enjoy
>  [!Note]
> If for some reason it doesnt run after this you may have to restart Maya after installing but I've tried to make it work without users having to do so.
>
> The maya2025 version should also work in anything newer than 2025, I've tested it in Maya 2027 and it runs fine, haven't had the chance to test 2026 yet but there's no reason it shouldn't

-----

### Table of Contents
* [About](#about)
* [Instructions](#instructions)
* [Planned_Features](#planned_features)
* [Thanks](#thanks)


-----

### About

My main objective was to create a tool that could help streamline the control/curve creation process when rigging in Maya. I tried my best to tailor the UI design and functionality of the tool towards simplicity and ease of use.



>  [!Note]
> My underlying goal with this tool was to further learn and practice Python and UI design in PySide2 and QT, I'm quite certain not everything is perfect but I'm really happy with how its turned out. I developed it primarily in Maya 2024 and PySide2 although I have tried to make a Maya 2025, Pyside6 version.
>
> I came back to it in November 2026 because while rigging my Woodboy character I kept wishing it could do a few more things, so now it can replace and recolor controls you've already built, stored curves finally get their own icons instead of the default one and you can rename them. I also fixed the visual elements that weren't showing up properly in the Pyside6 version and added a few new shapes from the Woodboy rig
> 
. 
---
  
### Instructions

I've done my best to make sure the tool itself feels pretty intuitive but if anything is confusing please don't hesitate to refer to the explained features below:

<br>

* UI Overview
 
  
> CLib comes with 21 preset Curves, these and all user created curves are displayed on the left hand side of the tool while the panel on the right has menus for curve customization. The panel on the right includes 2 menus, the first and default menu where most visuals of the stored curves can be customized before being created, and the second attribute menu where you can specify the name of the control before you create it and specify whether you'd like it to be created with
an offset/NPO group above it.

![image](https://github.com/user-attachments/assets/99d2c77a-4377-4638-b665-d70ca38cb412)

> 
. 

<br>

* Menu Navigation Buttons
 
  
> You can alternate between the two menus using the buttons at the top of the right Panel
> > 
. 
![CLib_Swapmenus](https://github.com/user-attachments/assets/6e73ac19-9971-4d49-b5f8-6157f9b8992c)

<br>

* Storing, Renaming and Deleting Controls
 
  
> Select a control you want to save and click *Store Control* , it'll even draw its own little icon from the curve now. To rename or delete a stored Control simply right click on it and click Rename or Delete
> > 
. 
![storing control](https://github.com/user-attachments/assets/130e56e5-e25c-46c1-8b0d-540861359f01)

<br>

* Recreating the Curve
 
 
> Typically the curve is created at the location of a selected object. If no object is selected the Curve is created at world origin (0, 0 , 0)
> > 
. 
![creating_control](https://github.com/user-attachments/assets/0e2a6723-b05f-4145-8ebc-1a100d2add3c)

<br>

* Primary Axis option
 
 
> You may have cases where the primary axis of your joints for example is the X-axis and the control is being oriented in an undesirable direction you can try using this option to adjust it
> > 
. 
![CLib_axis](https://github.com/user-attachments/assets/d6842b9d-5ae9-4044-9183-d89b6b65ac00)

<br>

* Replace Shape
 
 
> If you've already built a Control and decide it should be a different shape you can simply select it (or a bunch of them) and Ctrl+Click the shape you want in the library, or right click the shape and click *Replace Shape on Selected*. It only swaps out the curve so anything on the control itself like keys or constraints stays as it is, and it keeps its color and line width too. The new shape will use whatever scale and primary axis you currently have set, just note that anything connected directly to the old shape node won't carry over
> > 
. 
![CLib_Replace_Shape](https://github.com/user-attachments/assets/e8179993-d44b-4e2c-b8ce-ce33840b3005)


<br>

* Recolor
 
 
> Select the controls you want to recolor and click one of the preset colors (or pick a custom one) and they'll all change at once. If nothing is selected it just sets the color for the next Control you create
> > 
. 
![CLib_Recolor]("https://github.com/user-attachments/assets/064c46aa-aaed-48a4-991a-1d68f38d3bdb)


<br>

-----

### Planned_Features

more than just a Library I'd love this tool to be a Studio of some sorts, with ease of access to many control and curve creation/manipulation features while also keeping in mind UI real-estate. Currently my planned features are:

* ~~Auto-generated icons for custom curves~~
> ~~Automatically create icons for shapes users save instead of simply resorting to a default icon~~

* Overall improvements to the UI
> Polishing up the control layout, and overall improved scaling on different resolutions

* Control Filtering
> Enable users to save and filter curves by tags

* Automatic/smart hierarchy parenting of control curves
> More rig-aware control creation that will detect existing joint hierarchy and control relationships to parent created controls under the appropriate existing controls(if any).

* ~~Batch recolor of existing curves~~
> ~~Enable users to change color of an existing or multiple existing curves with the click of a button~~

* Mirror controls across axis
>Enable users to mirror control shapes across a specified axis

<br>

-----

### Thanks
A special thanks to you for reading this far down and giving this tool a go. If you run into any issues or have any suggestion please dont hesitate to reach out to me on LinkedIn or open an issue here on GitHub

