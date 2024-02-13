from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QComboBox, QLineEdit, QHBoxLayout

class ControlPanel(QWidget):
    """
    A customizable control panel class that extends QWidget.
    
    This class provides a flexible way to add various control elements like
    buttons, combo boxes, and text input fields to a user interface. It is built
    upon PyQt5's QWidget class and uses QVBoxLayout to organize its child widgets.
    """
    
    def __init__(self, parent=None):
        """
        Initializes the ControlPanel instance.
        
        :param parent: The parent widget to which this ControlPanel belongs. Default is None.
        """
        super().__init__(parent=parent)
        self.layout = QVBoxLayout(self)
        # Set the layout for this widget

    def addButton(self, text, action):
        """
        Adds a button with the specified text and action to the control panel.
        
        :param text: The text displayed on the button.
        :param action: The function to be called when the button is clicked.
        """
        button = QPushButton(text, self)
        button.clicked.connect(action)
        self.layout.addWidget(button)

    def addComboBox(self, label, options=[]):
        """
        Adds a combo box with a label and specified options to the control panel.
        
        :param label: The text label displayed next to the combo box.
        :param options: A list of option strings to be included in the combo box. Default is an empty list.
        :return: The created QComboBox instance.
        """
        row_layout = QHBoxLayout()
        row_layout.addWidget(QLabel(label))
        
        combo_box = QComboBox(self)
        for option in options:
            combo_box.addItem(option)
        row_layout.addWidget(combo_box)
        
        self.layout.addLayout(row_layout)
        return combo_box

    def addTextInput(self, placeholder, validator=None):
        """
        Adds a text input field to the control panel.
        
        :param placeholder: The placeholder text displayed in the text input field when it is empty.
        :param validator: An optional QValidator object to validate the input. Default is None.
        :return: The created QLineEdit instance.
        """
        text_input = QLineEdit(self)
        text_input.setPlaceholderText(placeholder)
        if validator:
            text_input.setValidator(validator)
        self.layout.addWidget(text_input)
        return text_input

    def addControlGroup(self, label=None, controls=[]):
        """
        Adds a group of controls to the control panel, optionally with a group label.
        
        :param label: An optional label for the group of controls. Default is None.
        :param controls: A list of control specifications, where each control is defined by a tuple
                         containing the control type ('button', 'combo', or 'text'), followed by
                         arguments specific to that control type.
        """
        group_layout = QVBoxLayout()
        if label:
            group_layout.addWidget(QLabel(label))
        
        for control_type, args in controls:
            if control_type == "button":
                # args expected to be (button text, action)
                button = QPushButton(args[0], self)
                button.clicked.connect(args[1])
                group_layout.addWidget(button)
            elif control_type == "combo":
                # args expected to be (label, options list)
                combo_box = self.addComboBox(*args)
                group_layout.addWidget(combo_box)
            elif control_type == "text":
                # args expected to be (placeholder, optional validator)
                text_input = self.addTextInput(*args)
                group_layout.addWidget(text_input)
        
        self.layout.addLayout(group_layout)

    def addFlexibleRow(self, controls):
        """
        Adds a row with a flexible combination of controls to the control panel.

        :param controls: A list of tuples, each specifying a control type ('button', 'combo', 'text')
                        and its parameters. For a button, expect (type, text, action). For a combo box,
                        expect (type, label, options) where options is a list of strings. For a text input,
                        expect (type, placeholder, validator) where validator is optional.
        """
        row_layout = QHBoxLayout()
        for control in controls:
            control_type, *args = control
            if control_type == 'button':
                button = QPushButton(args[0], self)
                button.clicked.connect(args[1])
                row_layout.addWidget(button)
            elif control_type == 'combo':
                label, options = args
                row_layout.addWidget(QLabel(label))
                combo_box = QComboBox(self)
                combo_box.addItems(options)
                row_layout.addWidget(combo_box)
            elif control_type == 'text':
                placeholder = args[0]
                validator = args[1] if len(args) > 1 else None
                text_input = QLineEdit(self)
                text_input.setPlaceholderText(placeholder)
                if validator:
                    text_input.setValidator(validator)
                row_layout.addWidget(text_input)
        self.layout.addLayout(row_layout)

