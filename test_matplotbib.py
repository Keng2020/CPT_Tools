import matplotlib.pyplot as plt
import numpy as np

# Generating a large number of lines with many data points
num_lines = 50  # Number of lines
points_per_line = 1000  # Data points per line

fig, ax = plt.subplots()
lines = []
for i in range(num_lines):
    x = np.linspace(0, 10, points_per_line)
    y = np.sin(x + i / 10.0) * (1 + i / 25.0)
    line, = ax.plot(x, y, marker='', linestyle='-', label=f'Line {i}')
    lines.append(line)

# Text annotation for displaying (x, y) values, with background
text = ax.text(0, 0, "", va="bottom", ha="left", visible=False,
               bbox=dict(boxstyle="round,pad=0.5", facecolor="yellow", alpha=0.5))

def update_annot(line, x, y):
    text.set_text(f"({x:.3f}, {y:.3f})")
    text.set_position((x, y))
    text.set_visible(True)

def hover(event, lines):
    if event.inaxes == ax:
        for line in lines:
            cont, ind = line.contains(event)
            if cont:
                xdata, ydata = line.get_data()
                x, y = xdata[ind['ind'][0]], ydata[ind['ind'][0]]
                update_annot(line, x, y)
                fig.canvas.draw_idle()
                return
        text.set_visible(False)
        fig.canvas.draw_idle()

def set_hover_behavior(ax, lines):
    # Connect the hover function to the motion_notify_event with lines information
    callback_id = fig.canvas.mpl_connect("motion_notify_event", lambda event: hover(event, lines))
    return callback_id

# Apply hover effect to multiple lines
set_hover_behavior(ax, lines)

plt.show()
