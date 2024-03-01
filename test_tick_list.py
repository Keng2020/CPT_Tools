import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QListWidget, QListWidgetItem, QCheckBox, QVBoxLayout, QWidget

class TodoList(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('To-Do List with Checkboxes')
        self.setGeometry(100, 100, 360, 250)

        # Create a central widget
        self.centralWidget = QWidget(self)
        self.setCentralWidget(self.centralWidget)

        # Create a QVBoxLayout
        self.layout = QVBoxLayout(self.centralWidget)

        # Create a QListWidget
        self.listWidget = QListWidget(self)
        self.layout.addWidget(self.listWidget)

        # Populate the list with tasks, each with a checkbox
        for i in range(1, 11):  # Example: 10 tasks
            self.addTask(f"Task {i}")

    def addTask(self, text):
        # Create a QListWidgetItem
        item = QListWidgetItem(self.listWidget)
        # Create a QCheckBox
        checkBox = QCheckBox(text)
        # Connect the stateChanged signal of the checkbox to the markAsCompleted method
        checkBox.stateChanged.connect(lambda state, item=item, checkBox=checkBox: self.markAsCompleted(state, item, checkBox))
        # Set the item to hold the checkbox
        self.listWidget.setItemWidget(item, checkBox)

    def markAsCompleted(self, state, item, checkBox):
        # If the checkbox is checked, modify the text to show the task is completed
        if state == 2:  # State 2 means the checkbox is checked
            checkBox.setText(f"{checkBox.text()} completed")
        else:  # If the checkbox is unchecked, revert to the original text
            original_text = checkBox.text().replace(" completed", "")
            checkBox.setText(original_text)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = TodoList()
    ex.show()
    sys.exit(app.exec_())
