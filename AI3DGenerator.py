# AI3DGenerator.py
import FreeCADGui
from PySide2 import QtWidgets, QtCore
from AI3DGeneratorWidget import AI3DGeneratorWidget


class AI3DGeneratorCommand:
    """
    A command to open the AI 3D Generator widget.
    """
    def GetResources(self):
        return {
            'Pixmap': '',
            'MenuText': 'AI 3D Generator',
            'ToolTip': 'Generate 3D models with AI'
        }

    def Activated(self):
        """
        Open the AI 3D Generator widget.
        If the widget is already open, bring it to the front.
        """
        if FreeCADGui.getMainWindow().findChild(QtWidgets.QDockWidget, "AI3DGeneratorDock"):
            return
        dock = QtWidgets.QDockWidget("AI 3D Generator", FreeCADGui.getMainWindow())
        dock.setObjectName("AI3DGeneratorDock")
        dock.setWidget(AI3DGeneratorWidget())
        FreeCADGui.getMainWindow().addDockWidget(QtCore.Qt.RightDockWidgetArea, dock)
        dock.setFloating(False)

    def IsActive(self):
        return True

FreeCADGui.addCommand('AI3DGenerator', AI3DGeneratorCommand())