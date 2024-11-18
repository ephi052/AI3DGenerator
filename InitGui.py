# InitGui.py
"""
This file is part of the FreeCAD CAx development system.
This is the main initialization file for the AI 3D Generator workbench.
Author: Ephi Cohen
"""
import FreeCADGui

class AI3DGeneratorWorkbench(FreeCADGui.Workbench):
    """
    AI 3D Generator Workbench
    This workbench provides tools for generating and executing 3D models with AI code generation.
    """
    MenuText = "AI 3D Generator"
    ToolTip = "Generate and execute 3D models with AI code generation"

    def Initialize(self):
        """ Initialize the workbench. """
        from AI3DGenerator import AI3DGeneratorCommand
        FreeCADGui.addCommand('AI3DGenerator', AI3DGeneratorCommand())
        self.appendToolbar("AI Tools", ["AI3DGenerator"])

    def GetClassName(self):
        """ Return the name of this workbench. """
        return "Gui::PythonWorkbench"

FreeCADGui.addWorkbench(AI3DGeneratorWorkbench())
