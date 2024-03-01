from PyQt5.QtWidgets import QWidget, QVBoxLayout, QCheckBox

class TickList(QWidget):
    def __init__(self, items, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.checkboxes = []

        for item in items:
            checkbox = QCheckBox(item)
            self.layout.addWidget(checkbox)
            self.checkboxes.append(checkbox)

    def get_selected_items(self):
        """Returns a list of selected items."""
        return [cb.text() for cb in self.checkboxes if cb.isChecked()]
