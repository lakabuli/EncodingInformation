"""
Functions for helping with complicated plots
"""

from cleanplots import *
import numpy as np
from tqdm import tqdm
from matplotlib.colors import LinearSegmentedColormap
import matplotlib
from mpl_toolkits.axes_grid1.inset_locator import inset_axes


def plot_samples(samples, ground_truth, model_names=['Samples'], contrast_cutoff=99):
    """
    Plot ground truth data and samples from model(s).
    
    Parameters
    ----------
    samples : list of np.ndarray
        List of samples from models. Each array represents model output.
    ground_truth : np.ndarray
        Ground truth data for comparison.
    model_names : list of str, optional
        List of names corresponding to each model.
    contrast_cutoff : int, optional
        Percentile to determine contrast cutoff for display. Defaults to 99.
    """

    vmin, vmax = np.percentile(ground_truth.flatten()[:5000], 100 - contrast_cutoff), np.percentile(ground_truth.flatten()[:5000], contrast_cutoff)

    if type(samples) is not list:
        samples = [samples]

    fig, axs = plt.subplots(len(samples) + 1, 8, figsize=(20, 2*(len(samples)+1)))
    
    for row_index, model_samples in enumerate(samples):
        for i, ax in enumerate(axs[row_index]):
            ax.imshow(model_samples[i], cmap='inferno', vmin=vmin, vmax=vmax)
            ax.axis('off')

    # plot ground truth
    for i, ax in enumerate(axs[-1]):
        ax.imshow(ground_truth[i], cmap='inferno', vmin=vmin, vmax=vmax)
        ax.axis('off')

    # set y labels to left of each row by adding new axes
    for i, (ax, name) in enumerate(zip(axs[:, 0], model_names + ['Ground Truth'])):
        ax.text(-0.1, 0.5, name,  transform=ax.transAxes, rotation=90, va='center', ha='center')

def plot_optimization_loss_history(val_loss_history):
    """
    Plot the validation loss history during an optimization process.
    
    Parameters
    ----------
    val_loss_history : list of float
        A list representing the history of validation loss over iterations.
    """

    fig, axs = plt.subplots(1, 1, figsize=(4, 4))
    
    axs.semilogy(val_loss_history, '-o', label='validation', color=get_color_cycle()[1])

    # ylim are 2x the range of the middle 80% of the data
    ylim = np.percentile(val_loss_history, [15, 85])
    diff = ylim[1] - ylim[0]
    ylim = [ylim[0] - diff, ylim[1] + diff]

    xlim = [0, len(val_loss_history)]

    ax_inset = inset_axes(axs, width='75%', height='75%', loc='upper right')
    ax_inset.semilogy(val_loss_history, '-o', label='Zoomed Inset', color=get_color_cycle()[1])
    ax_inset.set(xlim=xlim, ylim=ylim)
    # dont use scientific notation (use scalar formatter)

    # ax_inset.set_xticks([x1, x2])
    # ax_inset.set_yticks([y1, y2])

    axs.set(ylabel='Validation set negative log likelihood', xlabel='Iteration')
    clear_spines(axs)

    x1, x2 = xlim
    y1, y2 = ylim
    axs.plot([x1, x2, x2, x1, x1], [y1, y1, y2, y2, y1], linestyle="dotted", color="grey")
    
def plot_eigenvalues(*args, **kwargs):
    """
    Plot the eigenvalues of a set of covariance matrices.
    
    Parameters
    ----------
    *args : list of np.ndarray
        Covariance matrices to plot eigenvalues from.
    **kwargs : dict
        Named arguments where the name is the label and the value is the covariance matrix.
    """
    fig, axs = plt.subplots(1, 1, figsize=(4, 4))
    
    for i, arg in enumerate(args):
        kwargs[f'{i}'] = arg
    for name in kwargs.keys():
        cov_mat = kwargs[name]
        eig_vals = np.linalg.eigvalsh(cov_mat)
        axs.semilogy(eig_vals, '.-', label=name)
    axs.legend()
    clear_spines(axs)
    axs.set_xlabel('Eigenvalue index')
    axs.set_ylabel('Eigenvalue')


def plot_intensity_coord_histogram(ax, intensities_1, intensities_2, max,  cmap=None, 
                                   bins=50, colors=None, color=None,
                                   plot_center_coords=None, black_background=False, show_colorbar=True, **kwargs):
    """
    Plot 2D histograms of intensity coordinates from two groups of intensities.
    
    Parameters
    ----------
    ax : matplotlib.axes.Axes
        The axis on which to plot.
    intensities_1 : np.ndarray
        Intensity values for the x-axis.
    intensities_2 : np.ndarray
        Intensity values for the y-axis.
    max : float
        Maximum value for the bin edges.
    cmap : matplotlib.colors.Colormap, optional
        Colormap for the histogram.
    bins : int, optional
        Number of bins for the histogram.
    colors : list of str, optional
        List of colors for different intensity groups.
    color : str, optional
        Single color to use if `colors` is not provided.
    plot_center_coords : list of tuple, optional
        List of center coordinates to plot as circles.
    black_background : bool, optional
        Whether to use a black background in the plot.
    **kwargs : dict
        Additional keyword arguments passed to the plotting functions.
    """
    # make sure they are N groups x num samples
    intensities_1 = np.array(intensities_1)
    intensities_2 = np.array(intensities_2)
    intensities_1 = intensities_1.reshape(-1, intensities_1.shape[-1])
    intensities_2 = intensities_2.reshape(-1, intensities_2.shape[-1])

    if colors is None and color is None:
        colors = get_color_cycle()

    bins = np.linspace(0, max, bins)
    hists = []  
    cmaps = []
    cmaps_white = []
    if cmap is not None:
        cmaps.append(cmap)
        hist, xedges, yedges = np.histogram2d(intensities_2.ravel(), intensities_1.ravel(), bins=bins, density=True)
        hist = hist / np.max(hist)
        ax.imshow(cmap(hist), origin='lower', extent=[xedges[0], xedges[-1], yedges[0], yedges[-1]])
        # plot a center point circle
        if plot_center_coords is not None:
            for center_coord in plot_center_coords:
                ax.add_patch(matplotlib.patches.Circle(center_coord, 1, color=cmap(255)))


        ax.set(xlabel='Photons at x1', ylabel='Photons at x2')
        default_format(ax)

    else:
        for sample_points_1, sample_points_2, i in zip(intensities_1, intensities_2, range(intensities_1.shape[0])):
            hist, xedges, yedges = np.histogram2d(sample_points_2, sample_points_1, bins=bins, density=True)
            hists.append(hist)
            if color is None or i == 0:
        
                if not black_background:
                    if colors is not None:
                        cmaps.append(LinearSegmentedColormap.from_list(f'cmap{i}', [(1,1,1), colors[i]]))
                    else:
                        cmaps.append( LinearSegmentedColormap.from_list(f'cmap{i}', [(1,1,1), color]))
                else:
                    if colors is not None:
                        cmaps.append(LinearSegmentedColormap.from_list(f'cmap{i}', [(0, 0, 0, 0), colors[i]]))
                        cmaps_white.append(LinearSegmentedColormap.from_list(f'cmap{i}', [(1, 1, 1), colors[i]]))
                    else:
                        cmaps.append( LinearSegmentedColormap.from_list(f'cmap{i}', [(0,0,0, 0), color]))

        # Compute the color of each bin by blending the colors from the two colormaps
        # loop over all histograms and colormaps
        hists = [hist / np.max(hist) for hist in hists]
        if len(cmaps) > 1:
            if not black_background:
                # blended_color = np.min(np.stack([cmap(hist) for cmap, hist in zip(cmaps, hists)], axis=0), axis=0)
                blended_color = np.prod(np.stack([cmap(hist) for cmap, hist in zip(cmaps, hists)], axis=0), axis=0)
            else:
                color_blend = np.min(np.stack([cmap(hist) for cmap, hist in zip(cmaps_white, hists)], axis=0), axis=0)
                alpha_blend = np.max(np.stack([cmap(hist) for cmap, hist in zip(cmaps, hists)], axis=0), axis=0)
                blended_color = color_blend 
                blended_color[:, :, 3] = alpha_blend[:, :, 3]

        else:
            blended_color = cmaps[0](np.max(hists, axis=0))


        # Make a transparent background
        # add alpha based on luminance
        # 0.2126R + 0.7152G + 0.0722B
        # luminance = blended_color[:, :, 0] * 0.2126 + blended_color[:, :, 1] * 0.7152 + blended_color[:, :, 2] * 0.0722
        # (0.299*R + 0.587*G + 0.114*B)
        # luminance = blended_color[:, :, 0] * 0.299 + blended_color[:, :, 1] * 0.587 + blended_color[:, :, 2] * 0.114
        # sqrt( 0.299*R^2 + 0.587*G^2 + 0.114*B^2 )
        # luminance = np.sqrt(blended_color[:, :, 0]**2 * 0.299 + blended_color[:, :, 1]**2 * 0.587 + blended_color[:, :, 2]**2 * 0.114)


        # Plot the blended color image
        ax.imshow(blended_color, origin='lower', extent=[xedges[0], xedges[-1], yedges[0], yedges[-1]])
        
        # plot a center point circle
        if plot_center_coords is not None:
            for i, plot_center_coord in enumerate(plot_center_coords):                
                ax.add_patch(matplotlib.patches.Circle(plot_center_coord, 1, color=colors[i]))
        
        ax.set(xlabel='Photons at x1', ylabel='Photons at x2')
        clear_spines(ax)

    if show_colorbar:
        add_multiple_colorbars( ax, cmaps)

def add_multiple_colorbars(ax, cmaps):
    """
    Add multiple colorbars to the given axis, each corresponding to a different colormap.
    
    Parameters
    ----------
    ax : matplotlib.axes.Axes
        The axis on which the colorbars will be added.
    cmaps : list of matplotlib.colors.Colormap
        List of colormaps to add colorbars for.
    """
    # Add colorbars for each of the three objects
    # get fig from ax
    fig = ax.get_figure()
    width = 0.04 / len(cmaps)
    for i, cmap in enumerate(cmaps):
        cax = fig.add_axes([0.92 + i*width, 0.1, width, 0.8])  # Adjusted location and size of colorbar axes
        mappable = cm.ScalarMappable(cmap=cmap)
        mappable.set_array([])
        mappable.set_clim(0, 1) 
        cbar = fig.colorbar(mappable, cax=cax, boundaries=np.linspace(0, 1, 256))
        cbar.outline.set_linewidth(0.5)  # Set border line width of colorbar
        cbar.ax.tick_params(width=0.5)  # Set tick width of colorbar

        # Remove ticks for colorbars except the rightmost
        if i < len(cmaps) - 1:
            cbar.set_ticks([])
        else:
            cbar.set_ticks([])  
            cbar.set_label('Probability')  # Set label for the last colorbar



class OverlayedHistograms:
    """
    Class for plotting multiple histograms on the same axis with equal bin sizes.
    
    Attributes
    ----------
    ax : matplotlib.axes.Axes
        Axis to plot the histograms on.
    bins : np.ndarray or None
        Bin edges for the histograms.
    num_bins : int
        Number of bins for the histograms.
    log : bool
        Whether to use a logarithmic scale for the y-axis.
    logx : bool
        Whether to use a logarithmic scale for the x-axis.
    """
    def __init__(self, ax=None, bins=None, num_bins=50, log=True, logx=True):
        self.ax = ax
        self.all_values = []
        self.bins = bins
        self.num_bins = num_bins
        self.labels = []
        self.log = log
        self.logx = logx

    def add(self, values, label=None):
        """
        Add a set of values to the histogram.

        Parameters
        ----------
        values : np.ndarray
            The values to be added to the histogram.
        label : str, optional
            The label for the values.
        """
        self.all_values.append(values)
        self.labels.append(label)
    
    def get_hist_counts(self, eigenvalues):
        """
        Get the histogram counts for a set of eigenvalues.

        Parameters
        ----------
        eigenvalues : np.ndarray
            Eigenvalues to compute the histogram counts for.
        """
        if self.bins is None:
            self.generate_bins()
        counts, _ = np.histogram(eigenvalues, bins=self.bins)
        return counts
    
    def generate_bins(self):
        """
        Generate logarithmic or linear bin edges based on the values added.
        """
        min_value = np.array([np.min(e) for e in self.all_values]).min()
        max_value = np.array([np.max(e) for e in self.all_values]).max()
        if self.logx:
            self.bins = np.logspace(np.log(min_value), np.log(max_value), self.num_bins, base=np.e)
        else:
            self.bins = np.linspace(min_value, max_value, self.num_bins)
        return self.bins
        

    def plot(self, zorder=None, bottom=.5, **kwargs):
        """
        Plot the histograms on the axis.
        
        Parameters
        ----------
        zorder : dict, optional
            Order in which to plot the histograms.
        bottom : float, optional
            Baseline value for the histogram bars.
        **kwargs : dict
            Additional keyword arguments passed to the bar plot.
        """
        if self.bins is None or isinstance(self.bins, int):
            self.generate_bins()
        for eigenvalues, label in zip(self.all_values, self.labels):
            


            # _ = self.ax.hist(eigenvalues, bins=self.bins, log=self.log, label=label, alpha=0.5, 
            #                  zorder=zorder[label] if zorder is not None else 1, bottom=bottom,
            #                  **kwargs)   
            counts = np.histogram(eigenvalues, bins=self.bins)[0]
            counts[counts == 0] = bottom
            _ = self.ax.bar(self.bins[:-1], counts - bottom, width=np.diff(self.bins), log=self.log, label=label, alpha=0.5, 
                zorder=zorder[label] if zorder is not None else 1, bottom=bottom,
                **kwargs)
                              
                                     

        if self.logx:
            self.ax.set(xscale='log')

