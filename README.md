# Mathematical Equation Generator
This repository contains Blender add-on for generating mathematical equations based on mathematical notation of language Latex. Feel free to use it for your Blender project.

# Installation
First, download zip file of this repository. Open Blender (3.3+) and go to _Edit->Preferences->Add-ons_. Click on the _Install_ button and find path to the downloaded add-on. Choose file "mathematical-equations-main.zip" and click on the _Install Add-on_ button. A new field called _Mathematical Equation Generator_ should appear in the _Add-ons_ section. To activate the add-on please check the box next to it. That concludes the installation.

You can find the add-on on the right side of 3D Viewport, labeled as _Text Tool_.

# Supported Latex Commands
This version of addon supports only a limited number of Latex commands. To make it easier to navigate, all the supported features are listed below.
- most used mathematical symbols
- indexes and exponents (x^2, x_2, x^{\alpha}...), plus the use of both of them at the same time (x_1^2)
- command spaces (\! \; \, \quad...)
- \sqrt[]{} \sqrt{}
- \sum_{}^{}, \prod_{}^{}
- \frac{}{}
- \begin{matrix} ... \end{matrix} -- other versions of matrices (_pmatrix_, _Pmatrix_, _bmatrix_...) are also supported

# Usage
Add-on has six parameters that affect the generation of mathematical equations.

- Latex Text - expects a Latex string with mathematical equation 
- Font - expects a path to chosen font
- Scale - scales the result
- Thickness - extrudes the result
- Location - moves result on the x,y and z axes
- Rotation - rotates the result around x,y and z axes

# Troubleshooting
If you experience any trouble with the addon, check Blender's system console for any error messages. System console is located in _Window->Toggle System Console_.
