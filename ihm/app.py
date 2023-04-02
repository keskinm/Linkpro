import os
from pathlib import Path

from PySide6.QtCore import Slot
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout

from dotenv import load_dotenv

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LinkedIn Bot")
        self.setWindowIcon(QIcon("icon.png"))
        self.setMinimumWidth(300)
        self.setMinimumHeight(200)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout()
        central_widget.setLayout(layout)

        self.username_label = QLabel("Username:")
        self.username_input = QLineEdit()
        layout.addWidget(self.username_label)
        layout.addWidget(self.username_input)

        self.password_label = QLabel("Password:")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password_label)
        layout.addWidget(self.password_input)

        self.start_button = QPushButton("Start")
        self.start_button.clicked.connect(self.start_bot)
        layout.addWidget(self.start_button)

        load_dotenv()

    @Slot()
    def start_bot(self):
        browser = webdriver.Chrome(get_driver_path(), chrome_options=selenium_options())
        browser.get("https://www.linkedin.com/uas/login")
        browser.find_element(By.ID, 'username').send_keys(self.username_input.text())
        browser.find_element(By.ID, 'password').send_keys(self.password_input.text())
        browser.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()

    def closeEvent(self, event):
        event.accept()


def get_driver_path():
    return str(Path(__file__).parent.parent / "utils" / "chromedriver.exe")


def selenium_options():
    chrome_options = Options()
    chrome_options.add_experimental_option("detach", True)
    chrome_options.add_argument("--start-maximized")
    return chrome_options


if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()
