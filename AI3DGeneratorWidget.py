# AI3DGeneratorWidget.py
from PySide2 import QtWidgets, QtGui, QtCore
import FreeCAD
import FreeCADGui
import openai
import os
import time
import traceback

from ChatWindow import ChatWindow
from CommandHelper import CommandHelper

class AI3DGeneratorWidget(QtWidgets.QWidget):
    """
    Main widget for the AI 3D Generator tool.
    This widget provides a chat interface for interacting with the AI model and generating 3D models.

    Attributes:

        conversation_history (list): A list of messages exchanged in the chat.
        settings (QtCore.QSettings): The settings object for storing user settings.
        pre_prompt (str): The pre-prompt text to start the conversation.
        model (str): The AI model to use for generating responses.
        temperature (float): The temperature parameter for response generation.
        max_tokens (int): The maximum number of tokens for response generation.
        api_key (str): The OpenAI API key for accessing the model.
        save_folder (str): The folder path to save generated scripts.
        settings_button (QtWidgets.QPushButton): A button to open the settings dialog.
        chat_window (ChatWindow): The chat window widget for displaying messages.
        prompt_input (QtWidgets.QPlainTextEdit): The input box for user prompts.
        code_editor (QtWidgets.QPlainTextEdit): The code editor for displaying generated code.
        helper_button (QtWidgets.QPushButton): A button to open the command helper popup.
        command_helper (CommandHelper): The command helper popup widget.

    """
    def __init__(self):
        super().__init__()
        self.conversation_history = []
        
        # Load settings
        self.settings = QtCore.QSettings("FreeCAD", "AI3DGenerator")
        self.pre_prompt = self.settings.value("pre_prompt", "Default pre-prompt text here")
        self.model = self.settings.value("model", "gpt-4")
        self.temperature = float(self.settings.value("temperature", 1.0))
        self.max_tokens = int(self.settings.value("max_tokens", 2048))
        self.api_key = self.settings.value("api_key", "")
        self.save_folder = self.settings.value("save_folder", os.path.join(os.path.expanduser("~"), "Downloads"))

        layout = QtWidgets.QVBoxLayout()

        # Settings and Clear Chat buttons
        self.settings_button = QtWidgets.QPushButton("Settings")
        self.settings_button.clicked.connect(self.open_settings)
        layout.addWidget(self.settings_button)

        clear_button = QtWidgets.QPushButton("Clear Chat")
        clear_button.clicked.connect(self.clear_chat)
        layout.addWidget(clear_button)

        self.chat_window = ChatWindow()
        layout.addWidget(self.chat_window)

        # 3 lines high chat input
        self.prompt_input = QtWidgets.QPlainTextEdit()
        self.prompt_input.setPlaceholderText("Enter your prompt (e.g., 'Create a box')")
        self.prompt_input.setFixedHeight(50)
        self.prompt_input.setStyleSheet("background-color: #f0f0f0; color: #333;")
        self.prompt_input.setTabChangesFocus(True)
        send_button = QtWidgets.QPushButton("Send")
        send_button.clicked.connect(self.prompt_ai)

        prompt_layout = QtWidgets.QHBoxLayout()
        prompt_layout.addWidget(self.prompt_input)
        prompt_layout.addWidget(send_button)
        layout.addLayout(prompt_layout)

        self.code_editor = QtWidgets.QPlainTextEdit()
        self.code_editor.setFont(QtGui.QFont("Courier", 10))
        self.code_editor.setStyleSheet("background-color: #1e1e1e; color: #d4d4d4;")
        self.code_editor.setVisible(False)

        expand_button = QtWidgets.QPushButton("Expand Code")
        expand_button.clicked.connect(self.toggle_code_view)

        play_button = QtWidgets.QPushButton("Play Code")
        play_button.clicked.connect(self.run_script)

        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addWidget(expand_button)
        button_layout.addWidget(play_button)

        layout.addLayout(button_layout)
        layout.addWidget(self.code_editor)
        self.setLayout(layout)

        self.toggle_chat_input(bool(self.api_key))

        # Button to open command helper
        self.helper_button = QtWidgets.QPushButton("Command Helper")
        self.helper_button.clicked.connect(self.show_command_helper)
        layout.addWidget(self.helper_button)
        
        # Instantiate the helper popup (without showing it yet)
        self.command_helper = CommandHelper(self)

    def show_command_helper(self):
        """
        Show the command helper popup below the chat input.
        """
        pos = self.prompt_input.mapToGlobal(QtCore.QPoint(0, 0))
        self.command_helper.move(pos + QtCore.QPoint(0, self.prompt_input.height()))
        self.command_helper.show()

    def toggle_chat_input(self, enable):
        """
        Enable or disable the chat input based on the API key availability.
        """
        self.prompt_input.setEnabled(enable)
        self.chat_window.setEnabled(enable)
        self.settings_button.setEnabled(True)

    def toggle_code_view(self):
        """ Toggle the visibility of the code editor. """
        self.code_editor.setVisible(not self.code_editor.isVisible())

    def open_settings(self):
        """
        Open the settings dialog to configure the AI model and other settings.

        Settings:
            - Pre-prompt text
            - Model selection
            - Temperature
            - Max tokens
            - Save folder
            - API key
        """
        dialog = QtWidgets.QDialog(self)
        dialog.setWindowTitle("Settings")
        layout = QtWidgets.QVBoxLayout(dialog)

        # Editable Pre-prompt
        pre_prompt_label = QtWidgets.QLabel("Edit Pre-prompt:")
        layout.addWidget(pre_prompt_label)
        pre_prompt_input = QtWidgets.QPlainTextEdit(self.pre_prompt)
        layout.addWidget(pre_prompt_input)

        # Model selection
        model_label = QtWidgets.QLabel("Model:")
        layout.addWidget(model_label)
        model_input = QtWidgets.QLineEdit(self.model)
        layout.addWidget(model_input)

        # Temperature
        temp_label = QtWidgets.QLabel("Temperature:")
        layout.addWidget(temp_label)
        temp_input = QtWidgets.QDoubleSpinBox()
        temp_input.setValue(self.temperature)
        temp_input.setRange(0.0, 2.0)
        temp_input.setSingleStep(0.1)
        layout.addWidget(temp_input)

        # Max Tokens
        max_tokens_label = QtWidgets.QLabel("Max Tokens:")
        layout.addWidget(max_tokens_label)
        max_tokens_input = QtWidgets.QSpinBox()
        max_tokens_input.setMaximum(4096)
        max_tokens_input.setValue(self.max_tokens)
        layout.addWidget(max_tokens_input)

        # Save Folder Selection
        save_folder_button = QtWidgets.QPushButton("Select Save Folder")
        save_folder_label = QtWidgets.QLabel(self.save_folder)
        layout.addWidget(save_folder_button)
        layout.addWidget(save_folder_label)

        def select_save_folder():
            folder = QtWidgets.QFileDialog.getExistingDirectory(None, "Select Folder to Save Script", self.save_folder)
            if folder:
                self.save_folder = folder
                save_folder_label.setText(folder)
        
        save_folder_button.clicked.connect(select_save_folder)

        # API Key
        api_key_label = QtWidgets.QLabel("API Key:")
        layout.addWidget(api_key_label)
        api_key_input = QtWidgets.QLineEdit()
        api_key_input.setEchoMode(QtWidgets.QLineEdit.Password)
        api_key_input.setText(self.api_key)
        layout.addWidget(api_key_input)

        def save_settings():
            # Save all settings
            self.pre_prompt = pre_prompt_input.toPlainText()
            self.model = model_input.text()
            self.temperature = temp_input.value()
            self.max_tokens = max_tokens_input.value()
            self.api_key = api_key_input.text()
            self.settings.setValue("pre_prompt", self.pre_prompt)
            self.settings.setValue("model", self.model)
            self.settings.setValue("temperature", self.temperature)
            self.settings.setValue("max_tokens", self.max_tokens)
            self.settings.setValue("api_key", self.api_key)
            self.settings.setValue("save_folder", self.save_folder)
            self.toggle_chat_input(bool(self.api_key))
            dialog.accept()

        save_button = QtWidgets.QPushButton("Save")
        save_button.clicked.connect(save_settings)
        layout.addWidget(save_button)
        dialog.setLayout(layout)
        dialog.exec_()

    def prompt_ai(self):
        """
        Prompt the AI model with the user's message and display the response.
        If the response contains code, display the reasoning and code separately.
        If the response is empty, display an error message.
        If the response is successful, add the message to the conversation history.
        """
        user_message = self.prompt_input.toPlainText()
        if user_message:
            self.chat_window.add_message("User", user_message, is_user=True)
            self.prompt_input.clear()
            if not self.conversation_history:
                self.conversation_history.append({"role": "system", "content": self.pre_prompt})

            self.conversation_history.append({"role": "user", "content": user_message})
            self.chat_window.add_message("AI", "AI is thinking...", is_user=False)

            QtCore.QTimer.singleShot(100, self.get_ai_response_thread)

    def get_ai_response_thread(self):
        """ Run the AI response in a separate thread to avoid blocking the UI. !FIXME: This method is not working as expected. """
        response = self.get_openai_response(self.conversation_history)
        if response:
            self.conversation_history.append({"role": "assistant", "content": response})
            reasoning, code = self.extract_reasoning_and_code(response)
            self.chat_window.add_message("AI (Reasoning)", reasoning)
            self.chat_window.add_message("AI (Code)", code)
            self.code_editor.setPlainText(code)
        else:
            self.chat_window.add_message("AI", "Failed to fetch response. Try again.", is_user=False)

    def extract_reasoning_and_code(self, response):
        """ Extract the reasoning and code from the AI response. """
        reasoning = response.split("```python")[0]
        code = response.split("```python")[1].split("```")[0] if "```python" in response else response
        return reasoning.strip(), code.strip()

    def get_openai_response(self, conversation_history):
        """ Get the response from the OpenAI API based on the conversation history. """
        openai.api_key = self.api_key
        try:
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=conversation_history,
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            return response['choices'][0]['message']['content'].strip()
        except Exception as e:
            FreeCAD.Console.PrintError(f"Error fetching response: {str(e)}\n")
            return None

    def run_script(self):
        """
        Run the generated script and save it to a file.
        If the script is empty or the save folder is not selected, display an error message.
        If an error occurs while running the script, save the error traceback to a file and offer debugging options.
        """
        script = self.code_editor.toPlainText()
        chat_history = "\n".join([f"{msg['role']}: {msg['content']}" for msg in self.conversation_history])
        if script and self.save_folder:
            try:
                exec(script, globals())
                filename = f"AI3DGenerator_{time.strftime('%Y%m%d-%H%M%S')}.md"
                save_path = os.path.join(self.save_folder, filename)
                with open(save_path, 'w') as file:
                    file.write(f"# Script generated by AI3DGenerator\n\n")
                    file.write(f"## Run Date: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                    file.write(f"## Settings:\n\n- Model: {self.model}\n- Temperature: {self.temperature}\n- Max Tokens: {self.max_tokens}\n\n")
                    file.write(f"## Chat history:\n{chat_history}\n\n")
                FreeCAD.Console.PrintMessage(f"Script saved as {save_path}\n")
                if FreeCADGui.ActiveDocument:
                    view = FreeCADGui.ActiveDocument.ActiveView
                    view.setCameraType("Perspective")
                    view.viewAxometric()
                    view.fitAll()
            except Exception as e:
                error_traceback = traceback.format_exc()
                filename = f"AI3DGenerator_{time.strftime('%Y%m%d-%H%M%S')}_error.md"
                save_path = os.path.join(self.save_folder, filename)
                with open(save_path, 'w') as file:
                    file.write(f"# Script generated by AI3DGenerator\n\n")
                    file.write(f"## Run Date: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                    file.write(f"## Settings:\n\n- Model: {self.model}\n- Temperature: {self.temperature}\n- Max Tokens: {self.max_tokens}\n\n")
                    file.write(f"# Chat history:\n{chat_history}\n\n")
                    file.write(f"\n\n# Error running script:\n{error_traceback}")
                FreeCAD.Console.PrintError(f"Error running script:\n{error_traceback}")
                self.start_debugging_loop(error_traceback, script)
        else:
            FreeCAD.Console.PrintError("Please paste a script and select a save folder.\n")

    def start_debugging_loop(self, error_message, script):
        """ Start a debugging loop to fix the error in the script. """
        debug_button = QtWidgets.QPushButton("Debug")
        debug_button.clicked.connect(lambda: self.run_debugging_loop(error_message, script))
        self.layout().addWidget(debug_button)

    def run_debugging_loop(self, error_message, script):
        """ Run the debugging loop to fix the error in the script. """
        counter = 0
        while True:
            counter += 1
            FreeCAD.Console.PrintError(f"Debugging loop iteration {counter}\n")
            FreeCAD.Console.PrintError(f"Error message:\n{error_message}\n")
            
            # Ask user if they want to continue debugging
            reply = QtWidgets.QMessageBox.question( 
                None,
                "Continue Debugging?",
                f"Iteration {counter} failed. Do you want to continue debugging?\n\nError message:\n{error_message}",
                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                QtWidgets.QMessageBox.No
            )
            
            if reply == QtWidgets.QMessageBox.No:
                break  # Exit the loop if the user chooses 'No'

            # Debugging process
            prompt = f"The following script caused an error:\n\n{script}\n\nError message:\n{error_message}\n\nPlease fix the code."
            response = self.get_openai_response([{"role": "user", "content": prompt}])

            if response:
                new_code = self.extract_code_from_response(response)
                self.code_editor.setPlainText(new_code)
                try:
                    exec(new_code, globals())
                    QtWidgets.QMessageBox.information(None, "Debugging", "Debugging successful. Please run the script again.")
                    break  # Exit loop if successful
                except Exception as e:
                    error_message = traceback.format_exc()
                    script = new_code  # Update script for next loop iteration


    def extract_code_from_response(self, response):
        """ Extract the code from the AI response. """
        if "```python" in response:
            code = response.split("```python")[1].split("```")[0]
        else:
            code = response
        return code.strip()

    def clear_chat(self):
        """ Clear the chat window and the conversation history. !FIXME: This method is not working as expected. """
        self.conversation_history.clear()
        self.chat_window.clear_chat()
