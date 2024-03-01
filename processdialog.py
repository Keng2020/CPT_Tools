from PyQt5.QtWidgets import QMainWindow, QComboBox, QApplication, QDialog, QProgressBar, QVBoxLayout
from PyQt5.QtCore import Qt
import os

class ProgressDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Loading Files")
        self.setModal(True)
        self.progressBar = QProgressBar(self)
        layout = QVBoxLayout()
        layout.addWidget(self.progressBar)
        self.setLayout(layout)
        self.progressBar.setMaximum(100)  # Assume 100% as the completion value
        
    def update_progress(self, value):
        self.progressBar.setValue(value)
        if value >= 100:
            self.accept()  # Close the dialog when progress reaches 100%