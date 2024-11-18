
# ChatWindow.py
from PySide2 import QtWidgets, QtCore
class ChatWindow(QtWidgets.QWidget):
    """
    A widget that displays a chat conversation with messages from different senders.

    Attributes:
        layout (QtWidgets.QVBoxLayout): The layout of the widget.
        scroll_area (QtWidgets.QScrollArea): The scroll area for the chat content.
        chat_content (QtWidgets.QWidget): The widget containing the chat messages.
        chat_layout (QtWidgets.QVBoxLayout): The layout of the chat content.
    """
    def __init__(self):
        super().__init__()
        self.layout = QtWidgets.QVBoxLayout(self)
        self.scroll_area = QtWidgets.QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.chat_content = QtWidgets.QWidget()
        self.chat_layout = QtWidgets.QVBoxLayout(self.chat_content)
        self.scroll_area.setWidget(self.chat_content)
        self.layout.addWidget(self.scroll_area)
        self.chat_layout.setAlignment(QtCore.Qt.AlignTop)
        self.chat_content.setStyleSheet("background-color: #f0f0f0; border: 1px solid #ccc;")

    def add_message(self, sender, message, is_user=False):
        """
        Add a message to the chat window.

        Args:
            sender (str): The name of the message sender.
            message (str): The content of the message.
            is_user (bool): A flag indicating if the message is sent by the user.
        """
        message_layout = QtWidgets.QHBoxLayout()
        
        message_label = QtWidgets.QLabel(message)
        message_label.setWordWrap(True)
        message_label.setAlignment(QtCore.Qt.AlignLeft)
        message_label.setStyleSheet(
            "border-radius: 15px; padding: 10px; margin: 5px;"
            + ("background-color: #d1e7dd; color: #0f5132;" if is_user else "background-color: #d1d1d1; color: #333;")
        )

        if is_user:
            message_layout.addStretch()
            message_layout.addWidget(message_label)
        else:
            message_layout.addWidget(message_label)
            message_layout.addStretch()
        
        self.chat_layout.addLayout(message_layout)
        QtCore.QTimer.singleShot(0, self.scroll_to_bottom)

    def scroll_to_bottom(self):
        """
        Scroll the chat window to the bottom. !FIXME: This method is not working as expected.
        """
        self.scroll_area.verticalScrollBar().setValue(self.scroll_area.verticalScrollBar().maximum())

    def clear_chat(self):
        """
        Clear all messages from the chat window.  !FIXME: This method is not working as expected.
        """
        for i in reversed(range(self.chat_layout.count())):
            widget = self.chat_layout.itemAt(i).widget()
            if widget is not None:
                widget.deleteLater()

