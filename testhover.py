import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import gaussian_kde
from scipy.optimize import fmin
from matplotlib.path import Path

class ResultPlotter:
    def __init__(self, canvas, markersize=4, linewidth=1, color='0.5', marker='s'):
        self.canvas = canvas
        self.markersize = markersize
        self.linewidth = linewidth
        self.color = color
        self.marker = marker

    def plot_results(self, x, x_low_GP, x_up_GP):
        sig = np.sqrt(1 / np.exp(x[:, 0]))
        sofv = np.exp(x[:, 1])
        sofh = np.exp(x[:, 2])
        nuv = np.exp(x[:, 3])
        nuh = np.exp(x[:, 4])
        sig_t = np.sqrt(1 / np.exp(x[:, 5]))
        sofv_t = np.exp(x[:, 6])
        sofh_t = np.exp(x[:, 7])
        
        xlim_low = np.exp(x_low_GP)
        xlim_low[0] = np.sqrt(1 / xlim_low[0])
        xlim_low[5] = np.sqrt(1 / xlim_low[5])
        
        xlim_up = np.exp(x_up_GP)
        xlim_up[0] = np.sqrt(1 / xlim_up[0])
        xlim_up[5] = np.sqrt(1 / xlim_up[5])

        # Clear the current figure to prepare for new plots
        self.canvas.figure.clf()

        # Subplot 1
        ax1 = self.canvas.figure.add_subplot(221)
        self.plot95CIv2(ax1, nuv, sofv, xlim_low[3], xlim_up[3], xlim_low[1], xlim_up[1], r'$\nu_v$', r'$\delta_v (m)$')

        # Subplot 2
        ax2 = self.canvas.figure.add_subplot(222)
        self.plot95CIv2(ax2, nuh, sofh, xlim_low[4], xlim_up[4], xlim_low[2], xlim_up[2], r'$\nu_h$', r'$\delta_h (m)$')

        # Subplot 3
        ax3 = self.canvas.figure.add_subplot(223)
        self.plot95CIv2(ax3, sig, sig_t, xlim_up[0], xlim_low[0], xlim_up[5], xlim_low[5], r'$\sigma (MPa)$', r'$\sigma_t (MPa)$')

        # Subplot 4
        ax4 = self.canvas.figure.add_subplot(224)
        self.plot95CIv2(ax4, sofv_t, sofh_t, xlim_low[6], xlim_up[6], xlim_low[7], xlim_up[7], r'$\delta_v_t (m)$', r'$\delta_h_t (m)$')

        self.canvas.draw()

    def plot95CIv2(self, ax, x_data, y_data, xlim_low, xlim_up, ylim_low, ylim_up, xlabel, ylabel):
        data = np.column_stack((x_data, y_data))
        no_of_data = data.shape[0]
        data = np.log(data)
        data1, data2 = data[:, 0], data[:, 1]
        kde = gaussian_kde(data.T)
        
        # Create meshgrid
        x_min, x_max = data1.min() - 1, data1.max() + 1
        y_min, y_max = data2.min() - 1, data2.max() + 1
        X, Y = np.mgrid[x_min:x_max:100j, y_min:y_max:100j]
        positions = np.vstack([X.ravel(), Y.ravel()])
        
        # Evaluate KDE on grid
        F = np.reshape(kde(positions).T, X.shape)
        
        # Find contour level for 95% CI
        up_val = fmin(lambda u: self.funtemp(no_of_data, X, Y, F, data1, data2, u), np.mean(F), disp=False)
        
        # Plot contour
        ax.contour(np.exp(X), np.exp(Y), F, levels=[up_val], colors='b', linewidths=2)
        
        # Plot data points
        ax.scatter(np.exp(data1), np.exp(data2), s=self.markersize, color=self.color)

        ax.set_xlim([xlim_low, xlim_up])
        ax.set_ylim([ylim_low, ylim_up])
        ax.set_xscale('log')
        ax.set_yscale('log')
        ax.set_xlabel(xlabel, fontsize=14)
        ax.set_ylabel(ylabel, fontsize=14)
        ax.grid(True, which="both", ls="--")


# Assume `self.plot_canvas` is your PlotCanvas instance within the MainWindow
plotter = ResultPlotter(self.plot_canvas)

# Generate some random data
np.random.seed(0)  # For reproducible results
x = np.random.rand(100, 8) * 10
x_low_GP = np.random.rand(8) - 1
x_up_GP = np.random.rand(8) + 1

# Plot the results
plotter.plot_results(x, x_low_GP, x_up_GP)
