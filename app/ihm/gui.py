from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QPushButton, QLineEdit, QTextEdit
from PySide6.QtGui import QIcon
from PySide6.QtCore import Qt
from dotenv import load_dotenv
import os
from app.src.main import LinkedinBot


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Linkedin Prospecting Bot")

        # Create layout
        layout = QVBoxLayout()

        # Load .env variables
        load_dotenv()

        # For each variable in .env, create a label and text field
        self.env_vars = ["LINKEDIN_USERNAME", "LINKEDIN_PASSWORD", "LINKEDIN_SEARCH_LINK", "MAX_PAGES", "MAX_MESSAGE_PER_DAY", "MESSAGE"]
        self.text_fields = []
        for var in self.env_vars:
            label = QLabel(var)
            if var == "LINKEDIN_PASSWORD":
                text_field = QLineEdit()
                text_field.setEchoMode(QLineEdit.Password)
            elif var == "MESSAGE":
                text_field = QTextEdit()
            else:
                text_field = QLineEdit()
            text_field.setText(os.getenv(var, ""))  # Default to empty string if env var is not found
            layout.addWidget(label)
            layout.addWidget(text_field)
            self.text_fields.append(text_field)

        # Create Start Bot button
        start_button = QPushButton("Start Bot")
        start_button.clicked.connect(self.start_bot)
        layout.addWidget(start_button)

        # Set layout
        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def start_bot(self):
        # Get the necessary information from the text fields
        username = self.text_fields[0].text()
        password = self.text_fields[1].text()
        search_link = self.text_fields[2].text()
        max_pages = int(self.text_fields[3].text())
        max_messages = int(self.text_fields[4].text())
        message = self.text_fields[5].toPlainText()

        # Create an instance of the bot with the given parameters
        bot = LinkedinBot(username, password, search_link, max_pages, max_messages, message)

        # Start the bot
        bot.start()


# Create a Qt application
app = QApplication([])

# Create and show the main window
window = MainWindow()
window.show()

# Run the application -> python -m app.ihm.gui
app.exec()
