from PyQt5.QtWidgets import QLabel, QVBoxLayout, QWidget
from PyQt5.QtGui import QFont, QColor
from PyQt5.QtCore import Qt

class LightbulbIndicator(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()
    
    def initUI(self):
        # Create and configure the QLabel for the lightbulb
        self.lightbulb_label = QLabel("\U0001F4A1", self)  # Lightbulb Unicode character
        self.lightbulb_label.setFont(QFont("Arial", 24))  # Adjust font and size as needed
        self.lightbulb_label.setAlignment(Qt.AlignCenter)
        
        # Set the initial color to "off"
        self.updateIndicator(False)
        
        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.lightbulb_label)
        self.setLayout(layout)

    def updateIndicator(self, is_on):
        """
        Update the lightbulb indicator's color based on the is_on parameter.
        """
        color = QColor(255, 0, 0) if is_on else QColor(0, 0, 255)  # Yellow for "on", grey for "off"
        self.lightbulb_label.setStyleSheet(f"color: {color.name()};")

