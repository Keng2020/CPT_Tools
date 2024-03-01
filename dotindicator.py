from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QGraphicsDropShadowEffect
from PyQt5.QtGui import QFont, QColor
from PyQt5.QtCore import Qt

class DotIndicator(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()
    
    def initUI(self):
        self.dot_label = QLabel("●", self)
        self.dot_label.setFont(QFont("Arial", 48))  # Adjust the size as needed

        # Apply a drop shadow effect to the dot
        shadow_effect = QGraphicsDropShadowEffect(self.dot_label)
        shadow_effect.setOffset(5, 5)  # Shadow offset
        shadow_effect.setBlurRadius(8)  # Shadow blur radius
        shadow_effect.setColor(QColor(0, 0, 0, 60))  # Shadow color and transparency
        self.dot_label.setGraphicsEffect(shadow_effect)

        self.dot_label.setAlignment(Qt.AlignCenter)
        self.updateIndicator(False)  # Initialize with it "off"
        
        layout = QVBoxLayout()
        layout.addWidget(self.dot_label)
        self.setLayout(layout)

    def updateIndicator(self, is_on):
        if is_on:
            # Light yellow with transparency
            color = QColor(255, 255, 0, 128)  # Alpha set to 128 for semi-transparency
        else:
            # Light grey with transparency
            color = QColor(100, 100, 100, 128)  # Alpha set to 128 for semi-transparency
        self.dot_label.setStyleSheet(f"color: rgba({color.red()}, {color.green()}, {color.blue()}, {color.alpha()});")

