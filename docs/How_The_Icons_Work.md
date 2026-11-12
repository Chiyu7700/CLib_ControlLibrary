# How CLib Draws Its Own Icons

> "Would be cool to see if there's a way you can draw the shapes directly with QT and render them at runtime. Then you can also create icons for custom shapes too."
>
> Justin Pedersen - 2025

That comment from Justin ( cool dude ) set me down a long train of thought.

## The Key Problem

>Users need custom icons for their custom shapes. An icon is typically a 2D, 100x100 image ( think two axes, like X and Y) but the curve exists in 3D space ( think three axes, X, Y and Z). To turn it into a 2D icon I need to project the 3D shape onto two axes and ignore the third one.

But it won't always be the same two axes. For example if a circle is flat on the ground, all its points have a Y value of 0. If I use X and Z I get the correct shape, but if I used X and Y every point would end up at the same height and I'd get a flat straight line.

![Keeping X and Y vs keeping X and Z](https://github.com/user-attachments/assets/b8d1681f-67f2-4dfe-941c-f67bb84e030d)

So to avoid this, the code first checks which axis the shape is thinnest on and uses the other two to create the icon. ( It sounds simple but I'm proud of it) This lets it handle curves in different orientations instead of trying to make everything work from one fixed camera.

## Sampling The Curve

The CVs of a curve like the circle don't actually sit on the curve itself. So to get the real shape the code samples the curve, picking points directly off it with `pointOnCurve`.

![Just the CVs vs sampled along the curve](Images/Icons_02_Cage_Vs_Curve.png)

For linear curves things are simpler because they're made up of straight lines between CVs, so one point per CV is enough.

For curved shapes the code takes 12 points per span. Since the final icon is only 100 pixels that's enough detail to make the curve look smooth without making the process unnecessarily heavy.

It also takes one extra point so the sampling includes the very end of the curve, otherwise closed shapes would have a little gap in the icon where the line should join up.

## Is It Actually Flat?

To find that axis the code measures how big the shape is on X, Y and Z ( basically the size of its bounding box on each axis, the code calls these extents). For the circle on the ground that comes out to 49.6, 0 and 49.6 so Y is the flat one.

![The circle's extents](Images/Icons_03_Extents.png)

> I don't check for exactly 0 though, curves are rarely perfectly flat. Snap something slightly off or build it by hand and you'll end up with something like 0.00003 instead of 0, so anything smaller than 1% of the shape's biggest side counts as flat.

Depending on which axis is flat the code then looks at the shape from the top, the front or the side and keeps the two axes the shape actually has. ( Some of them flip Y with a minus sign because images count their pixels from the top down, without it every icon would come out upside down which would be a fun one to explain)

## Shapes That Aren't Flat

If none of the axes are flat, like the box or pyramid, looking at it straight on doesn't work either. A box from the front is just a square since the back face hides perfectly behind the front one, you'd never know it was a box.

![A box from the front vs the 3/4 view](Images/Icons_04_Front_Vs_Three_Quarter.png)

For these the code uses a 3/4 view instead, the same kind of angle as the hand made box and pyramid icons, the camera is turned 35 degrees around Y and tilted 25 degrees up.

> Its kind of like setting up an Aim Constraint (so if you've done it before you'll be fine) . `cam` is the aim vector ( the direction we're looking from), `right` is the side vector and it's kept flat on the ground so the icon never ends up rolled to one side. `up` then gets worked out from `cam` and `right` so it sits at 90 degrees to both of them, the same way an aim constraint only uses world up as a hint and corrects it. If I just used world up (0, 1, 0) it wouldn't be at 90 degrees to the camera because the camera is tilted, and the icon would come out sheared.

With those three every point gets measured against `right` ( how far across the icon it goes) and `up` ( how far up it goes) and whatever is left along `cam`, the depth, just gets thrown away. So it's pretty much an orthographic camera in a couple lines of code.

## Fitting It In The Square

After all that the drawing could be any size, and a tiny finger control and a massive root control should both fill their icons the same way. So the code measures the width and height of the drawing and scales it so the bigger side fills the icon, leaving an 8 pixel margin around the edge. Using the bigger side means both directions get scaled by the same amount so nothing gets stretched.

Then it moves the centre of the drawing to the centre of the icon and draws it in the same yellow and line thickness as the hand made icons so the stored ones don't stick out in the library.

![Icons CLib drew](Images/Icons_05_Results.png)

There's also a tiny 0.0001 in there, that's only there so a curve where every point sits in the same spot doesn't make the code divide by zero. Very unlikely to happen but I'd rather not find out the hard way.

## The Kryptonite Section

> Damn we were almost perfect. 
A flat shape that's tilted (say a circle rotated 45 degrees), has size on all three axes so it doesn't get caught as flat and gets the 3/4 view instead, so it comes out looking like an oval. Fixing that would mean finding the plane the shape actually sits on rather than just checking X, Y and Z, which is a bigger job than it sounds. ( believe me I tried, I am open to suggestions though )

Really busy shapes can also get a bit muddy at 100 pixels, but if a shape is that busy it's probably too busy to be a control anyway. ( I'm just saying )

> So thanks Justin, that one comment turned into a lot more maths than I expected.

---

If this helps anyone I'd be happy to explain how Replace Shape works too.

The code for all of this is in `get_curve_points` and `write_icon` in [main.py](../maya2025/CLib/main.py).
