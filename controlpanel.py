from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QPushButton, QLabel, 
                             QComboBox, QLineEdit, QHBoxLayout, QSizePolicy,
                             QSlider, QCheckBox)
from PyQt5.QtCore import QSize, Qt
from dotindicator import DotIndicator

class ControlPanel(QWidget):
    """
    A customizable contarol panel class that extends QWidget.
    
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
    

    def addPlotCanvas(self, plotcanvas):
        self.layout.addLayout(plotcanvas)


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
                        expect (type, placeholder, validator) where validator is optional. For a slider, 
                        expect (type, orientation, min, max, initial, tick_interval, action).
        """
        created_widgets = {}
        row_layout = QHBoxLayout()
        for control in controls:
            control_type, *args = control
            widget = None # Placeholder for the created widget
            if control_type == 'button':
                # args expected to be (button text, action)
                widget = QPushButton(args[0], self)
                widget.clicked.connect(args[1])
            elif control_type == 'combo':
                # args expected to be (label, options list)
                label, options = args
                row_layout.addWidget(QLabel(label))
                widget = QComboBox(self)
                # widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
                if options:
                    widget.addItems(options)
            elif control_type == 'text':
                # args expected to be (placeholder, optional validator)
                placeholder = args[0]
                validator = args[1] if len(args) > 1 else None
                widget = QLineEdit(self)
                widget.setPlaceholderText(placeholder)
                if validator:
                    widget.setValidator(validator)
            elif control_type == 'slider':
                # args expected to be (orientation, min, max, initial, tick_interval, action)
                widget_name, orientation, min_value, max_value, initial_value, tick_interval, action = args
                widget = QSlider(orientation, self)
                widget.setMinimum(min_value)
                widget.setMaximum(max_value)
                widget.setValue(initial_value)
                widget.setTickInterval(tick_interval)
                widget.setTickPosition(QSlider.TicksBelow)  # Adjust this as needed
                widget.valueChanged.connect(action)
            elif control_type == 'dot':
                widget = DotIndicator(self)
                if args:
                    widget.updateIndicator(args[1])  # Assuming the first arg is the boolean state
            elif control_type == 'ticklist':
                # Provide a default value for orientation if it's not included in args
                items, orientation = args[0], args[1] if len(args) > 1 else 'horizontal'
                ticklist_layout = QHBoxLayout() if orientation == 'horizontal' else QVBoxLayout()
                ticklist_container = QWidget()  # A container for the ticklist layout
                for item in items:
                    item_text, initial_state, text_on, text_off = item
                    checkbox = QCheckBox(text_on if initial_state else text_off)
                    checkbox.setChecked(initial_state)
                    # Connect the stateChanged signal to toggleCheckboxText
                    checkbox.stateChanged.connect(lambda state, cb=checkbox, on=text_on, off=text_off: self.toggleCheckboxText(state, cb, on, off))
                    ticklist_layout.addWidget(checkbox)
                    created_widgets[f"ticklist_{item_text}"] = checkbox
                ticklist_container.setLayout(ticklist_layout)
                row_layout.addWidget(ticklist_container)
            
            if widget:  # If a widget was created
                row_layout.addWidget(widget)
                # For sliders, create a unique key based on its range as it doesn't have a label like combo boxes
                control_key = f'{control_type}_{args[0]}' if control_type != 'slider' else f'{control_type}_{widget_name}'
                created_widgets[control_key] = widget

        self.layout.addLayout(row_layout)
        return created_widgets

    def set_tick_position(self, slider_widget, tick_interval, tick_position=QSlider.TicksBelow):
        """
        Sets the tick interval and position for a specified slider widget.

        :param slider_widget: The slider widget to modify.
        :param tick_interval: The interval between ticks.
        :param tick_position: The position of the ticks relative to the slider. Default is below the slider.
        """
        if slider_widget:
            slider_widget.setTickInterval(tick_interval)
            slider_widget.setTickPosition(tick_position)
        else:
            print("Slider widget not found.")

    def set_tick_labels(self, slider_widget, labels, tick_position=QSlider.TicksBelow):
        """
        Creates and sets tick labels for a specified slider widget.

        :param slider_widget: The slider widget to add tick labels.
        :param labels: A dictionary where keys are tick positions (integers) and values are the label texts (strings).
        :param tick_position: The position of the tick labels relative to the slider. Default is below the slider.
        """
        slider_range = slider_widget.maximum() - slider_widget.minimum()
        slider_length = slider_widget.width() if slider_widget.orientation() == Qt.Horizontal else slider_widget.height()
        
        for tick, label_text in labels.items():
            label = QLabel(label_text, self)
            # Calculate label position
            tick_ratio = (tick - slider_widget.minimum()) / slider_range
            if slider_widget.orientation() == Qt.Horizontal:
                label_x = slider_widget.pos().x() + tick_ratio * slider_length - (label.width() / 2)
                label_y = slider_widget.pos().y() + slider_widget.height() if tick_position == QSlider.TicksBelow else slider_widget.pos().y() - label.height()
            else:
                label_x = slider_widget.pos().x() + slider_widget.width() if tick_position == QSlider.TicksRight else slider_widget.pos().x() - label.width()
                label_y = slider_widget.pos().y() + tick_ratio * slider_length - (label.height() / 2)
            
            label.move(int(label_x), int(label_y))
            label.show()

    def setup_color_toggle_button(self, button, color1=(255, 0, 0), color2=(255, 255, 0), transparency=25):
        """
        Sets up a button to toggle its background color between two specified colors upon clicks.
        Colors are specified as RGB tuples, and transparency is defined by an alpha value (0-255).

        :param button: The QPushButton instance to modify.
        :param color1: The first color as an RGB tuple.
        :param color2: The second color as an RGB tuple.
        :param transparency: The transparency level as an alpha value (0-255), where 255 is fully opaque.
        """
        # Convert RGB tuples and transparency to RGBA strings
        color1_rgba = f"rgba({color1[0]}, {color1[1]}, {color1[2]}, {transparency})"
        color2_rgba = f"rgba({color2[0]}, {color2[1]}, {color2[2]}, {transparency})"

        # Set the button's initial color to color1
        button.setStyleSheet(f"background-color: {color1_rgba};")

        def on_click():
            # Toggle the button's background color between color1 and color2
            current_color = button.styleSheet()
            new_color = color2_rgba if color1_rgba in current_color else color1_rgba
            button.setStyleSheet(f"background-color: {new_color};")

        # Connect the on_click function to the button's clicked signal
        button.clicked.connect(on_click)

    def toggleCheckboxText(self, state, checkbox, text_on, text_off):
        """
        Toggles the text of a checkbox based on its checked state.

        :param state: The state of the checkbox (int).
        :param checkbox: The QCheckBox instance.
        :param text_on: The text to display when the checkbox is checked.
        :param text_off: The text to display when the checkbox is unchecked.
        """
        checkbox.setText(text_on if state else text_off)



    def addWidget(self, widget):
        self.layout.addWidget(widget)
