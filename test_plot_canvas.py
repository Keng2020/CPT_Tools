from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout, QMainWindow, QWidget, QApplication
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import sys
import numpy as np
from plotcanvas import PlotCanvas

class TestPlotCanvas(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.test_plot_single()
        self.test_plot_subplot()

    def initUI(self):
        self.setWindowTitle("TEST")

        # Create a widget for window content
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        # Create the horizontal layout for two columns
        layout = QHBoxLayout(self.central_widget)

        self.plot_canvas = PlotCanvas(parent=self)
        layout.addLayout(self.plot_canvas.get_layout())  


        self.plot_canvas_subplot = PlotCanvas(parent=self, use_subplots=True, nrows=2, ncols=2)
        layout.addLayout(self.plot_canvas_subplot.get_layout())


    def test_plot_single(self):
        lines = []
        for i in range(10):
            x = np.linspace(0, 10, 1000)
            y = np.sin(x + i*5 / 10.0) * (1 + i*5 / 25.0)
            self.plot_canvas.plot(x, y, marker='o', linestyle='-', label=f'Line {i}')
        self.plot_canvas.set_plot_attributes(title="Test", xlabel="haha")


    def test_plot_subplot(self):
        x = np.linspace(0, 5, 20)
        lines = []
        for i in range(3):
            x = np.linspace(0, 10, 1000)
            y = np.sin(x + i / 10.0) * (1 + i / 25.0)
            self.plot_canvas_subplot.plot(x, y, subplot_index=0 ,marker='o', linestyle='-', label=f'Line {i}')
        self.plot_canvas_subplot.plot(x, np.sin(x), subplot_index=1 ,marker='o', linestyle='-')
        self.plot_canvas_subplot.plot(x, np.cos(x), subplot_index=2 ,marker='o', linestyle='-')
        self.plot_canvas_subplot.plot(x, np.sinh(x), subplot_index=3 ,marker='o', linestyle='-')
        self.plot_canvas_subplot.set_plot_attributes(subplot_index=3, title="this is 0")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = TestPlotCanvas()
    ex.show()
    sys.exit(app.exec_())

