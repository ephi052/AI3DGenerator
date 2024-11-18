# ComandHelper.py
"""
This module contains the CommandHelper class, which is a popup widget that
displays a list of commands and allows the user to filter and insert them into
a text input.
"""
from PySide2 import QtWidgets, QtCore

class CommandHelper(QtWidgets.QWidget):
    """
    A popup widget that displays a list of commands and allows the user to 
    filter and insert them into a text input.

    Attributes:
        parent (QtWidgets.QTextEdit): The parent text input widget where the 
            command will be inserted.
        layout (QtWidgets.QVBoxLayout): The layout of the widget.
        search_bar (QtWidgets.QLineEdit): The search bar for filtering commands.
        command_list (QtWidgets.QListWidget): The list of commands to display.
        commands (list): A list of commands to display in the widget.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Command Helper")
        self.setWindowFlags(QtCore.Qt.Popup)
        self.layout = QtWidgets.QVBoxLayout(self)
        self.search_bar = QtWidgets.QLineEdit()
        self.search_bar.setPlaceholderText("Type to filter commands...")
        self.search_bar.textChanged.connect(self.filter_commands)
        self.layout.addWidget(self.search_bar)

        self.command_list = QtWidgets.QListWidget()
        self.command_list.itemClicked.connect(self.insert_command)
        self.layout.addWidget(self.command_list)

        self.commands = [
            "/Sketch: Generate a constrained 2D sketch using geometric",
            "and dimensional constraints.",
            "/Extrude: Extend a sketch into 3D, allowing control over depth and direction.",
            "/Cut: Subtract material from an object, for operations like drilling or hollowing.",
            "/Part: Create individual 3D parts with detailed features.",
            "/Assembly: Integrate parts into an assembly using constraints like alignment, "
            "concentricity, and parallelism.",
            "/Chamfer: Apply beveled edges to enhance aesthetics or reduce sharpness.",
            "/Fillet: Round edges for smoother finishes.",
            "/Draft: Add taper angles to extrusions or create draft elements.",
            "/Mirror: Duplicate geometry symmetrically across a specified plane.",
            "/Pattern: Arrange copies of a feature linearly or radially.",
            "/Pocket: Create recesses or cavities in a part.",
            "/Revolve: Form parts by rotating a profile around an axis.",
            "/Boolean: Perform union, intersection, or difference operations between parts."
        ]
        self.update_command_list()

    def update_command_list(self):
        """
        Update the command list with the current list of commands.
        """
        self.command_list.clear()
        self.command_list.addItems(self.commands)

    def filter_commands(self, text):
        """
        Filter the list of commands based on the given text.
        """
        filtered_commands = [cmd for cmd in self.commands if text.lower() in cmd.lower()]
        self.command_list.clear()
        self.command_list.addItems(filtered_commands)

    def insert_command(self, item):
        """
        Insert the selected command into the parent text input widget.
        """
        command_text = item.text().split(':')[0]  # Extract only the command tag
        self.parent().prompt_input.insertPlainText(f"{command_text} ")
        self.hide()
