import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import gaussian_kde

def plot_95CI_contour(data):
    # Estimate the density with Gaussian KDE
    kde = gaussian_kde(data.T)
    
    # Create grid
    xgrid = np.linspace(data[:,0].min(), data[:,0].max(), 100)
    ygrid = np.linspace(data[:,1].min(), data[:,1].max(), 100)
    X, Y = np.meshgrid(xgrid, ygrid)
    
    # Evaluate density on the grid
    Z = kde(np.vstack([X.ravel(), Y.ravel()])).reshape(X.shape)
    
    # Find the level corresponding to the 95% confidence interval
    # by integrating the density over the grid and finding the appropriate threshold
    t = np.linspace(0, Z.max(), 1000)
    integral = ((Z >= t[:, None, None]) * Z).sum(axis=(1,2)) * (xgrid[1] - xgrid[0]) * (ygrid[1] - ygrid[0])
    cutoff = t[np.where(np.cumsum(integral) >= 0.95 * integral[-1])[0][0]]
    
    # Plot the data and the contour
    plt.figure(figsize=(8, 6))
    plt.scatter(data[:,0], data[:,1], s=5)
    plt.contour(X, Y, Z, levels=[cutoff], colors='red')
    plt.title('95% Confidence Interval Contour')
    plt.xlabel('X')
    plt.ylabel('Y')

# Example data: Generate random data for demonstration
np.random.seed(0)
data = np.random.randn(100, 2)

# Adjust your data format as necessary
plot_95CI_contour(data)
plt.show()
