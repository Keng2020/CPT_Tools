from PyQt5.QtWidgets import QAction, QInputDialog, QFontDialog, QMainWindow, QApplication, QMenuBar, QWidget, QMenu

from PyQt5.QtWidgets import QAction, QInputDialog
from PyQt5.QtGui import QFont

class FontSizeAdjuster:
    def __init__(self, main_window):
        self.main_window = main_window
        self.default_font_size = 12
        self.default_font_family = "Consolas"
        self.setup_menubar()
        self.apply_default_font_settings()
        

    def setup_menubar(self):
        # Create a menubar
        menubar = self.main_window.menuBar()

        # Create a menu for settings
        settingsMenu = menubar.addMenu('Settings')

        # Create an action for font size changing
        changeFontSizeAction = QAction('Change Font Size', self.main_window)
        changeFontSizeAction.triggered.connect(self.change_font_size)

        # Add the action to the settings menu
        settingsMenu.addAction(changeFontSizeAction)

    def change_font_size(self):
        # Open a dialog to input the new font size
        fontSize, okPressed = QInputDialog.getInt(self.main_window, "Change Font Size", "Font Size:", self.default_font_size, 8, 40, 1)
        if okPressed:
            self.apply_font_size_to_widgets(fontSize)

    def apply_font_size_to_widgets(self, fontSize):
        # Create a font with the new size
        font = QFont(self.default_font_family, fontSize)
        font.setBold(True)  # Make the font bold

        # Apply the font to all widgets in the application
        self.apply_font_recursive(self.main_window, font)

    def apply_font_recursive(self, widget, font):
        # Apply the font to the current widget
        widget.setFont(font)

        # Recursively apply the font to child widgets
        for child in widget.children():
            if isinstance(child, QWidget):  # Check if the child is a widget
                self.apply_font_recursive(child, font)

    def apply_default_font_settings(self):
        # Apply the default font settings to the entire application
        self.apply_font_size_to_widgets(self.default_font_size)


    def apply_font_size_to_widgets(self, fontSize):
        # Create a font with the new size
        font = QFont(self.default_font_family, fontSize)
        font.setBold(True)  # Make the font bold

        # Apply the font to the entire application
        QApplication.instance().setFont(font)
